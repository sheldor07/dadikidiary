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

app.post("/upload", upload.single("image"), (req, res) => {
  // denugging

  console.log(req.file);
  console.log(req.body);
  if (!req.body.title) {
    return res.status(400).send("Please provide a title");
  }
  if (!req.file) {
    return res.status(400).send("Please upload a file");
  }

  // converting image to ocr
  // uploading ocr to blog

  res.status(200).json({
    message: "Blog post created successfully",
    fileSize: req.file.size,
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
