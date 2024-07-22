const axios = require("axios");
async function analyzeDocument(endpoint, subscriptionKey, modelId, fileBuffer) {
  const apiVersion = "2024-02-29-preview";
  const url = `${endpoint}/documentintelligence/documentModels/${modelId}:analyze?_overload=analyzeDocument&api-version=${apiVersion}`;

  const headers = {
    "Content-Type": "application/json",
    "Ocp-Apim-Subscription-Key": subscriptionKey,
  };
  const base64Source = fileBuffer.toString("base64");
  const data = {
    base64Source: base64Source,
  };

  try {
    const response = await axios.post(url, data, { headers });

    if (response.status === 202) {
      const operationLocation = response.headers["operation-location"];
      console.log(
        "Document analysis initiated. Operation URL:",
        operationLocation
      );
      return operationLocation;
    } else {
      throw new Error(`Unexpected response status: ${response.status}`);
    }
  } catch (error) {
    console.error("Error analyzing document:", error.message);
    throw error;
  }
}

async function getAnalysisResult(operationLocation, subscriptionKey) {
  const headers = {
    "Ocp-Apim-Subscription-Key": subscriptionKey,
  };

  while (true) {
    try {
      const response = await axios.get(operationLocation, { headers });

      if (response.data.status === "succeeded") {
        return response.data;
      } else if (response.data.status === "failed") {
        throw new Error("Document analysis failed");
      }

      // Wait before checking again
      await new Promise((resolve) => setTimeout(resolve, 2000));
    } catch (error) {
      console.error("Error getting analysis result:", error.message);
      throw error;
    }
  }
}
function extractContent(jsonResult) {
  if (
    !jsonResult ||
    !jsonResult.analyzeResult ||
    !jsonResult.analyzeResult.paragraphs
  ) {
    throw new Error("Invalid JSON structure");
  }
  const paragraphs = jsonResult.analyzeResult.paragraphs;
  let extractedContent = "";
  paragraphs.forEach((paragraph) => {
    if (paragraph.content) {
      extractedContent += paragraph.content + "\n";
    }
  });
  return extractedContent.trim();
}
module.exports = { analyzeDocument, getAnalysisResult, extractContent };
