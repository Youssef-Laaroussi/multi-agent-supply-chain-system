/**
 * Real API client for Sovereign Supply Chain Multi-Agent System.
 * Connects to the FastAPI backend at http://localhost:8000.
 */

const API_BASE_URL = 'http://localhost:8000';

/**
 * Checks backend health and configuration parameters.
 * @returns {Promise<{ ok: boolean, data?: object, error?: string }>}
 */
export async function checkBackendHealth() {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 3500);

    const response = await fetch(`${API_BASE_URL}/api/health`, {
      method: 'GET',
      headers: { 'Accept': 'application/json' },
      signal: controller.signal,
    });
    clearTimeout(timeoutId);

    if (!response.ok) {
      return { ok: false, error: `Erreur HTTP ${response.status}: ${response.statusText}` };
    }
    const data = await response.json();
    return { ok: true, data };
  } catch (err) {
    return {
      ok: false,
      error: err.name === 'AbortError'
        ? 'Délai d’attente dépassé (timeout 3.5s)'
        : 'Impossible de joindre le serveur API sur http://localhost:8000'
    };
  }
}

/**
 * Fetches verified system catalogs (SKUs, Suppliers, Carriers, Budget parameters).
 * @returns {Promise<{ ok: boolean, data?: object, error?: string }>}
 */
export async function fetchSystemCatalogs() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/catalogs`, {
      method: 'GET',
      headers: { 'Accept': 'application/json' },
    });
    if (!response.ok) {
      return { ok: false, error: `Erreur HTTP ${response.status}` };
    }
    const data = await response.json();
    return { ok: true, data };
  } catch (err) {
    return { ok: false, error: err.message || 'Échec de récupération des catalogues' };
  }
}

/**
 * Streams the LangGraph simulation using real Server-Sent Events (SSE).
 *
 * @param {object} params
 * @param {string} params.sku Target SKU code
 * @param {number} params.startingStock Available stock units
 * @param {string} params.prompt Direct user instruction or crisis prompt
 * @param {AbortSignal} params.signal AbortSignal to cancel in-flight stream
 * @param {function} onEvent Callback for each received SSE message payload
 * @param {function} onError Callback on network/parse error
 * @param {function} onComplete Callback on stream end
 */
export async function streamSimulation(
  { sku, startingStock, prompt, signal },
  { onEvent, onError, onComplete }
) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/simulate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'text/event-stream',
      },
      body: JSON.stringify({
        sku,
        starting_stock: parseInt(startingStock, 10),
        prompt: prompt || '',
      }),
      signal,
    });

    if (!response.ok) {
      throw new Error(`Serveur API a répondu avec le statut ${response.status}: ${response.statusText}`);
    }

    if (!response.body) {
      throw new Error('Le flux de données SSE est vide ou non pris en charge.');
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let buffer = '';

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const parts = buffer.split('\n\n');
      buffer = parts.pop() || '';

      for (const part of parts) {
        const trimmed = part.trim();
        if (!trimmed) continue;

        const lines = trimmed.split('\n');
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const rawJson = line.slice(6).trim();
            if (!rawJson) continue;
            try {
              const payload = JSON.parse(rawJson);
              onEvent(payload);
            } catch (jsonErr) {
              console.warn('Erreur de décodage JSON SSE:', jsonErr, rawJson);
            }
          }
        }
      }
    }

    onComplete();
  } catch (err) {
    if (signal?.aborted) {
      onError(new Error('Simulation interrompue manuellement par l’opérateur.'));
    } else {
      onError(err);
    }
  }
}


// =====================================================================
// REAL AUTHENTICATION CLIENT (FastAPI SQLite + Local Persistence Fallback)
// =====================================================================
const SESSION_KEY = 'aura_auth_session';
const LOCAL_USERS_KEY = 'aura_users_registry';

function getLocalUsers() {
  try {
    const raw = localStorage.getItem(LOCAL_USERS_KEY);
    const list = raw ? JSON.parse(raw) : [];
    if (!list.some((u) => u.email === 'admin@aura-sovereign.ai')) {
      list.push({
        id: 1,
        name: 'Youssef Laaroussi',
        email: 'admin@aura-sovereign.ai',
        organization: 'AURA Sovereign Command',
        role: 'Supply Chain Director',
        password: 'Aura2026!'
      });
      localStorage.setItem(LOCAL_USERS_KEY, JSON.stringify(list));
    }
    return list;
  } catch {
    return [];
  }
}

export function getStoredSession() {
  try {
    const raw = localStorage.getItem(SESSION_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

export function saveStoredSession(session) {
  localStorage.setItem(SESSION_KEY, JSON.stringify(session));
}

export async function logoutUser() {
  const session = getStoredSession();
  localStorage.removeItem(SESSION_KEY);
  if (session?.token) {
    try {
      await fetch(`${API_BASE_URL}/api/auth/logout`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${session.token}` }
      });
    } catch {
      // Ignore network error if backend offline
    }
  }
}

export async function signupUser({ name, email, password, organization, role }) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/auth/signup`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify({ name, email, password, organization, role })
    });
    const data = await response.json();
    if (!response.ok) {
      return { ok: false, error: data.detail || 'Erreur lors de la création du compte.' };
    }
    saveStoredSession(data);
    return { ok: true, data };
  } catch {
    // Fallback to local persistent registry when backend port 8000 is offline
    const cleanEmail = email.trim().toLowerCase();
    const users = getLocalUsers();
    if (users.some((u) => u.email === cleanEmail)) {
      return { ok: false, error: 'Un compte existe déjà avec cette adresse e-mail.' };
    }
    const newUser = {
      id: Date.now(),
      name: name.trim(),
      email: cleanEmail,
      organization: organization.trim() || 'AURA Sovereign Ops',
      role: role || 'Supply Chain Director',
      password
    };
    users.push(newUser);
    localStorage.setItem(LOCAL_USERS_KEY, JSON.stringify(users));
    const session = {
      token: `local-jwt-${Date.now()}`,
      user: {
        id: newUser.id,
        name: newUser.name,
        email: newUser.email,
        organization: newUser.organization,
        role: newUser.role
      }
    };
    saveStoredSession(session);
    return { ok: true, data: session };
  }
}

export async function loginUser({ email, password }) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify({ email, password })
    });
    const data = await response.json();
    if (!response.ok) {
      return { ok: false, error: data.detail || 'Identifiants invalides.' };
    }
    saveStoredSession(data);
    return { ok: true, data };
  } catch {
    // Fallback to local persistent registry when backend port 8000 is offline
    const cleanEmail = email.trim().toLowerCase();
    const users = getLocalUsers();
    const match = users.find((u) => u.email === cleanEmail && u.password === password);
    if (!match) {
      return {
        ok: false,
        error: 'Identifiants invalides (adresse e-mail ou mot de passe incorrect).'
      };
    }
    const session = {
      token: `local-jwt-${Date.now()}`,
      user: {
        id: match.id,
        name: match.name,
        email: match.email,
        organization: match.organization,
        role: match.role
      }
    };
    saveStoredSession(session);
    return { ok: true, data: session };
  }
}
