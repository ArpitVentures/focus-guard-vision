"""
FocusGuard AI - Drowsiness & Micro-sleep Detection Engine
"""
import time
from typing import Tuple
from utils.logger import logger


class DrowsinessDetector:
    """
    Monitors eye closure duration and manages drowsiness alert thresholds with single-trigger state logs.
    """
    def __init__(self, drowsy_time_threshold_sec: float = 1.5):
        self.drowsy_time_threshold_sec = drowsy_time_threshold_sec
        self.eyes_closed_start_time = None
        self.alert_logged = False  # Prevents logging warning every single frame
        logger.info(f"DrowsinessDetector initialized [Threshold: {self.drowsy_time_threshold_sec}s]")

    def process(self, is_eyes_closed: bool) -> Tuple[bool, float]:
        """
        Returns (is_drowsy_alert, duration_eyes_closed_seconds).
        """
        current_time = time.time()

        if is_eyes_closed:
            if self.eyes_closed_start_time is None:
                self.eyes_closed_start_time = current_time

            duration = current_time - self.eyes_closed_start_time
            is_drowsy = duration >= self.drowsy_time_threshold_sec

            if is_drowsy and not self.alert_logged:
                logger.warning(f"Drowsiness Alert Triggered! Closed Duration: {duration:.2f}s")
                self.alert_logged = True  # Logged ONCE per episode

            return is_drowsy, duration
        else:
            # Reset state on eye re-opening
            self.eyes_closed_start_time = None
            self.alert_logged = False
            return False, 0.0
