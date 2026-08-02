"""
FocusGuard AI - MediaPipe Face Mesh Processor
"""
import cv2
import numpy as np
import mediapipe as mp
from typing import Tuple, Any
from utils.logger import logger
from core.datatypes import FaceLandmarksData

# Dynamically import MediaPipe solutions at runtime
mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles


class FaceMeshDetector:
    """
    High-performance 468 3D Landmark Detector using MediaPipe Face Mesh.
    """
    def __init__(
        self,
        static_image_mode: bool = False,
        max_num_faces: int = 1,
        refine_landmarks: bool = True,
        min_detection_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5
    ):
        self.mp_face_mesh = mp_face_mesh
        self.mp_drawing = mp_drawing
        self.mp_drawing_styles = mp_drawing_styles

        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=static_image_mode,
            max_num_faces=max_num_faces,
            refine_landmarks=refine_landmarks,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        logger.info("MediaPipe FaceMesh engine initialized successfully.")

    def process_frame(self, frame: np.ndarray) -> Tuple[FaceLandmarksData, Any]:
        """
        Converts BGR frame to RGB and extracts 468 3D facial landmark points.
        """
        h, w, _ = frame.shape
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)

        data = FaceLandmarksData()

        if results.multi_face_landmarks:
            data.face_detected = True
            face_landmarks = results.multi_face_landmarks[0]  # Primary face

            pixel_coords = []
            norm_coords = []
            x_coords, y_coords = [], []

            for lm in face_landmarks.landmark:
                cx, cy = int(lm.x * w), int(lm.y * h)
                pixel_coords.append((cx, cy))
                norm_coords.append((lm.x, lm.y, lm.z))
                x_coords.append(cx)
                y_coords.append(cy)

            # Bounding box around primary face
            x_min, x_max = min(x_coords), max(x_coords)
            y_min, y_max = min(y_coords), max(y_coords)
            data.bbox = (x_min, y_min, x_max - x_min, y_max - y_min)

            data.pixel_landmarks = pixel_coords
            data.normalized_landmarks = norm_coords

        return data, results

    def draw_mesh(
        self,
        frame: np.ndarray,
        results: Any,
        draw_tessellation: bool = True,
        draw_contours: bool = True
    ) -> np.ndarray:
        """
        Renders HUD landmark overlays on top of the frame.
        """
        if not results or not results.multi_face_landmarks:
            return frame

        annotated_frame = frame.copy()
        for face_landmarks in results.multi_face_landmarks:
            if draw_tessellation:
                self.mp_drawing.draw_landmarks(
                    image=annotated_frame,
                    landmark_list=face_landmarks,
                    connections=self.mp_face_mesh.FACEMESH_TESSELATION,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=self.mp_drawing_styles.get_default_face_mesh_tesselation_style()
                )
            if draw_contours:
                self.mp_drawing.draw_landmarks(
                    image=annotated_frame,
                    landmark_list=face_landmarks,
                    connections=self.mp_face_mesh.FACEMESH_CONTOURS,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=self.mp_drawing_styles.get_default_face_mesh_contours_style()
                )
        return annotated_frame

    def release(self):
        """Releases MediaPipe C++ bindings cleanly."""
        self.face_mesh.close()
        logger.info("MediaPipe FaceMesh engine closed.")