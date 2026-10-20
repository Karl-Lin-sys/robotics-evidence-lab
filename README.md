# Robotics Evidence Lab

Imagine a little robot carrying a toy across a room.
It needs to **look**, **choose a clear path**, and **move carefully**.
It also needs an honest report card. Practising in the same room as the test
does not tell us how well it will do in a new room.

This is an independent learning project for a robotics engineering role.
It is not a company product, a full robot, or a reproduction of published results.
No employer data, recruitment text, photographs, model weights, or robot recordings
are included.

## Try it

Use Python 3.12. Open a terminal **in this repository folder**.
Run each command separately:

```powershell
python -m venv .venv
```

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

```powershell
.\.venv\Scripts\python.exe demo.py
```

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

The core demo needs only NumPy. Optional PyTorch, TensorFlow, and OpenCV tests
are skipped when their packages are absent. A skip is not a pass.
The exact development environment is recorded in `evidence/environment.txt`.

To run the optional PyTorch and OpenCV checks, install these separately:

```powershell
.\.venv\Scripts\python.exe -m pip install torch==2.14.1 --index-url https://download.pytorch.org/whl/cpu
```

```powershell
.\.venv\Scripts\python.exe -m pip install opencv-python-headless==5.0.0.93
```

For the TensorFlow adapter:

```powershell
.\.venv\Scripts\python.exe -m pip install tensorflow==2.21.0
```

Run the test command again after installing optional packages. These pins describe
this development environment; they are not a Jetson/CUDA compatibility promise.

## What the toy teaches

| Small idea | Implemented behaviour |
|---|---|
| Keep practice and test rooms apart | Manifest audit rejects shared groups or identical file hashes across splits |
| Do not guess how far away a chair is | Stop gate accepts metres; rejects relative-depth units |
| Stop when the picture is old or missing | Invalid depth or stale timestamps cause a simulated stop |
| Leave room for the robot's body | Grid inflation expands obstacles and treats unknown cells as blocked |
| Find a short path | Breadth-first search finds a shortest four-direction route on a static toy map |
| Do not stretch a joint too far | Simulation limiter checks position and speed limits |
| Count the hard tries too | Reports class recall, balanced accuracy, and success by condition |

In the artificial examples, always guessing “clear” earns **99% accuracy** but
finds **none of the obstacles**. Balanced accuracy is **50%**.
Nine easy successes and one hard failure earn **90% overall success**,
but equal weighting of the two conditions gives **50%** and the worst condition
gets **0%**. These are arithmetic examples, not measured robot performance.

## Read the evidence

- [Research comparison and three testable causes](docs/RESEARCH.md)
- [Function costs, evaluation protocol, and hardware gaps](docs/ENGINEERING.md)
- [Publication and Taiwan legal considerations](docs/PUBLICATION.md)
- [Primary source links](docs/SOURCES.md)
- [Recorded synthetic output](evidence/demo.json)
- [Test record](evidence/tests.txt)

**Recommended first experiment:** use a calibrated RGB-D sensor and an offline
recording; evaluate a small perception model separately from navigation. Depth
Anything V2 Small is a research candidate, not an installed dependency or a
source of guaranteed metric distances. See the comparison for trade-offs.

## Honest limits

The code does not implement SLAM, learned locomotion, manipulation, whole-body
dynamics, ROS 2 nodes, EtherCAT, or electrical/thermal integration. Those require
a robot specification, authorised data, calibration, hardware, and independent
validation. The joint limiter is not a balance controller. The depth gate is
not a certified collision-avoidance system.

The supplied job advertisement describes desired skills; it does not identify
a defective algorithm. We can propose and test causes, but cannot claim to have
diagnosed that employer's systems. Leakage, overfitting, selection bias, memory
leaks, and deployment risk cannot be universally “eliminated” by this package.

Original project files are offered under the MIT licence to the extent the
publisher holds applicable rights. Third-party works retain their own terms.
