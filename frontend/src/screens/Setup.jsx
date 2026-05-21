import { useState, useMemo } from 'react'
import './Setup.css'
const CATEGORIES = ['Communication','Productivity','Files & Storage','Web & Research','Finance','AI & Dev','Lifestyle']
function Setup({ tools, configuredKeys, setConfiguredKeys, onLaunch, onBack }) {
  const [activeCategory, setActiveCategory] = useState('Communication')
  const [searchQuery, setSearchQuery] = useState('')
  const toolsByCategory = useMemo(() => {
    const grouped = {}
    CATEGORIES.forEach(cat => { grouped[cat] = tools.filter(t => t.category === cat) })
    return grouped
  }, [tools])
  const filteredTools = useMemo(() => {
    if (!searchQuery) return toolsByCategory[activeCategory] || []
    return tools.filter(t => t.name.toLowerCase().includes(searchQuery.toLowerCase()) || t.description.toLowerCase().includes(searchQuery.toLowerCase()))
  }, [tools, toolsByCategory, activeCategory, searchQuery])
  const configuredCount = tools.filter(t => t.is_available).length
  const handleKeyChange = (key, value) => setConfiguredKeys(prev => ({ ...prev, [key]: value }))
  return (
    <div className="setup">
      <header className="setup-header">
        <button className="btn-back" onClick={onBack}>← Back</button>
        <h1>Tool Configuration</h1>
        <div className="tool-counter"><span className="counter-value">{configuredCount}</span><span className="counter-label">/ {tools.length} tools ready</span></div>
      </header>
      <div className="setup-body">
        <aside className="category-nav">
          {CATEGORIES.map(cat => (
            <button key={cat} className={`category-btn ${activeCategory === cat ? 'active' : ''}`} onClick={() => { setActiveCategory(cat); setSearchQuery('') }}>
              <span className="category-name">{cat}</span>
              <span className="category-count">{toolsByCategory[cat]?.filter(t => t.is_available).length || 0}</span>
            </button>
          ))}
        </aside>
        <main className="tools-panel">
          <div className="search-bar"><input type="text" className="input" placeholder="Search tools..." value={searchQuery} onChange={e => setSearchQuery(e.target.value)} /></div>
          <div className="tools-list">{filteredTools.map(tool => <ToolCard key={tool.name} tool={tool} configuredKeys={configuredKeys} onKeyChange={handleKeyChange} />)}</div>
        </main>
      </div>
      <footer className="setup-footer"><button className="btn btn-primary" onClick={onLaunch}>Launch Agent →</button></footer>
    </div>
  )
}
function ToolCard({ tool, configuredKeys, onKeyChange }) {
  const [expanded, setExpanded] = useState(false)
  const isConfigured = tool.is_available || tool.required_env_vars.every(v => configuredKeys[v])
  return (
    <div className={`tool-card ${isConfigured ? 'configured' : ''}`}>
      <div className="tool-header" onClick={() => setExpanded(!expanded)}>
        <div className="tool-info">
          <span className={`tool-status ${isConfigured ? 'active' : ''}`}>{isConfigured ? '●' : '○'}</span>
          <h3 className="tool-name">{tool.name}</h3>
          {tool.is_free && <span className="badge badge-free">FREE</span>}
        </div>
        <span className="expand-icon">{expanded ? '−' : '+'}</span>
      </div>
      {expanded && (
        <div className="tool-body fade-in">
          <p className="tool-description">{tool.description}</p>
          {tool.required_env_vars.length > 0 ? (
            <div className="env-vars">
              <h4>Required Environment Variables:</h4>
              {tool.required_env_vars.map(envVar => (
                <div key={envVar} className="env-var-row">
                  <label className="env-var-label">{envVar}</label>
                  <input type="password" className="input env-var-input" placeholder={tool.is_available ? '••••••••' : 'Paste API key...'} value={configuredKeys[envVar] || ''} onChange={e => onKeyChange(envVar, e.target.value)} disabled={tool.is_available} />
                </div>
              ))}
            </div>
          ) : <p className="no-config">No configuration required</p>}
        </div>
      )}
    </div>
  )
}
export default Setup
