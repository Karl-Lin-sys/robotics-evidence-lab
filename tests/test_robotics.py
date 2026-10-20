import hashlib
import tempfile
from pathlib import Path
import unittest
import numpy as np
from robotics import *


class RoboticsTests(unittest.TestCase):
    def test_split_group_and_duplicate_bytes(self):
        rows = [{"id": str(i), "group": str(i), "split": split, "condition": "room",
                 "sha256": hashlib.sha256(str(i).encode()).hexdigest()}
                for i, split in enumerate(("train", "validation", "test"))]
        self.assertEqual(len(audit_manifest(rows)), 3)
        for key in ("group", "sha256"):
            altered = [dict(r) for r in rows]
            altered[2][key] = altered[0][key]
            with self.assertRaises(ValueError):
                audit_manifest(altered)

    def test_hash_bytes(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "sample"
            p.write_bytes(b"robot")
            self.assertEqual(sha256_file(p), hashlib.sha256(b"robot").hexdigest())

    def test_depth_fails_closed(self):
        for image in (np.array([[0.0]]), np.array([[np.nan]]), np.array([[np.inf]])):
            self.assertTrue(depth_stop(image)["stop"])
        self.assertTrue(depth_stop([[2.0]], age_seconds=0.3)["stop"])
        self.assertTrue(depth_stop([[2.0]], age_seconds=-0.1)["stop"])
        self.assertTrue(depth_stop([[0.6]])["stop"])
        self.assertFalse(depth_stop([[0.61]])["stop"])
        with self.assertRaises(ValueError):
            depth_stop([[2.0]], units="relative")

    def test_inflation_blocks_unknown_and_edges(self):
        g = np.zeros((7, 7), int)
        g[3, 3] = -1
        b = inflate_grid(g)
        self.assertTrue(b[2:5, 2:5].all())
        self.assertTrue(b[0].all())
        self.assertFalse(b[1, 1])

    def test_shortest_path_and_no_path(self):
        g = np.zeros((5, 5), dtype=bool)
        self.assertEqual(len(plan_route(g, (0, 0), (4, 4))) - 1, 8)
        g[2, :] = True
        self.assertIsNone(plan_route(g, (0, 0), (4, 4)))
        self.assertIsNone(plan_route(g, (2, 0), (4, 4)))

    def test_routes_never_cross_blocked_cells(self):
        rng = np.random.default_rng(42)
        for _ in range(30):
            g = rng.random((10, 10)) < 0.15
            g[0, 0] = g[9, 9] = False
            path = plan_route(g, (0, 0), (9, 9))
            if path:
                self.assertTrue(all(not g[p] for p in path))
                self.assertTrue(all(abs(a[0]-b[0])+abs(a[1]-b[1]) == 1 for a, b in zip(path, path[1:])))

    def test_joint_bounds_and_bad_commands(self):
        q = joint_step([0], [1], [-1], [1], [0.5], 0.1)
        np.testing.assert_allclose(q, [0.05])
        for target in ([2], [np.nan]):
            with self.assertRaises(ValueError):
                joint_step([0], target, [-1], [1], [0.5], 0.1)

    def test_imbalance_and_missing_class(self):
        report = classification_report([0] * 99 + [1], [0] * 100, 2)
        self.assertEqual(report["accuracy"], 0.99)
        self.assertEqual(report["balanced_accuracy"], 0.5)
        self.assertEqual(report["recall"][1], 0)
        self.assertIsNone(classification_report([0], [0], 2)["balanced_accuracy"])
        with self.assertRaises(ValueError):
            classification_report([0.2], [0], 2)

    def test_episodes_include_rare_failures(self):
        data = [{"id": str(i), "condition": "easy", "success": True} for i in range(9)]
        data.append({"id": "hard", "condition": "hard", "success": False})
        report = episode_report(data)
        self.assertEqual(report["success_rate"], 0.9)
        self.assertEqual(report["equal_condition_success"], 0.5)
        self.assertEqual(report["worst_condition_success"], 0)
        with self.assertRaises(ValueError):
            episode_report(data + data)

    def test_small_integer_labels_do_not_overflow(self):
        report = classification_report(np.array([19], dtype=np.int8),
                                       np.array([19], dtype=np.int8), 20)
        self.assertEqual(report["confusion_matrix"][19][19], 1)
        self.assertEqual(report["accuracy"], 1.0)


if __name__ == "__main__":
    unittest.main()
