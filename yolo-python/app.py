from flask import Flask, request, jsonify, send_file, abort
from flask_cors import CORS
import os
import mimetypes
from werkzeug.utils import secure_filename
from process import load_model, run_detection  # Import from process.py

app = Flask(__name__)
CORS(app)

UPLOAD_DIR = os.path.abspath("./uploads")  # More reliable than /tmp on Windows
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".mp4", ".avi", ".mov"}

@app.route("/", methods=["GET"])
def home():
    
    return jsonify({"message": "YOLO API is running ✅"})

# Load YOLO model at startup
model = load_model()
if model is None:
    print("❌ Model failed to load. Check Hugging Face URL or local file.")
else:
    print("✅ YOLO model loaded and ready.")

@app.route("/detect", methods=["POST"])
def detect():
    if model is None:
        return jsonify({"error": "Model is not loaded. Try again later."}), 500

    file = request.files.get("file")
    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    filename = secure_filename(file.filename)
    ext = os.path.splitext(filename)[1].lower()

    if ext not in ALLOWED_EXTENSIONS:
        return jsonify({"error": f"Unsupported file type: {ext}"}), 400

    original_path = os.path.join(UPLOAD_DIR, filename)

    try:
        # Save file to disk
        file.save(original_path)
        file_size = os.path.getsize(original_path)
        print(f"📁 File saved to {original_path} ({file_size} bytes)")

        if file_size == 0:
            return jsonify({"error": "Uploaded file is empty"}), 400

        # Run YOLO detection
        processed_path = run_detection(original_path, model)

        if not processed_path or not os.path.exists(processed_path):
            return jsonify({"error": "Processing failed or no output generated"}), 500

    except Exception as e:
        print(f"❌ Error during detection: {str(e)}")
        return jsonify({"error": "Detection failed", "details": str(e)}), 500

    return jsonify({
        "filename": filename,
        "processed_filename": os.path.basename(processed_path),
        "message": f"Detection completed for {filename}"
    })

@app.route("/file/<filename>", methods=["GET", "HEAD"])
def serve_file(filename):
    file_path = os.path.join(UPLOAD_DIR, secure_filename(filename))
    if not os.path.exists(file_path):
        return abort(404)

    mime_type, _ = mimetypes.guess_type(file_path)
    return send_file(file_path, mimetype=mime_type or "application/octet-stream")

@app.route("/file/<filename>/processed", methods=["GET", "HEAD"])
def serve_processed_file(filename):
    processed_filename = f"processed_{secure_filename(filename)}"
    file_path = os.path.join(UPLOAD_DIR, processed_filename)

    if not os.path.exists(file_path):
        return abort(404)

    mime_type, _ = mimetypes.guess_type(file_path)
    return send_file(file_path, mimetype=mime_type or "application/octet-stream")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(debug=True, host="0.0.0.0", port=port)
