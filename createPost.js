const sgMail = require("@sendgrid/mail");
const config = require("./config");
sgMail.setApiKey(config.email.sendgridApiKey);
async function postToWordPress(title, content) {
  const msg = {
    to: config.wordpress.postByEmailAddress,
    from: config.email.fromAddress,
    subject: title,
    text: content,
  };
  try {
    await sgMail.send(msg);
    console.log("Email sent to WordPress");
    return "Email sent to WordPress";
  } catch (error) {
    console.error("Error sending email to WordPress:", error.message);
    throw error;
  }
}
module.exports = { postToWordPress };
