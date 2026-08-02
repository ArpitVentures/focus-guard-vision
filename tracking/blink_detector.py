import numpy as np
from typing import List, Tuple

from utils.logger import logger


class BlinkDetector:

    LEFT_EYE_INDICES = (33, 160, 158, 133, 153, 144)
    RIGHT_EYE_INDICES = (362, 385, 387, 263, 373, 380)

    def __init__(
        self,
        ear_threshold: float = 0.21,
        min_blink_frames: int = 2,
        max_blink_frames: int = 15,
    ):
        self.ear_threshold = ear_threshold
        self.min_blink_frames = min_blink_frames
        self.max_blink_frames = max_blink_frames

        self.closed_frame_counter = 0
        self.total_blinks = 0

        logger.info(
            f"BlinkDetector initialized [EAR={self.ear_threshold}]"
        )

    @staticmethod
    def calculate_ear(
        eye_points: List[Tuple[int, int]]
    ) -> float:

        p1, p2, p3, p4, p5, p6 = (
            np.asarray(pt, dtype=np.float64)
            for pt in eye_points
        )

        vertical_1 = np.linalg.norm(p2 - p6)
        vertical_2 = np.linalg.norm(p3 - p5)
        horizontal = np.linalg.norm(p1 - p4)

        if horizontal <= 1e-6:
            return 0.0

        return float(
            (vertical_1 + vertical_2)
            / (2.0 * horizontal)
        )

    def process(
        self,
        pixel_landmarks: List[Tuple[int, int]]
    ) -> Tuple[float, float, float, int, bool]:

        if len(pixel_landmarks) < 468:
            return (
                0.0,
                0.0,
                0.0,
                self.total_blinks,
                False,
            )

        left_points = [
            pixel_landmarks[i]
            for i in self.LEFT_EYE_INDICES
        ]

        right_points = [
            pixel_landmarks[i]
            for i in self.RIGHT_EYE_INDICES
        ]

        left_ear = self.calculate_ear(left_points)
        right_ear = self.calculate_ear(right_points)

        avg_ear = (left_ear + right_ear) / 2.0

        eyes_closed = avg_ear < self.ear_threshold

        if eyes_closed:

            self.closed_frame_counter += 1

        else:

            if (
                self.min_blink_frames
                <= self.closed_frame_counter
                <= self.max_blink_frames
            ):
                self.total_blinks += 1

            self.closed_frame_counter = 0

        return (
            left_ear,
            right_ear,
            avg_ear,
            self.total_blinks,
            eyes_closed,
        )