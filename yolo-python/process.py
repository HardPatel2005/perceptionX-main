import os
import requests
import tempfile
import subprocess
from dotenv import load_dotenv

from ultralytics import YOLO

# Required for image and video processing
import numpy as np
import cv2
from PIL import Image
import imageio_ffmpeg as ffmpeg

load_dotenv()

# Model config
HF_URL = "https://huggingface.co/hardbhai/yolo-best/resolve/main/best.pt"
weights_path = "./yolov11/best.pt"

def download_model_if_missing():
    if not os.path.exists(weights_path):
        os.makedirs(os.path.dirname(weights_path), exist_ok=True)
        print("⬇️ Downloading model from Hugging Face...")
        response = requests.get(HF_URL)
        if response.content.strip().startswith(b'<!DOCTYPE html>'):
            print("❌ Model download failed (HTML received).")
            return False
        with open(weights_path, "wb") as f:
            f.write(response.content)
        print("✅ Model downloaded.")
        return True
    return True

def load_model():
    if not os.path.exists(weights_path):
        if not download_model_if_missing():
            return None
    try:
        model = YOLO(weights_path)
        print(f"✅ Model loaded for task: {model.task}")
        return model
    except Exception as e:
        print("❌ Failed to load model:", e)
        return None

def run_detection(file_path, model):
    ext = os.path.splitext(file_path)[1].lower()
    if ext in [".jpg", ".jpeg", ".png"]:
        return run_image_detection(file_path, model)
    elif ext in [".mp4", ".avi", ".mov"]:
        return run_video_detection(file_path, model)
    else:
        return "Unsupported file type"

def run_image_detection(image_path, model):
    try:
        image = Image.open(image_path).convert("RGB")
        image_np = np.array(image)
        results = model(image_np)

        output_path = (
            image_path.replace(".jpg", "_output.jpg")
            .replace(".jpeg", "_output.jpg")
            .replace(".png", "_output.jpg")
        )

        # Copy image to annotate
        annotated_img = image_np.copy()

        # Extract boxes and class info
        if results[0].boxes:
            boxes = results[0].boxes.xyxy.cpu().numpy()  # bounding boxes
            confs = results[0].boxes.conf.cpu().numpy()  # confidence
            clses = results[0].boxes.cls.cpu().numpy().astype(int)  # class ids

            names = model.names  # class name dictionary

            for box, conf, cls in zip(boxes, confs, clses):
                x1, y1, x2, y2 = map(int, box)
                label = f"{names[cls]} {conf:.2f}"
                cv2.rectangle(annotated_img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(annotated_img, label, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        else:
            print("⚠️ No boxes detected.")

        # Save annotated image
        annotated_img_bgr = cv2.cvtColor(annotated_img, cv2.COLOR_RGB2BGR)
        cv2.imwrite(output_path, annotated_img_bgr)
        return output_path

    except Exception as e:
        print("❌ Image detection error:", e)
        return "Error during image detection"


def run_video_detection(video_path, model):
    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return "Error opening video file"

        output_avi = os.path.join(tempfile.gettempdir(), "output.avi")
        fourcc = cv2.VideoWriter_fourcc(*"XVID")
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        out = cv2.VideoWriter(output_avi, fourcc, fps, (width, height))

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            try:
                results = model(frame)
                try:
                    annotated = results[0].plot(show=False)
                except Exception:
                    print("⚠️ plot() failed on frame, using original.")
                    annotated = results[0].orig_img
                out.write(annotated)
            except Exception as e:
                print("❌ Frame processing error:", e)
                break

        cap.release()
        out.release()
        return convert_to_mp4(output_avi)

    except Exception as e:
        print("❌ Video detection error:", e)
        return "Error during video detection"

def convert_to_mp4(input_file):
    try:
        ffmpeg_exe = ffmpeg.get_ffmpeg_exe()
        output_file = input_file.replace(".avi", ".mp4")
        command = [
            ffmpeg_exe, "-y", "-i", input_file,
            "-vcodec", "libx264", "-crf", "23", "-preset", "fast", output_file
        ]
        subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return output_file
    except Exception as e:
        print("❌ MP4 conversion error:", e)
        return "Error converting to MP4"
