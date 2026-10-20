# Implementation and evaluation

## Scope against the role

| Role area | Delivered | Still requires target hardware and data |
|---|---|---|
| Perception | Depth validity/unit/age gate; framework adapters | Camera/LiDAR/LWIR/IMU drivers, extrinsics, time sync, trained model evaluation |
| Planning/navigation | Static occupancy grid inflation and shortest route | SLAM, state estimation, dynamic obstacles, ROS 2 integration, executable trajectory |
| Locomotion/manipulation/WBC | Joint position/velocity limiter in simulation; research comparison | Dynamics, contact, balance, torque/current limits, grasping and robot-specific control |
| Hardware integration | Explicit deployment acceptance plan | Optical, mechanical, electrical, power, battery, communication and thermal design |

The grid in `demo.py` is hand-authored. It is **not** reconstructed from its depth
image. Connecting those components needs projection, intrinsics/extrinsics,
robot pose, floor/height filtering, free-space ray tracing, and treatment of
occlusions. The demo keeps this missing transformation visible.

## Big-O for every production function

N = records/labels; B = file bytes; P = image pixels; V = grid cells;
E = grid edges (at most 4V); r = footprint radius in cells; J = joints;
C = class count; T = decoded frames; W = model parameters; F = model forward
operation count; A = peak live activations; I/O = input/output tensor sizes.
Expected dictionary/set access assumes ordinary non-adversarial hashing.

| Function | Time | Extra/live space and explanation |
|---|---|---|
| `audit_manifest` | O(N) expected | O(N), identifiers and split maps; string lengths assumed bounded |
| `sha256_file` | O(B) | O(1), fixed 1 MiB chunk; caller must verify actual file hashes |
| `depth_stop` | O(P) | O(P), vector masks; no temporal history |
| `inflate_grid` | O(V(r+1)²) | O((H+2r)(W+2r)); huge radius returns all blocked |
| `plan_route` | O(V+E) | O(V), queue and parent map; BFS optimal only for unit edge costs |
| `joint_step` | O(J) | O(J), validated arrays and output |
| `classification_report` | O(N+C²) | O(N+C²), converted labels and confusion matrix |
| `episode_report` | O(N) expected | O(N), duplicate detection and condition lists |
| `torch_predict` | O(W+F+I+O) | O(W+A+I+O); one device move/setup per call in this simple adapter |
| `make_tf_predictor` | O(1) wrapper creation | Graph/model-specific tracing and allocation occur on first call |
| returned TensorFlow `predict` | O(F+I+O) | O(W+A+I+O), graph-specific; signature avoids shape-based re-tracing for batch size |
| `process_video` | O(T × (decode + P + callback)) | O(P + decoder buffers + callback state), provided callback discards frames |
| `demo.main` | Sum of calls above | Fixed fixture size in this demo; not a scaling benchmark |

The simple radius loop is transparent but not optimal for very large footprints.
For a long narrow grid, padding costs O((H+2r)(W+2r)); the
inflation space bound is O(V + r(H+W) + r²), not universally O(V).
The time bound includes that padding cost. Use a footprint appropriate to the
robot and measured map resolution. At radius 0, inflation costs O(V).

Model operation count cannot honestly be expressed solely as “O(pixels)” for an
arbitrary neural network. Attention, feature width, token count, output resolution,
and precision affect compute and memory. For full attention with L tokens and
width D, the attention matrix alone is O(L²) storage and O(L²D) work.
These are algorithmic deductions, not measured paper reproduction results.

## Memory and performance practices

The PyTorch example uses `eval()` and `inference_mode()` together: disabling
autograd does not itself switch dropout/batch-normalization to evaluation.
For repeated production inference, prepare the model on its device once.
Returned NumPy outputs must not be accumulated forever by the caller.
The TensorFlow example builds one `tf.function` with an input signature and uses
`training=False`. Do not create it anew for every frame.
The OpenCV example decodes one frame at a time and releases capture in `finally`,
including callback exceptions. RGB conversion is explicit; model-specific
normalisation and resizing remain the caller's responsibility.
See [official API sources](SOURCES.md#frameworks).

These choices avoid specific retention and lifecycle mistakes. They do not prove
the absence of native allocator leaks. Profile a long run with fixed shapes;
separate allocator caching from continuously growing live memory. CUDA timing
requires correct synchronization. No GPU timing result is supplied here.

## Evaluation contract

1. Obtain authorised recordings and independent ground truth. Record site,
   session, sensor, lighting, surface, object class, and failure/timeout status.
2. Assign site groups to train/validation/test before preprocessing. If the same
   site spans multiple sessions, a session-only split is insufficient for a
   new-site claim. Store original-content hashes and augmentation parent IDs.
3. Run the manifest audit; recompute hashes with `sha256_file`. The auditor trusts
   supplied metadata and cannot detect all near-duplicates or pretrained-data
   overlap. Review those separately.
4. Use training only for fitting. Choose checkpoint, stopping rule, threshold and
   hyperparameters with validation only. Lock test labels from repeated tuning.
   Log every experiment, seeds, model/config hashes, and any test access.
5. Report all attempted episodes, including sensor failure, no route, timeout,
   collision, and rejected commands. A missing condition is not a successful one.
   Classification summaries are not substitutes for detection AP, depth error,
   navigation metrics, or control tracking error.
6. Publish condition coverage, repeated-seed spread, and uncertainty across
   independent groups. Bootstrap/confidence intervals are a protocol requirement
   for a future dataset, not implemented or estimated from this tiny demo.

## Deployment acceptance plan

Before connecting to ROS 2, define coordinate frames, metre/radian units, a
monotonic clock, synchronization tolerances, and bounded message queues. Test
sensor dropout and restart. Before EtherCAT/motor use, obtain a verified robot
model, actuator limits, controller frequency, watchdog and emergency-stop design.
Validate mechanical clearances, power/battery limits, thermal throttling, and
communication failure response on the target system. This is an engineering
plan, not a claim that the three permitted framework docs specify those systems.

For a real depth stop gate, derive clearance from geometry and stopping distance:
`margin + speed * latency + speed² / (2 * deceleration)` under stated constant-
deceleration assumptions. The demo's 0.6 m / 0.2 s values are illustrative only.
Camera rays do not prove the whole swept volume is clear; full-frame minimum
depth can also stop on the floor. Unknown cells stay blocked, which can make a
route unavailable. No route must remain a reported failure, not be silently
removed from an evaluation.
