document.addEventListener('DOMContentLoaded', () => {
  const startBtn = document.getElementById('start-btn');
  const skuInput = document.getElementById('sku-input');
  const stockInput = document.getElementById('stock-input');
  const terminalContent = document.getElementById('terminal-content');
  const connectionStatus = document.getElementById('connection-status');
  const decreePanel = document.getElementById('decree-panel');
  const decreeContent = document.getElementById('decree-content');
  
  let eventSource = null;

  function appendLog(message, type = 'agent-msg', agentName = null) {
    const logDiv = document.createElement('div');
    logDiv.className = `log ${type}`;
    
    if (agentName) {
      const nameSpan = document.createElement('span');
      nameSpan.className = 'agent-name';
      nameSpan.textContent = `[${agentName}]`;
      logDiv.appendChild(nameSpan);
    }
    
    const textNode = document.createTextNode(message);
    logDiv.appendChild(textNode);
    
    terminalContent.appendChild(logDiv);
    terminalContent.scrollTop = terminalContent.scrollHeight;
  }

  function resetUI() {
    terminalContent.innerHTML = '';
    decreePanel.classList.add('hidden');
    decreeContent.innerHTML = '';
    
    document.querySelectorAll('.agent-card').forEach(card => {
      card.classList.remove('active', 'done');
    });
  }

  function renderDecree(decision) {
    if (!decision || Object.keys(decision).length === 0) return;
    
    decreePanel.classList.remove('hidden');
    
    const formatMoney = (val) => new Intl.NumberFormat('en-EU', { style: 'currency', currency: 'EUR' }).format(val);
    
    const items = [
      { label: "Verdict Status", value: decision.verdict },
      { label: "Authorized Vendor", value: `${decision.authorized_supplier} (${decision.supplier_country})` },
      { label: "Replenishment", value: `${decision.units_ordered} units` },
      { label: "Total Budget", value: formatMoney(decision.total_commitment_eur) },
      { label: "Assigned Carrier", value: decision.carrier_assigned },
      { label: "Arrival To Dock", value: `${decision.estimated_arrival_days} days` }
    ];

    const grid = document.createElement('div');
    grid.className = 'decree-grid';
    
    items.forEach(item => {
      const div = document.createElement('div');
      div.className = 'decree-item';
      div.innerHTML = `<span class="label">${item.label}</span><span class="value">${item.value}</span>`;
      grid.appendChild(div);
    });
    
    decreeContent.appendChild(grid);
    
    // Smooth scroll to decree
    decreePanel.scrollIntoView({ behavior: 'smooth' });
  }

  startBtn.addEventListener('click', async () => {
    if (startBtn.disabled) return;
    
    const sku = skuInput.value;
    const stock = parseInt(stockInput.value);
    
    if (!sku || isNaN(stock)) {
      alert("Please provide valid SKU and Stock values.");
      return;
    }

    startBtn.disabled = true;
    startBtn.textContent = 'SIMULATING...';
    startBtn.classList.remove('pulse-glow');
    
    resetUI();
    appendLog(`Initializing crisis simulation for ${sku}...`, 'system');

    try {
      // 1. Send POST to trigger backend
      const response = await fetch('http://localhost:8000/api/simulate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sku: sku, starting_stock: stock })
      });

      if (!response.ok) {
        throw new Error('Failed to start simulation on server.');
      }

      // 2. Connect to SSE Stream (the FastAPI endpoint actually streams directly on the POST request response in our implementation)
      // Wait, standard EventSource only supports GET. Since we implemented POST in FastAPI that returns StreamingResponse, we need to read the stream manually using fetch API ReadableStream.
      
      connectionStatus.classList.replace('disconnected', 'connected');
      
      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      
      let buffer = '';
      
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        
        buffer += decoder.decode(value, { stream: true });
        
        const lines = buffer.split('\n\n');
        buffer = lines.pop(); // Keep the last incomplete chunk in the buffer
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const dataStr = line.replace('data: ', '');
            try {
              const data = JSON.parse(dataStr);
              handleStreamEvent(data);
            } catch (e) {
              console.error("JSON Parse error:", e);
            }
          }
        }
      }
      
    } catch (error) {
      appendLog(`Error: ${error.message}`, 'system');
      connectionStatus.classList.replace('connected', 'disconnected');
    } finally {
      startBtn.disabled = false;
      startBtn.textContent = 'INITIALIZE SIMULATION';
      startBtn.classList.add('pulse-glow');
      connectionStatus.classList.replace('connected', 'disconnected');
    }
  });
  
  let currentActiveAgentId = null;

  function handleStreamEvent(data) {
    if (data.node === 'END') {
      appendLog(data.message, 'system');
      return;
    }
    
    // Deactivate previous
    if (currentActiveAgentId) {
      const prevCard = document.getElementById(currentActiveAgentId);
      if (prevCard) {
        prevCard.classList.remove('active');
        prevCard.classList.add('done');
      }
    }
    
    // Activate new
    const agentId = `agent-${data.node}`;
    const card = document.getElementById(agentId);
    if (card) {
      card.classList.add('active');
      currentActiveAgentId = agentId;
    }
    
    // Log message
    const msgType = data.node === 'orchestrator_agent' ? 'orchestrator' : 'agent-msg';
    const cleanName = data.node.replace('_', ' ').toUpperCase();
    
    if (data.message) {
       appendLog(data.message, msgType, cleanName);
    } else {
       appendLog("Processing data...", 'system', cleanName);
    }
    
    // Check if it's the orchestrator and we have a decision
    if (data.node === 'orchestrator_agent' && data.state_update && data.state_update.orchestrator_decision) {
      renderDecree(data.state_update.orchestrator_decision);
    }
  }
});
