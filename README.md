# perceptionX-main
object detection
PerceptionX: Real-time Object Detection with YOLOv11
PerceptionX is a web-based application designed to perform object detection on images and videos using the state-of-the-art YOLOv11 model. It provides a user-friendly interface for uploading media, processing it with AI, and viewing the detected objects. The application leverages a Node.js backend for web serving and file management, a Python backend for AI inference, and MongoDB for data persistence.

Features
Image Object Detection: Upload an image and see detected objects with bounding boxes.

Video Object Detection: Upload a video and get an annotated video with objects detected frame by frame.

Real-time Progress: Live updates on the processing progress using WebSockets.

MongoDB Integration: Securely store original and processed media files in MongoDB Atlas.

Scalable Architecture: Modular design separating front-end, Node.js backend, and Python AI processing for better maintainability and potential for horizontal scaling.

Technologies Used
Frontend: HTML, CSS, JavaScript (served by Express)

Backend (Node.js/Express):

Express.js: Web framework for API and routing.

Mongoose: ODM for MongoDB interaction.

Multer: Middleware for handling file uploads.

Socket.IO: For real-time communication (progress updates).

Child Process (spawn): To execute the Python YOLO script from Node.js.

Backend (Python/YOLO):

Ultralytics YOLO: The core library for YOLOv11 object detection.

OpenCV (cv2): For image and video processing, frame manipulation, and drawing annotations.

Pillow (PIL): For image handling.

NumPy: For numerical operations on image data.

Motor (AsyncIO): Asynchronous MongoDB driver for Python.

Imageio-FFmpeg: For video format conversion (e.g., AVI to MP4).

Database:

MongoDB Atlas: Cloud-hosted NoSQL database for storing media files.

Project Setup (Local Development)
1. Prerequisites:

Node.js (LTS version recommended)

Python 3.8+

MongoDB Atlas Account (or a local MongoDB instance)

Git (for cloning the repository)

FFmpeg (installed on your system and accessible via PATH for video processing)

Windows: Download from ffmpeg.org and add to PATH.

Linux/macOS: sudo apt update && sudo apt install ffmpeg (Ubuntu/Debian) or brew install ffmpeg (macOS with Homebrew).

2. Clone the Repository:

Bash

git clone <your-repository-url>
cd perceptionX-main
3. Configure Environment Variables:

Create a .env file in the root of your perceptionX-main directory.

# .env
MONGO_URI="mongodb+srv://<username>:<password>@cluster0.azktf3m.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
PORT=3000
Replace <username> and <password> with your MongoDB Atlas credentials.

Ensure the MONGO_URI matches the one in your app.js if you have multiple defined.

4. Install Node.js Dependencies:

Bash

npm install
5. Set up Python Virtual Environment and Dependencies:

Bash

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Create requirements.txt if it doesn't exist
# requirements.txt content:
# ultralytics
# motor[asyncio]
# Pillow
# numpy
# opencv-python-headless
# imageio-ffmpeg

# Install Python dependencies
pip install -r requirements.txt
6. Place YOLOv11 Model Weights:

Ensure you have your pre-trained YOLOv11 model weights (e.g., best.pt).

Create a directory ./yolov11 in your project root.

Place your best.pt file inside the ./yolov11 directory.

Example: perceptionX-main/yolov11/best.pt

7. Start the Application:

Bash

# Ensure you are in the project root and your Python venv is activated
node app.js
The server should start on http://localhost:3000/.

Usage
Open your web browser and navigate to http://localhost:3000/.

Go to the "Detect" section.

Upload an image or video file.

Observe the processing progress.

View the processed image/video with object detections.  
