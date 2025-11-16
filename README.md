# 🎵 HandGesture Volume Control

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8--3.12-blue?logo=python)
![OpenCV](https://img.shields.io/badge/OpenCV-4.5+-green?logo=opencv)
![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10+-orange?logo=google)
![Platform](https://img.shields.io/badge/Platform-Windows%20|%20macOS%20|%20Linux-lightgrey)

A real-time hand gesture volume control system that uses computer vision to adjust your system volume through intuitive hand movements.

**Control your computer's volume with just your fingers!** ✋️ 🔊

</div>

## 🎥 Demo

*(You can add a GIF/video here later showing the project in action)*

## ✨ Features

- 🖐️ **Real-time hand tracking** using MediaPipe
- 🔊 **System volume control** via finger gestures  
- 📊 **Visual feedback** with volume level display
- 🎯 **Precise control** using thumb and index finger distance
- ⚡ **Low latency** and smooth performance

## ⚠️ Important Compatibility Note

**🚨 Python Version Requirement**: 
- This project requires **Python 3.8, 3.9, 3.10, 3.11, or 3.12**
- MediaPipe currently **does NOT support Python 3.13+** 
- If you have Python 3.13 or higher, please install Python 3.12

### 🔍 Verifying Your Python Version
```bash
python --version
📥 How to Install Python 3.12 if Needed:
Download Python 3.12 from python.org

During installation, check "Add Python to PATH"

Verify installation: python --version should show 3.12.x

🚀 Quick Start
Prerequisites
📹 Webcam

🖥️ Windows/macOS/Linux

🐍 Python 3.8-3.12

Installation & Setup
Clone the repository

bash
git clone https://github.com/tutorahmed123-bot/HandGesture-Volume-Control.git
cd HandGesture-Volume-Control
Install dependencies

bash
pip install -r requirements.txt
Run the application

bash
python run.py
🎮 How to Use
Launch the application - Run python run.py

Position your hand - Place your hand in front of the webcam

Control volume:

👆 Move thumb and index finger APART → Volume INCREASES

👌 Move thumb and index finger CLOSER → Volume DECREASES

Exit - Press 'Q' key to quit the application

🛠️ Troubleshooting
❌ "Import error: No module named 'pycaw'"
bash
pip install pycaw
❌ MediaPipe installation fails
Ensure you're using Python 3.8-3.12

Try: pip install --upgrade pip

Then: pip install mediapipe

❌ Webcam not working
Ensure no other application is using the camera

Check camera permissions in your system settings

Try a different USB port if using external camera

❌ Permission errors on installation
bash
pip install --user -r requirements.txt
📁 Project Structure
text
HandGesture-Volume-Control/
├── run.py                 # Main application entry point
├── requirements.txt       # Project dependencies
├── README.md             # Project documentation
├── src/                  # Source code modules
│   └── volume_hand_control.py
├── modules/              # Additional utility modules
└── docs/                 # Documentation assets
🛠️ Technologies Used
OpenCV - Computer vision and image processing

MediaPipe - Hand tracking and gesture recognition

Pycaw - Windows audio control

NumPy - Numerical computations

🤝 Contributing
Contributions are welcome! Feel free to:

🐛 Report bugs

💡 Suggest new features

🔧 Submit pull requests

📄 License
This project is open source and available under the MIT License.

<div align="center">
Made with ❤️ using Python and Computer Vision

⭐ Star this repo if you found it helpful!

</div> ```
