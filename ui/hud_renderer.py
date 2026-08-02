"""
FocusGuard AI - Minimalist In-Video HUD Renderer
"""
import cv2
import numpy as np
from core.datatypes import FocusTelemetry


class HUDRenderer:
    """
    Renders clean, minimal in-video overlays with dark glass badges.
    """
    def __init__(self):
        self.COLOR_INFO = (0, 215, 255)            # Electric Amber
        self.COLOR_TEXT_PRIMARY = (255, 255, 255)  # Pure White
        self.COLOR_ALERT_RED = (0, 0, 255)         # Crimson
        self.COLOR_ALERT_ORANGE = (0, 140, 255)     # Bright Orange

    def render(
        self,
        frame: np.ndarray,
        fps: float,
        telemetry: FocusTelemetry,
        face_detected: bool
    ) -> np.ndarray:
        """Renders minimal HUD overlays with rounded dark glass FPS badge."""
        display = frame.copy()

        # 1. Dark Glass FPS Badge Overlay (Top Left)
        fps_text = f"FPS: {fps:.1f}"
        # Draw semi-transparent dark box behind FPS
        overlay = display.copy()
        cv2.rectangle(overlay, (15, 15), (145, 55), (10, 15, 26), -1)
        cv2.addWeighted(overlay, 0.65, display, 0.35, 0, display)
        cv2.rectangle(display, (15, 15), (145, 55), (30, 41, 59), 1)  # Subdued border

        cv2.putText(display, fps_text, (28, 42),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, self.COLOR_INFO, 2, cv2.LINE_AA)

        # 2. Emergency Alert Banners (Top Center)
        if telemetry.attention_state == "DROWSY":
            cv2.rectangle(display, (260, 15), (1020, 75), self.COLOR_ALERT_RED, -1)
            cv2.putText(display, f"[!] DROWSINESS DETECTED: {telemetry.primary_reason}",
                        (280, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.65, self.COLOR_TEXT_PRIMARY, 2, cv2.LINE_AA)

        elif telemetry.attention_state == "LOOKING_AWAY":
            cv2.rectangle(display, (260, 15), (1020, 75), self.COLOR_ALERT_ORANGE, -1)
            cv2.putText(display, f"[!] DISTRACTION DETECTED: {telemetry.primary_reason}",
                        (280, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.65, self.COLOR_TEXT_PRIMARY, 2, cv2.LINE_AA)

        elif telemetry.attention_state == "NO_FACE":
            cv2.rectangle(display, (260, 15), (1020, 75), self.COLOR_ALERT_RED, -1)
            cv2.putText(display, "[!] NO USER DETECTED IN FRAME",
                        (280, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.65, self.COLOR_TEXT_PRIMARY, 2, cv2.LINE_AA)

        return display
