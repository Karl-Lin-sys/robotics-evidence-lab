"""Original, offline robotics evaluation utilities. Never sends motor commands.

See docs/ENGINEERING.md for assumptions, complexity, and evidence boundaries.
"""
from collections import deque
import hashlib
import math
import numpy as np


def audit_manifest(rows):
    """O(N) expected time/space. Reject group and exact-content split leakage."""
    if not rows:
        raise ValueError("Empty manifest")
    seen_ids, groups, hashes, counts = set(), {}, {}, {}
    for row in rows:
        for key in ("id", "group", "sha256", "split", "condition"):
            if not isinstance(row.get(key), str) or not row[key]:
                raise ValueError(f"Missing string: {key}")
        if row["split"] not in {"train", "validation", "test"}:
            raise ValueError("Unknown split")
        if len(row["sha256"]) != 64 or any(c not in "0123456789abcdef" for c in row["sha256"]):
            raise ValueError("Invalid SHA256")
        if row["id"] in seen_ids:
            raise ValueError("Duplicate sample id")
        seen_ids.add(row["id"])
        for value, registry in ((row["group"], groups), (row["sha256"], hashes)):
            if value in registry and registry[value] != row["split"]:
                raise ValueError("Cross-split group or content leakage")
            registry[value] = row["split"]
        key = row["split"] + "/" + row["condition"]
        counts[key] = counts.get(key, 0) + 1
    if {r["split"] for r in rows} != {"train", "validation", "test"}:
        raise ValueError("All three splits are required")
    return counts


def sha256_file(path):
    """O(B) time, O(1) bounded buffer; hashes actual bytes, not a filename."""
    h = hashlib.sha256()
    with open(path, "rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def depth_stop(depth_m, *, units="metres", stop_distance=0.6,
               age_seconds=0.0, max_age_seconds=0.2):
    """O(P) time/space. Toy full-frame stop gate; unknown pixels cause STOP."""
    if units != "metres":
        raise ValueError("Relative depth cannot be used as metric distance")
    values = (stop_distance, age_seconds, max_age_seconds)
    if not all(math.isfinite(v) for v in values) or stop_distance <= 0 or max_age_seconds <= 0:
        raise ValueError("Invalid gate configuration")
    depth = np.asarray(depth_m)
    if depth.ndim != 2 or depth.size == 0:
        raise ValueError("Expected a non-empty depth image")
    if age_seconds < 0 or age_seconds > max_age_seconds:
        return {"stop": True, "reason": "invalid_or_stale_timestamp"}
    if not np.isfinite(depth).all() or np.any(depth <= 0):
        return {"stop": True, "reason": "unknown_depth"}
    distance = float(depth.min())
    return {"stop": distance <= stop_distance, "reason": "distance",
            "nearest_metres": distance}


def inflate_grid(grid, radius=1):
    """O(V*(r+1)^2) time; O((H+2r)*(W+2r)) space. Unknown/outside is blocked."""
    grid = np.asarray(grid)
    if grid.ndim != 2 or grid.size == 0 or not np.isin(grid, [-1, 0, 1]).all():
        raise ValueError("Grid must contain -1 unknown, 0 free, 1 blocked")
    if not isinstance(radius, int) or radius < 0:
        raise ValueError("radius must be a non-negative integer")
    h, w = grid.shape
    if radius >= max(h, w):
        return np.ones_like(grid, dtype=bool)
    padded = np.pad(grid != 0, radius, constant_values=True)
    blocked = np.zeros((h, w), dtype=bool)
    for dy in range(2 * radius + 1):
        for dx in range(2 * radius + 1):
            blocked |= padded[dy:dy + h, dx:dx + w]
    return blocked


