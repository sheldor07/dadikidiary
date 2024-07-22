require("dotenv").config();
const {
  analyzeDocument,
  getAnalysisResult,
  extractContent,
} = require("./performOCR");
const express = require("express");
const multer = require("multer");

const app = express();
const port = process.env.PORT || 3000;

//configuring multer
/* storage defines how and where multer should store the uploaded files
 in this case, we are using memory storage*/

const storage = multer.memoryStorage();
/* upload is a configured multer instance that we'll use as a middleware */
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
    fileSize: 5 * 1024 * 1024, // no larger than 5mb
  },
});

app.use(express.json());

app.post("/upload", upload.single("image"), async (req, res) => {
  //   // denugging

  //   console.log(req.file);
  //   console.log(req.body);
  if (!req.body.title) {
    return res.status(400).send("Please provide a title");
  }
  if (!req.file) {
    return res.status(400).send("Please upload a file");
  }

  const fileBuffer = req.file.buffer;
  let content = "";
  try {
    const endpoint = process.env.AZURE_DOCUMENT_ENDPOINT;
    const subscriptionKey = process.env.AZURE_DOCUMENT_KEY;
    const modelId = "prebuilt-read";
    const operationLocation = await analyzeDocument(
      endpoint,
      subscriptionKey,
      modelId,
      fileBuffer
    );
    const result = await getAnalysisResult(operationLocation, subscriptionKey);
    content = extractContent(result);
  } catch (error) {
    console.error("Error:", error.message);
  }
  // converting image to ocr
  // uploading ocr to blog

  res.status(200).json({
    message: "text extracted successfully",
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
