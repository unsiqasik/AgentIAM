import React, { useState, useCallback, useEffect } from 'react';
import './YamlPolicyEditor.css';
import Editor from '@monaco-editor/react';

interface YamlPolicyEditorProps {
  agentId?: number;
  apiBase?: string;
  onChange?: (value: string) => void;
  onSave?: (value: string) => void;
  readOnly?: boolean;
  height?: string;
}

const DEFAULT_POLICY = `# Agent IAM Policy
# Define permissions for the agent

permissions:
  # Resource-level permissions
  github:
    read: true
    write: false
    delete: false
  
  # Wildcard resource permission
  # *: true  # Grants access to all resources
  
  # Fine-grained permissions
  database:
    query: true
    insert: false
    update: false
    delete: false
`;

const SAMPLE_POLICIES = [
  {
    name: 'Read-Only GitHub Access',
    yaml: `permissions:
  github:
    read: true
    write: false
    delete: false
`
  },
  {
    name: 'Full Database Access',
    yaml: `permissions:
  database:
    query: true
    insert: true
    update: true
    delete: true
`
  },
  {
    name: 'Admin Access',
    yaml: `permissions:
  "*": true
`
  },
  {
    name: 'Custom Policy',
    yaml: `permissions:
  api:
    read: true
    write: true
  storage:
    read: true
    upload: false
    delete: false
`
  }
];

export const YamlPolicyEditor: React.FC<YamlPolicyEditorProps> = ({
  agentId,
  apiBase = '/api/v1',
  onChange,
  onSave,
  readOnly = false,
  height = '400px'
}) => {
  const [value, setValue] = useState(DEFAULT_POLICY);
  const [showSamples, setShowSamples] = useState(false);
  const [loading, setLoading] = useState(!!agentId);
  const [error, setError] = useState<string | null>(null);
  const [policyId, setPolicyId] = useState<number | null>(null);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    if (!agentId) return;

    const fetchPolicy = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await fetch(`${apiBase}/policies/agent/${agentId}`);
        if (response.ok) {
          const data = await response.json();
          setValue(data.policy_yaml);
          setPolicyId(data.id);
        } else if (response.status === 404) {
          setValue(DEFAULT_POLICY);
          setPolicyId(null);
        } else {
          throw new Error('Failed to fetch policy');
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Error loading policy');
      } finally {
        setLoading(false);
      }
    };

    fetchPolicy();
  }, [agentId, apiBase]);

  const getValidationResult = useCallback((yaml: string) => {
    try {
      if (!yaml.trim()) {
        return { isValid: false, errorMessage: 'Policy cannot be empty' };
      }
      if (!yaml.includes('permissions:')) {
        return { isValid: false, errorMessage: 'Policy must contain "permissions" key' };
      }

      const lines = yaml.split('\n');
      let hasPermissions = false;
      let indentLevel = 0;

      for (const line of lines) {
        const trimmed = line.trim();
        if (!trimmed || trimmed.startsWith('#')) continue;

        if (trimmed === 'permissions:') {
          hasPermissions = true;
          indentLevel = 0;
          continue;
        }

        if (hasPermissions) {
          const currentIndent = line.search(/\S/);
          if (currentIndent > indentLevel) {
            indentLevel = currentIndent;
          }
        }
      }

      if (!hasPermissions) {
        return { isValid: false, errorMessage: 'Policy must contain "permissions" section' };
      }

      return { isValid: true, errorMessage: null };
    } catch (error) {
      return { 
        isValid: false, 
        errorMessage: `Invalid YAML: ${error instanceof Error ? error.message : 'Unknown error'}` 
      };
    }
  }, []);

  const { isValid, errorMessage } = getValidationResult(value);

  const handleEditorChange = useCallback((newValue: string | undefined) => {
    if (newValue !== undefined) {
      setValue(newValue);
      onChange?.(newValue);
    }
  }, [onChange]);

  const handleSave = useCallback(async () => {
    if (!isValid) return;

    if (!agentId) {
      onSave?.(value);
      alert('Policy "saved" locally (standalone mode)');
      return;
    }

    setIsSaving(true);
    try {
      let response;
      if (policyId) {
        response = await fetch(`${apiBase}/policies/${policyId}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ policy_yaml: value }),
        });
      } else {
        response = await fetch(`${apiBase}/policies/`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            agent_id: agentId,
            policy_yaml: value,
          }),
        });
      }

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to save policy');
      }

      const savedData = await response.json();
      setPolicyId(savedData.id);
      onSave?.(value);
      alert('Policy saved successfully!');
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Error saving policy');
    } finally {
      setIsSaving(false);
    }
  }, [isValid, policyId, apiBase, agentId, value, onSave]);

  const handleSampleSelect = useCallback((sample: typeof SAMPLE_POLICIES[0]) => {
    setValue(sample.yaml);
    onChange?.(sample.yaml);
    setShowSamples(false);
  }, [onChange]);

  if (loading) return <div className="editor-loading">Loading policy...</div>;

  return (
    <div className="yaml-policy-editor">
      <div className="editor-header">
        <div className="editor-title">
          <h3>Policy Editor {agentId ? `for Agent #${agentId}` : '(Standalone)'}</h3>
          <span className={`validation-status ${isValid ? 'valid' : 'invalid'}`}>
            {isValid ? '✓ Valid' : '✗ Invalid'}
          </span>
        </div>
        
        <div className="editor-actions">
          <button
            className="sample-button"
            onClick={() => setShowSamples(!showSamples)}
          >
            Sample Policies
          </button>
          
          {!readOnly && (
            <button
              className="save-button"
              onClick={handleSave}
              disabled={!isValid || isSaving}
            >
              {isSaving ? 'Saving...' : 'Save Policy'}
            </button>
          )}
        </div>
      </div>

      {error && (
        <div className="error-message">
          Error: {error}
        </div>
      )}

      {errorMessage && (
        <div className="error-message">
          {errorMessage}
        </div>
      )}

      {showSamples && (
        <div className="samples-dropdown">
          <h4>Sample Policies</h4>
          {SAMPLE_POLICIES.map((sample, index) => (
            <button
              key={index}
              className="sample-item"
              onClick={() => handleSampleSelect(sample)}
            >
              {sample.name}
            </button>
          ))}
        </div>
      )}

      <div className="editor-container">
        <Editor
          height={height}
          defaultLanguage="yaml"
          value={value}
          onChange={handleEditorChange}
          options={{
            readOnly,
            minimap: { enabled: false },
            fontSize: 14,
            lineNumbers: 'on',
            roundedSelection: false,
            scrollBeyondLastLine: false,
            automaticLayout: true,
            tabSize: 2,
            insertSpaces: true,
            wordWrap: 'on',
            formatOnPaste: true,
            formatOnType: true,
            suggest: {
              showKeywords: true,
              showSnippets: true
            }
          }}
          theme="vs-dark"
        />
      </div>

      <div className="editor-help">
        <p>
          <strong>YAML Policy Format:</strong> Define permissions using the <code>permissions</code> key.
          Resources can be granted specific actions (read, write, delete) or full access (<code>true</code>).
          Use <code>"*": true</code> for wildcard access to all resources.
        </p>
      </div>
    </div>
  );
};

export default YamlPolicyEditor;
