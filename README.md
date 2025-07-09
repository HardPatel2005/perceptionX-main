# PerceptionX: Real-time Object Detection with YOLOv11

## 🚀 Overview

PerceptionX is a web-based application designed to perform **real-time object detection** on images and videos using the cutting-edge **YOLOv11 model**. It offers a user-friendly interface for seamless media uploads, AI-powered processing, and intuitive visualization of detected objects. The application leverages a robust **Node.js** backend for web serving and file management, a specialized **Python** backend for AI inference, and **MongoDB Atlas** for secure data persistence.

## ✨ Features

* **Image Object Detection:** Upload an image and receive it back with bounding boxes highlighting detected objects.
* **Video Object Detection:** Upload a video and obtain an annotated video stream with objects detected frame-by-frame.
* **Real-time Progress:** Stay updated with live processing progress through WebSocket communication.
* **MongoDB Integration:** Securely store both original and processed media files in a cloud-hosted MongoDB Atlas database.
* **Scalable Architecture:** A modular design separates the frontend, Node.js backend, and Python AI processing, ensuring better maintainability and paving the way for horizontal scaling.

## 🛠️ Technologies Used

**Frontend:**
* HTML
* CSS
* JavaScript (served by Express)

**Backend (Node.js/Express):**
* `Express.js`: Robust web framework for API and routing.
* `Mongoose`: Elegant ODM (Object Data Modeling) for streamlined MongoDB interaction.
* `Multer`: Middleware specifically designed for handling multipart/form-data, primarily for file uploads.
* `Socket.IO`: Enables real-time, bidirectional, event-based communication for progress updates.
* `Child Process (spawn)`: Facilitates the execution of the Python YOLO script directly from Node.js.

**Backend (Python/YOLO):**
* `Ultralytics YOLO`: The powerful core library enabling YOLOv11 object detection.
* `OpenCV (cv2)`: Essential for comprehensive image and video processing, including frame manipulation and drawing annotations.
* `Pillow (PIL)`: A foundational library for various image handling tasks.
* `NumPy`: Provides fundamental support for numerical operations on image data.
* `Motor (AsyncIO)`: An asynchronous MongoDB driver for non-blocking database operations in Python.
* `Imageio-FFmpeg`: Facilitates efficient video format conversion (e.g., AVI to MP4).

**Database:**
* `MongoDB Atlas`: A highly scalable and reliable cloud-hosted NoSQL database for media file storage.

## 🚀 Project Setup (Local Development)

Follow these steps to get PerceptionX up and running on your local machine.

### 1. Prerequisites

Before you begin, ensure you have the following installed:

* **Node.js:** [LTS version recommended](https://nodejs.org/en/download/)
* **Python:** Python 3.8+ (Download from [python.org](https://www.python.org/downloads/))
* **MongoDB Atlas Account:** (or a local MongoDB instance running)
* **Git:** (for cloning the repository)
* **FFmpeg:** This is crucial for video processing.
    * **Windows:** Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add its binaries directory to your system's `PATH`.
    * **Linux/macOS:**
        * **Ubuntu/Debian:** `sudo apt update && sudo apt install ffmpeg`
        * **macOS (with Homebrew):** `brew install ffmpeg`

### 2. Clone the Repository

Open your terminal or command prompt and execute:

git clone <your-repository-url> # Replace with the actual URL of your repository
cd perceptionX-main
### 3. Configure Environment Variables

Create a new file named `.env` in the root of your `perceptionX-main` directory. This file will store your sensitive configurations.

dotenv
## .env
MONGO_URI="mongodb+srv://<username>:<password>@cluster0.azktf3m.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
PORT=3000
### 4. Install Node.js Dependencies
From your project root directory, install all Node.js packages:
npm install
### 5. Set up Python Virtual Environment and Dependencies
A virtual environment isolates your Python project's dependencies from your system's global Python installation, preventing conflicts.
## Create the virtual environment named 'venv'
python -m venv venv

## Activate the virtual environment
## For Windows (PowerShell or Command Prompt):
.\venv\Scripts\activate
## For macOS/Linux (Bash/Zsh):
source venv/bin/activate
then
pip install -r requirements.txt
###6. Place YOLOv11 Model Weights
You need your pre-trained YOLOv11 model weights.

Create a directory named yolov11 in your project root if it doesn't already exist.
Place your best.pt model file inside the ./yolov11 directory.
Example Path: perceptionX-main/yolov11/best.pt

### 7. Start the Application
With all dependencies installed and configurations set, you can now start the application.
# Ensure you are in the project root and your Python virtual environment is activated
node app.js
