from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QLabel, QPushButton, QVBoxLayout, QFrame

from ui.styles import DARK_THEME_QSS


class SessionSummaryDialog(QDialog):
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

        self.duration_sec = duration_sec
        self.avg_score = avg_score
        self.min_score = min_score
        self.blinks = blinks
        self.alerts = alerts

        self.setWindowTitle("Session Performance Report - FocusGuard Studio")
        self.setFixedSize(520, 520)
        self.setStyleSheet(DARK_THEME_QSS)

        self.init_ui()

    @staticmethod
    def _get_grade_info(score: float) -> tuple[str, str]:
        if score >= 90:
            return "Grade A+ (Elite Focus)", "#10B981"
        if score >= 80:
            return "Grade A (Excellent)", "#34D399"
        if score >= 70:
            return "Grade B (Good)", "#38BDF8"
        if score >= 60:
            return "Grade C (Average)", "#F59E0B"
        return "Grade D (Needs Improvement)", "#EF4444"

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        title = QLabel("📊 Session Performance Summary")
        title.setObjectName("HeaderTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        score_card = QFrame()
        score_card.setObjectName("CardPanel")
        score_layout = QVBoxLayout(score_card)

        header = QLabel("Average Focus Score")
        header.setObjectName("CardTitle")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)

        score = QLabel(f"{self.avg_score:.1f}%")
        score.setObjectName("MetricValue")
        score.setAlignment(Qt.AlignmentFlag.AlignCenter)

        grade, color = self._get_grade_info(self.avg_score)

        score.setStyleSheet(
            f"color:{color};font-size:38px;font-weight:800;"
        )

        badge = QLabel(grade)
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setStyleSheet(
            f"color:{color};font-size:15px;font-weight:bold;"
        )

        score_layout.addWidget(header)
        score_layout.addWidget(score)
        score_layout.addWidget(badge)

        layout.addWidget(score_card)

        details_card = QFrame()
        details_card.setObjectName("CardPanel")

        details_layout = QVBoxLayout(details_card)
        details_layout.setSpacing(10)

        h, rem = divmod(self.duration_sec, 3600)
        m, s = divmod(rem, 60)

        details = [
            f"⏱️ Total Duration: {h:02d}:{m:02d}:{s:02d}",
            f"📉 Lowest Focus Dip: {self.min_score:.1f}%",
            f"👁️ Total Blinks: {self.blinks}",
            f"🚨 Distraction/Drowsiness Alerts: {self.alerts}",
        ]

        for text in details:
            details_layout.addWidget(QLabel(text))

        layout.addWidget(details_card)

        button = QPushButton("Done & Save Record")
        button.setObjectName("PrimaryButton")
        button.clicked.connect(self.accept)

        layout.addWidget(button)
