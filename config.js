require("dotenv").config();

module.exports = {
  port: process.env.PORT || 3000,
  azure: {
    documentsEndpoint: process.env.AZURE_DOCUMENT_ENDPOINT,
    documentsKey: process.env.AZURE_DOCUMENT_KEY,
    modelId: process.env.MODEL_ID || "prebuilt-read",
  },
  uploadLimits: {
    fileSize: 5 * 1024 * 1024,
  },
  email: {
    sendgridApiKey: process.env.SENDGRID_API_KEY,
    fromAddress: process.env.EMAIL_FROM_ADDRESS,
  },
  wordpress: {
    postByEmailAddress: process.env.WP_POST_BY_EMAIL_ADDRESS,
  },
};
