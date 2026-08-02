DARK_THEME_QSS = """
QMainWindow, QDialog {
    background-color: #090D16;
    color: #F8FAFC;
    font-family: 'Segoe UI', Roboto, Helvetica, sans-serif;
}

QFrame#CardPanel {
    background-color: #111827;
    border: 1px solid #1F2937;
    border-radius: 14px;
}

QLabel#HeaderTitle {
    font-size: 20px;
    font-weight: bold;
    color: #38BDF8;
}

QLabel#CardTitle {
    font-size: 12px;
    font-weight: 700;
    color: #94A3B8;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

QLabel#MetricValue {
    font-size: 32px;
    font-weight: 800;
    color: #F8FAFC;
}

QLabel#SubMetricValue {
    font-size: 13px;
    font-weight: 600;
    color: #10B981;
}

QLabel#BadgeFocused {
    background-color: rgba(16, 185, 129, 0.15);
    color: #34D399;
    border: 1px solid #059669;
    border-radius: 16px;
    padding: 8px 16px;
    font-size: 14px;
    font-weight: bold;
}

QLabel#BadgeDistracted {
    background-color: rgba(245, 158, 11, 0.15);
    color: #FBBF24;
    border: 1px solid #D97706;
    border-radius: 16px;
    padding: 8px 16px;
    font-size: 14px;
    font-weight: bold;
}

QLabel#BadgeDrowsy {
    background-color: rgba(239, 68, 68, 0.15);
    color: #F87171;
    border: 1px solid #DC2626;
    border-radius: 16px;
    padding: 8px 16px;
    font-size: 14px;
    font-weight: bold;
}

QPushButton#PrimaryButton {
    background-color: #0284C7;
    color: #FFFFFF;
    border: none;
    border-radius: 10px;
    padding: 12px 20px;
    font-size: 14px;
    font-weight: bold;
}

QPushButton#PrimaryButton:hover {
    background-color: #0369A1;
}

QPushButton#PauseButton {
    background-color: #D97706;
    color: #FFFFFF;
    border: none;
    border-radius: 10px;
    padding: 12px 20px;
    font-size: 14px;
    font-weight: bold;
}

QPushButton#PauseButton:hover {
    background-color: #B45309;
}

QPushButton#StopButton {
    background-color: #E11D48;
    color: #FFFFFF;
    border: none;
    border-radius: 10px;
    padding: 12px 20px;
    font-size: 14px;
    font-weight: bold;
}

QPushButton#StopButton:hover {
    background-color: #BE123C;
}

QPushButton:disabled {
    background-color: #374151;
    color: #94A3B8;
}

QProgressBar {
    border: 1px solid #1F2937;
    border-radius: 8px;
    background-color: #030712;
    text-align: center;
    color: #FFFFFF;
    font-size: 11px;
    font-weight: bold;
    height: 16px;
}

QProgressBar#ProgressBarGreen::chunk {
    background-color: #10B981;
    border-radius: 6px;
}

QProgressBar#ProgressBarYellow::chunk {
    background-color: #F59E0B;
    border-radius: 6px;
}

QProgressBar#ProgressBarRed::chunk {
    background-color: #EF4444;
    border-radius: 6px;
}
"""
