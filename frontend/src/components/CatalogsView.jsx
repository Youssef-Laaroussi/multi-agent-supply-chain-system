import React, { useState } from 'react';
import { Building2, Truck, Scale, CheckCircle, XCircle, ShieldAlert } from 'lucide-react';

export default function CatalogsView({ catalogs = {} }) {
  const [subTab, setSubTab] = useState('suppliers'); // 'suppliers', 'carriers', 'parameters'

  const suppliers = catalogs.suppliers || [];
  const carriers = catalogs.carriers || [];
  const reserveFloor = catalogs.reserve_floor || 500;
  const spendingCeiling = catalogs.spending_ceiling_eur || 100000;
  const emergencyCeiling = catalogs.emergency_ceiling_eur || 250000;
  const sanctionedCountries = catalogs.sanctioned_countries || [];

  const formatEUR = (val) => {
    return new Intl.NumberFormat('fr-FR', {
      style: 'currency',
      currency: 'EUR',
      maximumFractionDigits: 2,
    }).format(val);
  };

  return (
    <section className="catalogs-section" aria-label="Catalogues et paramètres officiels">
      <div className="catalogs-nav" role="tablist" aria-label="Sous-sections des catalogues">
        <button
          type="button"
          role="tab"
          aria-selected={subTab === 'suppliers'}
          className={`catalog-tab-btn ${subTab === 'suppliers' ? 'active' : ''}`}
          onClick={() => setSubTab('suppliers')}
        >
          <Building2 size={15} aria-hidden="true" />
          <span>Fournisseurs Référencés ({suppliers.length})</span>
        </button>

        <button
          type="button"
          role="tab"
          aria-selected={subTab === 'carriers'}
          className={`catalog-tab-btn ${subTab === 'carriers' ? 'active' : ''}`}
          onClick={() => setSubTab('carriers')}
        >
          <Truck size={15} aria-hidden="true" />
          <span>Flottes & Transporteurs ({carriers.length})</span>
        </button>

        <button
          type="button"
          role="tab"
          aria-selected={subTab === 'parameters'}
          className={`catalog-tab-btn ${subTab === 'parameters' ? 'active' : ''}`}
          onClick={() => setSubTab('parameters')}
        >
          <Scale size={15} aria-hidden="true" />
          <span>Seuils Régaliens & Sanctions</span>
        </button>
      </div>

      <div className="catalogs-body">
        {/* TAB 1: SUPPLIERS */}
        {subTab === 'suppliers' && (
          <div className="table-wrapper">
            <table className="enterprise-table" aria-label="Répertoire des fournisseurs">
              <thead>
                <tr>
                  <th scope="col">Code Fournisseur</th>
                  <th scope="col">Entité Commerciale</th>
                  <th scope="col">Pays / Juridiction</th>
                  <th scope="col">Agrément d'État</th>
                  <th scope="col">Délai Nominal</th>
                  <th scope="col">Prix Unitaire</th>
                  <th scope="col">Capacité</th>
                  <th scope="col">Fiabilité</th>
                </tr>
              </thead>
              <tbody>
                {suppliers.length === 0 ? (
                  <tr>
                    <td colSpan={8} className="table-empty">
                      Aucune donnée de catalogue chargée. Connectez le backend API.
                    </td>
                  </tr>
                ) : (
                  suppliers.map((sup) => (
                    <tr key={sup.id} className={!sup.certified_by_state ? 'row-sanctioned' : ''}>
                      <td>
                        <code className="code-tag">{sup.id}</code>
                      </td>
                      <td>
                        <strong>{sup.name}</strong>
                        {sup.description && (
                          <div className="text-secondary-sub">{sup.description}</div>
                        )}
                      </td>
                      <td>
                        <span className={`country-badge ${sup.country === 'EMBARGO_LAND' ? 'badge-embargo' : ''}`}>
                          {sup.country}
                        </span>
                      </td>
                      <td>
                        {sup.certified_by_state ? (
                          <span className="pill-tag tag-success">
                            <CheckCircle size={11} aria-hidden="true" />
                            <span>Habilité</span>
                          </span>
                        ) : (
                          <span className="pill-tag tag-danger">
                            <XCircle size={11} aria-hidden="true" />
                            <span>Interdit (Embargo)</span>
                          </span>
                        )}
                      </td>
                      <td>{sup.lead_time_days} jour(s)</td>
                      <td>
                        <strong>{formatEUR(sup.unit_price_eur)}</strong>
                      </td>
                      <td>{sup.capacity_units ? `${sup.capacity_units.toLocaleString('fr-FR')} u` : '—'}</td>
                      <td>
                        <strong>{Math.round(sup.reliability_score * 100)}%</strong>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        )}

        {/* TAB 2: CARRIERS */}
        {subTab === 'carriers' && (
          <div className="table-wrapper">
            <table className="enterprise-table" aria-label="Flottes et transporteurs">
              <thead>
                <tr>
                  <th scope="col">Code Flotte</th>
                  <th scope="col">Compagnie de Transport</th>
                  <th scope="col">Classe de Vitesse</th>
                  <th scope="col">Délai Transit</th>
                  <th scope="col">Coût / Unité</th>
                  <th scope="col">Agrément Défense</th>
                </tr>
              </thead>
              <tbody>
                {carriers.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="table-empty">
                      Aucun transporteur chargé depuis le backend.
                    </td>
                  </tr>
                ) : (
                  carriers.map((car) => (
                    <tr key={car.id}>
                      <td>
                        <code className="code-tag">{car.id}</code>
                      </td>
                      <td>
                        <strong>{car.name}</strong>
                      </td>
                      <td>
                        <span className="pill-tag tag-neutral">{car.speed_tier}</span>
                      </td>
                      <td>{car.transit_days} jour(s)</td>
                      <td>
                        <strong>{formatEUR(car.cost_per_unit_eur)} / u</strong>
                      </td>
                      <td>
                        {car.certified_security ? (
                          <span className="pill-tag tag-success">
                            <CheckCircle size={11} aria-hidden="true" />
                            <span>Sécurisé Défense</span>
                          </span>
                        ) : (
                          <span className="pill-tag tag-neutral">Standard</span>
                        )}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        )}

        {/* TAB 3: SOVEREIGN PARAMETERS & SANCTIONS */}
        {subTab === 'parameters' && (
          <div className="parameters-grid">
            <div className="param-card">
              <h4 className="param-title">Plancher Légal de Réserve Stratégique</h4>
              <p className="param-desc">
                Seuil physique infranchissable dans les entrepôts d'État. Tout scénario prévoyant une descente en dessous de ce seuil déclenche une alerte de réapprovisionnement impératif.
              </p>
              <div className="param-stat">{reserveFloor.toLocaleString('fr-FR')} unités</div>
            </div>

            <div className="param-card">
              <h4 className="param-title">Plafond Achat Express d'Urgence</h4>
              <p className="param-desc">
                Montant maximum allouable sans appel d'offres européen complet en cas d'urgence impérieuse (Art. L2122-1 du Code de la commande publique).
              </p>
              <div className="param-stat">{formatEUR(spendingCeiling)}</div>
            </div>

            <div className="param-card">
              <h4 className="param-title">Plafond Décret de Crise Exceptionnelle</h4>
              <p className="param-desc">
                Plafond absolu sous arrêté ministériel de crise civile et militaire.
              </p>
              <div className="param-stat">{formatEUR(emergencyCeiling)}</div>
            </div>

            <div className="param-card full-width">
              <h4 className="param-title">
                <ShieldAlert size={16} className="text-danger inline-icon" aria-hidden="true" />
                <span>Territoires et Entités sous Embargo International</span>
              </h4>
              <p className="param-desc">
                Le <strong>Sovereign Guardrail</strong> applique un véto statutaire automatique et irrévocable à toute offre émanant de ces juridictions :
              </p>
              <div className="sanction-list">
                {sanctionedCountries.map((c) => (
                  <span key={c} className="sanction-tag">
                    {c}
                  </span>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </section>
  );
}
