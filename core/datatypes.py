from dataclasses import dataclass, field
from typing import List, Tuple


@dataclass(slots=True)
class FaceLandmarksData:
    face_detected: bool = False
    pixel_landmarks: List[Tuple[int, int]] = field(default_factory=list)
    normalized_landmarks: List[Tuple[float, float, float]] = field(default_factory=list)
    bbox: Tuple[int, int, int, int] | None = None


@dataclass(slots=True)
class EyeMetrics:
    left_ear: float = 0.0
    right_ear: float = 0.0
    avg_ear: float = 0.0
    is_eyes_closed: bool = False
    blink_count: int = 0
    blink_rate_bpm: float = 0.0
    drowsy_alert: bool = False
    drowsy_duration_sec: float = 0.0


@dataclass(slots=True)
class HeadPoseMetrics:
    pitch: float = 0.0
    yaw: float = 0.0
    roll: float = 0.0
    is_looking_away: bool = False
    looking_away_duration_sec: float = 0.0


@dataclass(slots=True)
class FocusTelemetry:
    focus_score: float = 100.0
    target_score: float = 100.0
    attention_state: str = "FOCUSED"
    primary_reason: str = "Optimal Attention"
    eye_metrics: EyeMetrics = field(default_factory=EyeMetrics)
    head_pose: HeadPoseMetrics = field(default_factory=HeadPoseMetrics)
