
import os
import sys
import asyncio
import tempfile
import subprocess
from io import BytesIO
from PIL import Image
import numpy as np
import cv2
import requests
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from ultralytics import YOLO
import imageio_ffmpeg as ffmpeg
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from dotenv import load_dotenv

os.environ["ULTRALYTICS_CONFIG_DIR"] = "/tmp/Ultralytics"
load_dotenv()

MONGO_URI = os.getenv("MONGODB_URI")
DATABASE_NAME = "test"
COLLECTION_NAME = "files"

client = AsyncIOMotorClient(MONGO_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

HF_URL = "https://huggingface.co/hardbhai/yolo-best/resolve/main/best.pt"
weights_path = "./yolov11/best.pt"

def download_model_if_missing():
    if not os.path.exists(weights_path):
        os.makedirs(os.path.dirname(weights_path), exist_ok=True)
        response = requests.get(HF_URL)
        if response.status_code == 200:
            if response.content.strip().startswith(b'<!DOCTYPE html>'):
                raise ValueError("Downloaded file is HTML, not a valid model.")
            with open(weights_path, "wb") as f:
                f.write(response.content)

def load_model():
    if not os.path.exists(weights_path):
        download_model_if_missing()
    return YOLO(weights_path)

model = load_model()

def run_detection(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext in [".jpg", ".jpeg", ".png"]:
        return run_image_detection(file_path)
    elif ext in [".mp4", ".avi", ".mov"]:
        return run_video_detection(file_path)
    else:
        return "Unsupported file type"

def run_image_detection(image_path):
    image = Image.open(image_path).convert("RGB")
    image_np = np.array(image)
    results = model(image_np)
    annotated = results[0].plot()
    output_path = image_path.replace(".jpg", "_output.jpg")
    cv2.imwrite(output_path, cv2.cvtColor(annotated, cv2.COLOR_RGB2BGR))
    return output_path

def run_video_detection(video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return "Error opening video file"

    output_path = os.path.join(tempfile.gettempdir(), "output.avi")
    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        results = model(frame)
        annotated = results[0].plot()
        out.write(annotated)

    cap.release()
    out.release()
    mp4_path = convert_to_mp4(output_path)
    return mp4_path

def convert_to_mp4(input_file):
    ffmpeg_exe = ffmpeg.get_ffmpeg_exe()
    output_file = input_file.replace(".avi", ".mp4")
    command = [ffmpeg_exe, "-y", "-i", input_file, "-vcodec", "libx264", "-crf", "23", "-preset", "fast", output_file]
    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return output_file
