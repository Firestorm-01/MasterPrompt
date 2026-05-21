import { useState, useEffect } from 'react'
import Splash from './screens/Splash'
import Setup from './screens/Setup'
import Chat from './screens/Chat'
import './App.css'
function App() {
  const [screen, setScreen] = useState('splash')
  const [tools, setTools] = useState([])
  const [configuredKeys, setConfiguredKeys] = useState({})
  const [sessionId] = useState(() => `session_${Date.now()}`)
  useEffect(() => { fetchTools() }, [])
  const fetchTools = async () => {
    try {
      const response = await fetch('http://localhost:8000/tools')
      const data = await response.json()
      setTools(data.tools)
    } catch (error) { console.error('Failed to fetch tools:', error) }
  }
  const handleLaunch = async () => {
    if (Object.keys(configuredKeys).length > 0) {
      await fetch('http://localhost:8000/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ env_vars: configuredKeys })
      })
      await fetchTools()
    }
    setScreen('chat')
  }
  if (screen === 'splash') return <Splash onContinue={() => setScreen('setup')} />
  if (screen === 'setup') return <Setup tools={tools} configuredKeys={configuredKeys} setConfiguredKeys={setConfiguredKeys} onLaunch={handleLaunch} onBack={() => setScreen('splash')} />
  return <Chat tools={tools.filter(t => t.is_available)} sessionId={sessionId} onSettings={() => setScreen('setup')} />
}
export default App
