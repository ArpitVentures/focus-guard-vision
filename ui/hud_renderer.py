import cv2
import numpy as np
from core.datatypes import FocusTelemetry


class HUDRenderer:

    def __init__(self):
        self.COLOR_INFO = (0, 215, 255)
        self.COLOR_TEXT_PRIMARY = (255, 255, 255)
        self.COLOR_ALERT_RED = (0, 0, 255)
        self.COLOR_ALERT_ORANGE = (0, 140, 255)

    def render(
            self,
            frame: np.ndarray,
            fps: float,
            telemetry: FocusTelemetry
    ) -> np.ndarray:

        overlay = frame.copy()
        cv2.rectangle(overlay, (15, 15), (145, 55), (10, 15, 26), -1)

        display = cv2.addWeighted(overlay, 0.65, frame, 0.35, 0)
        cv2.rectangle(display, (15, 15), (145, 55), (30, 41, 59), 1)

        fps_text = f"FPS: {fps:.1f}"
        cv2.putText(display, fps_text, (28, 42),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, self.COLOR_INFO, 2, cv2.LINE_AA)

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