"""
FocusGuard AI - Main Entry Point (Day 1 Milestone)
"""
import cv2
import time
from vision.camera import CameraStream
from utils.logger import logger


def main():
    logger.info("Starting FocusGuard AI - Live Engine Verification...")

    try:
        # Initialize and start threaded camera
        camera = CameraStream().start()
    except Exception as e:
        logger.critical(f"Initialization failure: {e}")
        return

    fps_counter = 0
    start_time = time.time()
    current_fps = 0

    logger.info("Live feed started. Press 'q' or 'ESC' on the camera window to exit.")

    while True:
        success, frame = camera.read()
        if not success or frame is None:
            continue

        # Real-time FPS Calculation
        fps_counter += 1
        elapsed_time = time.time() - start_time
        if elapsed_time >= 1.0:
            current_fps = fps_counter / elapsed_time
            fps_counter = 0
            start_time = time.time()

        # Render HUD Diagnostic Info
        cv2.putText(
            frame, f"FocusGuard AI - Day 1 Vision Pipeline", (30, 40),
            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 128), 2, cv2.LINE_AA
        )
        cv2.putText(
            frame, f"FPS: {current_fps:.1f}", (30, 80),
            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 215, 255), 2, cv2.LINE_AA
        )
        cv2.putText(
            frame, "Status: Hardware Capture Active", (30, 120),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA
        )

        cv2.imshow("FocusGuard AI - Studio Engine Test", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27:  # 27 is ESC key
            logger.info("User exit trigger received.")
            break

    # Shutdown hardware cleanly
    camera.stop()
    cv2.destroyAllWindows()
    logger.info("FocusGuard AI shut down safely.")


if __name__ == "__main__":
    main()