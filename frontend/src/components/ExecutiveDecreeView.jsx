import React, { useState } from 'react';
import {
  FileCheck,
  CheckCircle2,
  XCircle,
  Copy,
  Check,
  Download,
  Scale
} from 'lucide-react';

export default function ExecutiveDecreeView({ decree }) {
  const [copied, setCopied] = useState(false);

  if (!decree || !decree.executive_order_id) {
    return (
      <div className="decree-empty-state">
        <FileCheck size={28} className="empty-icon" aria-hidden="true" />
        <h3 className="empty-title">Aucun Décret Exécutif Signé</h3>
        <p className="empty-desc">
          Le décret statutaire est rédigé et scellé par le <strong>Master Orchestrator</strong> à l’étape 7 du pipeline LangGraph.
        </p>
      </div>
    );
  }

  const isApproved = decree.verdict === 'AUTHORIZED_AND_DISPATCHED';

  const copyDecree = () => {
    navigator.clipboard.writeText(JSON.stringify(decree, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const downloadJson = () => {
    const dataStr = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(decree, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute('href', dataStr);
    downloadAnchor.setAttribute('download', `${decree.executive_order_id || 'decree'}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  const formatEUR = (val) => {
    if (typeof val !== 'number') return '—';
    return new Intl.NumberFormat('fr-FR', {
      style: 'currency',
      currency: 'EUR',
      maximumFractionDigits: 2,
    }).format(val);
  };

  return (
    <article className={`decree-document ${isApproved ? 'doc-approved' : 'doc-vetoed'}`} aria-label="Décret Exécutif Officiel">
      {/* Official Header */}
      <div className="decree-head">
        <div className="head-meta">
          <span className="order-id-label">DÉCRET STATUTAIRE N°</span>
          <h3 className="order-id">{decree.executive_order_id}</h3>
          <span className="sku-tag">
            {decree.sku} {decree.sku_description ? `— ${decree.sku_description}` : ''}
          </span>
        </div>

        <div className="head-verdict">
          <div className={`verdict-stamp ${isApproved ? 'stamp-approved' : 'stamp-vetoed'}`}>
            {isApproved ? (
              <>
                <CheckCircle2 size={16} aria-hidden="true" />
                <span>ENGAGEMENT AUTORISÉ</span>
              </>
            ) : (
              <>
                <XCircle size={16} aria-hidden="true" />
                <span>OPÉRATION BLOQUÉE (VETO)</span>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Key Decisional Matrix */}
      <div className="decree-grid">
        <div className="decree-cell">
          <span className="cell-label">Fournisseur Habilité</span>
          <strong className="cell-val">{decree.authorized_supplier || 'Aucun'}</strong>
          <span className="cell-sub">{decree.supplier_country || 'Origine non spécifiée'}</span>
        </div>

        <div className="decree-cell">
          <span className="cell-label">Volume de Commande</span>
          <strong className="cell-val">
            {typeof decree.units_ordered === 'number'
              ? `${decree.units_ordered.toLocaleString('fr-FR')} unités`
              : '—'}
          </strong>
          <span className="cell-sub">
            {decree.strategic_reserve_secured ? '✓ Plancher 500u garanti' : '⚠️ Risque plancher'}
          </span>
        </div>

        <div className="decree-cell">
          <span className="cell-label">Acheminement & Flotte</span>
          <strong className="cell-val">{decree.carrier_assigned || 'Non assigné'}</strong>
          <span className="cell-sub">
            Délai estimé : {decree.estimated_arrival_days ? `${decree.estimated_arrival_days} jours` : '—'}
          </span>
        </div>

        <div className="decree-cell highlight">
          <span className="cell-label">Dépense Publique Totale</span>
          <strong className="cell-val financial">
            {formatEUR(decree.total_commitment_eur)}
          </strong>
          <span className="cell-sub">
            Matière : {formatEUR(decree.material_cost_eur)} | Fret : {formatEUR(decree.freight_cost_eur)}
          </span>
        </div>
      </div>

      {/* Executive Trade-off Rationale */}
      {decree.trade_off_resolution && (
        <div className="decree-rationale-box">
          <h4 className="rationale-title">Motifs et Justification de l'Arbitrage Régalien</h4>
          <p className="rationale-text">{decree.trade_off_resolution}</p>
        </div>
      )}

      {/* Legal Basis and Export Controls */}
      <div className="decree-foot">
        <div className="legal-basis">
          <Scale size={13} aria-hidden="true" />
          <span>Fondement juridique : {decree.legal_basis || 'Code de la commande publique Art. L2122-1'}</span>
        </div>

        <div className="foot-actions">
          <button
            type="button"
            className="secondary-btn-sm"
            onClick={copyDecree}
            title="Copier le JSON du décret"
          >
            {copied ? <Check size={12} /> : <Copy size={12} />}
            <span>{copied ? 'Copié' : 'Copier JSON'}</span>
          </button>

          <button
            type="button"
            className="secondary-btn-sm"
            onClick={downloadJson}
            title="Télécharger l'acte au format JSON"
          >
            <Download size={12} />
            <span>Télécharger (.json)</span>
          </button>
        </div>
      </div>
    </article>
  );
}
