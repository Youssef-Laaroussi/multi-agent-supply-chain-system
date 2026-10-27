import { useState, useRef, useEffect } from 'react';
import { 
  TrendingUp, 
  Package, 
  ShieldAlert, 
  ShoppingCart, 
  Scale, 
  Truck, 
  Network, 
  Activity, 
  User, 
  Settings, 
  Hexagon, 
  Play, 
  Loader2, 
  FileText,
  Send,
  Sparkles,
  RotateCcw
} from 'lucide-react';

export default function App() {
  const [sku, setSku] = useState('SKU-MED-901');
  const [stock, setStock] = useState(750);
  const [prompt, setPrompt] = useState('Urgent: Evaluate supply chain resilience for current inventory.');
  
  const [isSimulating, setIsSimulating] = useState(false);
  const [chatHistory, setChatHistory] = useState([
    { 
      role: 'system', 
      content: 'Bienvenue sur la Tour de Contrôle Multi-Agents. Tapez une instruction ci-dessous ou cliquez sur une suggestion rapide pour lancer la simulation.', 
      id: 'init' 
    }
  ]);
  const [activeAgent, setActiveAgent] = useState(null);
  const [doneAgents, setDoneAgents] = useState([]);
  const [decision, setDecision] = useState(null);
  const chatEndRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatHistory, decision]);

  const appendChat = (role, content, agentName = null) => {
    setChatHistory(prev => [...prev, { role, content, agentName, id: Math.random().toString() }]);
  };

  const clearChat = () => {
    setChatHistory([
      { 
        role: 'system', 
        content: 'Session réinitialisée. Prêt pour une nouvelle analyse.', 
        id: Math.random().toString() 
      }
    ]);
    setActiveAgent(null);
    setDoneAgents([]);
    setDecision(null);
  };

  const startSimulation = async (customPrompt = null) => {
    const textToSend = customPrompt !== null ? customPrompt : prompt;
    if (!sku || !stock || !textToSend) return;

    setIsSimulating(true);
    appendChat('user', `Cible: ${sku} | Stock: ${stock} unités\nInstruction: ${textToSend}`);
    appendChat('system', `Initialisation de la simulation multi-agents pour ${sku}...`);
    setDoneAgents([]);
    setActiveAgent(null);
    setDecision(null);

    try {
      const response = await fetch('http://localhost:8000/api/simulate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sku, starting_stock: parseInt(stock), prompt: textToSend })
      });

      if (!response.ok) throw new Error('Échec de la connexion au serveur API.');

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let buffer = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n\n');
        buffer = lines.pop(); 
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.replace('data: ', ''));
              handleStreamEvent(data);
            } catch (e) {}
          }
        }
      }
    } catch (error) {
      appendChat('system', `Erreur: ${error.message}`);
    } finally {
      setIsSimulating(false);
    }
  };

  const handleStreamEvent = (data) => {
    if (data.node === 'END') {
      appendChat('system', data.message);
      return;
    }
    
    setActiveAgent(prev => {
      if (prev && prev !== data.node) {
        setDoneAgents(d => [...new Set([...d, prev])]);
      }
      return data.node;
    });

    const cleanName = data.node.replace('_', ' ').toUpperCase();
    
    if (data.message) {
       appendChat(data.node === 'orchestrator_agent' ? 'orchestrator' : 'agent', data.message, cleanName);
    } else {
       appendChat('system', `[${cleanName}] analyse les données...`);
    }
    
    if (data.node === 'orchestrator_agent' && data.state_update?.orchestrator_decision) {
      setDecision(data.state_update.orchestrator_decision);
    }
  };

  const agents = [
    { id: 'demand_agent', icon: <TrendingUp size={18} />, name: 'Demand Forecaster' },
    { id: 'inventory_agent', icon: <Package size={18} />, name: 'Inventory Optimizer' },
    { id: 'risk_agent', icon: <ShieldAlert size={18} />, name: 'Risk Radar' },
    { id: 'procurement_agent', icon: <ShoppingCart size={18} />, name: 'Procurement' },
    { id: 'compliance_guardrail', icon: <Scale size={18} />, name: 'Compliance' },
    { id: 'logistics_agent', icon: <Truck size={18} />, name: 'Logistics' },
    { id: 'orchestrator_agent', icon: <Network size={18} />, name: 'Orchestrator', special: true },
  ];

  const quickPrompts = [
    { label: "🚢 Risque Transport Suez", text: "Alerte: Perturbation majeure sur le transit maritime. Évaluer les routes alternatives et le surcoût logistique." },
    { label: "📦 Rupture Stock Critique", text: "Urgence: Risque d'épuisement des stocks sous 10 jours. Activer réapprovisionnement prioritaire." },
    { label: "⚖️ Audit Conformité UE", text: "Audit réglementaire: Valider l'éligibilité des fournisseurs alternatifs selon les normes ISO/REACH." },
    { label: "💰 Optimisation Coûts", text: "Analyser le meilleur arbitrage coût / délai de livraison parmi les fournisseurs disponibles." }
  ];

  const formatMoney = (val) => {
    try {
      return new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR' }).format(val);
    } catch(e) {
      return val + " EUR";
    }
  };

  return (
    <div className="app-layout">
      {/* TOP NAVIGATION / METRICS */}
      <nav className="top-nav">
        <div className="nav-brand">
          <div className="brand-icon-container">
            <Hexagon className="brand-icon" size={28} />
          </div>
          <h1><span className="brand-highlight">Sovereign</span> MAS Control</h1>
        </div>
        <div className="nav-metrics">
          <div className="metric-pill">
            <span className="status-dot"></span>
            <span className="m-val">Système Opérationnel</span>
          </div>
          <div className="metric">
            <span className="m-label">Agents Réseau</span>
            <span className="m-val text-yellow">{agents.length} Nodes</span>
          </div>
        </div>
      </nav>

      <div className="main-content">
        {/* LEFT SIDEBAR: PARAMÈTRES ET STATUT DES AGENTS */}
        <aside className="control-panel">
          <div className="panel-section glass-panel">
            <h2><Settings size={20} className="section-icon" /> Paramètres Cibles</h2>
            <div className="input-group">
              <label>SKU Produit Cible</label>
              <input type="text" value={sku} onChange={e => setSku(e.target.value)} disabled={isSimulating} />
            </div>
            <div className="input-group">
              <label>Stock Disponible (Unités)</label>
              <input type="number" value={stock} onChange={e => setStock(e.target.value)} disabled={isSimulating} />
            </div>
            <button className={`primary-btn ${isSimulating ? 'simulating' : ''}`} onClick={() => startSimulation()} disabled={isSimulating}>
              {isSimulating ? (
                <><Loader2 size={20} className="spin-icon" /> Délibération...</>
              ) : (
                <><Play size={20} /> Lancer la Délibération</>
              )}
            </button>
          </div>

          <div className="panel-section glass-panel">
            <h2><Activity size={20} className="section-icon" /> Réseau des Agents</h2>
            <div className="agents-list">
              {agents.map(a => {
                const isActive = activeAgent === a.id;
                const isDone = doneAgents.includes(a.id);
                let statusClass = 'pending';
                if (isActive) statusClass = 'active';
                if (isDone) statusClass = 'done';
                
                return (
                  <div key={a.id} className={`agent-item ${statusClass} ${a.special ? 'special' : ''}`}>
                    <div className="agent-icon-wrapper">
                      {a.icon}
                    </div>
                    <span className="agent-name">{a.name}</span>
                    <span className="agent-status-badge">
                      {isActive ? 'En action' : (isDone ? 'Terminé' : 'En attente')}
                    </span>
                  </div>
                )
              })}
            </div>
          </div>
        </aside>

        {/* RIGHT AREA: CHAT INTERACTIF / TERMINAL */}
        <section className="terminal-area">
          <div className="terminal-header">
            <h3><Activity size={18} className="pulse-icon" /> Console de Dialogue & Décision Multi-Agents</h3>
            <div className="header-actions">
              {isSimulating && (
                <span className="live-badge">
                  <span className="live-dot"></span> Agents en réflexion...
                </span>
              )}
              <button className="reset-btn" onClick={clearChat} title="Effacer l'historique">
                <RotateCcw size={16} /> Réinitialiser
              </button>
            </div>
          </div>

          <div className="chat-history">
            {chatHistory.map((msg) => (
              <div key={msg.id} className={`chat-bubble-wrapper ${msg.role}`}>
                <div className="avatar">
                  {msg.role === 'user' ? <User size={20} /> : (msg.role === 'orchestrator' ? <Network size={20} /> : (msg.role === 'system' ? <Settings size={20} /> : <Activity size={20} />))}
                </div>
                <div className="chat-bubble">
                  {msg.agentName && <span className="sender-name">{msg.agentName}</span>}
                  <div className="message-content">{msg.content}</div>
                </div>
              </div>
            ))}

            {decision && (
              <div className="decree-card slide-up-anim">
                <div className="decree-header">
                  <FileText size={24} className="decree-icon" />
                  <h3>Décret Exécutif de la Chaîne d'Approvisionnement</h3>
                </div>
                <div className="decree-grid">
                  <div className="d-item"><span className="label">Verdict</span><span className="value highlight">{decision.verdict}</span></div>
                  <div className="d-item"><span className="label">Fournisseur Retenu</span><span className="value">{decision.authorized_supplier}</span></div>
                  <div className="d-item"><span className="label">Unités à Commander</span><span className="value highlight-blue">{decision.units_ordered}</span></div>
                  <div className="d-item"><span className="label">Budget Alloué</span><span className="value highlight-green">{formatMoney(decision.total_commitment_eur)}</span></div>
                  <div className="d-item"><span className="label">Transporteur</span><span className="value">{decision.carrier_assigned}</span></div>
                  <div className="d-item"><span className="label">Délai Estimé</span><span className="value">{decision.estimated_arrival_days} Jours</span></div>
                </div>
              </div>
            )}
            <div ref={chatEndRef} />
          </div>

          {/* BARRE D'INTERACTION DU CHAT (PROMPT INPUT & QUICK CHIPS) */}
          <div className="chat-input-container">
            <div className="quick-suggestions">
              <span className="suggestions-title"><Sparkles size={14} /> Suggestions :</span>
              {quickPrompts.map((qp, idx) => (
                <button 
                  key={idx} 
                  className="suggestion-pill"
                  onClick={() => {
                    setPrompt(qp.text);
                    startSimulation(qp.text);
                  }}
                  disabled={isSimulating}
                >
                  {qp.label}
                </button>
              ))}
            </div>

            <form 
              className="chat-input-form" 
              onSubmit={(e) => { 
                e.preventDefault(); 
                if (prompt.trim()) startSimulation(); 
              }}
            >
              <input
                type="text"
                className="chat-input-field"
                placeholder="Écrivez votre commande aux agents ici... (ex: Analyser les risques de rupture) puis Entrée"
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                disabled={isSimulating}
              />
              <button 
                type="submit" 
                className="chat-send-btn" 
                disabled={isSimulating || !prompt.trim()}
                title="Envoyer la commande (Entrée)"
              >
                {isSimulating ? <Loader2 size={18} className="spin-icon" /> : <Send size={18} />}
              </button>
            </form>
          </div>
        </section>
      </div>
    </div>
  );
}
