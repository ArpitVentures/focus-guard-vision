from collections import deque
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QProgressBar
)
from PyQt6.QtGui import QPixmap, QImage, QCloseEvent
from PyQt6.QtCore import Qt, QTimer

from ui.camera_worker import CameraWorker
from ui.styles import DARK_THEME_QSS
from ui.summary_dialog import SessionSummaryDialog
from database.db_manager import DatabaseManager
from core.datatypes import FocusTelemetry
from config.settings import (
    APP_NAME, SCORE_HIGH_THRESHOLD, SCORE_MEDIUM_THRESHOLD
)
from utils.logger import logger


COLOR_GREEN = "#10B981"
COLOR_YELLOW = "#F59E0B"
COLOR_RED = "#EF4444"

STATE_FOCUSED = "FOCUSED"
STATE_LOOKING_AWAY = "LOOKING_AWAY"
STATE_DROWSY = "DROWSY"
STATE_NO_USER = "NO_USER"

BADGE_STYLES = {
    STATE_FOCUSED: ("🟢 STATUS: FOCUSED", "BadgeFocused"),
    STATE_LOOKING_AWAY: ("🟠 STATUS: DISTRACTED", "BadgeDistracted"),
    STATE_DROWSY: ("🔴 STATUS: DROWSY", "BadgeDrowsy"),
    STATE_NO_USER: ("⚠️ STATUS: NO USER", "BadgeDrowsy")
}


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.resize(1280, 840)
        self.setStyleSheet(DARK_THEME_QSS)

        self.db = DatabaseManager()

        self.elapsed_seconds = 0
        self.alert_count = 0
        self.total_blinks = 0
        self.is_tracking = False
        self.is_paused = False
        self.last_state = STATE_FOCUSED

        self.score_history = deque(maxlen=5000)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_session_timer)

        self.worker = CameraWorker()
        self.worker.frame_processed.connect(self.update_ui)

        self.init_ui()
        logger.info("MainWindow PyQt6 Studio UI initialized with SQLite Integration.")

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        left_box = self._create_left_panel()
        right_box = self._create_right_panel()

        main_layout.addWidget(left_box, stretch=3)
        main_layout.addWidget(right_box, stretch=1)

    def _create_left_panel(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("CardPanel")
        layout = QVBoxLayout(panel)

        title_label = QLabel("🛡️ FocusGuard Studio")
        title_label.setObjectName("HeaderTitle")
        layout.addWidget(title_label)

        self.video_label = QLabel("Click 'Start Session' to launch vision pipeline...")
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setStyleSheet("background-color: #030712; border-radius: 10px; color: #64748B; font-size: 15px;")
        self.video_label.setMinimumSize(800, 520)
        layout.addWidget(self.video_label, stretch=1)

        button_layout = QHBoxLayout()
        self.start_btn = QPushButton("▶ Start Session")
        self.start_btn.setObjectName("PrimaryButton")
        self.start_btn.clicked.connect(self.toggle_tracking)

        self.stop_btn = QPushButton("⏹ End Session")
        self.stop_btn.setObjectName("StopButton")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.end_session)

        button_layout.addWidget(self.start_btn)
        button_layout.addWidget(self.stop_btn)
        layout.addLayout(button_layout)

        return panel

    def _create_right_panel(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("CardPanel")
        layout = QVBoxLayout(panel)
        layout.setSpacing(16)

        sidebar_title = QLabel("📊 Live Telemetry")
        sidebar_title.setObjectName("HeaderTitle")
        layout.addWidget(sidebar_title)

        self.state_badge = QLabel("🟢 STATUS: IDLE")
        self.state_badge.setObjectName("BadgeFocused")
        self.state_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.state_badge)

        layout.addWidget(self._create_score_card())
        layout.addWidget(self._create_telemetry_card())
        layout.addWidget(self._create_session_card())

        layout.addStretch()
        return panel

    def _create_score_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("CardPanel")
        layout = QVBoxLayout(card)

        score_title = QLabel("Live Focus Score")
        score_title.setObjectName("CardTitle")

        self.score_label = QLabel("100.0%")
        self.score_label.setObjectName("MetricValue")
        self.score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.sub_score_label = QLabel("Highly Attentive")
        self.sub_score_label.setObjectName("SubMetricValue")
        self.sub_score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.score_bar = QProgressBar()
        self.score_bar.setObjectName("ProgressBarGreen")
        self.score_bar.setValue(100)

        layout.addWidget(score_title)
        layout.addWidget(self.score_label)
        layout.addWidget(self.sub_score_label)
        layout.addWidget(self.score_bar)
        return card

    def _create_telemetry_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("CardPanel")
        layout = QVBoxLayout(card)
        layout.setSpacing(10)

        self.reason_label = QLabel("💡 Reason: Waiting for session...")
        self.reason_label.setWordWrap(True)
        self.reason_label.setStyleSheet("color: #38BDF8; font-weight: 600;")

        self.blink_label = QLabel("👁️ Total Blinks: 0")
        self.ear_label = QLabel("😴 Average EAR: 0.000")
        self.pose_label = QLabel("🧭 Head Yaw Angle: 0.0 deg")

        layout.addWidget(self.reason_label)
        layout.addWidget(self.blink_label)
        layout.addWidget(self.ear_label)
        layout.addWidget(self.pose_label)
        return card

    def _create_session_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("CardPanel")
        layout = QVBoxLayout(card)
        layout.setSpacing(8)

        session_title = QLabel("⏱️ Session Summary")
        session_title.setObjectName("CardTitle")

        self.session_time_label = QLabel("Session Time: 00:00:00")
        self.alert_count_label = QLabel("Total Alerts: 0")

        layout.addWidget(session_title)
        layout.addWidget(self.session_time_label)
        layout.addWidget(self.alert_count_label)
        return card

    def toggle_tracking(self):
        if not self.is_tracking:
            self._start_tracking_session()
        elif self.is_paused:
            self._resume_tracking_session()
        else:
            self._pause_tracking_session()

    def _start_tracking_session(self):
        self.is_tracking = True
        self.is_paused = False
        self._update_button_style(self.start_btn, "⏸ Pause Tracking", "PauseButton")
        self.stop_btn.setEnabled(True)

        self.elapsed_seconds = 0
        self.alert_count = 0
        self.total_blinks = 0
        self.score_history.clear()
        self.timer.start(1000)
        self.worker.start()
        logger.info("New Session started.")

    def _resume_tracking_session(self):
        self.is_paused = False
        self._update_button_style(self.start_btn, "⏸ Pause Tracking", "PauseButton")
        self.timer.start(1000)
        self.worker.start()
        logger.info("Session resumed.")

    def _pause_tracking_session(self):
        self.is_paused = True
        self._update_button_style(self.start_btn, "▶ Resume Tracking", "PrimaryButton")
        self.timer.stop()
        self.worker.stop()
        self.video_label.setText("Session Paused.")
        logger.info("Session paused.")

    def end_session(self):
        if not self.is_tracking:
            return

        self.timer.stop()
        self.worker.stop()

        avg_score, min_score = self._calculate_score_aggregates()

        self.db.save_session(
            duration_sec=self.elapsed_seconds,
            avg_score=avg_score,
            min_score=min_score,
            total_blinks=self.total_blinks,
            total_alerts=self.alert_count
        )

        summary_dialog = SessionSummaryDialog(
            duration_sec=self.elapsed_seconds,
            avg_score=avg_score,
            min_score=min_score,
            blinks=self.total_blinks,
            alerts=self.alert_count,
            parent=self
        )
        summary_dialog.exec()

        self._reset_session_state()

    def _calculate_score_aggregates(self) -> tuple[float, float]:
        avg_score = sum(self.score_history) / len(self.score_history) if self.score_history else 100.0
        min_score = min(self.score_history) if self.score_history else 100.0
        return avg_score, min_score

    def _reset_session_state(self):
        self.is_tracking = False
        self.is_paused = False
        self._update_button_style(self.start_btn, "▶ Start Session", "PrimaryButton")
        self.stop_btn.setEnabled(False)
        self.video_label.setText("Session Ended. Record saved to local database.")
        logger.info("Session ended and saved.")

    def _update_button_style(self, button: QPushButton, text: str, object_name: str):
        button.setText(text)
        button.setObjectName(object_name)
        button.setStyle(button.style())

    def update_session_timer(self):
        self.elapsed_seconds += 1
        hours = self.elapsed_seconds // 3600
        minutes = (self.elapsed_seconds % 3600) // 60
        seconds = self.elapsed_seconds % 60
        self.session_time_label.setText(f"Session Time: {hours:02d}:{minutes:02d}:{seconds:02d}")

    def update_ui(self, qt_image: QImage, telemetry: FocusTelemetry):
        self._render_video_frame(qt_image)
        self._update_score_ui(telemetry.focus_score)
        self._update_state_ui(telemetry.attention_state)
        self._update_telemetry_details(telemetry)

    def _render_video_frame(self, qt_image: QImage):
        pixmap = QPixmap.fromImage(qt_image)
        target_size = self.video_label.size()
        scaled_pixmap = pixmap.scaled(
            target_size,
            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation
        )
        x = (scaled_pixmap.width() - target_size.width()) // 2
        y = (scaled_pixmap.height() - target_size.height()) // 2
        cropped_pixmap = scaled_pixmap.copy(x, y, target_size.width(), target_size.height())
        self.video_label.setPixmap(cropped_pixmap)

    def _update_score_ui(self, score: float):
        self.score_history.append(score)
        self.score_label.setText(f"{score:.1f}%")
        self.score_bar.setValue(int(score))

        if score >= SCORE_HIGH_THRESHOLD:
            prog_object, label, color = "ProgressBarGreen", "Highly Attentive", COLOR_GREEN
        elif score >= SCORE_MEDIUM_THRESHOLD:
            prog_object, label, color = "ProgressBarYellow", "Slightly Distracted", COLOR_YELLOW
        else:
            prog_object, label, color = "ProgressBarRed", "Critical Attention Drop", COLOR_RED

        self.score_bar.setObjectName(prog_object)
        self.score_label.setStyleSheet(f"color: {color};")
        self.sub_score_label.setText(label)
        self.sub_score_label.setStyleSheet(f"color: {color};")
        self.score_bar.setStyle(self.score_bar.style())

    def _update_state_ui(self, state: str):
        if state != self.last_state and state in [STATE_LOOKING_AWAY, STATE_DROWSY]:
            self.alert_count += 1
            self.alert_count_label.setText(f"Total Alerts: {self.alert_count}")
        self.last_state = state

        text, object_name = BADGE_STYLES.get(state, BADGE_STYLES[STATE_NO_USER])
        self.state_badge.setText(text)
        self.state_badge.setObjectName(object_name)
        self.state_badge.setStyle(self.state_badge.style())

    def _update_telemetry_details(self, telemetry: FocusTelemetry):
        self.total_blinks = telemetry.eye_metrics.blink_count
        self.reason_label.setText(f"💡 Reason: {telemetry.primary_reason}")
        self.blink_label.setText(f"👁️ Total Blinks: {self.total_blinks}")
        self.ear_label.setText(f"😴 Average EAR: {telemetry.eye_metrics.avg_ear:.3f}")
        self.pose_label.setText(f"🧭 Head Yaw Angle: {telemetry.head_pose.yaw:.1f} deg")

    def closeEvent(self, event: QCloseEvent):
        self.worker.stop()
        super().closeEvent(event)