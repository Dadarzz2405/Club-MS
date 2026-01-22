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
        "Assalamu'alaikum. I can explain about Islamic teachings or guide you through Rohis activities. How can I assist you today?"
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
        console.log("Received data:", data); // Debug log
        
        // Handle the response based on the actual structure from ai.py
        if (data?.reply) {
          const reply = data.reply;
          
          // Check if it's a navigation response
          if (reply.action === "navigate" && reply.redirect) {
            addMessage("bot", "Taking you there...");
            setTimeout(() => {
              window.location.href = reply.redirect;
            }, 700);
          } 
          // Check if it's a chat response
          else if (reply.action === "chat" && reply.message) {
            addMessage("bot", reply.message);
          } 
          // Fallback for unexpected format
          else {
            console.warn("Unexpected reply format:", reply);
            addMessage("bot", "I'm not sure how to help with that.");
          }
        } 
        // Fallback if no reply object
        else {
          console.warn("No reply in response:", data);
          addMessage("bot", "I'm not sure how to help with that.");
        }
      })
      .catch(err => {
        console.error("Chat error:", err);
        addMessage("bot", "Error contacting server.");
      })
      .finally(() => {
        isSending = false;
        sendBtn.disabled = false;
      });
  }
});