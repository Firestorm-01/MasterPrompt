import { useState, useEffect } from 'react'
import './Splash.css'
function Splash({ onContinue }) {
  const [text, setText] = useState('')
  const [showContinue, setShowContinue] = useState(false)
  const fullText = `> AGENTIC AI ASSISTANT v1.0.0\n> Initializing neural pathways...\n> Loading 50 tool integrations...\n> Establishing LangGraph ReAct loop...\n> Memory systems online...\n> Ready for autonomous operation.`
  useEffect(() => {
    let i = 0
    const timer = setInterval(() => {
      if (i < fullText.length) { setText(fullText.slice(0, i + 1)); i++ }
      else { clearInterval(timer); setTimeout(() => setShowContinue(true), 500) }
    }, 20)
    return () => clearInterval(timer)
  }, [])
  return (
    <div className="splash">
      <div className="splash-content">
        <div className="logo"><span className="logo-bracket">[</span><span className="logo-text">AGENT</span><span className="logo-bracket">]</span></div>
        <pre className="terminal-output">{text}<span className="cursor"></span></pre>
        {showContinue && <button className="btn btn-primary fade-in" onClick={onContinue}>Initialize System →</button>}
        <div className="splash-footer"><span>Zero drag-and-drop. Zero YAML. Pure autonomous AI.</span></div>
      </div>
      <div className="grid-bg"></div>
    </div>
  )
}
export default Splash
