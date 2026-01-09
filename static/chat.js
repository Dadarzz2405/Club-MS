const chatToggle = document.getElementById("chat-toggle");
const chatBox = document.getElementById("chat-box");
const chatClose = document.getElementById("chat-close");
const sendBtn = document.getElementById("send-btn");
const input = document.getElementById("user-input");
const messages = document.getElementById("chat-messages");

chatToggle.onclick = () => {
  chatBox.style.display = "flex";
};

chatClose.onclick = () => {
  chatBox.style.display = "none";
};

function addMessage(role, text) {
  const div = document.createElement("div");
  div.className = role === "user" ? "message-wrapper user-msg" : "message-wrapper bot-msg";
  div.textContent = text;
  messages.appendChild(div);
  messages.scrollTop = messages.scrollHeight;
}

sendBtn.onclick = sendMessage;
input.addEventListener("keypress", e => {
  if (e.key === "Enter") sendMessage();
});

function sendMessage() {
  const text = input.value.trim();
  if (!text) return;

  addMessage("user", text);
  input.value = "";

  fetch("/chat", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ message: text })
  })
  .then(res => res.json())
  .then(data => addMessage("bot", data.reply))
  .catch(() => addMessage("bot", "Error contacting server"));
}
