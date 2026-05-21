const API_BASE = 'http://localhost:8000'
export async function fetchTools() {
  const response = await fetch(`${API_BASE}/tools`)
  if (!response.ok) throw new Error('Failed to fetch tools')
  return response.json()
}
export async function updateConfig(envVars) {
  const response = await fetch(`${API_BASE}/config`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ env_vars: envVars })
  })
  if (!response.ok) throw new Error('Failed to update config')
  return response.json()
}
export async function* streamChat(message, sessionId) {
  const response = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, session_id: sessionId })
  })
  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    const chunk = decoder.decode(value)
    for (const line of chunk.split('\n')) {
      if (line.startsWith('data: ')) {
        try { yield JSON.parse(line.slice(6)) } catch (e) {}
      }
    }
  }
}
export async function getHistory(sessionId) {
  const response = await fetch(`${API_BASE}/history/${sessionId}`)
  if (!response.ok) throw new Error('Failed to fetch history')
  return response.json()
}
export async function clearHistory(sessionId) {
  const response = await fetch(`${API_BASE}/history/${sessionId}`, { method: 'DELETE' })
  if (!response.ok) throw new Error('Failed to clear history')
  return response.json()
}
