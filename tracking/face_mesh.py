import cv2
import numpy as np
import mediapipe as mp
from typing import Any
from utils.logger import logger
from core.datatypes import FaceLandmarksData

mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles


class FaceMeshDetector:
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

    def process_frame(self, frame: np.ndarray) -> tuple[FaceLandmarksData, Any]:
        h, w = frame.shape[:2]

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb_frame.flags.writeable = False

        results = self.face_mesh.process(rgb_frame)

        data = FaceLandmarksData()

        if not results.multi_face_landmarks:
            return data, results

        data.face_detected = True
        face_landmarks = results.multi_face_landmarks[0]

        pixel_coords = []
        norm_coords = []
        x_coords = []
        y_coords = []

        for lm in face_landmarks.landmark:
            x = int(lm.x * w)
            y = int(lm.y * h)

            pixel_coords.append((x, y))
            norm_coords.append((lm.x, lm.y, lm.z))
            x_coords.append(x)
            y_coords.append(y)

        x_min = min(x_coords)
        x_max = max(x_coords)
        y_min = min(y_coords)
        y_max = max(y_coords)

        data.pixel_landmarks = pixel_coords
        data.normalized_landmarks = norm_coords
        data.bbox = (
            x_min,
            y_min,
            x_max - x_min,
            y_max - y_min
        )

        return data, results

    def draw_mesh(
        self,
        frame: np.ndarray,
        results: Any,
        draw_tessellation: bool = True,
        draw_contours: bool = True
    ) -> np.ndarray:

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
        if self.face_mesh is not None:
            self.face_mesh.close()
            logger.info("MediaPipe FaceMesh engine closed.")