import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.chat_models import ChatOllama
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from fastapi.middleware.cors import CORSMiddleware

# Load environment variables
load_dotenv()

app = FastAPI(title="SmartDocs RAG API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",      # Local development
        "http://localhost:7860",      # HF local testing
        "https://*.hf.space",         # All Hugging Face Spaces
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
DB_PATH = "./chroma_db"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Initialize Vector DB (Global)
embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
vector_db = Chroma(persist_directory=DB_PATH, embedding_function=embeddings)
retriever = vector_db.as_retriever(search_kwargs={"k": 3})

# Request Model
class ChatRequest(BaseModel):
    question: str
    model_type: str = "gemini" # "gemini" or "local"

# Prompt Template
template = """Answer the question based ONLY on the following context:
{context}

Question: {question}
"""
prompt = ChatPromptTemplate.from_template(template)

def get_llm(model_type: str):
    if model_type == "gemini":
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="GOOGLE_API_KEY not found in .env")
        return ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=api_key)
    elif model_type == "local":
        # Assumes Ollama is running with 'gemma:2b'
        return ChatOllama(model="gemma:2b")
    else:
        raise HTTPException(status_code=400, detail="Invalid model_type. Use 'gemini' or 'local'.")

def format_docs(docs):
    return "\n\n".join([d.page_content for d in docs])

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        llm = get_llm(request.model_type)
        
        # RAG Chain
        chain = (
            {"context": retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )
        
        response = chain.invoke(request.question)
        
        # Get sources
        source_docs = retriever.get_relevant_documents(request.question)
        sources = list(set([doc.metadata.get("source", "unknown") for doc in source_docs]))
        
        return {
            "answer": response,
            "sources": sources
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    from datetime import datetime
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "vector_db": "connected" if os.path.exists(DB_PATH) else "missing",
        "environment": "production" if os.getenv("HF_SPACE") else "development"
    }
