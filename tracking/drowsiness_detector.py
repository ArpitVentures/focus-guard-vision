import time
from typing import Tuple

from utils.logger import logger


class DrowsinessDetector:

    def __init__(self, drowsy_time_threshold_sec: float = 1.5):
        self.drowsy_time_threshold_sec = drowsy_time_threshold_sec
        self.eyes_closed_start_time: float | None = None
        self.alert_logged = False

        logger.info(
            f"DrowsinessDetector initialized [Threshold={self.drowsy_time_threshold_sec}s]"
        )

    def process(self, is_eyes_closed: bool) -> Tuple[bool, float]:

        if not is_eyes_closed:
            self.eyes_closed_start_time = None
            self.alert_logged = False
            return False, 0.0

        now = time.time()

        if self.eyes_closed_start_time is None:
            self.eyes_closed_start_time = now

        duration = now - self.eyes_closed_start_time
        is_drowsy = duration >= self.drowsy_time_threshold_sec

        if is_drowsy and not self.alert_logged:
            logger.warning(
                f"Drowsiness Alert Triggered ({duration:.2f}s)"
            )
            self.alert_logged = True

        return is_drowsy, duration
