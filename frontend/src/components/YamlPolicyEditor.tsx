import React, { useState, useCallback } from 'react';
import './YamlPolicyEditor.css';
import Editor from '@monaco-editor/react';

interface YamlPolicyEditorProps {
  initialValue?: string;
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
  initialValue = DEFAULT_POLICY,
  onChange,
  onSave,
  readOnly = false,
  height = '400px'
}) => {
  const [value, setValue] = useState(initialValue);
  const [showSamples, setShowSamples] = useState(false);

  const getValidationResult = useCallback((yaml: string) => {
    try {
      // Basic YAML validation
      if (!yaml.trim()) {
        return { isValid: false, errorMessage: 'Policy cannot be empty' };
      }

      // Check for required permissions key
      if (!yaml.includes('permissions:')) {
        return { isValid: false, errorMessage: 'Policy must contain "permissions" key' };
      }

      // Check for valid YAML structure
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

  const handleSave = useCallback(() => {
    if (isValid && onSave) {
      onSave(value);
    }
  }, [isValid, onSave, value]);

  const handleSampleSelect = useCallback((sample: typeof SAMPLE_POLICIES[0]) => {
    setValue(sample.yaml);
    onChange?.(sample.yaml);
    setShowSamples(false);
  }, [onChange]);

  return (
    <div className="yaml-policy-editor">
      {/* Header */}
      <div className="editor-header">
        <div className="editor-title">
          <h3>Policy Editor</h3>
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
          
          {!readOnly && onSave && (
            <button
              className="save-button"
              onClick={handleSave}
              disabled={!isValid}
            >
              Save Policy
            </button>
          )}
        </div>
      </div>

      {/* Error Message */}
      {errorMessage && (
        <div className="error-message">
          {errorMessage}
        </div>
      )}

      {/* Sample Policies Dropdown */}
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

      {/* Monaco Editor */}
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

      {/* Help Text */}
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