def plan_route(blocked, start, goal):
    """BFS on a static 4-connected unit-cost grid: O(V+E) time, O(V) space."""
    blocked = np.asarray(blocked)
    if blocked.ndim != 2 or blocked.dtype != np.bool_ or not blocked.size:
        raise ValueError("Expected non-empty Boolean blocked grid")
    h, w = blocked.shape
    for point in (start, goal):
        if len(point) != 2 or any(not isinstance(v, (int, np.integer)) for v in point):
            raise ValueError("Coordinates must be integer pairs")
        if not (0 <= point[0] < h and 0 <= point[1] < w):
            raise ValueError("Endpoint outside map")
    start, goal = tuple(start), tuple(goal)
    if blocked[start] or blocked[goal]:
        return None
    queue, parent = deque([start]), {start: None}
    while queue:
        current = queue.popleft()
        if current == goal:
            path = []
            while current is not None:
                path.append(current)
                current = parent[current]
            return path[::-1]
        y, x = current
        for point in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
            yy, xx = point
            if 0 <= yy < h and 0 <= xx < w and not blocked[point] and point not in parent:
                parent[point] = current
                queue.append(point)
    return None


def joint_step(position, target, lower, upper, max_speed, dt):
    """O(J) time/space. Simulation-only position/velocity limiter, not WBC."""
    arrays = [np.asarray(a, dtype=float) for a in (position, target, lower, upper, max_speed)]
    q, target, lo, hi, speed = arrays
    if q.ndim != 1 or not q.size or any(a.shape != q.shape for a in arrays):
        raise ValueError("Joint vectors must have the same non-empty shape")
    if any(not np.isfinite(a).all() for a in arrays) or not math.isfinite(dt) or dt <= 0:
        raise ValueError("Non-finite input or invalid dt")
    if np.any(lo > hi) or np.any(speed <= 0) or np.any(q < lo) or np.any(q > hi):
        raise ValueError("Invalid limits or starting position")
    if np.any(target < lo) or np.any(target > hi):
        raise ValueError("Target exceeds joint limits")
    return np.clip(q + np.clip(target - q, -speed * dt, speed * dt), lo, hi)


def classification_report(y_true, y_pred, classes):
    """O(N+C^2) time/space (inputs included). Missing classes stay undefined."""
    yt, yp = np.asarray(y_true), np.asarray(y_pred)
    if not isinstance(classes, int) or classes < 2 or yt.ndim != 1 or yt.shape != yp.shape or not yt.size:
        raise ValueError("Invalid class count or labels")
    if yt.dtype.kind not in "iu" or yp.dtype.kind not in "iu":
        raise ValueError("Integer labels required")
    if np.any(yt < 0) or np.any(yp < 0) or np.any(yt >= classes) or np.any(yp >= classes):
        raise ValueError("Label out of range")
    # Prevent int8/int16 multiplication overflow in flattened matrix indices.
    yt, yp = yt.astype(np.int64, copy=False), yp.astype(np.int64, copy=False)
    cm = np.bincount(yt * classes + yp, minlength=classes * classes).reshape(classes, classes)
    support, predicted = cm.sum(1), cm.sum(0)
    recall, f1 = [], []
    for k in range(classes):
        recall.append(float(cm[k, k] / support[k]) if support[k] else None)
        denom = support[k] + predicted[k]
        f1.append(float(2 * cm[k, k] / denom) if denom else None)
    complete = bool(np.all(support > 0))
    return {"confusion_matrix": cm.tolist(), "support": support.tolist(),
            "accuracy": float(np.trace(cm) / yt.size), "recall": recall, "f1": f1,
            "balanced_accuracy": float(np.mean(recall)) if complete else None,
            "macro_f1": float(np.mean(f1)) if complete else None,
            "complete_class_coverage": complete}


def episode_report(episodes):
    """O(N) expected time/space. One row per attempt; failures remain in denominator."""
    if not episodes:
        raise ValueError("No episodes")
    ids, groups = set(), {}
    for e in episodes:
        if e["id"] in ids or not isinstance(e["success"], bool) or not e["condition"]:
            raise ValueError("Duplicate episode or invalid record")
        ids.add(e["id"])
        groups.setdefault(e["condition"], []).append(int(e["success"]))
    rates = {g: sum(v) / len(v) for g, v in groups.items()}
    return {"attempts": len(episodes), "success_rate": sum(e["success"] for e in episodes) / len(episodes),
            "condition_counts": {g: len(v) for g, v in groups.items()},
            "condition_success": rates, "equal_condition_success": sum(rates.values()) / len(rates),
            "worst_condition_success": min(rates.values())}
