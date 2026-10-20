import importlib.util
from pathlib import Path
import tempfile
import unittest
import numpy as np
from adapters import torch_predict, make_tf_predictor, process_video


class AdapterTests(unittest.TestCase):
    @unittest.skipUnless(importlib.util.find_spec("torch"), "PyTorch unavailable")
    def test_torch_eval_and_no_graph(self):
        import torch
        model = torch.nn.Sequential(torch.nn.Linear(3, 2), torch.nn.Dropout(0.8))
        batch = torch.ones(4, 3, requires_grad=True)
        a, b = torch_predict(model, batch), torch_predict(model, batch)
        np.testing.assert_array_equal(a, b)
        self.assertFalse(model.training)
        self.assertIsNone(batch.grad)

    @unittest.skipUnless(importlib.util.find_spec("tensorflow"), "TensorFlow unavailable")
    def test_tf_fixed_signature(self):
        import tensorflow as tf
        model = tf.keras.Sequential([tf.keras.layers.Input((3,)), tf.keras.layers.Dense(2),
                                     tf.keras.layers.Dropout(0.8)])
        predict = make_tf_predictor(model, [None, 3])
        a = predict(tf.ones([2, 3])).numpy()
        b = predict(tf.ones([2, 3])).numpy()
        np.testing.assert_array_equal(a, b)
        predict(tf.ones([4, 3]))
        self.assertEqual(predict.experimental_get_tracing_count(), 1)

    @unittest.skipUnless(importlib.util.find_spec("cv2"), "OpenCV unavailable")
    def test_video_stream(self):
        import cv2
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "toy.avi"
            writer = cv2.VideoWriter(str(p), cv2.VideoWriter_fourcc(*"MJPG"), 5, (16, 16))
            self.assertTrue(writer.isOpened())
            try:
                for _ in range(5):
                    writer.write(np.full((16, 16, 3), (0, 0, 255), np.uint8))
            finally:
                writer.release()
            means = []
            self.assertEqual(process_video(p, lambda rgb: means.append(rgb.mean(axis=(0, 1))), 3), 3)
            self.assertTrue(all(m[0] > 240 and m[2] < 10 for m in means))
            def fail(_):
                raise RuntimeError("consumer failed")
            with self.assertRaises(RuntimeError):
                process_video(p, fail)
            # Re-opening and deleting checks the normal file lifecycle on Windows.
            self.assertEqual(process_video(p, lambda _: None), 5)
            p.unlink()
