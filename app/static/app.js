const messagesEl = document.getElementById("messages");
const formEl = document.getElementById("composer-form");
const composerEl = document.getElementById("composer");
const modelSelectEl = document.getElementById("model-select");
const systemPromptEl = document.getElementById("system-prompt");
const temperatureEl = document.getElementById("temperature");
const maxTokensEl = document.getElementById("max-tokens");
const temperatureValueEl = document.getElementById("temperature-value");
const maxTokensValueEl = document.getElementById("max-tokens-value");
const suggestionsEl = document.getElementById("suggestions");
const backendBadgeEl = document.getElementById("backend-badge");
const statusTextEl = document.getElementById("status-text");
const clearChatEl = document.getElementById("clear-chat");
const sendButtonEl = document.getElementById("send-button");

const state = {
  messages: [
    {
      role: "assistant",
      content: "Hi — I’m Silode. I can help you plan features, summarize notes, and draft polished responses locally on your Mac.",
    },
  ],
  sending: false,
};

function renderMessages() {
  messagesEl.innerHTML = "";

  state.messages.forEach((message) => {
    const wrapper = document.createElement("div");
    wrapper.className = `message ${message.role}`;

    const bubble = document.createElement("div");
    bubble.className = "bubble";
    bubble.textContent = message.content;

    wrapper.appendChild(bubble);
    messagesEl.appendChild(wrapper);
  });

  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function setBusy(isBusy) {
  state.sending = isBusy;
  sendButtonEl.disabled = isBusy;
  sendButtonEl.textContent = isBusy ? "Thinking…" : "Send";
}

async function loadStatus() {
  const response = await fetch("/api/status");
  const status = await response.json();

  backendBadgeEl.textContent = status.backend.toUpperCase();
  statusTextEl.textContent = `Ready for ${status.display_name} desktop mode with ${status.models.length} configured model(s).`;

  modelSelectEl.innerHTML = "";
  status.models.forEach((model) => {
    const option = document.createElement("option");
    option.value = model.name;
    option.textContent = model.name;
    if (model.name === status.default_model) {
      option.selected = true;
    }
    modelSelectEl.appendChild(option);
  });

  suggestionsEl.innerHTML = "";
  status.suggestions.forEach((prompt) => {
    const chip = document.createElement("button");
    chip.type = "button";
    chip.className = "chip";
    chip.textContent = prompt;
    chip.addEventListener("click", () => {
      composerEl.value = prompt;
      composerEl.focus();
    });
    suggestionsEl.appendChild(chip);
  });
}

async function sendMessage() {
  const text = composerEl.value.trim();
  if (!text || state.sending) {
    return;
  }

  state.messages.push({ role: "user", content: text });
  composerEl.value = "";
  renderMessages();
  setBusy(true);

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        model: modelSelectEl.value,
        system_prompt: systemPromptEl.value.trim(),
        max_tokens: Number(maxTokensEl.value),
        temperature: Number(temperatureEl.value),
        messages: state.messages,
      }),
    });

    if (!response.ok) {
      throw new Error("Silode could not answer the request.");
    }

    const payload = await response.json();
    state.messages.push(payload.message);
    renderMessages();
  } catch (error) {
    state.messages.push({
      role: "assistant",
      content: error.message || "Something went wrong while contacting the local runtime.",
    });
    renderMessages();
  } finally {
    setBusy(false);
  }
}

formEl.addEventListener("submit", async (event) => {
  event.preventDefault();
  await sendMessage();
});

composerEl.addEventListener("keydown", async (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    await sendMessage();
  }
});

clearChatEl.addEventListener("click", () => {
  state.messages = [
    {
      role: "assistant",
      content: "Chat cleared. What would you like to build on your Mac next?",
    },
  ];
  renderMessages();
});

temperatureEl.addEventListener("input", () => {
  temperatureValueEl.textContent = temperatureEl.value;
});

maxTokensEl.addEventListener("input", () => {
  maxTokensValueEl.textContent = maxTokensEl.value;
});

renderMessages();
loadStatus().catch(() => {
  backendBadgeEl.textContent = "OFFLINE";
  statusTextEl.textContent = "The local API is not reachable yet. Start the server to continue.";
});
