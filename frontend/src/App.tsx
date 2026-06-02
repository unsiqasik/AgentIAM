import { useState } from 'react'
import { ThemeToggle } from './components/ThemeToggle'
import { YamlPolicyEditor } from './components/YamlPolicyEditor'
import { AgentList } from './components/AgentList'
import { AuditCharts } from './components/AuditCharts'
import { AuditLogList } from './components/AuditLogList'
import './App.css'
import './components/AgentList.css'
import './components/AuditCharts.css'
import './components/AuditLogList.css'

function App() {
  const [activeTab, setActiveTab] = useState<'agents' | 'policy' | 'audit'>('agents')
  const [selectedAgentId, setSelectedAgentId] = useState<number | null>(null)

  const handleSelectAgent = (id: number) => {
    setSelectedAgentId(id)
    setActiveTab('policy')
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
            Policy Editor {selectedAgentId ? `(#${selectedAgentId})` : ''}
          </button>
          <button
            className={`tab-button ${activeTab === 'audit' ? 'active' : ''}`}
            onClick={() => setActiveTab('audit')}
          >
            Audit & Analytics
          </button>
        </nav>

        <div className="tab-content">
          {activeTab === 'agents' && (
            <section className="agents-section">
              <AgentList onSelectAgent={handleSelectAgent} />
            </section>
          )}

          {activeTab === 'audit' && (
            <section className="audit-section">
              <div className="audit-grid">
                <AuditCharts apiBaseUrl="/api/v1" />
                <AuditLogList apiBase="/api/v1" />
              </div>
            </section>
          )}

          {activeTab === 'policy' && (
            <section className="policy-section">
              {!selectedAgentId ? (
                <div className="no-agent-selected">
                  <p>Please select an agent from the list to edit its policy.</p>
                  <button onClick={() => setActiveTab('agents')}>Go to Agent List</button>
                </div>
              ) : (
                <>
                  <div className="policy-header">
                    <h2>Policy Editor for Agent #{selectedAgentId}</h2>
                    <p>Define what this agent can and cannot do.</p>
                  </div>
                  
                  <YamlPolicyEditor
                    agentId={selectedAgentId}
                    height="500px"
                  />
                </>
              )}
            </section>
          )}
        </div>
      </main>

      <style>{`
        .app-main {
          max-width: 1400px;
          margin: 0 auto;
          padding: 24px;
        }

        .tab-navigation {
          display: flex;
          gap: 8px;
          margin-bottom: 24px;
          border-bottom: 1px solid var(--border);
          padding-bottom: 16px;
        }

        .tab-button {
          padding: 12px 24px;
          background: var(--code-bg);
          border: 1px solid var(--border);
          border-radius: 6px;
          color: var(--text);
          cursor: pointer;
          font-size: 16px;
          transition: all 0.2s;
        }

        .tab-button:hover {
          background: var(--border);
        }

        .tab-button.active {
          background: #2563eb;
          color: white;
          border-color: #2563eb;
        }

        .tab-content {
          min-height: 60vh;
        }

        .audit-grid {
          display: flex;
          flex-direction: column;
          gap: 32px;
        }

        .no-agent-selected {
          text-align: center;
          padding: 60px;
          background: var(--code-bg);
          border-radius: 12px;
          border: 1px dashed var(--border);
        }

        .no-agent-selected button {
          margin-top: 16px;
          padding: 10px 20px;
          background: #2563eb;
          color: white;
          border: none;
          border-radius: 6px;
          cursor: pointer;
        }

        .agents-section, .policy-section, .audit-section {
          animation: fadeIn 0.3s ease-in;
        }

        .policy-header {
          margin-bottom: 24px;
        }

        .policy-header h2 {
          margin: 0 0 8px 0;
          font-size: 24px;
          color: var(--text-h);
        }

        .policy-header p {
          margin: 0;
          color: var(--text);
          font-size: 16px;
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
