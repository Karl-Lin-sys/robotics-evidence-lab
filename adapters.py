"""Small API examples, based only on the linked official framework documentation.

These accept caller-supplied models and preprocessing. They do not reproduce any
paper, download checkpoints, infer calibration, or connect to a robot.
"""
import numpy as np


def torch_predict(model, batch, device="cpu"):
    """O(W+F+I+O) time, O(W+A+I+O) space; move/setup once in production."""
    import torch
    model = model.to(device).eval()
    with torch.inference_mode():
        result = model(batch.to(device))
        if not isinstance(result, torch.Tensor):
            raise TypeError("Adapter requires a single tensor output")
        return result.cpu().numpy()


def make_tf_predictor(model, input_shape):
    """One traced function; O(1) wrapper setup plus lazy trace/model costs."""
    import tensorflow as tf

    @tf.function(input_signature=[tf.TensorSpec(input_shape, tf.float32)])
    def predict(batch):
        """O(F) time, O(W+A+I+O) space; fixed signature limits retracing."""
        return model(batch, training=False)
    return predict


def process_video(path, consume, max_frames=300):
    """O(T*(decode+P+callback)) time, O(P+callback space), no frame history."""
    import cv2
    if not isinstance(max_frames, int) or max_frames < 1:
        raise ValueError("max_frames must be positive")
    capture = cv2.VideoCapture(str(path))
    try:
        if not capture.isOpened():
            raise OSError("Cannot open video")
        count = 0
        while count < max_frames:
            ok, bgr = capture.read()
            if not ok:
                break
            rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
            consume(rgb)  # Consumer must not keep an unbounded history.
            count += 1
        return count
    finally:
        capture.release()
