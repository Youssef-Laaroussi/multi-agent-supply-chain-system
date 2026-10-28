import React, { useState } from 'react';
import { Play, Square, AlertCircle, Sparkles, Layers, Sliders } from 'lucide-react';

const CRISIS_TEMPLATES = [
  {
    tag: '🚨 Surtension Hôpitaux',
    sku: 'SKU-MED-901',
    stock: 620,
    prompt: 'Alerte Pandémique : Pic de consommation hospitalière de +65% détecté. Sécuriser 400 unités en urgence via un canal certifié d’État.'
  },
  {
    tag: '🚢 Crise Mer Rouge / Suez',
    sku: 'SKU-ENG-404',
    stock: 950,
    prompt: 'Alerte Transit Maritime : Déroutement obligatoire par le Cap de Bonne-Espérance (+6 jours). Évaluer les retards et réquisitionner un affrètement aérien prioritaire.'
  },
  {
    tag: '🛡️ Tentative Offre Embargo',
    sku: 'SKU-FOOD-101',
    stock: 480,
    prompt: 'Rupture imminente de ration : Une offre commerciale agressive provient d’une juridiction sous embargo international. Soumettre au Sovereign Guardrail.'
  }
];

export default function SimulationConsole({
  skuList = [],
  currentSku,
  onChangeSku,
  stock,
  onChangeStock,
  prompt,
  onChangePrompt,
  isSimulating,
  onStart,
  onAbort,
  onRunDemo,
  isBackendConnected
}) {
  const [validationError, setValidationError] = useState('');

  const handleStockChange = (e) => {
    const val = e.target.value;
    onChangeStock(val);
    const num = Number(val);
    if (isNaN(num) || num < 0) {
      setValidationError('Le stock doit être un entier positif.');
    } else {
      setValidationError('');
    }
  };

  const handleApplyTemplate = (tmpl) => {
    onChangeSku(tmpl.sku);
    onChangeStock(tmpl.stock);
    onChangePrompt(tmpl.prompt);
    setValidationError('');
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const num = Number(stock);
    if (isNaN(num) || num <= 0) {
      setValidationError('Veuillez spécifier un stock initial supérieur à zéro.');
      return;
    }
    setValidationError('');
    onStart();
  };

  return (
    <aside className="console-card" aria-label="Console de paramétrage de mission">
      <div className="console-card-header">
        <div className="header-title-box">
          <Sliders size={16} className="text-primary-600" />
          <h2 className="console-title">Directive Opérationnelle</h2>
        </div>
        <span className="console-status-indicator">Prêt pour délibération</span>
      </div>

      <form onSubmit={handleSubmit} className="console-form-body">
        {/* SKU Selector */}
        <div className="input-block">
          <label htmlFor="sku-select" className="input-label">
            <span>Article Stratégique Référencé</span>
            <span className="label-badge-pill">Plancher : 500u</span>
          </label>
          <div className="select-wrapper">
            <select
              id="sku-select"
              className="styled-select"
              value={currentSku}
              onChange={(e) => onChangeSku(e.target.value)}
              disabled={isSimulating}
            >
              {skuList.length > 0 ? (
                skuList.map((code) => (
                  <option key={code} value={code}>
                    {code} {code === 'SKU-MED-901' ? '(Filtres ICU & Antidotes)' : (code === 'SKU-ENG-404' ? '(Transformateurs Réseau)' : '(Rations Sécurité Civile)')}
                  </option>
                ))
              ) : (
                <option value="SKU-MED-901">SKU-MED-901 (Filtres Respirateurs ICU)</option>
              )}
            </select>
          </div>
        </div>

        {/* Stock Level Input */}
        <div className="input-block">
          <label htmlFor="stock-input" className="input-label">
            <span>Stock Physique en Entrepôt</span>
            <span className={`label-hint-pill ${Number(stock) < 500 ? 'hint-danger' : 'hint-ok'}`}>
              {Number(stock) < 500 ? '⚠️ Sous le seuil légal' : '✓ Plancher garanti'}
            </span>
          </label>
          <div className="number-input-group">
            <input
              id="stock-input"
              type="number"
              min="1"
              max="15000"
              className={`styled-input ${validationError ? 'input-invalid' : ''}`}
              value={stock}
              onChange={handleStockChange}
              disabled={isSimulating}
              required
            />
            <span className="input-unit-tag">unités</span>
          </div>
          {validationError && (
            <span className="error-hint" role="alert">
              <AlertCircle size={12} />
              <span>{validationError}</span>
            </span>
          )}
        </div>

        {/* Prompt Directive Textarea */}
        <div className="input-block">
          <label htmlFor="prompt-input" className="input-label">
            <span>Ordre de Mission & Contexte de Crise</span>
          </label>
          <textarea
            id="prompt-input"
            rows={3}
            className="styled-textarea"
            value={prompt}
            onChange={(e) => onChangePrompt(e.target.value)}
            disabled={isSimulating}
            placeholder="Ex : Alerte rupture de stock imminente..."
          />
        </div>

        {/* Predefined Crisis Scenarios */}
        <div className="scenario-section">
          <span className="scenario-section-label">
            <Sparkles size={12} />
            <span>Scénarios réels préconfigurés :</span>
          </span>
          <div className="scenario-buttons-stack">
            {CRISIS_TEMPLATES.map((tmpl, idx) => (
              <button
                key={idx}
                type="button"
                className="scenario-chip"
                onClick={() => handleApplyTemplate(tmpl)}
                disabled={isSimulating}
              >
                <span className="scenario-tag">{tmpl.tag}</span>
                <span className="scenario-sub">{tmpl.prompt.slice(0, 68)}...</span>
              </button>
            ))}
          </div>
        </div>

        {/* Form Actions */}
        <div className="console-actions">
          {!isSimulating ? (
            <button
              type="submit"
              className="launch-mission-btn"
              disabled={Boolean(validationError)}
            >
              <Play size={16} />
              <span>Lancer la Délibération des 7 Agents</span>
            </button>
          ) : (
            <button
              type="button"
              className="abort-mission-btn"
              onClick={onAbort}
              title="Interrompre immédiatement la délibération"
            >
              <Square size={14} />
              <span>Interrompre le Flux SSE</span>
            </button>
          )}

          {onRunDemo && !isSimulating && (
            <button
              type="button"
              className="demo-trigger-btn"
              onClick={onRunDemo}
              title="Visualiser immédiatement la simulation multi-agents"
            >
              <Sparkles size={13} />
              <span>Lancer en Mode Démo Immédiat</span>
            </button>
          )}
        </div>
      </form>
    </aside>
  );
}
