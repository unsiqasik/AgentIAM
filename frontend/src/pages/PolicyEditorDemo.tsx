import React, { useState } from 'react';
import { YamlPolicyEditor } from '../components/YamlPolicyEditor';

export const PolicyEditorDemo: React.FC = () => {
  const [savedPolicy, setSavedPolicy] = useState<string | null>(null);
  const [lastSaved, setLastSaved] = useState<Date | null>(null);

  const handleSave = (policy: string) => {
    setSavedPolicy(policy);
    setLastSaved(new Date());
    console.log('Policy saved:', policy);
  };

  const handleChange = (policy: string) => {
    console.log('Policy changed:', policy);
  };

  return (
    <div className="policy-editor-demo">
      <header className="demo-header">
        <h1>Agent IAM - Policy Editor</h1>
        <p>Create and edit YAML policies for your agents</p>
      </header>

      <main className="demo-content">
        <section className="editor-section">
          <YamlPolicyEditor
            onChange={handleChange}
            onSave={handleSave}
            height="500px"
          />
        </section>

        {savedPolicy && (
          <section className="saved-section">
            <h2>Last Saved Policy</h2>
            <div className="saved-info">
              <p><strong>Saved at:</strong> {lastSaved?.toLocaleString()}</p>
              <pre className="saved-policy">{savedPolicy}</pre>
            </div>
          </section>
        )}

        <section className="info-section">
          <h2>Policy Format Guide</h2>
          <div className="info-grid">
            <div className="info-card">
              <h3>Basic Structure</h3>
              <pre>{`permissions:
  resource_name:
    action: true/false`}</pre>
            </div>
            
            <div className="info-card">
              <h3>Wildcard Access</h3>
              <pre>{`permissions:
  "*": true  # Full access`}</pre>
            </div>
            
            <div className="info-card">
              <h3>Multiple Actions</h3>
              <pre>{`permissions:
  github:
    read: true
    write: true
    delete: false`}</pre>
            </div>
            
            <div className="info-card">
              <h3>Fine-grained Control</h3>
              <pre>{`permissions:
  database:
    query: true
    insert: false
    update: false
    delete: false`}</pre>
            </div>
          </div>
        </section>
      </main>

      <style>{`
        .policy-editor-demo {
          min-height: 100vh;
          background: #1a1a1a;
          color: #fff;
          padding: 24px;
        }

        .demo-header {
          text-align: center;
          margin-bottom: 32px;
        }

        .demo-header h1 {
          margin: 0 0 8px 0;
          font-size: 32px;
          color: #fff;
        }

        .demo-header p {
          margin: 0;
          color: #888;
          font-size: 16px;
        }

        .demo-content {
          max-width: 1200px;
          margin: 0 auto;
        }

        .editor-section {
          margin-bottom: 32px;
        }

        .saved-section {
          margin-bottom: 32px;
          padding: 24px;
          background: #252526;
          border-radius: 8px;
          border: 1px solid #333;
        }

        .saved-section h2 {
          margin: 0 0 16px 0;
          font-size: 20px;
          color: #fff;
        }

        .saved-info p {
          margin: 0 0 12px 0;
          color: #888;
        }

        .saved-policy {
          background: #1e1e1e;
          padding: 16px;
          border-radius: 4px;
          overflow-x: auto;
          font-family: monospace;
          font-size: 14px;
          line-height: 1.5;
        }

        .info-section {
          margin-bottom: 32px;
        }

        .info-section h2 {
          margin: 0 0 24px 0;
          font-size: 24px;
          color: #fff;
        }

        .info-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
          gap: 16px;
        }

        .info-card {
          background: #252526;
          padding: 20px;
          border-radius: 8px;
          border: 1px solid #333;
        }

        .info-card h3 {
          margin: 0 0 12px 0;
          font-size: 16px;
          color: #fff;
        }

        .info-card pre {
          background: #1e1e1e;
          padding: 12px;
          border-radius: 4px;
          font-size: 13px;
          line-height: 1.4;
          overflow-x: auto;
        }
      `}</style>
    </div>
  );
};

export default PolicyEditorDemo;
