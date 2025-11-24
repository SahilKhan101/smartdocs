import { useState, useRef, useEffect } from 'react'
import './App.css'

function App() {
  const [messages, setMessages] = useState([
    { text: "Hello! I'm SmartDocs. Ask me anything about OmegaCore.", sender: "bot" }
  ])
  const [input, setInput] = useState("")
  const [model, setModel] = useState("gemini")
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(scrollToBottom, [messages])

  // Environment-aware API URL
  const API_URL = window.location.hostname === 'localhost'
    ? 'http://localhost:8000'
    : '';  // Use relative URL in production (nginx proxy)

  const sendMessage = async () => {
    if (!input.trim()) return

    const userMessage = { text: input, sender: "user" }
    setMessages(prev => [...prev, userMessage])
    setInput("")
    setLoading(true)

    try {
      const endpoint = window.location.hostname === 'localhost'
        ? `${API_URL}/chat`  // Local: direct to backend
        : '/api/chat';        // Production: through nginx proxy

      const response = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: userMessage.text, model_type: model })
      })

      const data = await response.json()

      if (response.ok) {
        setMessages(prev => [...prev, {
          text: data.answer,
          sender: "bot",
          sources: data.sources
        }])
      } else {
        // Handle different error types
        let errorMessage = "Something went wrong. Please try again."

        if (response.status === 429) {
          // Rate limit exceeded
          errorMessage = "⏳ Whoa, slow down! You've hit the rate limit. Please wait a minute before asking another question."
        } else if (response.status === 500) {
          // Server error
          errorMessage = "🔧 Server error: " + (data.detail || data.error || "Internal server error")
        } else if (response.status === 400) {
          // Bad request
          errorMessage = "❌ Invalid request: " + (data.detail || data.error || "Bad request")
        } else if (data.detail) {
          errorMessage = "Error: " + data.detail
        } else if (data.error) {
          errorMessage = "Error: " + data.error
        }

        setMessages(prev => [...prev, {
          text: errorMessage,
          sender: "bot"
        }])
      }
    } catch (error) {
      setMessages(prev => [...prev, {
        text: "❌ Could not connect to server. Please check your connection and try again.",
        sender: "bot"
      }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app-container">
      <header className="header">
        <h1>📚 SmartDocs <span className="subtitle">OmegaCore Assistant</span></h1>
        <div className="model-selector">
          <label>Model:</label>
          <select value={model} onChange={(e) => setModel(e.target.value)}>
            <option value="gemini">Google Gemini (Cloud)</option>
            <option value="local">Ollama (Local)</option>
          </select>
        </div>
      </header>

      <div className="chat-window">
        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.sender}`}>
            <div className="message-content">
              {msg.text}
              {msg.sources && msg.sources.length > 0 && (
                <div className="sources">
                  <small>Sources: {msg.sources.join(", ")}</small>
                </div>
              )}
            </div>
          </div>
        ))}
        {loading && <div className="message bot"><div className="message-content typing">Thinking...</div></div>}
        <div ref={messagesEndRef} />
      </div>

      <div className="input-area">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
          placeholder="Ask a question about OmegaCore..."
          disabled={loading}
        />
        <button onClick={sendMessage} disabled={loading}>Send</button>
      </div>
    </div>
  )
}

export default App
