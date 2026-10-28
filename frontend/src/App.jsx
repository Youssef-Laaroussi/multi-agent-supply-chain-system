import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  Shield,
  Play,
  LayoutDashboard,
  Scale,
  Cpu,
  GitBranch,
  Database,
  CheckCircle2,
  ArrowRight,
  ArrowLeft,
  Terminal,
  FileCheck,
  BookOpen,
  RefreshCw,
  RotateCcw,
  Radio,
  Sparkles,
  Layers,
  Lock,
  Activity,
  Zap,
  Globe
} from 'lucide-react';

import ConnectionBanner from './components/ConnectionBanner';
import MetricRibbon from './components/MetricRibbon';
import PipelineGraph, { WORKFLOW_NODES } from './components/PipelineGraph';
import SimulationConsole from './components/SimulationConsole';
import NodeStateInspector from './components/NodeStateInspector';
import LiveStreamLogs from './components/LiveStreamLogs';
import ExecutiveDecreeView from './components/ExecutiveDecreeView';
import CatalogsView from './components/CatalogsView';
import { checkBackendHealth, fetchSystemCatalogs, streamSimulation } from './api/client';

const FALLBACK_CATALOGS = {
  strategic_skus: ['SKU-MED-901', 'SKU-ENG-404', 'SKU-FOOD-101'],
  reserve_floor: 500,
  spending_ceiling_eur: 100000,
  emergency_ceiling_eur: 250000,
  sanctioned_countries: ['EMBARGO_LAND', 'UNAPPROVED_OFFSHORE', 'NON_CERTIFIED_TERRITORY'],
  suppliers: [
    {
      id: 'SUP-DOMESTIC-01',
      name: 'Hexagon National Strategic Industries',
      country: 'DOMESTIC',
      certified_by_state: true,
      lead_time_days: 2,
      unit_price_eur: 120.0,
      capacity_units: 1500,
      reliability_score: 0.98,
      description: 'Partenaire souverain certifié Défense avec dédouanement prioritaire.'
    },
    {
      id: 'SUP-GLOBAL-02',
      name: 'Pan-Euro Logistics & Supplies',
      country: 'ALLIED_EU',
      certified_by_state: true,
      lead_time_days: 5,
      unit_price_eur: 95.0,
      capacity_units: 3000,
      reliability_score: 0.91,
      description: 'Fournisseur allié européen, optimal pour les réapprovisionnements planifiés.'
    },
    {
      id: 'SUP-EMBARGO-03',
      name: 'DarkBay Grey-Market Components',
      country: 'EMBARGO_LAND',
      certified_by_state: false,
      lead_time_days: 1,
      unit_price_eur: 60.0,
      capacity_units: 5000,
      reliability_score: 0.65,
      description: 'Rapide et bas coût, mais juridiction sous embargo et non certifiée.'
    }
  ],
  carriers: [
    {
      id: 'CARRIER-STATE-AIR',
      name: 'National Sovereign Air Express',
      speed_tier: 'CRITICAL_EXPRESS',
      transit_days: 1,
      cost_per_unit_eur: 15.0,
      certified_security: true
    },
    {
      id: 'CARRIER-EURO-ROAD',
      name: 'Trans-Continental Freight Fleet',
      speed_tier: 'STANDARD_ROAD',
      transit_days: 3,
      cost_per_unit_eur: 5.0,
      certified_security: true
    },
    {
      id: 'CARRIER-LOW-ECO',
      name: 'SlowRail Maritime & Intermodal',
      speed_tier: 'ECONOMY_SLOW',
      transit_days: 7,
      cost_per_unit_eur: 1.5,
      certified_security: false
    }
  ]
};

