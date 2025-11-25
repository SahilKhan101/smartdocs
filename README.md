# SmartDocs RAG System

[![CI/CD](https://github.com/YOUR_USERNAME/smartdocs/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/smartdocs/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A production-ready **Retrieval-Augmented Generation (RAG)** system that allows users to ask questions about technical documentation using natural language. Built with FastAPI, React, and LangChain.

![SmartDocs Demo](https://via.placeholder.com/800x400?text=SmartDocs+Demo)

## ✨ Features

- 🤖 **Dual LLM Support**: Switch between Google Gemini (cloud) and Ollama (local)
- 📚 **Document Ingestion**: Automatically processes Markdown documentation
- 🔍 **Semantic Search**: Uses ChromaDB for fast vector similarity search
- 💬 **Modern UI**: Clean, responsive React interface
- 📊 **Source Citations**: Shows which documents were used to generate answers
- 🔒 **Privacy-First**: Option to run completely offline with local models

## 🏗️ Architecture

```
User Question → React Frontend → FastAPI Backend → ChromaDB (Vector Search)
                                        ↓
                                   LangChain RAG Pipeline
                                        ↓
                            Google Gemini / Ollama (LLM)
                                        ↓
                                Answer + Sources → User
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- Google AI API Key (free from [Google AI Studio](https://aistudio.google.com/))
- (Optional) Ollama for local mode

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/smartdocs.git
   cd smartdocs
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure Environment**
   ```bash
   echo "GOOGLE_API_KEY=your_key_here" > .env
   ```

4. **Ingest Documentation**
   ```bash
   python ingest.py
   ```

5. **Start Backend**
   ```bash
   uvicorn main:app --reload --port 8000
   ```

6. **Frontend Setup** (in a new terminal)
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

7. **Access the App**
   Open [http://localhost:5173](http://localhost:5173)

## 📖 Documentation

- **[Development Guide](DEVELOPMENT_GUIDE.md)**: Complete step-by-step tutorial
- **[Features & Implementation](FEATURES.md)**: Deep dive into how features work
- **[Walkthrough](walkthrough.md)**: Testing and verification guide
- **[API Documentation](http://localhost:8000/docs)**: Auto-generated FastAPI docs (when server is running)

## 🛠️ Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **LangChain**: LLM application framework
- **ChromaDB**: Vector database for embeddings
- **Sentence Transformers**: Text embedding model
- **Google Gemini API**: Cloud LLM
- **Ollama**: Local LLM runtime

### Frontend
- **React**: UI library
- **Vite**: Build tool and dev server

## 📝 Example Questions

Try asking SmartDocs:
- "What is OmegaCore?"
- "How do I install OmegaCore on Linux?"
- "What is error code 501?"
- "Does it work with Docker?"

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [LangChain](https://python.langchain.com/)
- Powered by [Google Gemini](https://ai.google.dev/)
- Vector search by [ChromaDB](https://www.trychroma.com/)
- Embeddings from [Sentence Transformers](https://www.sbert.net/)

## 📧 Contact

Your Name - [@yourtwitter](https://twitter.com/yourtwitter)

Project Link: [https://github.com/YOUR_USERNAME/smartdocs](https://github.com/YOUR_USERNAME/smartdocs)
