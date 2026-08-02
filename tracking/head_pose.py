import time
from typing import List, Tuple

import cv2
import numpy as np

from core.datatypes import HeadPoseMetrics
from utils.logger import logger


class HeadPoseEstimator:
    NOSE_TIP = 1
    CHIN = 152
    LEFT_EYE_CORNER = 33
    RIGHT_EYE_CORNER = 263
    LEFT_MOUTH_CORNER = 61
    RIGHT_MOUTH_CORNER = 291

    MODEL_POINTS_3D = np.array(
        [
            (0.0, 0.0, 0.0),
            (0.0, -330.0, -65.0),
            (-225.0, 170.0, -135.0),
            (225.0, 170.0, -135.0),
            (-150.0, -150.0, -125.0),
            (150.0, -150.0, -125.0),
        ],
        dtype=np.float64,
    )

    def __init__(
        self,
        yaw_threshold: float = 25.0,
        pitch_threshold: float = 18.0,
        looking_away_time_threshold: float = 1.0,
    ):
        self.yaw_threshold = yaw_threshold
        self.pitch_threshold = pitch_threshold
        self.looking_away_time_threshold = looking_away_time_threshold
        self.looking_away_start_time: float | None = None

        logger.info("HeadPoseEstimator initialized.")

    def process(
        self,
        pixel_landmarks: List[Tuple[int, int]],
        frame_shape: Tuple[int, int, int],
    ) -> HeadPoseMetrics:

        metrics = HeadPoseMetrics()

        if len(pixel_landmarks) < 468:
            self.looking_away_start_time = None
            return metrics

        h, w = frame_shape[:2]

        image_points = np.array(
            [
                pixel_landmarks[self.NOSE_TIP],
                pixel_landmarks[self.CHIN],
                pixel_landmarks[self.LEFT_EYE_CORNER],
                pixel_landmarks[self.RIGHT_EYE_CORNER],
                pixel_landmarks[self.LEFT_MOUTH_CORNER],
                pixel_landmarks[self.RIGHT_MOUTH_CORNER],
            ],
            dtype=np.float64,
        )

        focal_length = float(w)
        center = (w / 2.0, h / 2.0)

        camera_matrix = np.array(
            [
                [focal_length, 0.0, center[0]],
                [0.0, focal_length, center[1]],
                [0.0, 0.0, 1.0],
            ],
            dtype=np.float64,
        )

        dist_coeffs = np.zeros((4, 1), dtype=np.float64)

        success, rotation_vector, translation_vector = cv2.solvePnP(
            self.MODEL_POINTS_3D,
            image_points,
            camera_matrix,
            dist_coeffs,
            flags=cv2.SOLVEPNP_ITERATIVE,
        )

        if not success:
            return metrics

        rotation_matrix, _ = cv2.Rodrigues(rotation_vector)
        projection_matrix = np.hstack((rotation_matrix, translation_vector))

        _, _, _, _, _, _, euler_angles = cv2.decomposeProjectionMatrix(
            projection_matrix
        )

        metrics.pitch = float(euler_angles[0, 0])
        metrics.yaw = float(euler_angles[1, 0])
        metrics.roll = float(euler_angles[2, 0])

        threshold_crossed = (
            abs(metrics.yaw) > self.yaw_threshold
            or abs(metrics.pitch) > self.pitch_threshold
        )

        if threshold_crossed:
            if self.looking_away_start_time is None:
                self.looking_away_start_time = time.time()

            metrics.looking_away_duration_sec = (
                time.time() - self.looking_away_start_time
            )

            metrics.is_looking_away = (
                metrics.looking_away_duration_sec
                >= self.looking_away_time_threshold
            )
        else:
            self.looking_away_start_time = None

        return metrics