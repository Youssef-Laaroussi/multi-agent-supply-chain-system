import React from 'react';
import { Package, ShieldCheck, DollarSign, Truck, AlertTriangle } from 'lucide-react';

export default function MetricRibbon({
  selectedSku = 'SKU-MED-901',
  currentStock = 750,
  reserveFloor = 500,
  spendingCeiling = 100000,
  graphState = {}
}) {
  const stockNumber = Number(currentStock) || 0;
  const stockDelta = stockNumber - reserveFloor;
  const isBreached = stockNumber < reserveFloor;
  const percentageOfFloor = Math.min(100, Math.round((stockNumber / 1000) * 100));

  // Compliance status
  const compliance = graphState.compliance_review;
  const isVetoed = compliance?.status === 'REJECTED_VETO';
  const isApproved = compliance?.status === 'APPROVED';

  // Decision & expenditure
  const decision = graphState.orchestrator_decision;
  const committedAmount = decision?.total_commitment_eur;
  const hasCommitment = typeof committedAmount === 'number' && committedAmount > 0;
  const budgetRatio = hasCommitment ? Math.min(100, (committedAmount / spendingCeiling) * 100) : 0;

  // Logistics
  const logistics = graphState.logistics_plan;
  const hasLogistics = Boolean(logistics && logistics.carrier_name);

  const formatEUR = (val) => {
    return new Intl.NumberFormat('fr-FR', {
      style: 'currency',
      currency: 'EUR',
      maximumFractionDigits: 0
    }).format(val);
  };

  return (
    <section className="kpi-grid" aria-label="Tableau de bord stratégique">
      {/* KPI 1: Strategic Reserve Floor */}
      <div className={`kpi-card ${isBreached ? 'kpi-danger' : 'kpi-emerald'}`}>
        <div className="kpi-card-header">
          <span className="kpi-label">Stock & Réserve Stratégique</span>
          <div className="kpi-icon-squircle emerald">
            <Package size={17} />
          </div>
        </div>

        <div className="kpi-metric-row">
          <span className="kpi-number">{stockNumber.toLocaleString('fr-FR')}</span>
          <span className="kpi-unit">unités</span>
        </div>

        <div className="kpi-gauge-track">
          <div
            className={`kpi-gauge-bar ${isBreached ? 'bar-danger' : 'bar-emerald'}`}
            style={{ width: `${percentageOfFloor}%` }}
          ></div>
        </div>

        <div className="kpi-card-footer">
          <span className="kpi-subtext">Plancher d'État : <strong>{reserveFloor}u</strong></span>
          <span className={`status-pill ${isBreached ? 'pill-danger' : 'pill-emerald'}`}>
            <span className="glow-dot"></span>
            <span>{isBreached ? `Rupture (${stockDelta}u)` : `Sécurisé (+${stockDelta}u)`}</span>
          </span>
        </div>
      </div>

      {/* KPI 2: Governance & Statutory Veto */}
      <div className={`kpi-card ${isVetoed ? 'kpi-danger' : (isApproved ? 'kpi-emerald' : 'kpi-indigo')}`}>
        <div className="kpi-card-header">
          <span className="kpi-label">Gouvernance & Veto État</span>
          <div className={`kpi-icon-squircle ${isVetoed ? 'danger' : (isApproved ? 'emerald' : 'indigo')}`}>
            <ShieldCheck size={17} />
          </div>
        </div>

        <div className="kpi-metric-row">
          <span className="kpi-status-headline">
            {isVetoed ? 'VETO STATUTAIRE' : (isApproved ? 'OFFRE VALIDÉE' : 'SURVEILLANCE ACTIVE')}
          </span>
        </div>

        <div className="kpi-gauge-track">
          <div
            className={`kpi-gauge-bar ${isVetoed ? 'bar-danger' : (isApproved ? 'bar-emerald' : 'bar-indigo')}`}
            style={{ width: isVetoed ? '100%' : (isApproved ? '100%' : '50%') }}
          ></div>
        </div>

        <div className="kpi-card-footer">
          <span className="kpi-subtext">Code Marchés Publics Art. L2122-1</span>
          <span className={`status-pill ${isVetoed ? 'pill-danger' : (isApproved ? 'pill-emerald' : 'pill-indigo')}`}>
            <span className="glow-dot"></span>
            <span>{isVetoed ? 'Embargo Détecté' : (isApproved ? 'Agrément Défense' : 'Prêt à Délibérer')}</span>
          </span>
        </div>
      </div>

      {/* KPI 3: Committed Budget */}
      <div className={`kpi-card ${hasCommitment ? 'kpi-indigo' : 'kpi-neutral'}`}>
        <div className="kpi-card-header">
          <span className="kpi-label">Plafond Budgétaire Express</span>
          <div className="kpi-icon-squircle indigo">
            <DollarSign size={17} />
          </div>
        </div>

        <div className="kpi-metric-row">
          <span className="kpi-number">{hasCommitment ? formatEUR(committedAmount) : '0 €'}</span>
          <span className="kpi-unit">engagé</span>
        </div>

        <div className="kpi-gauge-track">
          <div
            className="kpi-gauge-bar bar-indigo"
            style={{ width: `${budgetRatio}%` }}
          ></div>
        </div>

        <div className="kpi-card-footer">
          <span className="kpi-subtext">Plafond : {formatEUR(spendingCeiling)}</span>
          <span className={`status-pill ${hasCommitment ? 'pill-indigo' : 'pill-slate'}`}>
            <span className="glow-dot"></span>
            <span>{hasCommitment ? `${budgetRatio.toFixed(1)}% alloué` : 'En attente d’engagement'}</span>
          </span>
        </div>
      </div>

      {/* KPI 4: Logistics & Fleet */}
      <div className={`kpi-card ${hasLogistics ? 'kpi-amber' : 'kpi-neutral'}`}>
        <div className="kpi-card-header">
          <span className="kpi-label">Acheminement & Fret Sécurisé</span>
          <div className="kpi-icon-squircle amber">
            <Truck size={17} />
          </div>
        </div>

        <div className="kpi-metric-row">
          <span className="kpi-subheadline">
            {hasLogistics ? logistics.carrier_name : 'Flotte en attente'}
          </span>
        </div>

        <div className="kpi-gauge-track">
          <div
            className="kpi-gauge-bar bar-amber"
            style={{ width: hasLogistics ? '100%' : '30%' }}
          ></div>
        </div>

        <div className="kpi-card-footer">
          <span className="kpi-subtext">
            {hasLogistics ? `Délai : ${logistics.transit_days}j ouvré(s)` : 'Transit standard'}
          </span>
          <span className={`status-pill ${hasLogistics ? 'pill-amber' : 'pill-slate'}`}>
            <span className="glow-dot"></span>
            <span>{hasLogistics ? (logistics.security_certified ? 'Escorte Militaire' : 'Certifié') : 'Flotte Prête'}</span>
          </span>
        </div>
      </div>
    </section>
  );
}
