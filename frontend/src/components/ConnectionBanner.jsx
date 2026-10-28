import React, { useState } from 'react';
import { Terminal, Copy, Check, RefreshCw, Sparkles, X } from 'lucide-react';

export default function ConnectionBanner({ onRetry, isChecking, onRunDemo }) {
  const [copied, setCopied] = useState(false);
  const [dismissed, setDismissed] = useState(false);
  const command = 'source ylenv/bin/activate && uvicorn src.api.main:app --port 8000 --reload';

  const copyCommand = () => {
    navigator.clipboard.writeText(command);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (dismissed) return null;

  return (
    <div className="connection-bar" role="alert" aria-live="polite">
      <div className="connection-bar-inner">
        <div className="connection-info">
          <span className="live-status-pill offline">
            <span className="status-dot"></span>
            <span>API Port 8000 Hors-ligne</span>
          </span>
          <span className="connection-msg">
            Pour connecter l’agent LangGraph réel, lancez le serveur FastAPI :
          </span>
          <div className="code-pill">
            <Terminal size={12} aria-hidden="true" />
            <code>uvicorn src.api.main:app --port 8000</code>
            <button
              type="button"
              className="copy-mini-btn"
              onClick={copyCommand}
              title="Copier la commande complète"
            >
              {copied ? <Check size={11} /> : <Copy size={11} />}
              <span>{copied ? 'Copié' : 'Copier'}</span>
            </button>
          </div>
        </div>

        <div className="connection-actions">
          <button
            type="button"
            className="action-btn-retry"
            onClick={onRetry}
            disabled={isChecking}
          >
            <RefreshCw size={12} className={isChecking ? 'spin' : ''} />
            <span>{isChecking ? 'Connexion...' : 'Vérifier'}</span>
          </button>

          {onRunDemo && (
            <button
              type="button"
              className="action-btn-demo"
              onClick={onRunDemo}
              title="Tester immédiatement l'interface avec des données réalistes"
            >
              <Sparkles size={12} />
              <span>Aperçu Démo</span>
            </button>
          )}

          <button
            type="button"
            className="close-bar-btn"
            onClick={() => setDismissed(true)}
            aria-label="Masquer la notification"
            title="Masquer"
          >
            <X size={14} />
          </button>
        </div>
      </div>
    </div>
  );
}