const AGENT_SPECS = [
  {
    step: '01',
    id: 'demand_agent',
    name: 'Demand Forecasting Agent',
    tool: 'calculate_demand_forecast_tool',
    summary: 'Modélise la consommation sur 7 jours, détecte les chocs pandémiques ou industriels (+80%) et quantifie le besoin net.',
    outputKey: 'state.demand_forecast'
  },
  {
    step: '02',
    id: 'inventory_agent',
    name: 'Inventory Optimization Agent',
    tool: 'calculate_inventory_metrics_tool',
    summary: 'Calcule le Reorder Point (ROP = d·L + SS), le stock de sécurité (Z=1.96) et vérifie le plancher légal de 500 unités.',
    outputKey: 'state.inventory_analysis'
  },
  {
    step: '03',
    id: 'risk_agent',
    name: 'Risk & Disruption Radar Agent',
    tool: 'query_risk_radar_tool',
    summary: 'Analyse les perturbations géopolitiques et maritimes (Canal de Suez, tempêtes) et calcule les pénalités de délai par fournisseur.',
    outputKey: 'state.risk_assessment'
  },
  {
    step: '04',
    id: 'procurement_agent',
    name: 'Procurement & Sourcing Agent',
    tool: 'evaluate_supplier_proposals_tool',
    summary: 'Interroge le catalogue fournisseurs, intègre les délais de crise et classe les offres selon coût, capacité et fiabilité.',
    outputKey: 'state.selected_procurement'
  },
  {
    step: '05',
    id: 'compliance_guardrail',
    name: 'Sovereign Compliance Guardrail',
    tool: 'Command[Literal["logistics_agent", "orchestrator_agent"]]',
    summary: 'Exerce un droit de VETO statutaire sur tout pays sous embargo (EMBARGO_LAND), valide les plafonds budgétaires (100k€/250k€) et route le graphe.',
    outputKey: 'state.compliance_review',
    isGuardrail: true
  },
  {
    step: '06',
    id: 'logistics_agent',
    name: 'Logistics & Fleet Agent',
    tool: 'plan_freight_dispatch_tool',
    summary: 'Alloue les flottes habilitées Défense (Pont Aérien Souverain 24h ou Route Sécurisée) selon le niveau d’urgence.',
    outputKey: 'state.logistics_plan'
  },
  {
    step: '07',
    id: 'orchestrator_agent',
    name: 'Master Control Tower Orchestrator',
    tool: 'Executive Decree Synthesizer',
    summary: 'Arbitre le compromis Coût / Délai / Souveraineté et scelle le Décret Exécutif JSON conforme à l’Art. L2122-1 du Code de la commande publique.',
    outputKey: 'state.orchestrator_decision',
    isOrchestrator: true
  }
];

