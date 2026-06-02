import { useState } from 'react'
import { ThemeToggle } from './components/ThemeToggle'
import { YamlPolicyEditor } from './components/YamlPolicyEditor'
import { AgentList } from './components/AgentList'
import { AuditCharts } from './components/AuditCharts'
import './App.css'
import './components/AgentList.css'
import './components/AuditCharts.css'

function App() {
  const [activeTab, setActiveTab] = useState<'agents' | 'policy' | 'audit'>('agents')
  const [savedPolicy, setSavedPolicy] = useState<string | null>(null)

  const handleSavePolicy = (policy: string) => {
    setSavedPolicy(policy)
    console.log('Policy saved:', policy)
  }

  return (
    <>
      <header className="app-header">
        <div className="header-left">
          <span className="logo-text">AgentIAM</span>
        </div>
        <div className="header-right">
          <ThemeToggle />
        </div>
      </header>

      <main className="app-main">
        <nav className="tab-navigation">
          <button
            className={`tab-button ${activeTab === 'agents' ? 'active' : ''}`}
            onClick={() => setActiveTab('agents')}
          >
            Agents
          </button>
          <button
            className={`tab-button ${activeTab === 'policy' ? 'active' : ''}`}
            onClick={() => setActiveTab('policy')}
          >
            Policy Editor
          </button>
          <button
            className={`tab-button ${activeTab === 'audit' ? 'active' : ''}`}
            onClick={() => setActiveTab('audit')}
          >
            Audit Dashboard
          </button>
        </nav>

        <div className="tab-content">
          {activeTab === 'agents' && (
            <section className="agents-section">
              <AgentList />
            </section>
          )}

          {activeTab === 'audit' && (
            <section className="audit-section">
              <AuditCharts apiBaseUrl="/api/v1" />
            </section>
          )}

          {activeTab === 'policy' && (
            <section className="policy-section">
              <div className="policy-header">
                <h2>Policy Editor</h2>
                <p>Create and edit YAML policies for your agents</p>
              </div>
              
              <YamlPolicyEditor
                onSave={handleSavePolicy}
                height="500px"
              />

              {savedPolicy && (
                <div className="saved-policy-preview">
                  <h3>Last Saved Policy</h3>
                  <pre>{savedPolicy}</pre>
                </div>
              )}
            </section>
          )}
        </div>
      </main>

      <style>{`
        .app-main {
          max-width: 1200px;
          margin: 0 auto;
          padding: 24px;
        }

        .tab-navigation {
          display: flex;
          gap: 8px;
          margin-bottom: 24px;
          border-bottom: 1px solid #333;
          padding-bottom: 16px;
        }

        .tab-button {
          padding: 12px 24px;
          background: #333;
          border: none;
          border-radius: 6px;
          color: #fff;
          cursor: pointer;
          font-size: 16px;
          transition: all 0.2s;
        }

        .tab-button:hover {
          background: #444;
        }

        .tab-button.active {
          background: #2563eb;
        }

        .tab-content {
          min-height: 60vh;
        }

        .agents-section, .policy-section {
          animation: fadeIn 0.3s ease-in;
        }

        .policy-header {
          margin-bottom: 24px;
        }

        .policy-header h2 {
          margin: 0 0 8px 0;
          font-size: 24px;
          color: #fff;
        }

        .policy-header p {
          margin: 0;
          color: #888;
          font-size: 16px;
        }

        .saved-policy-preview {
          margin-top: 24px;
          padding: 20px;
          background: #252526;
          border-radius: 8px;
          border: 1px solid #333;
        }

        .saved-policy-preview h3 {
          margin: 0 0 12px 0;
          font-size: 18px;
          color: #fff;
        }

        .saved-policy-preview pre {
          background: #1e1e1e;
          padding: 16px;
          border-radius: 4px;
          font-family: monospace;
          font-size: 14px;
          line-height: 1.5;
          overflow-x: auto;
        }

        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}</style>
    </>
  )
}

export default App
