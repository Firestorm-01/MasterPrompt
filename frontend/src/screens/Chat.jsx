import { useState, useRef, useEffect } from 'react'
import './Chat.css'
function Chat({ tools, sessionId, onSettings }) {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [currentSteps, setCurrentSteps] = useState([])
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)
  useEffect(() => { messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages, currentSteps])
  useEffect(() => { inputRef.current?.focus() }, [])
  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return
    const userMessage = input.trim()
    setInput('')
    setMessages(prev => [...prev, { role: 'user', content: userMessage }])
    setIsLoading(true)
    setCurrentSteps([])
    try {
      const response = await fetch('http://localhost:8000/chat', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ message: userMessage, session_id: sessionId }) })
      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let assistantMessage = ''
      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        for (const line of decoder.decode(value).split('\n')) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6))
              if (data.type === 'thought') setCurrentSteps(prev => [...prev, { type: 'thought', content: data.content }])
              else if (data.type === 'tool_call') setCurrentSteps(prev => [...prev, { type: 'tool', content: `Calling ${data.tool}...` }])
              else if (data.type === 'tool_result') setCurrentSteps(prev => [...prev, { type: 'result', content: data.content }])
              else if (data.type === 'final_answer') assistantMessage = data.content
              else if (data.type === 'error') assistantMessage = `Error: ${data.content}`
            } catch (e) {}
          }
        }
      }
      if (assistantMessage) setMessages(prev => [...prev, { role: 'assistant', content: assistantMessage }])
    } catch (error) { setMessages(prev => [...prev, { role: 'assistant', content: `Connection error: ${error.message}` }]) }
    setIsLoading(false)
    setCurrentSteps([])
    inputRef.current?.focus()
  }
  return (
    <div className="chat">
      <aside className="chat-sidebar">
        <div className="sidebar-header"><h2>Active Tools</h2><span className="tool-count">{tools.length}</span></div>
        <div className="tool-list">{tools.map(tool => (<div key={tool.name} className="sidebar-tool"><span className="tool-dot">●</span><span className="tool-label">{tool.name}</span></div>))}</div>
        <button className="settings-btn" onClick={onSettings}>⚙ Settings</button>
      </aside>
      <main className="chat-main">
        <div className="messages">
          {messages.length === 0 && (
            <div className="welcome-message">
              <h2>Agentic AI Ready</h2>
              <p>I can chain multiple tools to complete complex tasks autonomously.</p>
              <div className="example-prompts">
                <span>Try:</span>
                <button onClick={() => setInput("What's the weather in Tokyo and convert 100 USD to JPY")}>Weather + Currency</button>
                <button onClick={() => setInput("Search for the latest AI papers on arXiv and summarize the top 3")}>Research + Summary</button>
                <button onClick={() => setInput("Get AAPL stock price and Bitcoin price")}>Stocks + Crypto</button>
              </div>
            </div>
          )}
          {messages.map((msg, i) => (
            <div key={i} className={`message ${msg.role}`}>
              <div className="message-label">{msg.role === 'user' ? '> you' : '> agent'}</div>
              <div className="message-content">{msg.content}</div>
            </div>
          ))}
          {currentSteps.length > 0 && (
            <div className="thinking-steps">
              {currentSteps.map((step, i) => (
                <div key={i} className={`step ${step.type}`}>
                  {step.type === 'tool' && <span className="step-icon">⚡</span>}
                  {step.type === 'thought' && <span className="step-icon">💭</span>}
                  {step.type === 'result' && <span className="step-icon">✓</span>}
                  <span className="step-content">{step.content}</span>
                </div>
              ))}
            </div>
          )}
          {isLoading && currentSteps.length === 0 && (<div className="loading"><span className="loading-dot">●</span><span className="loading-dot">●</span><span className="loading-dot">●</span></div>)}
          <div ref={messagesEndRef} />
        </div>
        <form className="input-area" onSubmit={handleSubmit}>
          <span className="input-prompt">&gt;</span>
          <input ref={inputRef} type="text" className="chat-input" placeholder="Ask me anything..." value={input} onChange={e => setInput(e.target.value)} disabled={isLoading} />
          <button type="submit" className="send-btn" disabled={isLoading || !input.trim()}>Execute</button>
        </form>
      </main>
    </div>
  )
}
export default Chat
