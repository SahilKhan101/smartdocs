# 🚀 SmartDocs Features & Implementation Guide

This document details the core features implemented in the SmartDocs application, explaining the theory behind them and their technical implementation.

---

## 1. 💡 Question Suggestions

**Theory:**
To reduce friction for new users (the "cold start" problem), we provide clickable example questions. This helps users understand what kind of queries the system can handle and encourages immediate interaction without needing to think of a prompt.

**Implementation:**

*   **Frontend-Only Logic:** The feature is implemented entirely in `App.jsx` to keep it lightweight.
*   **Conditional Rendering:** Suggestions are only displayed when the chat history is empty (specifically, when `messages.length === 1`, containing only the bot's greeting).
*   **Interactive Cards:** Each suggestion is a clickable card that:
    1.  Populates the input field with the question text.
    2.  Automatically hides itself once the user sends a message (as `messages.length` increases).

**Code Snippet (`frontend/src/App.jsx`):**
```javascript
// Only show when just the greeting exists
{messages.length === 1 && (
  <div className="suggestions-container">
    {suggestionQuestions.map((q) => (
      <div onClick={() => setInput(q)} ... >
        {q}
      </div>
    ))}
  </div>
)}
```

---

## 2. 🧠 Conversation History (Context Awareness)

**Theory:**
A natural conversation involves "context" — referring to previous statements. For example, if a user asks "What is OmegaCore?" and then "How do I install **it**?", the AI must know that "**it**" refers to OmegaCore. Without history, the AI treats every request as an isolated event.

**Implementation:**

We implemented a **sliding window context** approach:

1.  **Frontend (`App.jsx`):**
    *   Maintains the full chat state in `messages`.
    *   Before sending a request, it extracts the last **5 exchanges** (10 messages).
    *   Formats them into a structured list of `{ role: "user" | "assistant", content: "..." }` objects.
    *   Sends this list in the `history` field of the API request.

2.  **Backend (`main.py`):**
    *   **Pydantic Model:** Updated `ChatRequest` to accept `history: list[Message]`.
    *   **Prompt Engineering:** The system prompt was modified to include a `{history}` placeholder before the current question.
    *   **Formatting:** A helper function `format_history` converts the structured list into a string format the LLM understands (e.g., "User: ... \n Assistant: ...").
    *   **Token Safety:** A hard limit of 10 messages is enforced in the backend to prevent exceeding the LLM's context window.

**Flow:**
```
User Input -> Frontend (Slice last 10 msgs) -> API -> Backend (Format History) -> LLM Prompt -> Response
```

---

## 3. 🎨 Branding & UI Polish

**Theory:**
A professional appearance builds trust. Consistent branding (favicons, titles) and modern UI patterns (glassmorphism) make the application feel like a polished product rather than a prototype.

**Implementation:**

*   **Dynamic Favicon:**
    *   Instead of a static file, we used an **SVG Data URI** in `index.html`.
    *   This allows us to create a high-quality, scalable icon (the "SD" logo with gradient) directly in code without needing external image assets.
    *   **Code:** `<link rel="icon" href="data:image/svg+xml,<svg...>...</svg>">`

*   **Glassmorphism:**
    *   Used `backdrop-filter: blur(20px)` and semi-transparent backgrounds (`rgba(255, 255, 255, 0.05)`) to create a frosted glass effect.
    *   This is applied to the chat window and suggestion cards for a modern, depth-rich look.

*   **Animations:**
    *   **CSS Keyframes:** Added `fadeInUp` and `slideDown` animations.
    *   Elements like suggestion cards "float" up when they appear, making the UI feel alive.

---

## 4. ⚡ Streaming Responses

**Theory:**
Large Language Models (LLMs) take time to generate full answers. Instead of making the user wait for the entire response (which could take 5-10 seconds), we "stream" the response token by token as it's being generated. This reduces the **Time to First Byte (TTFB)** perception, making the app feel instant.

**Implementation:**

*   **Backend:**
    *   Uses `StreamingResponse` from FastAPI.
    *   The LangChain `chain.astream()` method yields chunks of text.
    *   We wrap these chunks in **NDJSON** (Newline Delimited JSON) format: `{"type": "token", "data": "..."}`.

*   **Frontend:**
    *   Uses the `fetch` API's `response.body.getReader()`.
    *   A `while` loop reads the stream chunk by chunk.
    *   **TextDecoder** converts bytes to text, and the UI is updated in real-time as new tokens arrive.

---

## 5. 🛡️ Rate Limiting

**Theory:**
To prevent abuse and manage costs (LLM API quotas), we limit how many requests a user can make in a given timeframe.

**Implementation:**

*   **Library:** `slowapi` (based on limits).
*   **Strategy:** **Fixed Window** (e.g., "10 requests per minute").
*   **Identification:** Uses the client's IP address (`get_remote_address`) to track usage.
*   **Feedback:** If a user exceeds the limit, the backend returns a `429 Too Many Requests` status, which the frontend handles by showing a friendly "Whoa, slow down!" message.
