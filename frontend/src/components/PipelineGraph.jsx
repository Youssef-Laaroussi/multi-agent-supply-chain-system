import React from 'react';
import {
  TrendingUp,
  Package,
  ShieldAlert,
  ShoppingCart,
  Scale,
  Truck,
  Network,
  CheckCircle2,
  XCircle,
  Loader2,
  ArrowRight
} from 'lucide-react';

export const WORKFLOW_NODES = [
  {
    id: 'demand_agent',
    step: '01',
    title: 'Demand Forecaster',
    role: 'Pic de consommation & Anomalies',
    icon: TrendingUp,
    colorScheme: 'indigo',
    stateKey: 'demand_forecast'
  },
  {
    id: 'inventory_agent',
    step: '02',
    title: 'Inventory Optimizer',
    role: 'ROP & Plancher légal 500u',
    icon: Package,
    colorScheme: 'emerald',
    stateKey: 'inventory_analysis'
  },
  {
    id: 'risk_agent',
    step: '03',
    title: 'Risk Radar',
    role: 'Alertes météo & Canaux maritimes',
    icon: ShieldAlert,
    colorScheme: 'amber',
    stateKey: 'risk_assessment'
  },
  {
    id: 'procurement_agent',
    step: '04',
    title: 'Procurement Sourcing',
    role: 'Bilan devis & Capacité usine',
    icon: ShoppingCart,
    colorScheme: 'teal',
    stateKey: 'selected_procurement'
  },
  {
    id: 'compliance_guardrail',
    step: '05',
    title: 'Sovereign Guardrail',
    role: 'Contrôle Sanctions & Droit de Veto',
    icon: Scale,
    colorScheme: 'purple',
    stateKey: 'compliance_review',
    isGuardrail: true
  },
  {
    id: 'logistics_agent',
    step: '06',
    title: 'Logistics Fleet',
    role: 'Affrètement prioritaire certifié',
    icon: Truck,
    colorScheme: 'blue',
    stateKey: 'logistics_plan'
  },
  {
    id: 'orchestrator_agent',
    step: '07',
    title: 'Master Orchestrator',
    role: 'Arbitrage régalien & Décret d’État',
    icon: Network,
    colorScheme: 'sapphire',
    stateKey: 'orchestrator_decision',
    isOrchestrator: true
  }
];

export default function PipelineGraph({
  activeNodeId,
  completedNodeIds = [],
  selectedNodeId,
  onSelectNode,
  graphState = {}
}) {
  const isVetoed = graphState.compliance_review?.status === 'REJECTED_VETO';

  return (
    <section className="pipeline-wrapper" aria-label="Pipeline d’exécution des agents">
      <div className="pipeline-header-row">
        <div>
          <h2 className="pipeline-heading">Pipeline Multi-Agents LangGraph</h2>
          <p className="pipeline-subheading">
            Propagation décentralisée de l’état typé sous arbitrage légal strict. Cliquez sur un agent pour inspecter ses variables en temps réel.
          </p>
        </div>
        <div className="pipeline-meta-tags">
          <span className="meta-chip">7 Nœuds Connectés</span>
          <span className="meta-chip active">StateGraph v0.2</span>
        </div>
      </div>

      <div className="nodes-flow-container">
        {WORKFLOW_NODES.map((node, index) => {
          const Icon = node.icon;
          const isActive = activeNodeId === node.id;
          const isDone = completedNodeIds.includes(node.id);
          const isSelected = selectedNodeId === node.id;
          const hasOutput = Boolean(graphState[node.stateKey]);

          let statusClass = 'status-idle';
          let statusLabel = 'En veille';

          if (isActive) {
            statusClass = 'status-active';
            statusLabel = 'Analyse...';
          } else if (isDone) {
            if (node.id === 'compliance_guardrail' && isVetoed) {
              statusClass = 'status-veto';
              statusLabel = 'Veto Légal';
            } else {
              statusClass = 'status-done';
              statusLabel = 'Certifié';
            }
          }

          return (
            <React.Fragment key={node.id}>
              <div
                tabIndex={0}
                role="button"
                className={`pipeline-card ${statusClass} ${isSelected ? 'selected' : ''} ${node.isGuardrail ? 'guardrail' : ''} ${node.isOrchestrator ? 'orchestrator' : ''}`}
                onClick={() => onSelectNode(node.id)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    onSelectNode(node.id);
                  }
                }}
              >
                <div className="node-card-top">
                  <span className="step-number">{node.step}</span>
                  <div className={`node-icon-bubble ${node.colorScheme}`}>
                    <Icon size={16} />
                  </div>
                </div>

                <div className="node-card-center">
                  <div className="node-name">{node.title}</div>
                  <div className="node-detail">{node.role}</div>
                </div>

                <div className="node-card-bottom">
                  <span className={`pill-badge badge-${statusClass}`}>
                    {isActive ? (
                      <>
                        <Loader2 size={11} className="spin" />
                        <span>En cours</span>
                      </>
                    ) : isDone ? (
                      node.id === 'compliance_guardrail' && isVetoed ? (
                        <>
                          <XCircle size={11} />
                          <span>Veto</span>
                        </>
                      ) : (
                        <>
                          <CheckCircle2 size={11} />
                          <span>Prêt</span>
                        </>
                      )
                    ) : (
                      <>
                        <span className="dot-idle"></span>
                        <span>En veille</span>
                      </>
                    )}
                  </span>
                  {hasOutput && <span className="output-pulse-dot" title="Données d’état disponibles">●</span>}
                </div>
              </div>

              {index < WORKFLOW_NODES.length - 1 && (
                <div className="flow-arrow-separator" aria-hidden="true">
                  <ArrowRight size={14} />
                </div>
              )}
            </React.Fragment>
          );
        })}
      </div>
    </section>
  );
}
