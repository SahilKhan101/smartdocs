---
title: SmartDocs RAG Assistant
emoji: 📚
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
---

# SmartDocs - Technical Documentation Q&A

Ask questions about the OmegaCore library using natural language!

## 🚀 Features

- 🤖 **Powered by Google Gemini** - State-of-the-art language model
- 🔍 **Semantic Search** - ChromaDB vector database for intelligent retrieval
- 📚 **RAG Pipeline** - Retrieval-Augmented Generation for accurate answers
- 💬 **Chat Interface** - User-friendly React frontend
- 📖 **Source Citations** - See which documents were used for answers

## 💡 How to Use

1. Type your question in the chat box
2. Select your preferred model (Gemini or Local)
3. Get answers with source citations!

## 🎯 Example Questions

Try asking:
- "What is OmegaCore?"
- "How do I install OmegaCore on Linux?"
- "What is error code 501?"
- "Does it work with Docker?"
- "What is Neural Compression?"

## 🛠️ Tech Stack

- **Backend:** FastAPI + LangChain
- **Frontend:** React + Vite
- **Vector DB:** ChromaDB
- **Embeddings:** sentence-transformers/all-MiniLM-L6-v2
- **LLM:** Google Gemini 2.5 Flash / Ollama (gemma:2b)

## 📦 Architecture

```
User Question → React UI → FastAPI → ChromaDB (Vector Search)
                                ↓
                         LangChain RAG Pipeline
                                ↓
                    Google Gemini / Ollama (LLM)
                                ↓
                     Answer + Sources → User
```

## 🔗 Links

- **GitHub:** [SahilKhan101/smartdocs](https://github.com/SahilKhan101/smartdocs)
- **Documentation:** [Development Guide](https://github.com/SahilKhan101/smartdocs/blob/main/DEVELOPMENT_GUIDE.md)

---

Built with ❤️ using RAG technology
