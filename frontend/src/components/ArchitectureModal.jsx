import React from 'react';
import { X, Layers, GitBranch, Shield, Cpu, BookOpen, CheckCircle2 } from 'lucide-react';

export default function ArchitectureModal({ isOpen, onClose }) {
  if (!isOpen) return null;

  return (
    <div className="modal-backdrop" onClick={onClose} role="dialog" aria-modal="true" aria-label="Architecture Multi-Agents">
      <div className="modal-container" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div className="modal-title-cluster">
            <Layers size={20} className="text-cyan" />
            <div>
              <h3 className="modal-title">Architecture Multi-Agents LangGraph v1.0</h3>
              <p className="modal-sub">
                Spécifications techniques, protocoles de souveraineté et délibération d&apos;agents
              </p>
            </div>
          </div>
          <button type="button" className="modal-close-btn" onClick={onClose} aria-label="Fermer">
            <X size={18} />
          </button>
        </div>

        <div className="modal-body">
          <div className="arch-highlights-grid">
            <div className="arch-card">
              <GitBranch size={18} className="text-cyan" />
              <h4>StateGraph &amp; MessagesState</h4>
              <p>
                Les 7 agents partagent une structure typée <code>SupplyChainState</code> avec réducteur d&apos;historique immuable <code>Annotated[list[BaseMessage], add_messages]</code>.
              </p>
            </div>

            <div className="arch-card">
              <Cpu size={18} className="text-emerald" />
              <h4>Prebuilt ToolNode &amp; @tool</h4>
              <p>
                5 outils déterministes validés par Pydantic (prévisions statistiques, calcul du ROP, scan d&apos;alertes maritimes, cotations fournisseurs et fret).
              </p>
            </div>

            <div className="arch-card">
              <Shield size={18} className="text-rose" />
              <h4>Sovereign Guardrails &amp; Veto</h4>
              <p>
                Le nœud de gouvernance utilise <code>Command[Literal[&quot;logistics_agent&quot;, &quot;orchestrator_agent&quot;]]</code> pour exercer un Veto statutaire contre toute entité sous embargo.
              </p>
            </div>

            <div className="arch-card">
              <BookOpen size={18} className="text-violet" />
              <h4>MemorySaver &amp; Checkpoints</h4>
              <p>
                Chaque crise s&apos;exécute sous un <code>thread_id</code> persistant. Toutes les étapes, logs d&apos;audit et décisions sont auditables et rejouables sans perte.
              </p>
            </div>
          </div>

          <div className="arch-sequence-section">
            <h4 className="section-title">Séquence Opérationnelle des 7 Nœuds</h4>
            <div className="sequence-step-list">
              <div className="seq-step">
                <span className="step-num">01</span>
                <div>
                  <strong>demand_agent</strong>
                  <p>Évalue la consommation historique et applique le facteur de choc (+80%).</p>
                </div>
              </div>
              <div className="seq-step">
                <span className="step-num">02</span>
                <div>
                  <strong>inventory_agent</strong>
                  <p>Calcule le ROP (d·L + SS) et audite le plancher légal de 500 unités.</p>
                </div>
              </div>
              <div className="seq-step">
                <span className="step-num">03</span>
                <div>
                  <strong>risk_agent</strong>
                  <p>Scanne le radar géopolitique et maritime (Suez, tempêtes) et calcule les retards induits.</p>
                </div>
              </div>
              <div className="seq-step">
                <span className="step-num">04</span>
                <div>
                  <strong>procurement_agent</strong>
                  <p>Interroge le catalogue fournisseurs et classe les offres de réapprovisionnement.</p>
                </div>
              </div>
              <div className="seq-step highlight-guardrail">
                <span className="step-num">05</span>
                <div>
                  <strong>compliance_guardrail</strong>
                  <p>Vérifie la nationalité, bloque EMBARGO_LAND par Veto et route dynamiquement via Command API.</p>
                </div>
              </div>
              <div className="seq-step">
                <span className="step-num">06</span>
                <div>
                  <strong>logistics_agent</strong>
                  <p>Alloue un vecteur d&apos;acheminement certifié Secret-Défense (Pont Aérien Souverain 24h).</p>
                </div>
              </div>
              <div className="seq-step">
                <span className="step-num">07</span>
                <div>
                  <strong>orchestrator_agent</strong>
                  <p>Arbitre le compromis Coût / Délai / Souveraineté et signe le Décret Exécutif officiel.</p>
                </div>
              </div>
            </div>
          </div>

          <div className="arch-footer-banner">
            <CheckCircle2 size={16} className="text-emerald" />
            <span>
              Conforme aux exigences <strong>LangGraph v1.0</strong>, <strong>LangChain Core</strong> et <strong>Code de la commande publique (Art. L2122-1)</strong>.
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}

