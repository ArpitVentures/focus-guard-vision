"""
FocusGuard AI - 3D Head Pose & Looking Away Estimator
"""
import cv2
import numpy as np
import time
from typing import List, Tuple
from utils.logger import logger
from core.datatypes import HeadPoseMetrics


class HeadPoseEstimator:
    """
    Estimates 3D head rotation angles (Pitch, Yaw, Roll) using OpenCV solvePnP.
    """
    NOSE_TIP = 1
    CHIN = 152
    LEFT_EYE_CORNER = 33
    RIGHT_EYE_CORNER = 263
    LEFT_MOUTH_CORNER = 61
    RIGHT_MOUTH_CORNER = 291

    MODEL_POINTS_3D = np.array([
        (0.0, 0.0, 0.0),             # Nose tip
        (0.0, -330.0, -65.0),        # Chin
        (-225.0, 170.0, -135.0),     # Left eye corner
        (225.0, 170.0, -135.0),      # Right eye corner
        (-150.0, -150.0, -125.0),    # Left mouth corner
        (150.0, -150.0, -125.0)      # Right mouth corner
    ], dtype=np.float64)

    def __init__(
        self,
        yaw_threshold: float = 25.0,
        pitch_threshold: float = 20.0,
        looking_away_time_threshold: float = 1.0
    ):
        self.yaw_threshold = yaw_threshold
        self.pitch_threshold = pitch_threshold
        self.looking_away_time_threshold = looking_away_time_threshold
        self.looking_away_start_time = None
        logger.info("HeadPoseEstimator engine initialized successfully.")

    def process(self, pixel_landmarks: List[Tuple[int, int]], frame_shape: Tuple[int, int, int]) -> HeadPoseMetrics:
        """Calculates Pitch, Yaw, Roll angles and determines looking away state."""
        metrics = HeadPoseMetrics()

        if not pixel_landmarks or len(pixel_landmarks) < 468:
            return metrics

        h, w, _ = frame_shape

        image_points_2d = np.array([
            pixel_landmarks[self.NOSE_TIP],
            pixel_landmarks[self.CHIN],
            pixel_landmarks[self.LEFT_EYE_CORNER],
            pixel_landmarks[self.RIGHT_EYE_CORNER],
            pixel_landmarks[self.LEFT_MOUTH_CORNER],
            pixel_landmarks[self.RIGHT_MOUTH_CORNER]
        ], dtype=np.float64)

        focal_length = w
        center = (w / 2.0, h / 2.0)
        camera_matrix = np.array([
            [focal_length, 0, center[0]],
            [0, focal_length, center[1]],
            [0, 0, 1]
        ], dtype=np.float64)

        dist_coeffs = np.zeros((4, 1), dtype=np.float64)

        success, rotation_vec, translation_vec = cv2.solvePnP(
            self.MODEL_POINTS_3D,
            image_points_2d,
            camera_matrix,
            dist_coeffs,
            flags=cv2.SOLVEPNP_ITERATIVE
        )

        if not success:
            return metrics

        rotation_mat, _ = cv2.Rodrigues(rotation_vec)
        pose_mat = np.hstack((rotation_mat, translation_vec))
        _, _, _, _, _, _, euler_angles = cv2.decomposeProjectionMatrix(pose_mat)

        metrics.pitch = float(euler_angles[0][0])
        metrics.yaw = float(euler_angles[1][0])
        metrics.roll = float(euler_angles[2][0])

        current_time = time.time()

        if abs(metrics.yaw) > self.yaw_threshold or abs(metrics.pitch) > self.pitch_threshold:
            if self.looking_away_start_time is None:
                self.looking_away_start_time = current_time

            metrics.looking_away_duration_sec = current_time - self.looking_away_start_time

            if metrics.looking_away_duration_sec >= self.looking_away_time_threshold:
                metrics.is_looking_away = True
        else:
            self.looking_away_start_time = None
            metrics.is_looking_away = False

        return metrics
