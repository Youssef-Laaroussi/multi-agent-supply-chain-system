import React, { useRef, useEffect, useState } from 'react';
import { Copy, Check, RotateCcw, Activity, Terminal } from 'lucide-react';

export default function LiveStreamLogs({
  logs = [],
  onClearLogs,
  isSimulating
}) {
  const [autoScroll, setAutoScroll] = useState(true);
  const [copied, setCopied] = useState(false);
  const logsEndRef = useRef(null);

  useEffect(() => {
    if (autoScroll) {
      logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs, autoScroll]);

  const copyAllLogs = () => {
    if (logs.length === 0) return;
    const text = logs
      .map((l) => `[${l.timestamp}] ${l.node || l.sender}: ${l.content}`)
      .join('\n');
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const getNodeBadgeStyle = (node, role) => {
    const n = (node || '').toLowerCase();
    if (role === 'guardrail-veto' || n.includes('veto')) return 'chip-danger';
    if (n.includes('orchestrator')) return 'chip-orchestrator';
    if (n.includes('guardrail') || n.includes('compliance')) return 'chip-guardrail';
    if (n.includes('demand')) return 'chip-demand';
    if (n.includes('inventory')) return 'chip-inventory';
    if (n.includes('risk')) return 'chip-risk';
    if (n.includes('procurement')) return 'chip-procurement';
    if (n.includes('logistics')) return 'chip-logistics';
    if (role === 'user') return 'chip-user';
    return 'chip-system';
  };

  return (
    <section className="terminal-card" aria-label="Journal d'exécution en direct">
      <div className="terminal-card-header">
        <div className="header-identity">
          <div className="terminal-dot-cluster">
            <span className="window-dot red"></span>
            <span className="window-dot yellow"></span>
            <span className="window-dot green"></span>
          </div>
          <div className="terminal-title-wrap">
            <h2 className="terminal-title">Journal des Délibérations en Direct</h2>
            <span className="log-counter-tag">{logs.length} messages</span>
          </div>
        </div>

        <div className="terminal-controls">
          <label className="scroll-checkbox" title="Défilement automatique">
            <input
              type="checkbox"
              checked={autoScroll}
              onChange={(e) => setAutoScroll(e.target.checked)}
            />
            <span>Auto-scroll</span>
          </label>

          <button
            type="button"
            className="control-icon-btn"
            onClick={copyAllLogs}
            disabled={logs.length === 0}
            title="Copier le journal"
          >
            {copied ? <Check size={12} /> : <Copy size={12} />}
            <span>{copied ? 'Copié' : 'Copier'}</span>
          </button>

          <button
            type="button"
            className="control-icon-btn"
            onClick={onClearLogs}
            disabled={isSimulating || logs.length === 0}
            title="Effacer le journal"
          >
            <RotateCcw size={12} />
            <span>Effacer</span>
          </button>
        </div>
      </div>

      <div
        className="terminal-stream-body"
        role="log"
        aria-live="polite"
        aria-atomic="false"
      >
        {logs.length === 0 ? (
          <div className="empty-stream-state">
            <Terminal size={24} className="text-muted" />
            <p>Journal d’exécution en attente de délibération.</p>
            <span>Lancez une mission pour visualiser les échanges et raisonnements des agents.</span>
          </div>
        ) : (
          logs.map((entry) => {
            const badgeStyle = getNodeBadgeStyle(entry.node, entry.role);

            return (
              <div key={entry.id} className={`stream-log-entry ${entry.role || ''}`}>
                <div className="entry-header">
                  <span className={`agent-chip ${badgeStyle}`}>
                    <span className="chip-dot"></span>
                    <span>{entry.node || entry.sender}</span>
                  </span>
                  <time className="entry-timestamp">{entry.timestamp}</time>
                </div>
                <div className="entry-text-bubble">
                  {entry.content}
                </div>
              </div>
            );
          })
        )}
        <div ref={logsEndRef} />
      </div>
    </section>
  );
}
