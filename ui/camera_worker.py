"""
FocusGuard AI - PyQt6 Threaded Vision Worker Engine
"""
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QImage
import cv2
import time

from vision.camera import CameraStream
from core.vision_pipeline import VisionPipeline
from ui.hud_renderer import HUDRenderer
from utils.logger import logger


class CameraWorker(QThread):
    """
    Background QThread that continuously captures camera frames, runs vision pipeline,
    and emits PyQt signals to update the desktop interface smoothly.
    """
    frame_processed = pyqtSignal(QImage, object)

    def __init__(self):
        super().__init__()
        self.running = False

    def run(self):
        logger.info("Initializing CameraWorker thread...")

        try:
            camera = CameraStream().start()
            pipeline = VisionPipeline()
            hud_renderer = HUDRenderer()
        except Exception as e:
            logger.critical(f"Failed to initialize vision worker pipeline: {e}")
            return

        self.running = True
        fps_counter = 0
        start_time = time.time()
        current_fps = 0.0

        while self.running and camera.is_running():
            success, frame = camera.read()
            if not success or frame is None:
                continue

            # 1. Execute Core Pipeline Service
            display_frame, focus_telemetry, face_detected = pipeline.process_frame(frame)

            # 2. FPS Computation
            fps_counter += 1
            elapsed = time.time() - start_time
            if elapsed >= 1.0:
                current_fps = fps_counter / elapsed
                fps_counter = 0
                start_time = time.time()

            # 3. HUD Overlay Rendering
            rendered_frame = hud_renderer.render(
                frame=display_frame,
                fps=current_fps,
                telemetry=focus_telemetry,
                face_detected=face_detected
            )

            # 4. Convert BGR NumPy Array to Qt QImage
            rgb_frame = cv2.cvtColor(rendered_frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w

            qt_image = QImage(
                bytes(rgb_frame.data),
                w,
                h,
                bytes_per_line,
                QImage.Format.Format_RGB888
            )

            self.frame_processed.emit(qt_image.copy(), focus_telemetry)
            time.sleep(0.005)

        # Cleanup hardware on thread termination
        pipeline.release()
        camera.stop()
        logger.info("CameraWorker thread stopped cleanly.")

    def stop(self):
        """Signals worker loop to terminate."""
        self.running = False
        self.wait()
