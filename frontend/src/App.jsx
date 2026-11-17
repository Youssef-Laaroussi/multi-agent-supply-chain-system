import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  Terminal,
  FileCheck2,
  BookOpen,
  RefreshCw,
  RotateCcw,
  Layers,
  Zap,
  Shield,
  BarChart3,
  ChevronDown,
  ArrowRight,
  Play
} from 'lucide-react';

import HeroGlobeIllustration from './components/HeroGlobeIllustration';
import AuthView from './components/AuthView';
import ConnectionBanner from './components/ConnectionBanner';
import MetricRibbon from './components/MetricRibbon';
import PipelineGraph from './components/PipelineGraph';
import SimulationConsole from './components/SimulationConsole';
import NodeStateInspector from './components/NodeStateInspector';
import LiveStreamLogs from './components/LiveStreamLogs';
import ExecutiveDecreeView from './components/ExecutiveDecreeView';
import CatalogsView from './components/CatalogsView';
import ArchitectureModal from './components/ArchitectureModal';
import {
  checkBackendHealth,
  fetchSystemCatalogs,
  streamSimulation,
  getStoredSession,
  logoutUser
} from './api/client';

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
      description: 'Partenaire souverain certifié Défense avec dédouanement prioritaire et chaîne d’approvisionnement sécurisée.'
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
      description: 'Fournisseur allié européen certifié, adapté pour les réapprovisionnements planifiés hors crise immédiate.'
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
      description: 'Coût unitaire bas mais juridiction sous embargo strict. Rejeté automatiquement par le Sovereign Guardrail.'
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

const resolvePageFromPath = (pathname) => {
  const clean = (pathname || '/').replace(/\/+$/, '') || '/';
  if (clean === '/login') return 'login';
  if (clean === '/signup') return 'signup';
  if (clean === '/platform') return 'platform';
  return 'home';
};

