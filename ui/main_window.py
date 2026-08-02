"""
FocusGuard AI - Main Desktop Studio Dashboard Window (Final Production Version)
"""
import time
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
from config.settings import APP_NAME
from utils.logger import logger


class MainWindow(QMainWindow):
    """
    Main Studio Dashboard featuring Center Crop scaling, SQLite Session Telemetry, and Smart Controls.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.resize(1280, 840)
        self.setStyleSheet(DARK_THEME_QSS)

        # UI Attributes
        self.video_label: QLabel
        self.start_btn: QPushButton
        self.stop_btn: QPushButton
        self.state_badge: QLabel
        self.score_label: QLabel
        self.sub_score_label: QLabel
        self.score_bar: QProgressBar
        self.reason_label: QLabel
        self.blink_label: QLabel
        self.ear_label: QLabel
        self.pose_label: QLabel
        self.session_time_label: QLabel
        self.alert_count_label: QLabel

        # Database Manager
        self.db = DatabaseManager()

        # Session Telemetry State
        self.elapsed_seconds = 0
        self.alert_count = 0
        self.is_tracking = False
        self.is_paused = False
        self.last_state = "FOCUSED"

        # Focus Score Statistics
        self.score_history = []

        # Session Timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_session_timer)

        # Worker Thread
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

        # ================= LEFT PANEL: LIVE VIDEO =================
        left_box = QFrame()
        left_box.setObjectName("CardPanel")
        left_layout = QVBoxLayout(left_box)

        # Header Title
        title_label = QLabel("🛡️ FocusGuard Studio")
        title_label.setObjectName("HeaderTitle")
        left_layout.addWidget(title_label)

        # Video Container
        self.video_label = QLabel("Click 'Start Session' to launch vision pipeline...")
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setStyleSheet("background-color: #030712; border-radius: 10px; color: #64748B; font-size: 15px;")
        self.video_label.setMinimumSize(800, 520)
        left_layout.addWidget(self.video_label, stretch=1)

        # Controls Layout
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
        left_layout.addLayout(button_layout)

        main_layout.addWidget(left_box, stretch=3)

        # ================= RIGHT PANEL: TELEMETRY SIDEBAR =================
        right_box = QFrame()
        right_box.setObjectName("CardPanel")
        right_layout = QVBoxLayout(right_box)
        right_layout.setSpacing(16)

        sidebar_title = QLabel("📊 Live Telemetry")
        sidebar_title.setObjectName("HeaderTitle")
        right_layout.addWidget(sidebar_title)

        # 1. Pill Status Badge
        self.state_badge = QLabel("🟢 STATUS: IDLE")
        self.state_badge.setObjectName("BadgeFocused")
        self.state_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(self.state_badge)

        # 2. Focus Score Meter Card
        score_card = QFrame()
        score_card.setObjectName("CardPanel")
        score_layout = QVBoxLayout(score_card)

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

        score_layout.addWidget(score_title)
        score_layout.addWidget(self.score_label)
        score_layout.addWidget(self.sub_score_label)
        score_layout.addWidget(self.score_bar)
        right_layout.addWidget(score_card)

        # 3. Telemetry Details Card
        telemetry_card = QFrame()
        telemetry_card.setObjectName("CardPanel")
        telemetry_layout = QVBoxLayout(telemetry_card)
        telemetry_layout.setSpacing(10)

        self.reason_label = QLabel("💡 Reason: Waiting for session...")
        self.reason_label.setWordWrap(True)
        self.reason_label.setStyleSheet("color: #38BDF8; font-weight: 600;")

        self.blink_label = QLabel("👁️ Total Blinks: 0")
        self.ear_label = QLabel("😴 Average EAR: 0.000")
        self.pose_label = QLabel("🧭 Head Yaw Angle: 0.0 deg")

        telemetry_layout.addWidget(self.reason_label)
        telemetry_layout.addWidget(self.blink_label)
        telemetry_layout.addWidget(self.ear_label)
        telemetry_layout.addWidget(self.pose_label)
        right_layout.addWidget(telemetry_card)

        # 4. Session Analytics Summary Card
        session_card = QFrame()
        session_card.setObjectName("CardPanel")
        session_layout = QVBoxLayout(session_card)
        session_layout.setSpacing(8)

        session_title = QLabel("⏱️ Session Summary")
        session_title.setObjectName("CardTitle")

        self.session_time_label = QLabel("Session Time: 00:00:00")
        self.alert_count_label = QLabel("Total Alerts: 0")

        session_layout.addWidget(session_title)
        session_layout.addWidget(self.session_time_label)
        session_layout.addWidget(self.alert_count_label)
        right_layout.addWidget(session_card)

        right_layout.addStretch()
        main_layout.addWidget(right_box, stretch=1)

    def toggle_tracking(self):
        """Handles Smart Button State: Start -> Pause -> Resume"""
        if not self.is_tracking:
            # Start Session
            self.is_tracking = True
            self.is_paused = False
            self.start_btn.setText("⏸ Pause Tracking")
            self.start_btn.setObjectName("PauseButton")
            self.start_btn.setStyle(self.start_btn.style())
            self.stop_btn.setEnabled(True)

            self.elapsed_seconds = 0
            self.alert_count = 0
            self.score_history.clear()
            self.timer.start(1000)
            self.worker.start()
            logger.info("New Session started.")

        elif self.is_paused:
            # Resume Session
            self.is_paused = False
            self.start_btn.setText("⏸ Pause Tracking")
            self.start_btn.setObjectName("PauseButton")
            self.start_btn.setStyle(self.start_btn.style())
            self.timer.start(1000)
            self.worker.start()
            logger.info("Session resumed.")

        else:
            # Pause Session
            self.is_paused = True
            self.start_btn.setText("▶ Resume Tracking")
            self.start_btn.setObjectName("PrimaryButton")
            self.start_btn.setStyle(self.start_btn.style())
            self.timer.stop()
            self.worker.stop()
            self.video_label.setText("Session Paused.")
            logger.info("Session paused.")

    def end_session(self):
        """Terminates active session, saves metrics to SQLite DB, and opens report dialog."""
        if not self.is_tracking:
            return

        self.timer.stop()
        self.worker.stop()

        # Compute Session Aggregates
        avg_score = sum(self.score_history) / len(self.score_history) if self.score_history else 100.0
        min_score = min(self.score_history) if self.score_history else 100.0
        total_blinks = int(self.blink_label.text().split(":")[-1].strip()) if ":" in self.blink_label.text() else 0

        # Save to SQLite Database
        self.db.save_session(
            duration_sec=self.elapsed_seconds,
            avg_score=avg_score,
            min_score=min_score,
            total_blinks=total_blinks,
            total_alerts=self.alert_count
        )

        # Show Performance Report Dialog
        summary_dialog = SessionSummaryDialog(
            duration_sec=self.elapsed_seconds,
            avg_score=avg_score,
            min_score=min_score,
            blinks=total_blinks,
            alerts=self.alert_count,
            parent=self
        )
        summary_dialog.exec()

        # Reset Controls
        self.is_tracking = False
        self.is_paused = False
        self.start_btn.setText("▶ Start Session")
        self.start_btn.setObjectName("PrimaryButton")
        self.start_btn.setStyle(self.start_btn.style())
        self.stop_btn.setEnabled(False)
        self.video_label.setText("Session Ended. Record saved to local database.")
        logger.info("Session ended and saved.")

    def update_session_timer(self):
        """Updates HH:MM:SS timer readout every second."""
        self.elapsed_seconds += 1
        hours = self.elapsed_seconds // 3600
        minutes = (self.elapsed_seconds % 3600) // 60
        seconds = self.elapsed_seconds % 60
        self.session_time_label.setText(f"Session Time: {hours:02d}:{minutes:02d}:{seconds:02d}")

    def update_ui(self, qt_image: QImage, telemetry: FocusTelemetry):
        """Updates UI with Center Crop video scaling, telemetry, and score tracking."""
        pixmap = QPixmap.fromImage(qt_image)

        # Center Crop Scaling
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

        # Focus Score & History
        score = telemetry.focus_score
        self.score_history.append(score)
        self.score_label.setText(f"{score:.1f}%")
        self.score_bar.setValue(int(score))

        if score >= 80.0:
            self.score_bar.setObjectName("ProgressBarGreen")
            self.score_label.setStyleSheet("color: #10B981;")
            self.sub_score_label.setText("Highly Attentive")
            self.sub_score_label.setStyleSheet("color: #10B981;")
        elif score >= 50.0:
            self.score_bar.setObjectName("ProgressBarYellow")
            self.score_label.setStyleSheet("color: #F59E0B;")
            self.sub_score_label.setText("Slightly Distracted")
            self.sub_score_label.setStyleSheet("color: #F59E0B;")
        else:
            self.score_bar.setObjectName("ProgressBarRed")
            self.score_label.setStyleSheet("color: #EF4444;")
            self.sub_score_label.setText("Critical Attention Drop")
            self.sub_score_label.setStyleSheet("color: #EF4444;")

        self.score_bar.setStyle(self.score_bar.style())

        # Pill Status Badge & Alert Counter
        state = telemetry.attention_state
        if state != self.last_state and state in ["LOOKING_AWAY", "DROWSY"]:
            self.alert_count += 1
            self.alert_count_label.setText(f"Total Alerts: {self.alert_count}")
        self.last_state = state

        if state == "FOCUSED":
            self.state_badge.setText("🟢 STATUS: FOCUSED")
            self.state_badge.setObjectName("BadgeFocused")
        elif state == "LOOKING_AWAY":
            self.state_badge.setText("🟠 STATUS: DISTRACTED")
            self.state_badge.setObjectName("BadgeDistracted")
        elif state == "DROWSY":
            self.state_badge.setText("🔴 STATUS: DROWSY")
            self.state_badge.setObjectName("BadgeDrowsy")
        else:
            self.state_badge.setText("⚠️ STATUS: NO USER")
            self.state_badge.setObjectName("BadgeDrowsy")

        self.state_badge.setStyle(self.state_badge.style())

        # Telemetry Labels
        self.reason_label.setText(f"💡 Reason: {telemetry.primary_reason}")
        self.blink_label.setText(f"👁️ Total Blinks: {telemetry.eye_metrics.blink_count}")
        self.ear_label.setText(f"😴 Average EAR: {telemetry.eye_metrics.avg_ear:.3f}")
        self.pose_label.setText(f"🧭 Head Yaw Angle: {telemetry.head_pose.yaw:.1f} deg")

    def closeEvent(self, event: QCloseEvent) -> None:
        """Clean shutdown when user closes app window."""
        self.worker.stop()
        super().closeEvent(event)
