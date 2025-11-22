// chatbot.js

const toggle = document.getElementById('chatbot-toggle');
const chatbot = document.getElementById('chatbot');
const header = document.getElementById('chatbot-header');
const messages = document.getElementById('chatbot-messages');
const input = document.getElementById('user-input');

toggle.onclick = () => {
  toggle.style.display = 'none';
  chatbot.style.display = 'flex';
};

header.onclick = () => {
  chatbot.style.display = 'none';
  toggle.style.display = 'flex';
};

function appendMessage(sender, text) {
  const msg = document.createElement('div');
  msg.innerHTML = `<strong>${sender}:</strong> ${text}`;
  messages.appendChild(msg);
  messages.scrollTop = messages.scrollHeight;
}

function sendMessage() {
  const userText = input.value.trim();
  if (!userText) return;
  appendMessage('You', userText);
  input.value = '';

  fetch('/ask', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message: userText })
  })
  .then(res => res.json())
  .then(data => {
    appendMessage('Gyman', data.reply);
  });
}

input.addEventListener("keydown", e => {
  if (e.key === "Enter") sendMessage();
});
