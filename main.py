"""
FocusGuard AI - Clean Production Orchestrator
"""
import cv2
import time
from vision.camera import CameraStream
from tracking.face_mesh import FaceMeshDetector
from tracking.eye_tracker import EyeTracker
from tracking.head_pose import HeadPoseEstimator
from analytics.focus_engine import FocusEngine
from ui.hud_renderer import HUDRenderer
from core.datatypes import EyeMetrics
from utils.logger import logger


def main():
    logger.info("Initializing FocusGuard AI - Production Vision Engine...")

    try:
        camera = CameraStream().start()
        mesh_detector = FaceMeshDetector()
        eye_tracker = EyeTracker()
        pose_estimator = HeadPoseEstimator()
        focus_engine = FocusEngine()
        hud_renderer = HUDRenderer()
    except RuntimeError as e:
        logger.critical(f"Hardware initialization failed: {e}")
        return
    except Exception as e:
        logger.critical(f"Unexpected pipeline failure: {e}")
        return

    fps_counter = 0
    start_time = time.time()
    current_fps = 0.0

    logger.info("Vision Engine loop active. Press 'q' or 'ESC' to terminate.")

    while camera.is_running():
        success, frame = camera.read()
        if not success or frame is None:
            continue

        # 1. Landmark Mesh Inference
        face_data, results = mesh_detector.process_frame(frame)
        display_frame = mesh_detector.draw_mesh(frame, results, draw_tessellation=False, draw_contours=True)

        # 2. Telemetry Processing
        if face_data.face_detected:
            eye_metrics = eye_tracker.process(face_data.pixel_landmarks)
            head_pose = pose_estimator.process(face_data.pixel_landmarks, frame.shape)
        else:
            eye_metrics = EyeMetrics()
            head_pose = pose_estimator.process([], frame.shape)

        # 3. Focus Telemetry
        focus_telemetry = focus_engine.compute(face_data.face_detected, eye_metrics, head_pose)

        # 4. Real-time FPS Calculation
        fps_counter += 1
        elapsed = time.time() - start_time
        if elapsed >= 1.0:
            current_fps = fps_counter / elapsed
            fps_counter = 0
            start_time = time.time()

        # 5. Decoupled HUD Rendering
        rendered_frame = hud_renderer.render(
            frame=display_frame,
            fps=current_fps,
            telemetry=focus_telemetry,
            face_detected=face_data.face_detected
        )

        cv2.imshow("FocusGuard AI - Production Studio", rendered_frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27:
            logger.info("User requested termination.")
            camera.stop()
            break

    # Clean Hardware Release
    mesh_detector.release()
    cv2.destroyAllWindows()
    logger.info("FocusGuard AI shut down safely.")


if __name__ == "__main__":
    main()
