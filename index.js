require("dotenv").config();
const express = require("express");
const multer = require("multer");
const config = require("./config");
const {
  analyzeDocument,
  getAnalysisResult,
  extractContent,
} = require("./performOCR");

const app = express();
const port = process.env.PORT || 3000;

const storage = multer.memoryStorage(); // storage defines how and where multer should store the uploaded files in this case, we are using memory storage*/

const upload = multer({
  storage: storage,
  fileFilter: function (req, file, cb) {
    if (file.mimetype.startsWith("image/")) {
      cb(null, true);
    } else {
      cb(new Error("Not an image! Please uplaod an image."), false);
    }
  },
  limits: {
    fileSize: config.uploadLimits.fileSize,
  },
}); //  upload is a configured multer instance that we'll use as a middleware

app.use(express.json());

app.post("/upload", upload.single("image"), async (req, res) => {
  if (!req.body.title) {
    return res.status(400).send("Please provide a title");
  }
  if (!req.file) {
    return res.status(400).send("Please upload a file");
  }
  const fileBuffer = req.file.buffer;
  let content = "";
  try {
    console.log("Analyzing document...");
    const operationLocation = await analyzeDocument(fileBuffer);
    const result = await getAnalysisResult(operationLocation);
    content = extractContent(result);
  } catch (error) {
    console.error("Error:", error.message);
    return res
      .status(500)
      .send(`An error occurred while processing the image ${error.message}`);
  }
  res.status(200).json({
    message: "Text extracted successfully",
    content: content,
  });
});

app.use((err, req, res, next) => {
  if (err instanceof multer.MulterError) {
    if (err.code === "LIMIT_FILE_SIZE") {
      return res
        .status(400)
        .send("File size is too large. Please upload a file less than 5mb");
    }
    res.status(500).send(err.message);
  }
});

app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
});