export default function App() {
  // Two separate pages: 'landing' (Page d'accueil) | 'dashboard' (Control Tower plein écran)
  const [currentPage, setCurrentPage] = useState('landing');
  const [activeTab, setActiveTab] = useState('operations');

  const [backendHealth, setBackendHealth] = useState({ ok: false });
  const [isCheckingHealth, setIsCheckingHealth] = useState(false);
  const [catalogs, setCatalogs] = useState(FALLBACK_CATALOGS);

  const [currentSku, setCurrentSku] = useState('SKU-MED-901');
  const [stock, setStock] = useState(750);
  const [prompt, setPrompt] = useState(
    'Alerte Pandémique : Pic de consommation hospitalière de +80% détecté. Sécuriser le plancher de 500 unités via un fournisseur souverain certifié.'
  );

  const [isSimulating, setIsSimulating] = useState(false);
  const [activeNodeId, setActiveNodeId] = useState(null);
  const [completedNodeIds, setCompletedNodeIds] = useState([]);
  const [selectedNodeId, setSelectedNodeId] = useState('demand_agent');
  const [graphState, setGraphState] = useState({});
  const [logs, setLogs] = useState([]);

  const abortControllerRef = useRef(null);

  const appendLog = useCallback((node, content, role = 'agent') => {
    const timestamp = new Date().toLocaleTimeString('fr-FR', { hour12: false });
    setLogs((prev) => [
      ...prev,
      { id: `${Date.now()}-${Math.random()}`, timestamp, node, content, role }
    ]);
  }, []);

  const refreshBackendStatus = useCallback(async () => {
    setIsCheckingHealth(true);
    const health = await checkBackendHealth();
    setBackendHealth(health);
    if (health.ok) {
      const catRes = await fetchSystemCatalogs();
      if (catRes.ok && catRes.data) {
        setCatalogs(catRes.data);
      }
    }
    setIsCheckingHealth(false);
  }, []);

  useEffect(() => {
    refreshBackendStatus();
  }, [refreshBackendStatus]);

  const handleResetSession = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    setIsSimulating(false);
    setActiveNodeId(null);
    setCompletedNodeIds([]);
    setGraphState({});
    setLogs([]);
    setActiveTab('operations');
  };

  const runRealisticDemo = async () => {
    setCurrentPage('dashboard');
    setActiveTab('operations');
    setIsSimulating(true);
    setActiveNodeId(null);
    setCompletedNodeIds([]);
    setGraphState({});
    setLogs([]);

    const stockNum = Number(stock) || 750;
    const reserveFloor = catalogs.reserve_floor || 500;
    const reorderQty = Math.max(400, reserveFloor + 1732 + 51 - stockNum);

    appendLog('OPÉRATEUR', `Mission initiée sur ${currentSku} (Stock: ${stockNum}u | Plancher: ${reserveFloor}u).`, 'user');

    const demoSteps = [
      {
        node: 'demand_agent',
        log: `📈 DEMAND_AGENT: Évaluation ${currentSku} via @tool calculate_demand_forecast_tool. Pic d'anomalie: +80% | Demande 7j: 1 732 unités.`,
        update: {
          demand_forecast: {
            sku: currentSku,
            baseline_daily_average: 137.5,
            adjusted_daily_forecast: 247.5,
            planning_horizon_days: 7,
            total_projected_demand: 1732,
            emergency_shock_factor: 0.8,
            surge_percentage: '80%',
            anomaly_detected: true
          }
        }
      },
      {
        node: 'inventory_agent',
        log: `📦 INVENTORY_AGENT: Stock actuel ${stockNum}u vs Plancher d'État ${reserveFloor}u. Rupture projetée sous 72h: OUI | Reorder: ${reorderQty} unités.`,
        update: {
          inventory_analysis: {
            current_stock: stockNum,
            strategic_reserve_floor: reserveFloor,
            daily_demand: 247.5,
            lead_time_days: 3,
            safety_stock: 51,
            reorder_point: 793,
            days_of_supply: +(stockNum / 247.5).toFixed(1),
            projected_post_lead_stock: Math.round(stockNum - 742.5),
            strategic_reserve_breach: true,
            reorder_needed: true,
            recommended_reorder_qty: reorderQty
          }
        }
      },
      {
        node: 'risk_agent',
        log: `🚨 RISK_AGENT: Scan @tool query_risk_radar_tool — Niveau HIGH (2 alertes : Perturbation Mer Rouge +5j, Tempête Atlantique).`,
        update: {
          risk_assessment: {
            sku: currentSku,
            risk_level: 'HIGH',
            active_alerts_count: 2,
            disruptions: [
              { code: 'MARITIME-SUEZ-01', severity: 'HIGH', induced_delay_days: 5, impacted_supplier_id: 'SUP-GLOBAL-02' }
            ],
            recommendation: 'Privilégier un fournisseur souverain domestique et un fret aérien certifié.'
          }
        }
      },
      {
        node: 'procurement_agent',
        log: `🤝 PROCUREMENT_AGENT: 3 offres évaluées via @tool evaluate_supplier_proposals_tool. Offre moins-disante initiale : DarkBay Grey-Market (EMBARGO_LAND) soumise au contrôle régalien.`,
        update: {
          selected_procurement: {
            supplier_id: 'SUP-EMBARGO-03',
            supplier_name: 'DarkBay Grey-Market Components',
            country: 'EMBARGO_LAND',
            certified_by_state: false,
            effective_lead_time_days: 1,
            unit_price_eur: 60.0,
            quantity_quoted: reorderQty,
            total_material_cost_eur: reorderQty * 60
          }
        }
      },
      {
        node: 'compliance_guardrail',
        log: `🏛️ COMPLIANCE_AGENT (Command Routing): VETO exercé contre 'DarkBay Grey-Market' (EMBARGO_LAND). Re-routage automatique vers 'Hexagon National Strategic Industries' (DOMESTIC, Certifié Défense).`,
        update: {
          selected_procurement: {
            supplier_id: 'SUP-DOMESTIC-01',
            supplier_name: 'Hexagon National Strategic Industries',
            country: 'DOMESTIC',
            certified_by_state: true,
            effective_lead_time_days: 2,
            unit_price_eur: 120.0,
            quantity_quoted: reorderQty,
            total_material_cost_eur: reorderQty * 120
          },
          compliance_review: {
            status: 'APPROVED',
            veto_exercised: true,
            approved_supplier_id: 'SUP-DOMESTIC-01',
            approved_supplier_name: 'Hexagon National Strategic Industries',
            sovereign_decree_active: true,
            audit_trail: [
              'VETO: Juridiction EMBARGO_LAND bloquée par embargo_sanction_guardrail.',
              'ALTERNATIVE CERTIFIÉE: Hexagon National Strategic Industries (DOMESTIC) validée.',
              'BUDGET GUARDRAIL: Plafond d’urgence (250 000 €) respecté.',
              'RESERVE GUARDRAIL: Plancher stratégique de 500 unités sécurisé.'
            ]
          }
        }
      },
      {
        node: 'logistics_agent',
        log: `🚚 LOGISTICS_AGENT: Flotte assignée via @tool plan_freight_dispatch_tool : National Sovereign Air Express (Transit 1j, Escorte Sécurité).`,
        update: {
          logistics_plan: {
            carrier_id: 'CARRIER-STATE-AIR',
            carrier_name: 'National Sovereign Air Express',
            speed_tier: 'CRITICAL_EXPRESS',
            urgency_tier: 'CRITICAL',
            transit_days: 1,
            quantity_dispatched: reorderQty,
            total_freight_cost_eur: reorderQty * 15.0,
            security_certified: true
          }
        }
      },
      {
        node: 'orchestrator_agent',
        log: `👑 MASTER ORCHESTRATOR: Décret Exécutif signé — ${reorderQty} unités de ${currentSku} autorisées auprès de Hexagon National Strategic Industries.`,
        update: {
          orchestrator_decision: {
            executive_order_id: `EX-DECREE-${new Date().toISOString().slice(0, 10).replace(/-/g, '')}-901`,
            sku: currentSku,
            sku_description: 'Filtres Respiratoires ICU & Réserve Nationale de Santé',
            verdict: 'AUTHORIZED_AND_DISPATCHED',
            authorized_supplier: 'Hexagon National Strategic Industries',
            supplier_country: 'DOMESTIC',
            units_ordered: reorderQty,
            material_cost_eur: reorderQty * 120,
            carrier_assigned: 'National Sovereign Air Express',
            freight_cost_eur: reorderQty * 15,
            total_commitment_eur: reorderQty * 135,
            estimated_arrival_days: 3,
            strategic_reserve_secured: true,
            legal_basis: 'Code de la commande publique — Art. L2122-1 (Urgence Impérieuse)',
            trade_off_resolution:
              "Malgré un surcoût unitaire face à l'offre offshore sous embargo (60 €/u), le Sovereign Guardrail a exercé son droit de veto légal. Le Master Orchestrator valide l'engagement auprès du partenaire national certifié Défense (Hexagon National Strategic Industries) avec pont aérien express (3 jours de cycle total) afin de garantir l'intégrité du plancher stratégique de 500 unités."
          }
        }
      }
    ];

    for (const step of demoSteps) {
      setActiveNodeId(step.node);
      setSelectedNodeId(step.node);
      await new Promise((r) => setTimeout(r, 650));
      setGraphState((prev) => ({ ...prev, ...step.update }));
      setCompletedNodeIds((prev) => [...new Set([...prev, step.node])]);
      appendLog(step.node.toUpperCase(), step.log);
    }

    setActiveNodeId(null);
    setIsSimulating(false);
  };

  const handleStartSimulation = async () => {
    if (isSimulating) return;
    setCurrentPage('dashboard');
    setActiveTab('operations');

    const health = await checkBackendHealth();
    setBackendHealth(health);

    if (!health.ok) {
      await runRealisticDemo();
      return;
    }

    setIsSimulating(true);
    setActiveNodeId(null);
    setCompletedNodeIds([]);
    setGraphState({});
    setLogs([]);

    appendLog(
      'OPÉRATEUR',
      `Connexion SSE au StateGraph LangGraph (${currentSku} | Stock: ${stock}u)...`,
      'user'
    );

    const controller = new AbortController();
    abortControllerRef.current = controller;

    await streamSimulation(
      {
        sku: currentSku,
        startingStock: Number(stock) || 750,
        prompt,
        signal: controller.signal
      },
      {
        onEvent: (payload) => {
          if (payload.node === 'END') {
            appendLog('SYSTÈME', payload.message || 'Délibération LangGraph terminée.', 'system');
            return;
          }
          setActiveNodeId(payload.node);
          setSelectedNodeId(payload.node);
          setCompletedNodeIds((prev) => [...new Set([...prev, payload.node])]);
          if (payload.state_update) {
            setGraphState((prev) => ({ ...prev, ...payload.state_update }));
          }
          if (payload.message) {
            appendLog(payload.node.toUpperCase(), payload.message);
          }
        },
        onError: (err) => {
          appendLog('ERREUR', err.message || 'Interruption du flux SSE.', 'guardrail-veto');
          setIsSimulating(false);
          setActiveNodeId(null);
        },
        onComplete: () => {
          setIsSimulating(false);
          setActiveNodeId(null);
        }
      }
    );
  };

  const handleAbortSimulation = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    setIsSimulating(false);
    setActiveNodeId(null);
  };

  /* =========================================================================
     PAGE 1: ENTERPRISE WHITE LANDING PAGE (DATABRICKS / SNOWFLAKE STYLE)
     ========================================================================= */
  if (currentPage === 'landing') {
    return (
      <div className="enterprise-landing">
        {/* Clean White Sticky Navbar */}
        <header className="landing-navbar">
          <div className="landing-nav-inner">
            <div className="brand-identity">
              <div className="brand-mark">
                <Shield size={22} strokeWidth={2.5} />
              </div>
              <div className="brand-text">
                <span className="brand-title">AURA SOVEREIGN</span>
                <span className="brand-version">LangGraph v1.0</span>
              </div>
            </div>

            <nav className="landing-nav-links" aria-label="Sections de la page">
              <a href="#plateforme">Plateforme</a>
              <a href="#agents">Les 7 Agents</a>
              <a href="#guardrails">Sovereign Guardrails</a>
              <a href="#architecture">Standards LangGraph</a>
            </nav>

            <div className="landing-nav-cta">
              <button
                type="button"
                className="btn-ghost"
                onClick={runRealisticDemo}
              >
                <Play size={15} />
                <span>Démo Live</span>
              </button>
              <button
                type="button"
                className="btn-primary-coral"
                onClick={() => setCurrentPage('dashboard')}
              >
                <LayoutDashboard size={16} />
                <span>Ouvrir le Control Tower</span>
                <ArrowRight size={15} />
              </button>
            </div>
          </div>
        </header>

        {/* SECTION 1: HERO (Pure White, Generous Spacing, Real Product Preview) */}
        <section className="hero-section" id="plateforme">
          <div className="hero-container">
            <div className="hero-copy-col">
              <div className="eyebrow-pill">
                <span className="eyebrow-dot" />
                <span>MULTI-AGENT SUPPLY CHAIN SYSTEM • LANGGRAPH v1.0 & LANGCHAIN</span>
              </div>

              <h1 className="hero-display-title">
                Orchestration Multi-Agents Autonome pour{' '}
                <span className="accent-coral">Réserves Stratégiques d’État</span>.
              </h1>

              <p className="hero-lead-paragraph">
                Une architecture d’IA agentique de production conçue avec <strong>LangGraph StateGraph</strong>,{' '}
                <strong>ToolNode</strong> et <strong>Command API</strong>. Sept agents spécialisés anticipent les
                ruptures critiques, bloquent par veto les juridictions sous embargo et scellent des décrets
                d’approvisionnement auditables en temps réel.
              </p>

              <div className="hero-action-row">
                <button
                  type="button"
                  className="btn-primary-coral btn-lg"
                  onClick={() => setCurrentPage('dashboard')}
                >
                  <LayoutDashboard size={18} />
                  <span>Accéder au Control Tower Dashboard</span>
                  <ArrowRight size={17} />
                </button>

                <button
                  type="button"
                  className="btn-secondary-white btn-lg"
                  onClick={runRealisticDemo}
                >
                  <Play size={17} />
                  <span>Lancer un Scénario de Crise</span>
                </button>
              </div>

              <div className="hero-trust-badges">
                <div className="trust-item">
                  <CheckCircle2 size={16} className="icon-coral" />
                  <span><strong>StateGraph & ToolNode</strong> Officiels</span>
                </div>
                <div className="trust-item">
                  <CheckCircle2 size={16} className="icon-coral" />
                  <span><strong>Command API</strong> & Droit de Veto</span>
                </div>
                <div className="trust-item">
                  <CheckCircle2 size={16} className="icon-coral" />
                  <span><strong>MemorySaver</strong> Checkpointing</span>
                </div>
              </div>
            </div>

            {/* Right Column: Clean White Product Architecture Preview Card */}
            <div className="hero-preview-col">
              <div className="product-preview-card">
                <div className="preview-card-top">
                  <div className="preview-title-group">
                    <span className="status-live-badge">
                      <span className="live-pulse" />
                      STATEGRAPH PIPELINE
                    </span>
                    <span className="preview-thread-id">thread_id: crisis-med-901</span>
                  </div>
                  <span className="preview-framework-tag">LangGraph v1.0</span>
                </div>

                <div className="preview-metrics-row">
                  <div className="mini-metric-box">
                    <span className="mm-label">Plancher Légal</span>
                    <strong className="mm-value">500 unités</strong>
                    <span className="mm-tag ok">Seuil Infranchissable</span>
                  </div>
                  <div className="mini-metric-box">
                    <span className="mm-label">Plafond Crise</span>
                    <strong className="mm-value">250 000 €</strong>
                    <span className="mm-tag info">Art. L2122-1</span>
                  </div>
                  <div className="mini-metric-box">
                    <span className="mm-label">Sovereign Guardrail</span>
                    <strong className="mm-value">Veto Actif</strong>
                    <span className="mm-tag coral">Anti-Embargo</span>
                  </div>
                </div>

                <div className="preview-pipeline-list">
                  {WORKFLOW_NODES.slice(0, 5).map((node) => {
                    const Icon = node.icon;
                    return (
                      <div key={node.id} className="preview-node-item">
                        <div className="p-node-left">
                          <span className="p-node-step">{node.step}</span>
                          <div className="p-node-icon">
                            <Icon size={16} />
                          </div>
                          <div>
                            <div className="p-node-title">{node.title}</div>
                            <div className="p-node-sub">{node.role}</div>
                          </div>
                        </div>
                        <span className={`p-node-pill ${node.isGuardrail ? 'pill-coral' : ''}`}>
                          {node.isGuardrail ? 'Command Routing' : '@tool + ToolNode'}
                        </span>
                      </div>
                    );
                  })}
                </div>

                <div className="preview-card-footer">
                  <span>7 nœuds connectés • Streaming SSE FastAPI • 14/14 Tests Pytest</span>
                  <button
                    type="button"
                    className="link-btn-coral"
                    onClick={() => setCurrentPage('dashboard')}
                  >
                    Inspecter en direct →
                  </button>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* SECTION 2: BENCHMARK & ARCHITECTURAL METRICS BAR */}
        <section className="metrics-banner-section">
          <div className="section-container">
            <div className="benchmark-grid">
              <div className="benchmark-card">
                <span className="bm-number">7 Agents</span>
                <strong className="bm-title">Spécialisés & Autonomes</strong>
                <p className="bm-desc">
                  Sous-graphes ReAct compilés avec <code>MessagesState</code>, <code>ToolNode</code> et{' '}
                  <code>tools_condition</code>.
                </p>
              </div>

              <div className="benchmark-card">
                <span className="bm-number">5 Outils</span>
                <strong className="bm-title">LangChain @tool + Pydantic</strong>
                <p className="bm-desc">
                  Calculs déterministes de prévision, ROP, stock de sécurité, fret et scoring fournisseurs.
                </p>
              </div>

              <div className="benchmark-card">
                <span className="bm-number">3 Guardrails</span>
                <strong className="bm-title">Conformité & Droit de Veto</strong>
                <p className="bm-desc">
                  Contrôle statutaire des sanctions internationales, du plafond budgétaire et du plancher de 500u.
                </p>
              </div>

              <div className="benchmark-card">
                <span className="bm-number">14 / 14</span>
                <strong className="bm-title">Tests Automatisés Pytest</strong>
                <p className="bm-desc">
                  Exécution déterministe hors-ligne (<code>MockDeterministicChatModel</code>) ou LLM Live (OpenAI / DeepSeek).
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* SECTION 3: THE 7 SPECIALIZED AGENTS (DATABRICKS PRODUCT GRID) */}
        <section className="agents-showcase-section" id="agents">
          <div className="section-container">
            <div className="section-header-center">
              <span className="section-kicker">PIPELINE D’EXÉCUTION MULTI-AGENTS</span>
              <h2 className="section-heading">
                7 Nœuds Spécialisés Orchestrés par <code>StateGraph</code>
              </h2>
              <p className="section-description">
                Chaque agent lit et enrichit un état partagé strictement typé (<code>SupplyChainState</code>)
                tout en accumulant l’historique de conversation via le réducteur officiel{' '}
                <code>Annotated[list[BaseMessage], add_messages]</code>.
              </p>
            </div>

            <div className="agents-cards-grid">
              {AGENT_SPECS.map((ag) => (
                <article
                  key={ag.id}
                  className={`agent-spec-card ${ag.isGuardrail ? 'spec-guardrail' : ''} ${ag.isOrchestrator ? 'spec-orchestrator' : ''}`}
                >
                  <div className="spec-card-top">
                    <span className="spec-step-badge">ÉTAPE {ag.step}</span>
                    <code className="spec-node-id">{ag.id}</code>
                  </div>

                  <h3 className="spec-agent-name">{ag.name}</h3>
                  <p className="spec-agent-summary">{ag.summary}</p>

                  <div className="spec-card-meta">
                    <div className="spec-meta-row">
                      <span className="meta-label">Primitive :</span>
                      <code className="meta-code">{ag.tool}</code>
                    </div>
                    <div className="spec-meta-row">
                      <span className="meta-label">Clé d’état :</span>
                      <code className="meta-code">{ag.outputKey}</code>
                    </div>
                  </div>
                </article>
              ))}
            </div>
          </div>
        </section>

        {/* SECTION 4: SOVEREIGN GUARDRAILS & LANGGRAPH V1.0 ARCHITECTURE */}
        <section className="guardrails-section" id="guardrails">
          <div className="section-container">
            <div className="split-feature-layout">
              <div className="split-left-col">
                <span className="section-kicker">GOUVERNANCE RÉGALIENNE & SÉCURITÉ</span>
                <h2 className="section-heading-left">
                  Trois Guardrails Statutaires avec Routage Dynamique <code>Command</code>
                </h2>
                <p className="section-lead-left">
                  Contrairement aux pipelines LLM classiques, les règles de souveraineté ne reposent pas sur un
                  simple prompt : elles sont exécutées par des validateurs déterministes capables d’opposer un{' '}
                  <strong>Veto immédiat</strong> et de re-router l’exécution.
                </p>

                <div className="guardrail-feature-list">
                  <div className="gf-item">
                    <div className="gf-icon">
                      <Lock size={20} />
                    </div>
                    <div className="gf-text">
                      <h4>1. Embargo & Sanctions Guardrail</h4>
                      <p>
                        Bloque toute soumission issue de juridictions sanctionnées (<code>EMBARGO_LAND</code>,{' '}
                        <code>UNAPPROVED_OFFSHORE</code>) et exige <code>certified_by_state == True</code>.
                      </p>
                    </div>
                  </div>

                  <div className="gf-item">
                    <div className="gf-icon">
                      <Scale size={20} />
                    </div>
                    <div className="gf-text">
                      <h4>2. Public Procurement Budget Guardrail</h4>
                      <p>
                        Applique le plafond de dépense standard de <strong>100 000 €</strong> et active
                        automatiquement le plafond ministériel d’urgence de <strong>250 000 €</strong> en cas de
                        rupture imminente.
                      </p>
                    </div>
                  </div>

                  <div className="gf-item">
                    <div className="gf-icon">
                      <Shield size={20} />
                    </div>
                    <div className="gf-text">
                      <h4>3. Strategic Reserve Floor Guardrail (500u)</h4>
                      <p>
                        Garantit que le stock net projeté après délai de livraison reste strictement supérieur
                        au plancher national de <strong>500 unités</strong>.
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Clean Light Code & Architecture Specification Box */}
              <div className="split-right-col" id="architecture">
                <div className="light-code-showcase">
                  <div className="code-showcase-header">
                    <div className="code-file-tabs">
                      <span className="code-tab active">agent_factory.py</span>
                      <span className="code-tab">compliance_agent.py</span>
                    </div>
                    <span className="code-standard-badge">LangGraph v1.0 Official Standard</span>
                  </div>

                  <pre className="light-code-pre">
                    <code>{`from typing import Literal
from langgraph.graph import StateGraph, MessagesState, START
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.types import Command

# 1. Official ReAct Subgraph with prebuilt ToolNode
def build_react_agent(tools: list):
    model = get_agent_llm().bind_tools(tools)

    def call_model(state: MessagesState):
        return {"messages": [model.invoke(state["messages"])]}

    workflow = StateGraph(MessagesState)
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", ToolNode(tools))
    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges("agent", tools_condition)
    workflow.add_edge("tools", "agent")
    return workflow.compile()

# 2. Sovereign Guardrail Node with Command Routing
def compliance_governance_node(
    state: SupplyChainState,
) -> Command[Literal["logistics_agent", "orchestrator_agent"]]:
    goto = "logistics_agent" if is_compliant else "orchestrator_agent"
    return Command(goto=goto, update={"is_compliant": is_compliant})`}</code>
                  </pre>

                  <div className="code-showcase-footer">
                    <span>Architecture 100% conforme à la documentation officielle LangGraph v1.0</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* SECTION 5: BOTTOM CALL TO ACTION & FOOTER */}
        <footer className="landing-footer">
          <div className="section-container">
            <div className="footer-cta-banner">
              <div className="footer-cta-text">
                <h2>Prêt à inspecter l’exécution des 7 agents en temps réel ?</h2>
                <p>
                  Passez sur le Control Tower Dashboard pour lancer une simulation SSE, inspecter l’état JSON de
                  chaque nœud et télécharger le Décret Exécutif officiel.
                </p>
              </div>
              <div className="footer-cta-buttons">
                <button
                  type="button"
                  className="btn-primary-coral btn-lg"
                  onClick={() => setCurrentPage('dashboard')}
                >
                  <LayoutDashboard size={18} />
                  <span>Ouvrir le Control Tower Dashboard</span>
                  <ArrowRight size={17} />
                </button>
              </div>
            </div>

            <div className="footer-bottom-row">
              <div className="brand-identity">
                <div className="brand-mark sm">
                  <Shield size={16} />
                </div>
                <span className="footer-brand-name">AURA SOVEREIGN — Multi-Agent Supply Chain System</span>
              </div>
              <span className="footer-copyright">
                Propulsé par Python 3.12 • LangGraph v1.0 • LangChain • FastAPI • React 18
              </span>
            </div>
          </div>
        </footer>
      </div>
    );
  }

  /* =========================================================================
     PAGE 2: FULL-SCREEN CONTROL TOWER DASHBOARD (100% LIGHT / WHITE THEME)
     ========================================================================= */
  return (
    <div className="dashboard-page-shell">
      {/* Top Control Tower Header */}
      <header className="dashboard-topbar" role="banner">
        <div className="dashboard-topbar-inner">
          <div className="topbar-left">
            <button
              type="button"
              className="back-to-landing-btn"
              onClick={() => setCurrentPage('landing')}
            >
              <ArrowLeft size={16} />
              <span>Accueil & Architecture</span>
            </button>

            <div className="topbar-divider" />

            <div className="brand-identity">
              <div className="brand-mark sm">
                <Shield size={18} strokeWidth={2.4} />
              </div>
              <div>
                <div className="brand-title-line">
                  <span className="brand-title">CONTROL TOWER DASHBOARD</span>
                  <span className="brand-version">StateGraph Live</span>
                </div>
              </div>
            </div>
          </div>

          <div className="topbar-right">
            <div className="engine-chip">
              <Radio size={14} className="icon-coral" />
              <span>LangGraph v1.0 + MemorySaver</span>
            </div>

            <div
              className={`api-status-pill ${backendHealth?.ok ? 'status-connected' : 'status-disconnected'}`}
            >
              <span className="pulse-indicator-dot" />
              <span>{backendHealth?.ok ? 'API FastAPI Connectée (8000)' : 'Mode Démo Autonome'}</span>
              <button
                type="button"
                className="refresh-indicator-btn"
                onClick={refreshBackendStatus}
                disabled={isCheckingHealth}
                title="Vérifier la connexion backend"
              >
                <RefreshCw size={13} className={isCheckingHealth ? 'spin' : ''} />
              </button>
            </div>

            <button
              type="button"
              className="navbar-reset-btn"
              onClick={handleResetSession}
              disabled={isSimulating}
            >
              <RotateCcw size={14} />
              <span>Réinitialiser</span>
            </button>
          </div>
        </div>
      </header>

      {/* Main Spacious Dashboard Body */}
      <main className="dashboard-container">
        {!backendHealth?.ok && (
          <ConnectionBanner
            onRetry={refreshBackendStatus}
            isChecking={isCheckingHealth}
            onRunDemo={runRealisticDemo}
          />
        )}

        {/* 1. Spacious 4-KPI Metric Ribbon */}
        <MetricRibbon
          selectedSku={currentSku}
          currentStock={stock}
          reserveFloor={catalogs.reserve_floor || 500}
          spendingCeiling={catalogs.spending_ceiling_eur || 100000}
          graphState={graphState}
        />

        {/* 2. Spacious 7-Node Interactive Pipeline */}
        <PipelineGraph
          activeNodeId={activeNodeId}
          completedNodeIds={completedNodeIds}
          selectedNodeId={selectedNodeId}
          onSelectNode={(nodeId) => {
            setSelectedNodeId(nodeId);
            setActiveTab('operations');
          }}
          graphState={graphState}
        />

        {/* 3. Main 2-Column Workspace (Generous Gap & Padding) */}
        <div className="workspace-grid">
          <SimulationConsole
            skuList={catalogs.strategic_skus}
            currentSku={currentSku}
            onChangeSku={setCurrentSku}
            stock={stock}
            onChangeStock={setStock}
            prompt={prompt}
            onChangePrompt={setPrompt}
            isSimulating={isSimulating}
            onStart={handleStartSimulation}
            onAbort={handleAbortSimulation}
            onRunDemo={runRealisticDemo}
            isBackendConnected={backendHealth?.ok}
          />

          <div className="workspace-right-panel">
            <div className="workspace-tabs-bar" role="tablist">
              <button
                type="button"
                role="tab"
                aria-selected={activeTab === 'operations'}
                className={`ws-tab-btn ${activeTab === 'operations' ? 'active' : ''}`}
                onClick={() => setActiveTab('operations')}
              >
                <Terminal size={16} />
                <span>Journal Temps Réel & Inspecteur d’État</span>
              </button>

              <button
                type="button"
                role="tab"
                aria-selected={activeTab === 'decree'}
                className={`ws-tab-btn ${activeTab === 'decree' ? 'active' : ''}`}
                onClick={() => setActiveTab('decree')}
              >
                <FileCheck size={16} />
                <span>Décret Exécutif Officiel</span>
                {graphState.orchestrator_decision?.executive_order_id && (
                  <span className="tab-dot-ready" />
                )}
              </button>

              <button
                type="button"
                role="tab"
                aria-selected={activeTab === 'catalogs'}
                className={`ws-tab-btn ${activeTab === 'catalogs' ? 'active' : ''}`}
                onClick={() => setActiveTab('catalogs')}
              >
                <BookOpen size={16} />
                <span>Catalogues & Guardrails d’État</span>
              </button>
            </div>

            <div className="workspace-tab-content">
              {activeTab === 'operations' && (
                <div className="operations-split-grid">
                  <LiveStreamLogs
                    logs={logs}
                    onClearLogs={() => setLogs([])}
                    isSimulating={isSimulating}
                  />
                  <NodeStateInspector
                    selectedNodeId={selectedNodeId}
                    graphState={graphState}
                  />
                </div>
              )}

              {activeTab === 'decree' && (
                <ExecutiveDecreeView decree={graphState.orchestrator_decision} />
              )}

              {activeTab === 'catalogs' && <CatalogsView catalogs={catalogs} />}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
