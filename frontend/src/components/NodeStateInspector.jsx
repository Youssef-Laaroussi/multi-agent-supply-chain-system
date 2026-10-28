import React, { useState } from 'react';
import { WORKFLOW_NODES } from './PipelineGraph';
import { Copy, Check, Code, Eye, Info } from 'lucide-react';

export default function NodeStateInspector({
  selectedNodeId,
  graphState = {},
  onClose
}) {
  const [copied, setCopied] = useState(false);
  const [viewMode, setViewMode] = useState('summary'); // 'summary' or 'raw'

  const nodeInfo = WORKFLOW_NODES.find((n) => n.id === selectedNodeId);
  if (!nodeInfo) return null;

  const nodeData = graphState[nodeInfo.stateKey];
  const hasData = Boolean(nodeData && Object.keys(nodeData).length > 0);

  const copyJson = () => {
    if (!hasData) return;
    navigator.clipboard.writeText(JSON.stringify(nodeData, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <aside className="inspector-panel" aria-label={`Inspecteur d'état: ${nodeInfo.title}`}>
      <div className="inspector-header">
        <div className="inspector-title-group">
          <span className="step-tag">Nœud {nodeInfo.step}/7</span>
          <h3 className="inspector-title">{nodeInfo.title}</h3>
          <span className="state-key-tag">`state.{nodeInfo.stateKey}`</span>
        </div>

        <div className="inspector-actions">
          {hasData && (
            <div className="view-switch" role="group" aria-label="Mode d'affichage">
              <button
                type="button"
                className={`switch-btn ${viewMode === 'summary' ? 'active' : ''}`}
                onClick={() => setViewMode('summary')}
              >
                <Eye size={12} aria-hidden="true" />
                <span>Synthèse</span>
              </button>
              <button
                type="button"
                className={`switch-btn ${viewMode === 'raw' ? 'active' : ''}`}
                onClick={() => setViewMode('raw')}
              >
                <Code size={12} aria-hidden="true" />
                <span>JSON</span>
              </button>
            </div>
          )}

          {hasData && (
            <button
              type="button"
              className="icon-text-btn"
              onClick={copyJson}
              title="Copier le payload JSON"
            >
              {copied ? <Check size={12} /> : <Copy size={12} />}
              <span>{copied ? 'Copié' : 'Copier'}</span>
            </button>
          )}

          {onClose && (
            <button
              type="button"
              className="close-btn"
              onClick={onClose}
              title="Fermer l'inspecteur"
              aria-label="Fermer"
            >
              ×
            </button>
          )}
        </div>
      </div>

      <div className="inspector-content">
        {!hasData ? (
          <div className="inspector-empty">
            <Info size={18} aria-hidden="true" />
            <p>Ce nœud n'a pas encore produit de données dans l'état partagé.</p>
            <span>Lancez une simulation pour déclencher son exécution par LangGraph.</span>
          </div>
        ) : viewMode === 'raw' ? (
          <pre className="json-block">
            <code>{JSON.stringify(nodeData, null, 2)}</code>
          </pre>
        ) : (
          <div className="summary-view">
            <div className="summary-grid">
              {Object.entries(nodeData).map(([key, val]) => {
                if (typeof val === 'object' && val !== null) {
                  return (
                    <div key={key} className="summary-row full-width">
                      <span className="summary-key">{key}</span>
                      <pre className="summary-json-sub">
                        {JSON.stringify(val, null, 2)}
                      </pre>
                    </div>
                  );
                }

                let displayVal = String(val);
                if (typeof val === 'boolean') {
                  displayVal = val ? 'OUI' : 'NON';
                }

                return (
                  <div key={key} className="summary-row">
                    <span className="summary-key">{key}</span>
                    <strong className="summary-val">{displayVal}</strong>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </aside>
  );
}
