"""
FocusGuard AI - Production HUD Overlay Rendering Engine
"""
import cv2
import numpy as np
from core.datatypes import FocusTelemetry


class HUDRenderer:
    """
    Decoupled UI Renderer responsible for drawing HUD overlays.
    """
    def __init__(self):
        self.COLOR_ACCENT = (0, 255, 128)        # Mint Green
        self.COLOR_INFO = (0, 215, 255)          # Electric Amber
        self.COLOR_TEXT_PRIMARY = (255, 255, 255)# Pure White
        self.COLOR_TEXT_SECONDARY = (200, 200, 200) # Slate
        self.COLOR_ALERT_RED = (0, 0, 255)       # Crimson
        self.COLOR_ALERT_ORANGE = (0, 140, 255)   # Orange
        self.COLOR_SUCCESS = (0, 255, 0)         # Green

    def render(
        self,
        frame: np.ndarray,
        fps: float,
        telemetry: FocusTelemetry,
        face_detected: bool
    ) -> np.ndarray:
        """Renders diagnostic overlay and HUD state."""
        display = frame.copy()

        # 1. Header & Performance
        cv2.putText(display, "FocusGuard AI - Production Engine", (30, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, self.COLOR_ACCENT, 2, cv2.LINE_AA)
        cv2.putText(display, f"FPS: {fps:.1f}", (30, 75),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, self.COLOR_INFO, 2, cv2.LINE_AA)

        # 2. Score & Attention State
        score = telemetry.focus_score
        score_color = self.COLOR_SUCCESS if score > 70 else self.COLOR_INFO if score > 40 else self.COLOR_ALERT_RED

        cv2.putText(display, f"Focus Score: {score:.1f}%", (30, 115),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.75, score_color, 2, cv2.LINE_AA)
        cv2.putText(display, f"State: {telemetry.attention_state}", (30, 150),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, self.COLOR_TEXT_PRIMARY, 2, cv2.LINE_AA)

        # Explainable AI Reason Tag
        cv2.putText(display, f"Reason: {telemetry.primary_reason}", (30, 185),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, self.COLOR_INFO, 1, cv2.LINE_AA)

        eye = telemetry.eye_metrics
        pose = telemetry.head_pose

        cv2.putText(display, f"Blinks: {eye.blink_count}", (30, 220),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, self.COLOR_TEXT_PRIMARY, 1, cv2.LINE_AA)

        if face_detected:
            cv2.putText(display, f"EAR: {eye.avg_ear:.3f} | Yaw: {pose.yaw:.1f}°", (30, 250),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, self.COLOR_TEXT_SECONDARY, 1, cv2.LINE_AA)

        # 3. Alert Banners
        if telemetry.attention_state == "DROWSY":
            cv2.rectangle(display, (280, 20), (1000, 80), self.COLOR_ALERT_RED, -1)
            cv2.putText(display, f"DROWSINESS ALERT! {telemetry.primary_reason}",
                        (300, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.65, self.COLOR_TEXT_PRIMARY, 2, cv2.LINE_AA)
        elif telemetry.attention_state == "LOOKING_AWAY":
            cv2.rectangle(display, (280, 20), (1000, 80), self.COLOR_ALERT_ORANGE, -1)
            cv2.putText(display, f"DISTRACTION ALERT! {telemetry.primary_reason}",
                        (300, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.65, self.COLOR_TEXT_PRIMARY, 2, cv2.LINE_AA)
        elif telemetry.attention_state == "NO_FACE":
            cv2.rectangle(display, (280, 20), (1000, 80), self.COLOR_ALERT_RED, -1)
            cv2.putText(display, "NO USER DETECTED! Attention Tracking Suspended",
                        (300, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.65, self.COLOR_TEXT_PRIMARY, 2, cv2.LINE_AA)

        return display
