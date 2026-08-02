"""
FocusGuard AI - Blink Detection Engine
"""
import numpy as np
from typing import List, Tuple
from utils.logger import logger


class BlinkDetector:
    """
    Computes Eye Aspect Ratio (EAR) and detects valid physiological blinks.
    Prevents false blink increments during prolonged eye closures (drowsiness/sleep).
    """
    # MediaPipe 468 Face Mesh Indices for Eyes
    LEFT_EYE_INDICES = [33, 160, 158, 133, 153, 144]
    RIGHT_EYE_INDICES = [362, 385, 387, 263, 373, 380]

    def __init__(
        self,
        ear_threshold: float = 0.21,
        min_blink_frames: int = 2,
        max_blink_frames: int = 15  # ~0.5 sec max at 30 FPS. Longer closure = Drowsiness, not Blink
    ):
        self.ear_threshold = ear_threshold
        self.min_blink_frames = min_blink_frames
        self.max_blink_frames = max_blink_frames

        self.closed_frame_counter = 0
        self.total_blinks = 0
        logger.info(f"BlinkDetector initialized [EAR Threshold: {self.ear_threshold}]")

    @staticmethod
    def calculate_ear(eye_pts: List[Tuple[int, int]]) -> float:
        """Calculates Eye Aspect Ratio (EAR) using Euclidean distances."""
        p1, p2, p3, p4, p5, p6 = [np.array(pt, dtype=np.float64) for pt in eye_pts]

        v1 = float(np.linalg.norm(p2 - p6))
        v2 = float(np.linalg.norm(p3 - p5))
        h = float(np.linalg.norm(p1 - p4))

        if h < 1e-6:
            return 0.0

        return (v1 + v2) / (2.0 * h)

    def process(self, pixel_landmarks: List[Tuple[int, int]]) -> Tuple[float, float, float, int, bool]:
        """
        Derives Left EAR, Right EAR, Avg EAR, Total Blinks, and current Eye Closed State.
        """
        if not pixel_landmarks or len(pixel_landmarks) < 468:
            return 0.0, 0.0, 0.0, self.total_blinks, False

        left_pts = [pixel_landmarks[idx] for idx in self.LEFT_EYE_INDICES]
        right_pts = [pixel_landmarks[idx] for idx in self.RIGHT_EYE_INDICES]

        left_ear = self.calculate_ear(left_pts)
        right_ear = self.calculate_ear(right_pts)
        avg_ear = (left_ear + right_ear) / 2.0

        is_closed = avg_ear < self.ear_threshold

        if is_closed:
            self.closed_frame_counter += 1
        else:
            # Eyes re-opened: Verify if closure duration matches a physiological blink duration
            if self.min_blink_frames <= self.closed_frame_counter <= self.max_blink_frames:
                self.total_blinks += 1
                logger.debug(f"Valid Blink detected! Total Blinks: {self.total_blinks}")

            self.closed_frame_counter = 0  # Reset counter

        return left_ear, right_ear, avg_ear, self.total_blinks, is_closed
