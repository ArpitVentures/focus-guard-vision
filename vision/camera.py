"""
FocusGuard AI - Threaded Camera Engine
"""
import cv2
import threading
import time
from typing import Optional, Tuple
import numpy as np
from utils.logger import logger
from config.settings import CAMERA_INDEX, FRAME_WIDTH, FRAME_HEIGHT


class CameraStream:
    """
    Threaded Camera Controller to ensure low latency and high FPS capture.
    """
    def __init__(self, src: int = CAMERA_INDEX, width: int = FRAME_WIDTH, height: int = FRAME_HEIGHT):
        self.src = src
        self.width = width
        self.height = height
        self.thread = None

        self.cap = cv2.VideoCapture(self.src, cv2.CAP_DSHOW)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)

        if not self.cap.isOpened():
            logger.error(f"Failed to open camera hardware source at index {self.src}")
            raise RuntimeError(f"Cannot open camera index {self.src}")

        self.grabbed, self.frame = self.cap.read()
        self.stopped = False
        self.lock = threading.Lock()

        logger.info(f"Camera initialized successfully [{self.width}x{self.height}] at index {self.src}")

    def start(self) -> "CameraStream":
        """Starts background thread for frame reading."""
        self.thread = threading.Thread(
            target=self._update,
            name="CameraThread",
            daemon=True
        )
        self.thread.start()
        logger.info("Camera capture worker thread started.")
        return self

    def _update(self):
        """Continuously fetches frames from device stream."""
        while not self.stopped:
            grabbed, frame = self.cap.read()
            if not grabbed:
                logger.warning("Blank frame grabbed from camera stream.")
                continue

            with self.lock:
                self.grabbed = grabbed
                self.frame = frame
            time.sleep(0.005)

    def is_running(self) -> bool:
        """Returns True if the camera stream is active and not stopped."""
        return not self.stopped and self.cap.isOpened()

    def read(self) -> Tuple[bool, Optional[np.ndarray]]:
        """Returns the latest captured frame safely."""
        with self.lock:
            if not self.grabbed or self.frame is None:
                return False, None
            return True, self.frame.copy()

    def stop(self):
        """Signals thread termination and releases hardware resources."""
        self.stopped = True
        if self.thread is not None:
            self.thread.join(timeout=1.0)

        if self.cap.isOpened():
            self.cap.release()
        logger.info("Camera resources released successfully.")
