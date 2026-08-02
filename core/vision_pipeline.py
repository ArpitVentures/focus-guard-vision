"""
FocusGuard AI - Core Vision Pipeline Engine (Service Layer)
"""
from typing import Tuple, cast
import numpy as np

from tracking.face_mesh import FaceMeshDetector
from tracking.eye_tracker import EyeTracker
from tracking.head_pose import HeadPoseEstimator
from analytics.focus_engine import FocusEngine
from core.datatypes import EyeMetrics, FocusTelemetry
from utils.logger import logger


class VisionPipeline:
    """
    Centralized Vision Processing Service that orchestrates Face Mesh,
    Eye Analytics, Head Pose Estimation, and Focus Telemetry computation.
    """
    def __init__(self):
        self.mesh_detector = FaceMeshDetector()
        self.eye_tracker = EyeTracker()
        self.pose_estimator = HeadPoseEstimator()
        self.focus_engine = FocusEngine()
        logger.info("VisionPipeline core service initialized successfully.")

    def process_frame(self, frame: np.ndarray) -> Tuple[np.ndarray, FocusTelemetry, bool]:
        """
        Executes complete AI pipeline on a single frame.
        Returns: (display_frame_with_mesh, focus_telemetry, face_detected)
        """
        frame_shape = cast(Tuple[int, int, int], frame.shape)

        # 1. Landmark Mesh Inference
        face_data, results = self.mesh_detector.process_frame(frame)
        display_frame = self.mesh_detector.draw_mesh(
            frame, results, draw_tessellation=False, draw_contours=True
        )

        # 2. Extract Telemetry
        if face_data.face_detected:
            eye_metrics = self.eye_tracker.process(face_data.pixel_landmarks)
            head_pose = self.pose_estimator.process(face_data.pixel_landmarks, frame_shape)
        else:
            eye_metrics = EyeMetrics()
            head_pose = self.pose_estimator.process([], frame_shape)

        # 3. Compute Priority & Focus Score
        focus_telemetry = self.focus_engine.compute(
            face_data.face_detected, eye_metrics, head_pose
        )

        return display_frame, focus_telemetry, face_data.face_detected

    def release(self):
        """Releases internal C++ MediaPipe bindings cleanly."""
        self.mesh_detector.release()
        logger.info("VisionPipeline resources released.")