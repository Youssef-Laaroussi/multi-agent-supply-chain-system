import React from 'react';
import { Shield, RefreshCw, Radio, RotateCcw, Activity } from 'lucide-react';

export default function Header({
  backendHealth,
  isCheckingHealth,
  onRefreshHealth,
  onResetSession,
  isSimulating
}) {
  const isHealthy = backendHealth?.ok;

  return (
    <header className="top-navbar" role="banner">
      <div className="navbar-container">
        {/* Brand Group */}
        <div className="brand-group">
          <div className="brand-icon-shield">
            <Shield size={20} strokeWidth={2.4} />
          </div>
          <div className="brand-copy">
            <div className="brand-title-line">
              <span className="brand-name">AURA SOVEREIGN</span>
              <span className="brand-pill">Tour de Contrôle</span>
            </div>
            <p className="brand-tagline">
              Système Multi-Agents d’Approvisionnement Stratégique & Réserve d’État
            </p>
          </div>
        </div>

        {/* Right Status Group */}
        <div className="navbar-right">
          {/* Engine indicator */}
          <div className="engine-chip">
            <Radio size={13} className="text-primary-600" />
            <span>LangGraph StateGraph</span>
          </div>

          {/* Health indicator */}
          <div
            className={`api-status-pill ${isHealthy ? 'status-connected' : 'status-disconnected'}`}
            title={isHealthy ? 'API Backend opérationnelle sur port 8000' : 'Backend non détecté'}
          >
            <span className="pulse-indicator-dot"></span>
            <span className="status-text">
              {isHealthy ? 'API Connectée (8000)' : 'API Hors-ligne'}
            </span>
            <button
              type="button"
              className="refresh-indicator-btn"
              onClick={onRefreshHealth}
              disabled={isCheckingHealth}
              title="Tester la connexion"
            >
              <RefreshCw size={12} className={isCheckingHealth ? 'spin' : ''} />
            </button>
          </div>

          {/* Reset session button */}
          <button
            type="button"
            className="navbar-reset-btn"
            onClick={onResetSession}
            disabled={isSimulating}
            title="Réinitialiser l'état de la session"
          >
            <RotateCcw size={13} />
            <span>Réinitialiser</span>
          </button>
        </div>
      </div>
    </header>
  );
}
