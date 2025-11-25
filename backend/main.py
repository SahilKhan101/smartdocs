import os
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.chat_models import ChatOllama
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from fastapi.middleware.cors import CORSMiddleware

# Configure logging
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Load environment variables
load_dotenv()

# Session-based rate limiting (works better with proxies/load balancers)
def get_rate_limit_key(request: Request):
    """
    Generate a unique key for rate limiting based on IP + User-Agent.
    This works better than IP-only on platforms with load balancers (like HF).
    """
    import hashlib
    import logging
    
    logger = logging.getLogger("rate_limiter")
    
    # Get client IP (handle proxies)
    forwarded_for = request.headers.get("x-forwarded-for")
    x_real_ip = request.headers.get("x-real-ip")
    client_host = request.client.host
    
    # Debug logging
    logger.info(f"Headers - X-Forwarded-For: {forwarded_for}, X-Real-IP: {x_real_ip}, Client: {client_host}")
    
    if forwarded_for:
        ip = forwarded_for.split(",")[0].strip()
    elif x_real_ip:
        ip = x_real_ip
    else:
        ip = client_host
    
    # Combine with user agent for better uniqueness
    user_agent = request.headers.get("user-agent", "unknown")
    session_key = f"{ip}:{user_agent}"
    
    # Hash it for privacy
    key_hash = hashlib.md5(session_key.encode()).hexdigest()
    
    # Debug logging
    logger.info(f"Rate limit key: {key_hash[:16]}... (IP: {ip[:15]}..., UA: {user_agent[:30]}...)")
    
    return key_hash

# Initialize rate limiter
limiter = Limiter(key_func=get_rate_limit_key)
app = FastAPI(title="SmartDocs RAG API")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

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

# Initialize Vector DB (Global) - Force CPU to avoid CUDA errors
embeddings = HuggingFaceEmbeddings(
    model_name=EMBEDDING_MODEL,
    model_kwargs={'device': 'cpu'}  # Force CPU usage
)
vector_db = Chroma(persist_directory=DB_PATH, embedding_function=embeddings)
retriever = vector_db.as_retriever(search_kwargs={"k": 3})

# Request Model
class Message(BaseModel):
    role: str  # "user" or "assistant"
    content: str

class ChatRequest(BaseModel):
    question: str
    model_type: str = "gemini"  # "gemini" or "local"
    history: list[Message] = []  # Optional conversation history

# Prompt Template with conversation history support
template = """Answer the question based ONLY on the following context:
{context}

{history}Question: {question}
"""
prompt = ChatPromptTemplate.from_template(template)

def format_history(history: list[Message]) -> str:
    """Format conversation history for the prompt."""
    if not history:
        return ""
    
    # Limit to last 5 exchanges (10 messages) to prevent token overflow
    recent_history = history[-10:] if len(history) > 10 else history
    
    formatted = "Previous conversation:\n"
    for msg in recent_history:
        role = "User" if msg.role == "user" else "Assistant"
        formatted += f"{role}: {msg.content}\n"
    formatted += "\n"
    return formatted

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
@limiter.limit("3/minute")  # Testing: 3 requests per minute
async def chat(request: Request, chat_request: ChatRequest):
    from fastapi.responses import StreamingResponse
    import json
    
    user_key = get_rate_limit_key(request)
    logger = logging.getLogger("rate_limiter")
    logger.info(f"Request from: {user_key[:16]}...")
    
    try:
        llm = get_llm(chat_request.model_type)
        
        # Format conversation history
        history_text = format_history(chat_request.history)
        
        # Create streaming chain with history support
        chain = (
            {"context": retriever | format_docs, "question": RunnablePassthrough(), "history": lambda _: history_text}
            | prompt
            | llm
            | StrOutputParser()
        )
        
        # Stream generator function
        async def generate():
            try:
                # First, get and send the sources
                docs = retriever.get_relevant_documents(chat_request.question)
                sources = list(set([doc.metadata.get("source", "unknown") for doc in docs]))
                
                # Send sources as first chunk
                yield json.dumps({"type": "sources", "data": sources}) + "\n"
                
                # Stream the answer token by token
                async for chunk in chain.astream(chat_request.question):
                    yield json.dumps({"type": "token", "data": chunk}) + "\n"
                
                # Send completion signal
                yield json.dumps({"type": "done"}) + "\n"
                
            except Exception as e:
                logger.error(f"Streaming error: {str(e)}")
                yield json.dumps({"type": "error", "data": str(e)}) + "\n"
        
        return StreamingResponse(
            generate(),
            media_type="application/x-ndjson"
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
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
