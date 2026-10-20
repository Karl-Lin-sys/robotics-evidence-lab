"""Run with python demo.py. All data are artificial."""
import json
import numpy as np
from robotics import (inflate_grid, plan_route, depth_stop, joint_step,
                      classification_report, episode_report)


def main():
    """Costs are the sum of called functions; this fixture has fixed small size."""
    grid = np.zeros((9, 9), dtype=int)
    grid[4, 2:6] = 1
    path = plan_route(inflate_grid(grid, radius=1), (1, 1), (7, 7))
    output = {
        "data": "synthetic; not a robot benchmark",
        "route": path,
        "route_steps": len(path) - 1 if path else None,
        "valid_depth": depth_stop(np.full((4, 4), 2.0)),
        "invalid_depth": depth_stop(np.full((4, 4), np.nan)),
        "joint_step": joint_step([0.0], [0.8], [-1.0], [1.0], [0.5], 0.1).tolist(),
        "imbalanced_example": classification_report([0] * 99 + [1], [0] * 100, 2),
        "episodes": episode_report([
            {"id": f"bright-{i}", "condition": "bright", "success": True} for i in range(9)
        ] + [{"id": "dark-0", "condition": "dark", "success": False}]),
    }
    print(json.dumps(output, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
