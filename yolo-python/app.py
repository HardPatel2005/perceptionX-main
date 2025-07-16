from flask import Flask, request, jsonify
from flask_cors import CORS
import os

# Create Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS

# Example route to test the app
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "YOLO API is running ✅"})

# Example POST route for detection (adjust as needed)
@app.route("/detect", methods=["POST"])
def detect():
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    # You can save the file temporarily or directly process it
    temp_path = os.path.join("/tmp", file.filename)
    file.save(temp_path)

    # Do your YOLO detection logic here
    # For now, return a dummy success message
    return jsonify({
        "filename": file.filename,
        "message": "Detection completed (placeholder)"
    })

# Needed for running directly (optional for Gunicorn)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(debug=True, host="0.0.0.0", port=port)

# import sys
# # import os
# import asyncio
# import subprocess
# import tempfile
# from io import BytesIO

# import cv2
# import numpy as np
# import requests
# from PIL import Image
# from bson import ObjectId
# from motor.motor_asyncio import AsyncIOMotorClient
# from ultralytics import YOLO
# import imageio_ffmpeg as ffmpeg
# import matplotlib
# matplotlib.use('Agg')  # For headless environments like Render
# import matplotlib.pyplot as plt
# from dotenv import load_dotenv

# # Ensure Ultralytics config doesn't attempt GUI access
# os.environ["ULTRALYTICS_CONFIG_DIR"] = "/tmp/Ultralytics"

# # 🔹 Load environment variables
# load_dotenv()

# MONGO_URI = os.getenv("MONGODB_URI")
# if not MONGO_URI:
#     print("❌ MONGODB_URI not found in .env file")
#     exit(1)

# DATABASE_NAME = "test"
# COLLECTION_NAME = "files"

# # 🔹 MongoDB Client
# client = AsyncIOMotorClient(MONGO_URI)
# db = client[DATABASE_NAME]
# collection = db[COLLECTION_NAME]

# # 🔹 YOLO model download from Hugging Face
# HF_URL = "https://huggingface.co/hardbhai/yolo-best/resolve/main/best.pt"
# weights_path = "./yolov11/best.pt"

# def download_model_if_missing():
#     if not os.path.exists(weights_path):
#         print("📥 Downloading best.pt from Hugging Face...")
#         os.makedirs(os.path.dirname(weights_path), exist_ok=True)
#         response = requests.get(HF_URL)
#         if response.status_code == 200:
#             if response.content.strip().startswith(b'<!DOCTYPE html>'):
#                 print("❌ ERROR: Downloaded file is HTML, not a valid model.")
#                 exit(1)
#             with open(weights_path, "wb") as f:
#                 f.write(response.content)
#             print("✅ best.pt downloaded successfully!")
#         else:
#             print(f"❌ Failed to download: {response.status_code}")
#             exit(1)

# download_model_if_missing()

# def load_model():
#     print(f"🔍 Checking if model exists: {weights_path}")
#     if not os.path.exists(weights_path):
#         print(f" Model NOT FOUND at {weights_path}")
#         exit(1)
#     print(f" Model exists: {weights_path}")    
#     model = YOLO(weights_path)
#     print("✅ YOLO model loaded successfully!")
#     return model

# async def fetch_file_from_mongo(file_id):
#     print(f"🔍 Searching for file ID: {file_id}")
#     try:
#         object_id = ObjectId(file_id)
#     except Exception as e:
#         print(f"❌ Invalid ObjectId format: {e}")
#         return None

#     file = await collection.find_one({"_id": object_id})

#     if file:
#         print(f"📁 File Found: {file['filename']}")
#         file_data = file.get("data")
#         if not file_data:
#             print("❌ File data is missing in MongoDB")
#             return None
#         return file_data
#     else:
#         print("❌ File not found in MongoDB")
#         return None

# async def save_processed_file(file_id, processed_data):
#     try:
#         object_id = ObjectId(file_id)
#     except Exception as e:
#         print(f"❌ Invalid ObjectId format: {e}")
#         return

#     result = await collection.update_one(
#         {"_id": object_id},
#         {"$set": {"processedData": processed_data}}
#     )

#     if result.modified_count > 0:
#         print(f"✅ Processed file saved to MongoDB for file ID: {file_id}")
#     else:
#         print("❌ Failed to save processed file in MongoDB")

# async def process_image(file_id, model):
#     image_data = await fetch_file_from_mongo(file_id)
#     if not image_data:
#         return

#     try:
#         image = Image.open(BytesIO(image_data))
#         image.verify()
#         image = Image.open(BytesIO(image_data)).convert("RGB")
#     except Exception as e:
#         print(f"❌ Image decoding error: {e}")
#         return

#     image_np = np.array(image)
#     results = model(image_np)
#     annotated_image = results[0].plot()

#     _, buffer = cv2.imencode(".jpg", cv2.cvtColor(annotated_image, cv2.COLOR_RGB2BGR))
#     processed_image_binary = buffer.tobytes()

#     await save_processed_file(file_id, processed_image_binary)

# async def process_video(file_id, model):
#     file_data = await fetch_file_from_mongo(file_id)
#     if not file_data:
#         return

#     temp_video_path = os.path.join(tempfile.gettempdir(), "temp_video.mp4")
#     with open(temp_video_path, "wb") as f:
#         f.write(file_data)

#     cap = cv2.VideoCapture(temp_video_path)
#     if not cap.isOpened():
#         print("❌ Error opening video file")
#         return

#     total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
#     processed_frames = 0
#     temp_output = os.path.join(tempfile.gettempdir(), "temp_output.avi")

#     fourcc = cv2.VideoWriter_fourcc(*"XVID")
#     fps = int(cap.get(cv2.CAP_PROP_FPS))
#     width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
#     height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
#     out = cv2.VideoWriter(temp_output, fourcc, fps, (width, height))

#     while cap.isOpened():
#         ret, frame = cap.read()
#         if not ret:
#             break
#         results = model(frame)
#         annotated_frame = results[0].plot()
#         out.write(annotated_frame)
#         processed_frames += 1
#         progress = int((processed_frames / total_frames) * 100)
#         print(f"📹 Video Processing Progress: {progress}%")

#     cap.release()
#     out.release()

#     processed_video_path = convert_to_mp4(temp_output)

#     with open(processed_video_path, "rb") as f:
#         processed_video_binary = f.read()

#     await save_processed_file(file_id, processed_video_binary)

# def convert_to_mp4(input_file):
#     ffmpeg_command = ffmpeg.get_ffmpeg_exe()
#     output_file = input_file.replace(".avi", ".mp4")
#     command = [ffmpeg_command, "-y", "-i", input_file, "-vcodec", "libx264", "-crf", "23", "-preset", "fast", output_file]
#     subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#     return output_file

# if __name__ == "__main__":
#     if len(sys.argv) < 3:
#         print("Usage: python app.py <file_id> <file_type>")
#         sys.exit(1)

#     file_id = sys.argv[1]
#     file_type = sys.argv[2]
#     model = load_model()

#     try:
#         loop = asyncio.get_running_loop()
#     except RuntimeError:
#         loop = asyncio.new_event_loop()
#         asyncio.set_event_loop(loop)

#     if file_type.startswith("image"):
#         loop.run_until_complete(process_image(file_id, model))
#     elif file_type.startswith("video"):
#         loop.run_until_complete(process_video(file_id, model))
#     else:
#         print("❌ Invalid file type. Use 'image' or 'video'")
