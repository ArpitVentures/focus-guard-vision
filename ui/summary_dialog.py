"""
FocusGuard AI - Session Summary Report Dialog with Recruiter Grades
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
)
from PyQt6.QtCore import Qt
from ui.styles import DARK_THEME_QSS


class SessionSummaryDialog(QDialog):
    """
    Modal Dialog displaying detailed metrics & performance grades upon session completion.
    """
    def __init__(
        self,
        duration_sec: int,
        avg_score: float,
        min_score: float,
        blinks: int,
        alerts: int,
        parent=None
    ):
        super().__init__(parent)
        self.setWindowTitle("Session Performance Report - FocusGuard Studio")
        self.setFixedSize(520, 520)
        self.setStyleSheet(DARK_THEME_QSS)

        self.duration_sec = duration_sec
        self.avg_score = avg_score
        self.min_score = min_score
        self.blinks = blinks
        self.alerts = alerts

        self.init_ui()

    def _get_grade_info(self, score: float):
        """Calculates performance grade and styling based on average score."""
        if score >= 90.0:
            return "Grade A+ (Elite Focus)", "#10B981"
        elif score >= 80.0:
            return "Grade A (Excellent)", "#34D399"
        elif score >= 70.0:
            return "Grade B (Good)", "#38BDF8"
        elif score >= 60.0:
            return "Grade C (Average)", "#F59E0B"
        else:
            return "Grade D (Needs Improvement)", "#EF4444"

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        # Header Title
        title = QLabel("📊 Session Performance Summary")
        title.setObjectName("HeaderTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Main Scorecard & Grade
        score_card = QFrame()
        score_card.setObjectName("CardPanel")
        score_layout = QVBoxLayout(score_card)

        score_header = QLabel("Average Focus Score")
        score_header.setObjectName("CardTitle")
        score_header.setAlignment(Qt.AlignmentFlag.AlignCenter)

        score_val = QLabel(f"{self.avg_score:.1f}%")
        score_val.setObjectName("MetricValue")
        score_val.setAlignment(Qt.AlignmentFlag.AlignCenter)

        grade_text, grade_color = self._get_grade_info(self.avg_score)

        grade_badge = QLabel(grade_text)
        grade_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        grade_badge.setStyleSheet(f"color: {grade_color}; font-size: 15px; font-weight: bold;")

        score_val.setStyleSheet(f"color: {grade_color}; font-size: 38px; font-weight: 800;")

        score_layout.addWidget(score_header)
        score_layout.addWidget(score_val)
        score_layout.addWidget(grade_badge)
        layout.addWidget(score_card)

        # Details Grid
        details_card = QFrame()
        details_card.setObjectName("CardPanel")
        details_layout = QVBoxLayout(details_card)
        details_layout.setSpacing(10)

        hours = self.duration_sec // 3600
        mins = (self.duration_sec % 3600) // 60
        secs = self.duration_sec % 60
        time_str = f"{hours:02d}:{mins:02d}:{secs:02d}"

        t_lbl = QLabel(f"⏱️ Total Duration:  {time_str}")
        m_lbl = QLabel(f"📉 Lowest Focus Dip:  {self.min_score:.1f}%")
        b_lbl = QLabel(f"👁️ Total Blinks:  {self.blinks}")
        a_lbl = QLabel(f"🚨 Distraction/Drowsiness Alerts:  {self.alerts}")

        details_layout.addWidget(t_lbl)
        details_layout.addWidget(m_lbl)
        details_layout.addWidget(b_lbl)
        details_layout.addWidget(a_lbl)
        layout.addWidget(details_card)

        # Close Button
        close_btn = QPushButton("Done & Save Record")
        close_btn.setObjectName("PrimaryButton")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
