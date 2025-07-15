if (process.env.NODE_ENV !== "production") {
    require("dotenv").config(); // Load .env only in development
}

const express = require("express");
const mongoose = require("mongoose");
const multer = require("multer");
const { spawn } = require("child_process");
const cors = require("cors");
const path = require("path");
const methodOverride = require("method-override");
const ejsMate = require("ejs-mate");
const http = require("http");
const socketIo = require("socket.io");
const fs = require("fs");
const os = require("os");

const File = require(path.join(__dirname, "models", "perceps.js"));

const app = express();
const server = http.createServer(app);
const io = socketIo(server);

// Middleware
app.use(cors());
app.set("view engine", "ejs");
app.set("views", path.join(__dirname, "views"));
app.use(express.urlencoded({ extended: true }));
app.use(methodOverride("_method"));
app.engine("ejs", ejsMate);
app.use(express.static(path.join(__dirname, "/public")));

// MongoDB Connection
const dbUrl = process.env.MONGODB_URI;
mongoose.connect(dbUrl)
    .then(() => console.log("✅ MongoDB Connected"))
    .catch(err => console.error("❌ MongoDB Connection Failed:", err));

// Multer Configuration (Store in Memory)
const storage = multer.memoryStorage();
const upload = multer({ storage });

// Routes
app.get("/", (req, res) => {
    res.render("./perceps/index.ejs");
});

app.get("/detect", (req, res) => {
    res.render("./perceps/detect.ejs");
});

app.post("/process", upload.single("file"), async (req, res) => {
    if (!req.file) {
        return res.status(400).json({ error: "No file uploaded" });
    }

    const fileType = req.file.mimetype.startsWith("image") ? "image" : "video";
    try {
        const newFile = new File({
            filename: req.file.originalname,
            mimetype: req.file.mimetype,
            size: req.file.size,
            data: Buffer.from(req.file.buffer),
            processedData: null
        });

        const savedFile = await newFile.save();
        const pythonScript = path.join(__dirname, "..", "yolo-python", "app.py");
        const pythonProcess = spawn("python", [pythonScript, savedFile._id.toString(), fileType]);

        pythonProcess.stdout.on("data", (data) => {
            console.log(`Python Output: ${data.toString()}`);
            const progressMatch = data.toString().match(/Progress: (\d+)%/);
            if (progressMatch) {
                io.emit("progress", parseInt(progressMatch[1]));
            }
        });

        pythonProcess.stderr.on("data", (data) => {
            console.error(`Python Error: ${data.toString()}`);
        });

        pythonProcess.on("close", (code) => {
            console.log("Python process closed with code:", code);
            if (code === 0) {
                io.emit("progress", 100);
                res.json({ fileId: savedFile._id });
            } else {
                res.status(500).json({ error: "Processing failed" });
            }
        });

    } catch (error) {
        console.error("Error processing file:", error);
        res.status(500).json({ error: "Error processing file." });
    }
});

app.get("/file/:id", async (req, res) => {
    try {
        const file = await File.findById(req.params.id);
        if (!file) {
            return res.status(404).json({ error: "File not found" });
        }

        res.set("Content-Type", file.mimetype);
        res.send(file.data);
    } catch (error) {
        console.error("Error fetching file:", error);
        res.status(500).json({ error: "Error retrieving file." });
    }
});

app.get("/file/:id/processed", async (req, res) => {
    try {
        const file = await File.findById(req.params.id);
        if (!file || !file.processedData) {
            return res.status(404).json({ error: "Processed file not found" });
        }

        if (file.mimetype.startsWith("video")) {
            res.set("Content-Type", file.mimetype);
            res.send(file.processedData);
        } else if (file.mimetype.startsWith("image")) {
            res.set("Content-Type", "image/jpeg");
            res.send(file.processedData);
        } else {
            res.status(400).json({ error: "Unsupported file type" });
        }
    } catch (error) {
        console.error("Error retrieving processed file:", error);
        res.status(500).json({ error: "Error retrieving file." });
    }
});

// Start server
const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
    console.log(`🚀 Server running on http://localhost:${PORT}/`);
});
