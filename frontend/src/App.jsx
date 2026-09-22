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
  FileText
} from 'lucide-react';

export default function App() {
  const [sku, setSku] = useState('SKU-MED-901');
  const [stock, setStock] = useState(750);
  const [prompt, setPrompt] = useState('Urgent: Evaluate supply chain resilience for current inventory.');
  
  const [isSimulating, setIsSimulating] = useState(false);
  const [chatHistory, setChatHistory] = useState([
    { role: 'system', content: 'System ready. Waiting to start simulation...', id: 'init' }
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

  const startSimulation = async () => {
    if (!sku || !stock) return;

    setIsSimulating(true);
    appendChat('user', `Target: ${sku} | Stock: ${stock}\nCommand: ${prompt}`);
    appendChat('system', `Initializing multi-agent simulation...`);
    setDoneAgents([]);
    setActiveAgent(null);
    setDecision(null);

    try {
      const response = await fetch('http://localhost:8000/api/simulate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sku, starting_stock: parseInt(stock), prompt })
      });

      if (!response.ok) throw new Error('Failed to start simulation on server.');

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
      appendChat('system', `Error: ${error.message}`);
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
       appendChat('system', `[${cleanName}] is analyzing data...`);
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
          <h1>Sovereign MAS Control</h1>
        </div>
        <div className="nav-metrics">
          <div className="metric">
            <span className="m-label">System Health</span>
            <span className="m-val text-green">
              <span className="status-dot"></span> Online
            </span>
          </div>
          <div className="metric">
            <span className="m-label">Active Agents</span>
            <span className="m-val text-glow">{agents.length} Nodes</span>
          </div>
        </div>
      </nav>

      <div className="main-content">
        {/* LEFT SIDEBAR: FUNCTIONALITY & CONTROLS */}
        <aside className="control-panel">
          <div className="panel-section glass-panel">
            <h2><Settings size={20} className="section-icon" /> Simulation Parameters</h2>
            <div className="input-group">
              <label>Target SKU</label>
              <input type="text" value={sku} onChange={e => setSku(e.target.value)} disabled={isSimulating} />
            </div>
            <div className="input-group">
              <label>Current Stock Units</label>
              <input type="number" value={stock} onChange={e => setStock(e.target.value)} disabled={isSimulating} />
            </div>
            <div className="input-group">
              <label>Natural Language Command</label>
              <textarea 
                value={prompt} 
                onChange={e => setPrompt(e.target.value)} 
                disabled={isSimulating}
                rows={3}
              />
            </div>
            <button className={`primary-btn ${isSimulating ? 'simulating' : ''}`} onClick={startSimulation} disabled={isSimulating}>
              {isSimulating ? (
                <><Loader2 size={20} className="spin-icon" /> Simulating...</>
              ) : (
                <><Play size={20} /> Execute Mission</>
              )}
            </button>
          </div>

          <div className="panel-section glass-panel">
            <h2><Activity size={20} className="section-icon" /> Agent Network</h2>
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
                      {isActive ? 'Working' : (isDone ? 'Complete' : 'Idle')}
                    </span>
                  </div>
                )
              })}
            </div>
          </div>
        </aside>

        {/* RIGHT AREA: CHAT / TERMINAL */}
        <section className="terminal-area">
          <div className="terminal-header">
            <h3><Activity size={18} className="pulse-icon" /> Live Event Stream</h3>
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
                  <h3>Executive Supply Chain Decree</h3>
                </div>
                <div className="decree-grid">
                  <div className="d-item"><span className="label">Verdict</span><span className="value highlight">{decision.verdict}</span></div>
                  <div className="d-item"><span className="label">Vendor</span><span className="value">{decision.authorized_supplier}</span></div>
                  <div className="d-item"><span className="label">Units Ordered</span><span className="value highlight-blue">{decision.units_ordered}</span></div>
                  <div className="d-item"><span className="label">Total Budget</span><span className="value highlight-green">{formatMoney(decision.total_commitment_eur)}</span></div>
                  <div className="d-item"><span className="label">Carrier</span><span className="value">{decision.carrier_assigned}</span></div>
                  <div className="d-item"><span className="label">ETA</span><span className="value">{decision.estimated_arrival_days} Days</span></div>
                </div>
              </div>
            )}
            <div ref={chatEndRef} />
          </div>
        </section>
      </div>
    </div>
  );
}
