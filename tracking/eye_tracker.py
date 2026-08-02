from typing import List, Tuple

from core.datatypes import EyeMetrics
from tracking.blink_detector import BlinkDetector
from tracking.drowsiness_detector import DrowsinessDetector


class EyeTracker:

    def __init__(
        self,
        ear_threshold: float = 0.21,
        min_blink_frames: int = 2,
        max_blink_frames: int = 15,
        drowsy_time_threshold: float = 1.5,
    ):

        self.blink_detector = BlinkDetector(
            ear_threshold=ear_threshold,
            min_blink_frames=min_blink_frames,
            max_blink_frames=max_blink_frames,
        )

        self.drowsiness_detector = DrowsinessDetector(
            drowsy_time_threshold_sec=drowsy_time_threshold
        )

    def process(
        self,
        pixel_landmarks: List[Tuple[int, int]],
    ) -> EyeMetrics:

        metrics = EyeMetrics()

        if len(pixel_landmarks) < 468:
            return metrics

        (
            metrics.left_ear,
            metrics.right_ear,
            metrics.avg_ear,
            metrics.blink_count,
            metrics.is_eyes_closed,
        ) = self.blink_detector.process(pixel_landmarks)

        (
            metrics.drowsy_alert,
            metrics.drowsy_duration_sec,
        ) = self.drowsiness_detector.process(
            metrics.is_eyes_closed
        )

        return metrics
