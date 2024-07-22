require("dotenv").config();
const endpoint = process.env.AZURE_DOCUMENT_ENDPOINT;
const subscriptionKey = process.env.AZURE_DOCUMENT_KEY;
const modelId = "prebuilt-read";
module.exports = { endpoint, subscriptionKey, modelId };
