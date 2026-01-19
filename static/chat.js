document.addEventListener("DOMContentLoaded", () => {
  const chatToggle = document.getElementById("chat-toggle");
  const chatBox = document.getElementById("chat-box");
  const chatClose = document.getElementById("chat-close");
  const sendBtn = document.getElementById("send-btn");
  const input = document.getElementById("user-input");
  const messages = document.getElementById("chat-messages");

  if (!chatToggle || !chatBox || !sendBtn || !input || !messages) {
    // Silently fail if elements are not present (e.g. on login page)
    return;
  }

  let greeted = false;
  let isSending = false;

  // Open chat
  chatToggle.addEventListener("click", () => {
    chatBox.style.display = "flex";

    if (!greeted) {
      addMessage(
        "bot",
        "Assalamu’alaikum. I can help explain features or guide you to pages like attendance or dashboard."
      );
      greeted = true;
    }
  });

  // Close chat
  chatClose?.addEventListener("click", () => {
    chatBox.style.display = "none";
  });

  // Add message to UI
  function addMessage(role, text) {
    const div = document.createElement("div");
    div.className =
      role === "user"
        ? "message-wrapper user-msg"
        : "message-wrapper bot-msg";
    div.textContent = text;
    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
  }

  // Enter to send, Shift+Enter for newline
  input.addEventListener("keydown", e => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });

  sendBtn.addEventListener("click", sendMessage);

  function sendMessage() {
    if (isSending) return;

    const text = input.value.trim();
    if (!text) return;

    addMessage("user", text);
    input.value = "";
    isSending = true;
    sendBtn.disabled = true;

    fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text })
    })
      .then(res => {
        if (!res.ok) throw new Error("Server error");
        return res.json();
      })
      .then(data => {
        if (data?.action === "navigate" && data.redirect) {
          addMessage("bot", "Taking you there...");
          setTimeout(() => {
            window.location.href = data.redirect;
          }, 700);
        } else if (data?.action === "chat" && data.message) {
          addMessage("bot", data.message);
        } else {
          addMessage("bot", "I’m not sure how to help with that.");
        }
      })
      .catch(err => {
        console.error(err);
        addMessage("bot", "Error contacting server.");
      })
      .finally(() => {
        isSending = false;
        sendBtn.disabled = false;
      });
  }
});