export default function App() {
  const [activePage, setActivePage] = useState(() =>
    resolvePageFromPath(window.location.pathname)
  ); // 'home' | 'login' | 'signup' | 'platform'
  const [currentUser, setCurrentUser] = useState(() => getStoredSession()?.user || null);
  const [activeTab, setActiveTab] = useState('operations'); // 'operations' | 'decree' | 'catalogs'
  const [isArchModalOpen, setIsArchModalOpen] = useState(false);

  const navigate = useCallback((path) => {
    if (window.location.pathname !== path) {
      window.history.pushState({}, '', path);
    }
    setActivePage(resolvePageFromPath(path));
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, []);

  useEffect(() => {
    const onPopState = () => {
      setActivePage(resolvePageFromPath(window.location.pathname));
    };
    window.addEventListener('popstate', onPopState);
    return () => window.removeEventListener('popstate', onPopState);
  }, []);

  const [backendHealth, setBackendHealth] = useState({ ok: false });
  const [isCheckingHealth, setIsCheckingHealth] = useState(false);
  const [catalogs, setCatalogs] = useState(FALLBACK_CATALOGS);

  const [currentSku, setCurrentSku] = useState('SKU-MED-901');
  const [stock, setStock] = useState(750);
  const [prompt, setPrompt] = useState(
    'Alerte Pandémique : Pic de consommation hospitalière de +80% détecté. Sécuriser le plancher de 500 unités via un canal certifié d’État.'
  );

  const [isSimulating, setIsSimulating] = useState(false);
  const [activeNodeId, setActiveNodeId] = useState(null);
  const [completedNodeIds, setCompletedNodeIds] = useState([]);
  const [selectedNodeId, setSelectedNodeId] = useState('demand_agent');
  const [graphState, setGraphState] = useState({});
  const [logs, setLogs] = useState([]);

  const abortControllerRef = useRef(null);

  // Enforce clean light emerald aesthetic
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', 'aura-emerald');
  }, []);

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
    navigate('/platform');
    setActiveTab('operations');
    setIsSimulating(true);
    setActiveNodeId(null);
    setCompletedNodeIds([]);
    setGraphState({});
    setLogs([]);

    const stockNum = Number(stock) || 750;
    const reserveFloor = catalogs.reserve_floor || 500;
    const reorderQty = Math.max(400, reserveFloor + 1732 + 51 - stockNum);

    appendLog('OPÉRATEUR', `Directive opérationnelle initiée sur ${currentSku} (Stock physique: ${stockNum}u | Plancher inaliénable: ${reserveFloor}u).`, 'user');

    const demoSteps = [
      {
        node: 'demand_agent',
        sound: 'step',
        log: `📈 DEMAND_AGENT: Exécution @tool calculate_demand_forecast_tool. Détection choc hospitalier +80%. Demande brute 7 jours : 1 732 unités.`,
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
        sound: 'step',
        log: `📦 INVENTORY_AGENT: Calcul @tool calculate_inventory_metrics_tool. Stock actuel ${stockNum}u vs Plancher régalien ${reserveFloor}u. Rupture projetée sous 72h : OUI. Reorder requis : ${reorderQty} unités.`,
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
        sound: 'step',
        log: `🚨 RISK_AGENT: Interrogation @tool query_risk_radar_tool. Menace HIGH sur détroit maritime Mer Rouge (+5 jours de transit induit sur l'offre alliée SUP-GLOBAL-02).`,
        update: {
          risk_assessment: {
            sku: currentSku,
            risk_level: 'HIGH',
            active_alerts_count: 2,
            disruptions: [
              { code: 'MARITIME-SUEZ-01', severity: 'HIGH', induced_delay_days: 5, impacted_supplier_id: 'SUP-GLOBAL-02' }
            ],
            recommendation: 'Privilégier impérativement un opérateur souverain domestique et un fret aérien certifié.'
          }
        }
      },
      {
        node: 'procurement_agent',
        sound: 'step',
        log: `🤝 PROCUREMENT_AGENT: Évaluation 3 devis via @tool evaluate_supplier_proposals_tool. Soumission moins-disante financière initiale : DarkBay Grey-Market (EMBARGO_LAND). Transmise au contrôle régalien.`,
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
        sound: 'veto',
        log: `🏛️ COMPLIANCE_GUARDRAIL (Command API): VETO STATUTAIRE exercé contre 'DarkBay Grey-Market' (Juridiction sous embargo). Re-routage forcé vers 'Hexagon National Strategic Industries' (DOMESTIC, Certifié Défense).`,
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
              'VETO STATUTAIRE : Juridiction EMBARGO_LAND bloquée par embargo_sanction_guardrail.',
              'ALTERNATIVE VALIDÉE : Hexagon National Strategic Industries (DOMESTIC, Habilité Secret-Défense).',
              'CONFORMITÉ BUDGET : Plafond d’urgence de 250 000 € (Art. L2122-1) strictement respecté.',
              'RESERVE FLOOR : Plancher stratégique inaliénable de 500 unités sécurisé à 100%.'
            ]
          }
        }
      },
      {
        node: 'logistics_agent',
        sound: 'step',
        log: `🚚 LOGISTICS_AGENT: Allocation flotte @tool plan_freight_dispatch_tool : National Sovereign Air Express (Pont Aérien 24h, Escorte Sécurité Défense).`,
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
        sound: 'decree',
        log: `👑 MASTER ORCHESTRATOR: Décret d'Urgence Impérieuse signé sous l'Art. L2122-1. ${reorderQty} unités autorisées pour un engagement public total de ${(reorderQty * 135).toLocaleString('fr-FR')} € TTC.`,
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
      await new Promise((r) => setTimeout(r, 700));
      setGraphState((prev) => ({ ...prev, ...step.update }));
      setCompletedNodeIds((prev) => [...new Set([...prev, step.node])]);
      appendLog(step.node.toUpperCase(), step.log);
    }

    setActiveNodeId(null);
    setIsSimulating(false);
  };

  const handleStartSimulation = async () => {
    if (isSimulating) return;
    navigate('/platform');
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
            appendLog('SYSTÈME', payload.message || 'Délibération LangGraph terminée et checkpointée.', 'system');
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

  const handleSelectAgentFromHero = (agentId) => {
    setSelectedNodeId(agentId);
    navigate('/platform');
    setActiveTab('operations');
  };

  /* Standalone Pages: /login and /signup */
  if (activePage === 'login' || activePage === 'signup') {
    return (
      <div className="aura-app-shell">
        <AuthView
          mode={activePage}
          onNavigate={navigate}
          onSuccess={(user) => {
            setCurrentUser(user);
            navigate('/platform');
          }}
        />
      </div>
    );
  }

  return (
    <div className="aura-app-shell">
      {/* Official AURA SOVEREIGN Navigation Bar */}
      <header className="aura-navbar" role="banner">
        <div className="aura-nav-inner">
          {/* Left: Wave Crest Logo + Brand */}
          <button
            type="button"
            className="aura-brand-btn"
            onClick={() => navigate('/')}
          >
            <svg className="aura-wave-logo" width="38" height="24" viewBox="0 0 42 26" fill="none" aria-hidden="true">
              <path
                d="M2 21 C 10 21, 14 5, 23 5 C 31 5, 34 15, 40 15"
                stroke="url(#auraLogoGrad)"
                strokeWidth="4.2"
                strokeLinecap="round"
              />
              <path
                d="M2 23 C 11 23, 18 11, 27 11 C 33 11, 36 18, 40 18"
                stroke="#0D5C52"
                strokeOpacity="0.28"
                strokeWidth="2.8"
                strokeLinecap="round"
              />
              <defs>
                <linearGradient id="auraLogoGrad" x1="2" y1="21" x2="40" y2="10" gradientUnits="userSpaceOnUse">
                  <stop offset="0%" stopColor="#24B68C" />
                  <stop offset="55%" stopColor="#1A9E7D" />
                  <stop offset="100%" stopColor="#0D5C52" />
                </linearGradient>
              </defs>
            </svg>
            <span className="aura-brand-wordmark">AURA SOVEREIGN</span>
          </button>

          {/* Center: Navigation Links */}
          <nav className="aura-nav-links" aria-label="Navigation principale">
            <button
              type="button"
              className={`aura-nav-link ${activePage === 'home' ? 'is-active' : ''}`}
              onClick={() => navigate('/')}
            >
              <span>Accueil</span>
            </button>

            <button
              type="button"
              className={`aura-nav-link ${activePage === 'platform' && activeTab === 'operations' ? 'is-active' : ''}`}
              onClick={() => {
                navigate('/platform');
                setActiveTab('operations');
              }}
            >
              <span>Plateforme</span>
              <ChevronDown size={14} className="nav-chevron" />
            </button>

            <button
              type="button"
              className={`aura-nav-link ${activePage === 'platform' && activeTab === 'decree' ? 'is-active' : ''}`}
              onClick={() => {
                navigate('/platform');
                setActiveTab('decree');
              }}
            >
              <span>Solutions</span>
              <ChevronDown size={14} className="nav-chevron" />
            </button>

            <button
              type="button"
              className={`aura-nav-link ${activePage === 'platform' && activeTab === 'catalogs' ? 'is-active' : ''}`}
              onClick={() => {
                navigate('/platform');
                setActiveTab('catalogs');
              }}
            >
              <span>Ressources</span>
              <ChevronDown size={14} className="nav-chevron" />
            </button>

            <button
              type="button"
              className="aura-nav-link"
              onClick={() => setIsArchModalOpen(true)}
            >
              <span>À propos</span>
            </button>
          </nav>

          {/* Right: Action Pills */}
          <div className="aura-nav-actions">
            {currentUser ? (
              <div className="aura-user-pill-group">
                <button
                  type="button"
                  className="aura-btn-outline"
                  onClick={() => navigate('/platform')}
                  title={`Connecté en tant que ${currentUser.email}`}
                >
                  <span>{currentUser.name}</span>
                </button>
                <button
                  type="button"
                  className="aura-logout-link"
                  onClick={async () => {
                    await logoutUser();
                    setCurrentUser(null);
                    navigate('/');
                  }}
                >
                  Déconnexion
                </button>
              </div>
            ) : (
              <button
                type="button"
                className="aura-btn-outline"
                onClick={() => navigate('/login')}
              >
                Se connecter
              </button>
            )}
            <button
              type="button"
              className="aura-btn-solid"
              onClick={handleStartSimulation}
            >
              <span>Demander une démo</span>
              <ArrowRight size={15} />
            </button>
          </div>
        </div>
      </header>

      {/* ====================================================================
          VUE 1 : ACCUEIL HERO AURA SOVEREIGN (FIDÈLE À LA MAQUETTE)
         ==================================================================== */}
      {activePage === 'home' && (
        <main className="aura-home-wrapper">
          <section className="aura-hero-section">
            <div className="aura-hero-grid">
              {/* Left Copy Column */}
              <div className="aura-hero-copy">
                <p className="aura-eyebrow">
                  AI-POWERED SUPPLY CHAIN
                </p>

                <h1 className="aura-hero-h1">
                  Predict, optimize &amp;<br className="h1-br" />
                  secure your supply chain<br className="h1-br" />
                  with <span className="text-mint-accent">AI agents.</span>
                </h1>

                <p className="aura-hero-lead">
                  Autonomous agents for demand, inventory, risk, and end-to-end compliance.
                </p>

                <div className="aura-hero-cta-row">
                  <button
                    type="button"
                    className="aura-btn-solid aura-btn-lg"
                    onClick={handleStartSimulation}
                  >
                    <span>Demander une démo</span>
                    <ArrowRight size={16} />
                  </button>

                  <button
                    type="button"
                    className="aura-btn-outline aura-btn-lg"
                    onClick={runRealisticDemo}
                  >
                    <Play size={14} className="play-tri-icon" />
                    <span>Voir la vidéo (2 min)</span>
                  </button>
                </div>
              </div>

            </div>

            {/* Full-bleed right artwork, blended into the page background */}
            <div className="aura-hero-visual" aria-hidden="true">
              <HeroGlobeIllustration />
            </div>
          </section>

          {/* 4-Pillar Feature Strip */}
          <section className="aura-pillars-strip" aria-label="Piliers de la plateforme">
            <div className="aura-pillars-inner">
              <div className="aura-pillar-item">
                <span className="pillar-icon-badge"><Zap size={17} /></span>
                <span className="pillar-label">Décision en temps réel</span>
              </div>
              <div className="pillar-divider" aria-hidden="true" />
              <div className="aura-pillar-item">
                <span className="pillar-icon-badge"><Layers size={17} /></span>
                <span className="pillar-label">Orchestration multi-agents</span>
              </div>
              <div className="pillar-divider" aria-hidden="true" />
              <div className="aura-pillar-item">
                <span className="pillar-icon-badge"><Shield size={17} /></span>
                <span className="pillar-label">Gouvernance &amp; conformité</span>
              </div>
              <div className="pillar-divider" aria-hidden="true" />
              <div className="aura-pillar-item">
                <span className="pillar-icon-badge"><BarChart3 size={17} /></span>
                <span className="pillar-label">Performance opérationnelle</span>
              </div>
            </div>
          </section>
        </main>
      )}

      {/* ====================================================================
          VUE 2 : PLATEFORME CONTROL TOWER LANGGRAPH
         ==================================================================== */}
      {activePage === 'platform' && (
        <main className="command-room-body">
          {/* Platform Operations Sub-header */}
          <div className="platform-subbar">
            <div className="platform-subbar-left">
              <span className="subbar-badge">CONTROL TOWER LANGGRAPH v1.0</span>
              <span className="subbar-desc">
                Orchestration multi-agents en temps réel • Réserves Stratégiques &amp; Conformité État
              </span>
            </div>

            <div className="platform-subbar-right">
              <button
                type="button"
                className="header-ghost-btn"
                onClick={() => setIsArchModalOpen(true)}
              >
                <Layers size={14} />
                <span>Spécifications</span>
              </button>

              <div
                className={`api-connectivity-pill ${backendHealth?.ok ? 'is-connected' : 'is-disconnected'}`}
              >
                <span className="conn-dot" />
                <span className="conn-label">
                  {backendHealth?.ok ? 'API FASTAPI (8000)' : 'DÉMO AUTONOME'}
                </span>
                <button
                  type="button"
                  className="conn-refresh-btn"
                  onClick={refreshBackendStatus}
                  disabled={isCheckingHealth}
                  title="Tester la connexion backend"
                >
                  <RefreshCw size={12} className={isCheckingHealth ? 'spin' : ''} />
                </button>
              </div>

              <button
                type="button"
                className="header-reset-btn"
                onClick={handleResetSession}
                disabled={isSimulating}
              >
                <RotateCcw size={13} />
                <span>Réinitialiser</span>
              </button>
            </div>
          </div>

          {!backendHealth?.ok && (
            <ConnectionBanner
              onRetry={refreshBackendStatus}
              isChecking={isCheckingHealth}
              onRunDemo={runRealisticDemo}
            />
          )}

          {/* Top Strategic Metric Ribbon */}
          <MetricRibbon
            selectedSku={currentSku}
            currentStock={stock}
            reserveFloor={catalogs.reserve_floor || 500}
            spendingCeiling={catalogs.spending_ceiling_eur || 100000}
            graphState={graphState}
          />

          {/* LangGraph 7-Node Execution Pipeline */}
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

          {/* Dual Operational Deck */}
          <div className="operations-split-deck">
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

            <div className="mission-deck-panel">
              <nav className="mission-deck-tabs" role="tablist" aria-label="Sections du poste de commande">
                <button
                  type="button"
                  role="tab"
                  aria-selected={activeTab === 'operations'}
                  className={`mission-tab-btn ${activeTab === 'operations' ? 'active' : ''}`}
                  onClick={() => setActiveTab('operations')}
                >
                  <Terminal size={15} />
                  <span>Journal d&apos;Audit &amp; Inspecteur d&apos;État</span>
                </button>

                <button
                  type="button"
                  role="tab"
                  aria-selected={activeTab === 'decree'}
                  className={`mission-tab-btn ${activeTab === 'decree' ? 'active' : ''}`}
                  onClick={() => setActiveTab('decree')}
                >
                  <FileCheck2 size={15} />
                  <span>Décret Exécutif Officiel</span>
                  {graphState.orchestrator_decision?.executive_order_id && (
                    <span className="decree-ready-pulse" />
                  )}
                </button>

                <button
                  type="button"
                  role="tab"
                  aria-selected={activeTab === 'catalogs'}
                  className={`mission-tab-btn ${activeTab === 'catalogs' ? 'active' : ''}`}
                  onClick={() => setActiveTab('catalogs')}
                >
                  <BookOpen size={15} />
                  <span>Catalogues &amp; Radar Embargo</span>
                </button>
              </nav>

              <div className="mission-deck-content">
                {activeTab === 'operations' && (
                  <div className="tab-operations-grid">
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

                {activeTab === 'catalogs' && (
                  <CatalogsView catalogs={catalogs} />
                )}
              </div>
            </div>
          </div>
        </main>
      )}

      {/* Architecture Specifications Modal */}
      <ArchitectureModal
        isOpen={isArchModalOpen}
        onClose={() => setIsArchModalOpen(false)}
      />
    </div>
  );
}
