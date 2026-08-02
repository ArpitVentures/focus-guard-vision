"""
FocusGuard AI - Production Priority Engine & Damped Focus Analytics
"""
from core.datatypes import EyeMetrics, HeadPoseMetrics, FocusTelemetry
from utils.logger import logger


class FocusEngine:
    """
    Priority-based attention state machine with smooth score damping and XAI reason tags.
    """
    def __init__(self, damping_factor: float = 0.1):
        self.current_score = 100.0
        self.damping_factor = damping_factor  # Controls smooth transition speed
        logger.info("FocusEngine initialized with Priority Ladder & Smooth Damping.")

    def compute(
        self,
        face_detected: bool,
        eye_metrics: EyeMetrics,
        head_pose: HeadPoseMetrics
    ) -> FocusTelemetry:
        """
        Evaluates strict priority matrix: NO_FACE >> DROWSY >> LOOKING_AWAY >> FOCUSED
        """
        telemetry = FocusTelemetry()
        telemetry.eye_metrics = eye_metrics
        telemetry.head_pose = head_pose

        # --- Priority Matrix Resolution ---
        if not face_detected:
            telemetry.attention_state = "NO_FACE"
            telemetry.primary_reason = "No User Detected in Frame"
            target_score = 0.0

        elif eye_metrics.drowsy_alert:
            telemetry.attention_state = "DROWSY"
            telemetry.primary_reason = f"Eyes Closed ({eye_metrics.drowsy_duration_sec:.1f}s)"
            target_score = max(0.0, 100.0 - (eye_metrics.drowsy_duration_sec * 25.0))

        elif head_pose.is_looking_away:
            telemetry.attention_state = "LOOKING_AWAY"
            if head_pose.yaw > 25.0:
                direction = "Right"
            elif head_pose.yaw < -25.0:
                direction = "Left"
            elif head_pose.pitch > 20.0:
                direction = "Up"
            else:
                direction = "Down"

            telemetry.primary_reason = f"Head Turned {direction} ({abs(head_pose.yaw):.0f}°)"
            target_score = max(20.0, 100.0 - (head_pose.looking_away_duration_sec * 15.0))

        else:
            telemetry.attention_state = "FOCUSED"
            telemetry.primary_reason = "Target Focus Maintained"
            target_score = 100.0

        # --- Smooth Score Interpolation (Prevents abrupt jumps) ---
        self.current_score += (target_score - self.current_score) * self.damping_factor

        telemetry.target_score = round(target_score, 1)
        telemetry.focus_score = round(self.current_score, 1)

        return telemetry
