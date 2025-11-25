import { useState, useRef, useEffect } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import rehypeHighlight from 'rehype-highlight'
import 'highlight.js/styles/github-dark.css'
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
    let botMessageIndex; // Declare botMessageIndex here

    setMessages(prev => {
      botMessageIndex = prev.length + 1; // Calculate index for the bot's response
      return [...prev, userMessage];
    });
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

      if (!response.ok) {
        const data = await response.json()
        // Handle errors
        let errorMessage = "Something went wrong. Please try again."

        if (response.status === 429) {
          errorMessage = "⏳ Whoa, slow down! You've hit the rate limit. Please wait a minute before asking another question."
        } else if (response.status === 500) {
          errorMessage = "🔧 Server error: " + (data.detail || data.error || "Internal server error")
        } else if (response.status === 400) {
          errorMessage = "❌ Invalid request: " + (data.detail || data.error || "Bad request")
        } else if (data.detail) {
          errorMessage = "Error: " + data.detail
        } else if (data.error) {
          errorMessage = "Error: " + data.error
        }

        setMessages(prev => {
          const newMessages = [...prev]
          newMessages[botMessageIndex] = { text: errorMessage, sender: "bot", streaming: false }
          return newMessages
        })
        setLoading(false)
        return
      }

      // Handle streaming response
      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ""
      let currentText = ""
      let sources = []

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() // Keep incomplete line in buffer

        for (const line of lines) {
          if (!line.trim()) continue

          try {
            const chunk = JSON.parse(line)

            if (chunk.type === "sources") {
              sources = chunk.data
            } else if (chunk.type === "token") {
              currentText += chunk.data
              // Update message in real-time
              setMessages(prev => {
                const newMessages = [...prev]
                // Create message if it doesn't exist yet
                if (!newMessages[botMessageIndex]) {
                  newMessages[botMessageIndex] = {
                    text: currentText,
                    sender: "bot",
                    sources: sources,
                    streaming: true
                  }
                } else {
                  newMessages[botMessageIndex] = {
                    text: currentText,
                    sender: "bot",
                    sources: sources,
                    streaming: true
                  }
                }
                return newMessages
              })
            } else if (chunk.type === "done") {
              // Mark streaming as complete
              setMessages(prev => {
                const newMessages = [...prev]
                newMessages[botMessageIndex] = {
                  ...newMessages[botMessageIndex],
                  streaming: false
                }
                return newMessages
              })
            } else if (chunk.type === "error") {
              setMessages(prev => {
                const newMessages = [...prev]
                newMessages[botMessageIndex] = {
                  text: "Error: " + chunk.data,
                  sender: "bot",
                  streaming: false
                }
                return newMessages
              })
            }
          } catch (e) {
            console.error("Error parsing chunk:", e, line)
          }
        }
      }

    } catch (error) {
      console.error("Fetch error:", error)
      setMessages(prev => {
        const newMessages = [...prev]
        newMessages[botMessageIndex] = {
          text: "❌ Could not connect to server. Please check your connection and try again.",
          sender: "bot",
          streaming: false
        }
        return newMessages
      })
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
            <div className={`message-content ${msg.streaming ? 'streaming' : ''}`}>
              {msg.sender === 'bot' ? (
                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  rehypePlugins={[rehypeHighlight]}
                  components={{
                    code({ node, inline, className, children, ...props }) {
                      return inline ? (
                        <code className={className} {...props}>
                          {children}
                        </code>
                      ) : (
                        <code className={className} {...props}>
                          {children}
                        </code>
                      )
                    }
                  }}
                >
                  {msg.text || 'Thinking...'}
                </ReactMarkdown>
              ) : (
                msg.text
              )}
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
