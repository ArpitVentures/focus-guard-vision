"""
FocusGuard AI - Unified Eye Analytics Aggregator
"""
from typing import List, Tuple
from core.datatypes import EyeMetrics
from tracking.blink_detector import BlinkDetector
from tracking.drowsiness_detector import DrowsinessDetector


class EyeTracker:
    """
    Facade class combining Blink Detection and Drowsiness Tracking engines.
    """
    def __init__(
        self,
        ear_threshold: float = 0.21,
        min_blink_frames: int = 2,
        max_blink_frames: int = 15,
        drowsy_time_threshold: float = 1.5
    ):
        self.blink_detector = BlinkDetector(
            ear_threshold=ear_threshold,
            min_blink_frames=min_blink_frames,
            max_blink_frames=max_blink_frames
        )
        self.drowsiness_detector = DrowsinessDetector(
            drowsy_time_threshold_sec=drowsy_time_threshold
        )

    def process(self, pixel_landmarks: List[Tuple[int, int]]) -> EyeMetrics:
        """Processes landmarks and outputs structured EyeMetrics object."""
        metrics = EyeMetrics()

        if not pixel_landmarks or len(pixel_landmarks) < 468:
            return metrics

        # 1. Process Blink & EAR
        left_ear, right_ear, avg_ear, blink_count, is_closed = self.blink_detector.process(pixel_landmarks)

        # 2. Process Drowsiness
        is_drowsy, drowsy_duration = self.drowsiness_detector.process(is_closed)

        # 3. Assemble Telemetry
        metrics.left_ear = left_ear
        metrics.right_ear = right_ear
        metrics.avg_ear = avg_ear
        metrics.is_eyes_closed = is_closed
        metrics.blink_count = blink_count
        metrics.drowsy_alert = is_drowsy
        metrics.drowsy_duration_sec = drowsy_duration

        return metrics
