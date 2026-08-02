"""
FocusGuard AI - Core Data Models
"""
from dataclasses import dataclass, field
from typing import List, Tuple, Optional

@dataclass
class FaceLandmarksData:
    """Encapsulates raw and normalized landmark coordinates for a detected face."""
    face_detected: bool = False
    pixel_landmarks: List[Tuple[int, int]] = field(default_factory=list)
    normalized_landmarks: List[Tuple[float, float, float]] = field(default_factory=list)
    bbox: Optional[Tuple[int, int, int, int]] = None  # (x, y, w, h)