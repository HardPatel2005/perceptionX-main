if (process.env.NODE_ENV !== "production") {
    require("dotenv").config(); // Load .env only in development
}

const express = require("express");
const mongoose = require("mongoose");
const multer = require("multer");
const axios = require("axios");
const cors = require("cors");
const path = require("path");
const methodOverride = require("method-override");
const ejsMate = require("ejs-mate");
const http = require("http");
const socketIo = require("socket.io");
const fs = require("fs");
const os = require("os");
const FormData = require('form-data');
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
    .then(() => console.log("\u2705 MongoDB Connected"))
    .catch(err => console.error("\u274C MongoDB Connection Failed:", err));

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

    const formData = new FormData();
    formData.append("file", req.file.buffer, {
        filename: req.file.originalname,
        contentType: req.file.mimetype,
    });

    try {
        const response = await axios.post(
            "http://localhost:10000/detect",
            formData,
            {
                headers: formData.getHeaders(),
            }
        );

        // \u2705 Log the content-type here (inside try block)
        const contentType = response.headers["content-type"];
        console.log("File content type from detect API:", contentType);

        res.json({
            filename: response.data.filename,
            message: response.data.message,
        });

    } catch (error) {
        console.error("Detection failed:", error.message);
        res.status(500).json({ error: "Detection failed" });
    }
});

// Start server
const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
    console.log(`\uD83D\uDE80 Server running on http://localhost:${PORT}/`);
});
