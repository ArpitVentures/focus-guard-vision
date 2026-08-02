# 🛡️ FocusGuard Studio 

> **AI-powered desktop application for real-time focus monitoring using Computer Vision, Explainable AI (XAI), and Edge Computing.**

FocusGuard Studio is a real-time desktop application that continuously monitors user attention using Computer Vision and Explainable AI (XAI). The system performs facial landmark detection, blink analysis, drowsiness detection, and 3D head pose estimation to evaluate focus levels entirely on the local machine without requiring any cloud connectivity.

Built with **Python, PyQt6, OpenCV, MediaPipe, and SQLite**, the application follows a modular multi-threaded architecture that separates the computer vision pipeline from the user interface, ensuring smooth real-time performance. Every focus decision is accompanied by a human-readable explanation, making the system transparent, interpretable, and suitable for AI-based attention analysis.

---

# ✨ Key Features

- 🎯 Real-time 478-point MediaPipe Face Mesh tracking
- 👁️ Eye Aspect Ratio (EAR) based blink detection
- 😴 Micro-sleep and drowsiness detection
- 🧭 3D Head Pose Estimation using OpenCV `solvePnP`
- 🧠 Explainable AI (XAI) priority-based focus engine
- 📈 Dynamic focus score calculation with smooth score damping
- 💻 Modern PyQt6 desktop dashboard with live telemetry
- 🚨 Real-time HUD overlays and distraction alerts
- 💾 SQLite-based session history and analytics
- 📊 Session performance report with recruiter-friendly grading
- 🔒 Fully offline edge AI processing (No cloud dependency)

---

# 🛠️ Tech Stack

| Category | Technologies |
|----------|--------------|
| Programming Language | Python 3 |
| Desktop Framework | PyQt6 |
| Computer Vision | OpenCV |
| Face Tracking | MediaPipe Face Mesh (478 Landmarks) |
| Numerical Computing | NumPy |
| Database | SQLite |
| Architecture | Modular Multi-threaded Desktop Application |
| AI Logic | Explainable AI (XAI) Priority Engine |

---

# 📂 Project Structure

```text
focus-guard-vision/
├── analytics/
├── assets/
├── config/
├── core/
├── database/
├── logs/
├── tests/
├── tracking/
├── ui/
├── utils/
├── vision/
├── main.py
├── requirements.txt
└── README.md
```

---

# 📸 Screenshots

> Screenshots and demo GIF will be added in the next documentation update.

---

# 🚀 Installation

```bash
git clone https://github.com/ArpitVentures/focus-guard-vision.git

cd focus-guard-vision

pip install -r requirements.txt

python main.py
```

---

# 🎯 Future Roadmap

- Session history dashboard
- Historical analytics visualization
- Export reports (CSV / PDF)
- AI-based distraction classification improvements
- Productivity insights
- Multi-user support

---

# 📄 License

This project is licensed under the MIT License.

---

# 👨‍💻 Author

**Arpit Srivastava**

GitHub: [@ArpitVentures](https://github.com/ArpitVentures)
