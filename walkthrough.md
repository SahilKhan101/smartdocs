# SmartDocs RAG System - Walkthrough

We have successfully built and deployed the **SmartDocs** RAG system. This system allows you to chat with the "OmegaCore" technical documentation using either Google Gemini or a local Ollama model.

## 🚀 Quick Start

1.  **Frontend**: Open [http://localhost:5173](http://localhost:5173) in your browser.
2.  **Backend**: Running on [http://localhost:8000](http://localhost:8000).

## 🧪 Features Verified

*   **Data Ingestion**:
    *   Generated "messy" documentation (Introduction, Installation, API Reference, Troubleshooting).
    *   Ingested 349 chunks into ChromaDB using `sentence-transformers/all-MiniLM-L6-v2`.
*   **Backend API**:
    *   `/chat` endpoint accepts questions and model selection (`gemini` or `local`).
    *   Retrieves relevant context from ChromaDB.
    *   Generates answers using the selected LLM.
*   **Frontend UI**:
    *   Modern dark-mode interface.
    *   Real-time streaming (simulated via loading state).
    *   Source citations displayed below answers.
    *   Model switcher (Cloud vs. Local).

## 📝 How to Test

1.  **Ask about Installation**:
    *   *User*: "How do I install OmegaCore on Linux?"
    *   *Expected*: Should mention `pip install omegacore` and warn about Alpine Linux issues.
2.  **Ask about Errors**:
    *   *User*: "What is error code 501?"
    *   *Expected*: Should explain "ERR_QUANTUM_DECOHERENCE" and suggest checking network connection.
3.  **Test Local Mode**:
    *   Switch the dropdown to **Ollama (Local)**.
    *   Ask: "What is Neural Compression?"
    *   *Note*: Ensure `ollama run gemma:2b` is running in a separate terminal if not already started.

## 🔧 Troubleshooting

*   **"Google API Key not found"**: Ensure `backend/.env` has your key.
*   **"Connection Refused"**: Ensure the backend server is running (`uvicorn main:app`).
*   **"Ollama connection failed"**: Ensure Ollama is installed and running.
