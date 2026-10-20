# Validation record

20 October 2026. Windows, Python 3.12, CPU execution.

- `python -m unittest discover -s tests -v`: **13 passed, 0 skipped**.
- PyTorch 2.14.1+cpu: evaluation mode and deterministic dropout-disabled output checked.
- TensorFlow 2.21.0: fixed input signature, evaluation output, and batch-size reuse checked.
- OpenCV 5.0.0.93: synthetic video decoding, BGR/RGB conversion, frame limit,
  callback exception, re-opening and file deletion checked.
- Core checks: cross-split group/hash leakage, actual file hashing, unknown/stale
  depth, obstacle inflation, routes/no-route, joint limits, class imbalance,
  missing-class reporting, narrow integer labels, and failed episode inclusion.
- `python -m pip check`: no broken requirements.
- `python demo.py`: saved in `demo.json`.
- Python compilation and local Markdown file targets checked.

The first run skipped TensorFlow before it was installed. The final recorded
run includes it. Exact packages are in `environment.txt`, raw test output in
`tests.txt`. Tests use artificial data and small framework models, not research
checkpoints. No GPU, Jetson, ROS 2, physical sensor, robot, or paper benchmark was
tested. No long-run native memory-leak or real-time deadline claim is made.
