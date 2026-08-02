"""
FocusGuard AI - Day 2 MediaPipe Face Mesh Pipeline Test
"""
import cv2
import time
from vision.camera import CameraStream
from tracking.face_mesh import FaceMeshDetector
from utils.logger import logger

def main():
    logger.info("Initializing FocusGuard AI - Day 2 Face Mesh Pipeline...")

    try:
        camera = CameraStream().start()
        detector = FaceMeshDetector()
    except Exception as e:
        logger.critical(f"Pipeline startup failed: {e}")
        return

    fps_counter = 0
    start_time = time.time()
    current_fps = 0

    logger.info("Face Mesh pipeline active. Press 'q' or 'ESC' on window to exit.")

    while True:
        success, frame = camera.read()
        if not success or frame is None:
            continue

        # Process MediaPipe Mesh
        face_data, results = detector.process_frame(frame)

        # Draw Mesh HUD Overlay
        display_frame = detector.draw_mesh(frame, results, draw_tessellation=True, draw_contours=True)

        # Calculate FPS
        fps_counter += 1
        elapsed = time.time() - start_time
        if elapsed >= 1.0:
            current_fps = fps_counter / elapsed
            fps_counter = 0
            start_time = time.time()

        # Render HUD Diagnostic Info
        status_color = (0, 255, 128) if face_data.face_detected else (0, 0, 255)
        status_text = f"Status: {'FACE TRACKED' if face_data.face_detected else 'SEARCHING...'}"

        cv2.putText(display_frame, f"FocusGuard AI - Mesh Engine", (30, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 128), 2, cv2.LINE_AA)
        cv2.putText(display_frame, f"FPS: {current_fps:.1f}", (30, 75),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 215, 255), 2, cv2.LINE_AA)
        cv2.putText(display_frame, status_text, (30, 110),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, status_color, 2, cv2.LINE_AA)

        if face_data.face_detected:
            cv2.putText(display_frame, f"Landmarks: {len(face_data.pixel_landmarks)} points", (30, 145),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)

            # Draw Face Bounding Box
            x, y, w, h = face_data.bbox
            cv2.rectangle(display_frame, (x, y), (x + w, y + h), (0, 255, 255), 1)

        cv2.imshow("FocusGuard AI - Day 2 Mesh Test", display_frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27:
            logger.info("User termination requested.")
            break

    # Release resources cleanly
    detector.release()
    camera.stop()
    cv2.destroyAllWindows()
    logger.info("FocusGuard AI closed cleanly.")

if __name__ == "__main__":
    main()