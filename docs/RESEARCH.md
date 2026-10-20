# Evidence-based selection

Review date: 20 October 2026, Asia/Taipei. Technology window:
20 October 2023–20 October 2026. Diagnostic evidence window:
20 October 2021–20 October 2026. Dates refer to the peer-reviewed conference
version, not the first preprint upload. RSS is included as a leading robotics
conference under the request's “etc.” scope.

Only proceedings, author-maintained repositories, official framework references,
and official Taiwan law pages are used. The latter are necessary for the separate
legal question. No blog, forum, or unreviewed preprint supports a research claim.
No resolved issue is cited because no matching framework defect was diagnosed.

## Compare by job, not by an unrelated leaderboard

Stars below were queried directly from GitHub's API on the review date.
Full commit SHAs are in `evidence/repositories.json`. They rank this bounded
shortlist, not every repository on GitHub. Stars indicate attention, not
reproducibility, correctness, commercial permission, or job suitability.

| Candidate and conference | Stars | What it contributes | Main limitation and decision |
|---|---:|---|---|
| [Depth Anything V2](SOURCES.md#p2), NeurIPS 2024 | 9,000 | Single-image depth; released models and inference examples | Relative output is not metres. Start with Small for an offline perception experiment; separately validate metric models/calibration. |
| [Depth Anything](SOURCES.md#p1), CVPR 2024 | 8,241 | Earlier monocular-depth baseline | Useful controlled V1/V2 comparison; no measured local winner is claimed. |
| [SplaTAM](SOURCES.md#p3), CVPR 2024 | 2,213 | RGB-D tracking and dense mapping using 3D Gaussians | Requires depth and camera assumptions; GPU/runtime and growing-map costs must be measured. Compare in a separate SLAM experiment. |
| [ASAP](SOURCES.md#p5), RSS 2025 | 2,130 | Learning whole-body skills while compensating for simulation/real dynamics mismatch | Requires motion data, a simulator, and real robot experience. Research direction for locomotion/WBC; not a drop-in Python joint controller. |
| [OK-Robot](SOURCES.md#p4), RSS 2024 | 617 | Integrates perception, navigation, and grasping for mobile manipulation | Lower-star integration reference retained for task fit; dependency and hardware requirements differ from depth systems. |

These systems solve different problems. Comparing their headline accuracy or
success numbers as if they share one dataset would be misleading. The official
repositories provide code/configuration entry points, but this project has not
reproduced their paper tables. Commit pinning helps locate an implementation;
it does not freeze upstream weights, datasets, CUDA, or simulator licences.

Our engineering recommendation is to build an observable RGB-D baseline first.
Use PyTorch for the selected depth research ecosystem; use OpenCV for bounded
video decoding. TensorFlow is an alternative inference backend when the chosen
model has a supported TensorFlow implementation. Running both model frameworks
in the same robot process has no demonstrated benefit here.

Depth Anything V2's authors report improved fine detail and robustness. Its
Small checkpoint is Apache-2.0; Base/Large/Giant checkpoints are CC-BY-NC-4.0.
The repository's top-level licence must not be mistaken for every weight's
licence. [Paper and official implementation](SOURCES.md#p2)

## Exactly three candidate causes and concrete remedies

These are **testable hypotheses**, not findings about the employer.

1. **Practice scenes leak into testing, or a model learns the room instead of the task.**
   Consecutive video frames share information; a random frame split can give an
   unrealistically easy test. Group complete sites/sessions before any training.
   Keep augmentation descendants with their originals. `audit_manifest` rejects
   cross-split groups and exact hashes; `sha256_file` computes hashes from bytes.
   Use held-out sites and validation-only checkpoint selection. SWAD supplies
   recent peer-reviewed evidence on overfitting and domain generalization;
   its flat-minimum argument is not a guarantee for this robot. Our grouping
   policy is an engineering safeguard, not an implementation of SWAD.
   **Test:** compare a deliberately leaky split against site-disjoint splits;
   inspect per-site error and report repeated-seed variation. If the gap remains,
   investigate sensor/scene shift rather than declaring leakage the sole cause.
   [NeurIPS 2021 SWAD](SOURCES.md#p6)

2. **The test contains many easy cases and too few rare obstacles or difficult rooms.**
   Overall accuracy estimates performance under the sampled mixture:
   `accuracy = sum(class_prevalence * class_recall)`. A rare class can fail
   completely while that average stays high. `classification_report` exposes
   support, confusion counts, per-class recall/F1, and equal-class averages.
   `episode_report` counts every attempt and reports equal-condition and worst-
   condition success. Missing classes leave aggregate class metrics undefined.
   Collect more independent rare-condition episodes; keep natural-prevalence
   and balanced summaries side by side. The 2023 re-sampling paper shows why
   balancing alone can preserve or amplify irrelevant context correlations.
   **Test:** cross class and background/lighting conditions; compare training
   interventions only on validation groups. Confirm on untouched test groups.
   Equal weighting changes the target quantity; it does not remove selection
   bias from unobserved conditions. [NeurIPS 2023 re-sampling](SOURCES.md#p7)

3. **The controller receives a representation or dynamics model that does not match reality.**
   A relative depth map cannot justify metre-based clearance. A static grid
   cannot represent moving people, and a joint limit cannot maintain balance.
   Keep metric depth, time, camera frame, and calibration explicit. `depth_stop`
   rejects relative units and stale/unknown inputs; grid inflation uses a stated
   footprint; `joint_step` enforces only position and velocity in simulation.
   ASAP provides evidence that simulation/real dynamics mismatch matters and
   studies a residual-action remedy. Use that approach only after a validated
   robot/simulator/data pipeline exists. **Test:** replay timestamp delays,
   missing depth, changed calibration, friction and payload shifts; measure
   perception, planning, and tracking failures separately. A corrected depth
   scale does not solve missing geometry or locomotion dynamics.
   [Depth V2](SOURCES.md#p2), [ASAP](SOURCES.md#p5)

## What would justify a model choice?

Use the same held-out episodes, calibration, input resolution, machine, precision,
and warm-up policy. Fix thresholds on validation data before opening test data.
Record depth error in metres where valid metric ground truth exists, invalid-depth
coverage, navigation success/collisions/timeouts, and per-condition counts.
Report p50/p95/p99 end-to-end latency, deadline misses, peak resident/device memory,
and power/temperature on the target device. Compare paired episodes and bootstrap
at the independent site/session level, not individual frames.

No measured speed, accuracy, power, memory-leak freedom, or superiority of a
research candidate is claimed by this release.
