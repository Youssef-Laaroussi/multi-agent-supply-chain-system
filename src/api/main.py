import os
import json
import sqlite3
import hashlib
import secrets
import hmac
import asyncio
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, HTTPException, Header
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.messages import HumanMessage
from pydantic import BaseModel

from src.supply_chain.graph import supply_chain_app
from src.supply_chain.config import SystemConfig, SUPPLIER_CATALOG, CARRIER_CATALOG

app = FastAPI(title="Sovereign Supply Chain API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================================
# REAL SQLITE AUTHENTICATION & SESSION STORE
# =====================================================================
AUTH_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "reports", "aura_users.db")


def _get_db() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(AUTH_DB_PATH), exist_ok=True)
    conn = sqlite3.connect(AUTH_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _hash_password(password: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 120_000).hex()


def _init_auth_db() -> None:
    with _get_db() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                organization TEXT NOT NULL,
                role TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                token TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
            """
        )
        # Seed default operator account if not present
        cur = conn.execute("SELECT id FROM users WHERE email = ?", ("admin@aura-sovereign.ai",))
        if not cur.fetchone():
            salt = secrets.token_hex(16)
            pwd_hash = _hash_password("Aura2026!", salt)
            conn.execute(
                """
                INSERT INTO users (name, email, organization, role, password_hash, salt, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "Youssef Laaroussi",
                    "admin@aura-sovereign.ai",
                    "AURA Sovereign Command",
                    "Supply Chain Director",
                    pwd_hash,
                    salt,
                    datetime.now().isoformat(),
                ),
            )
        conn.commit()


_init_auth_db()


class SignupRequest(BaseModel):
    name: str
    email: str
    password: str
    organization: str = "AURA Sovereign Ops"
    role: str = "Supply Chain Director"


class LoginRequest(BaseModel):
    email: str
    password: str


@app.post("/api/auth/signup")
async def auth_signup(req: SignupRequest):
    email = req.email.strip().lower()
    name = req.name.strip()
    if not email or "@" not in email:
        raise HTTPException(status_code=400, detail="Veuillez saisir une adresse e-mail valide.")
    if not name:
        raise HTTPException(status_code=400, detail="Veuillez indiquer votre nom complet.")
    if len(req.password) < 6:
        raise HTTPException(status_code=400, detail="Le mot de passe doit contenir au moins 6 caractères.")

    salt = secrets.token_hex(16)
    pwd_hash = _hash_password(req.password, salt)
    now = datetime.now().isoformat()

    with _get_db() as conn:
        existing = conn.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
        if existing:
            raise HTTPException(status_code=409, detail="Un compte existe déjà avec cette adresse e-mail.")

        cur = conn.execute(
            """
            INSERT INTO users (name, email, organization, role, password_hash, salt, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (name, email, req.organization.strip() or "AURA Sovereign Ops", req.role, pwd_hash, salt, now),
        )
        user_id = cur.lastrowid
        token = secrets.token_urlsafe(32)
        conn.execute("INSERT INTO sessions (token, user_id, created_at) VALUES (?, ?, ?)", (token, user_id, now))
        conn.commit()

    return {
        "token": token,
        "user": {
            "id": user_id,
            "name": name,
            "email": email,
            "organization": req.organization.strip() or "AURA Sovereign Ops",
            "role": req.role,
        },
    }


@app.post("/api/auth/login")
async def auth_login(req: LoginRequest):
    email = req.email.strip().lower()
    with _get_db() as conn:
        row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        if not row:
            raise HTTPException(status_code=401, detail="Identifiants invalides (adresse e-mail ou mot de passe incorrect).")

        expected_hash = _hash_password(req.password, row["salt"])
        if not hmac.compare_digest(expected_hash, row["password_hash"]):
            raise HTTPException(status_code=401, detail="Identifiants invalides (adresse e-mail ou mot de passe incorrect).")

        token = secrets.token_urlsafe(32)
        conn.execute(
            "INSERT INTO sessions (token, user_id, created_at) VALUES (?, ?, ?)",
            (token, row["id"], datetime.now().isoformat()),
        )
        conn.commit()

    return {
        "token": token,
        "user": {
            "id": row["id"],
            "name": row["name"],
            "email": row["email"],
            "organization": row["organization"],
            "role": row["role"],
        },
    }


@app.get("/api/auth/me")
async def auth_me(authorization: Optional[str] = Header(default=None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Session non authentifiée.")
    token = authorization.split(" ", 1)[1].strip()
    with _get_db() as conn:
        row = conn.execute(
            """
            SELECT u.id, u.name, u.email, u.organization, u.role
            FROM sessions s
            JOIN users u ON u.id = s.user_id
            WHERE s.token = ?
            """,
            (token,),
        ).fetchone()
        if not row:
            raise HTTPException(status_code=401, detail="Session expirée ou invalide.")
        return {"user": dict(row)}


@app.post("/api/auth/logout")
async def auth_logout(authorization: Optional[str] = Header(default=None)):
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ", 1)[1].strip()
        with _get_db() as conn:
            conn.execute("DELETE FROM sessions WHERE token = ?", (token,))
            conn.commit()
    return {"status": "logged_out"}


@app.get("/api/health")
async def health_check():
    """Returns API health status, LangGraph engine metadata, and statutory parameters."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "engine": "LangGraph v1.0 StateGraph + ToolNode + Command",
        "checkpointer": "MemorySaver (Active)",
        "strategic_reserve_floor": SystemConfig.CRITICAL_STRATEGIC_RESERVE_FLOOR,
        "spending_ceiling_eur": SystemConfig.MAX_EXPRESS_PURCHASE_BUDGET_EUR,
    }


@app.get("/api/catalogs")
async def get_catalogs():
    """Returns system catalogs: strategic SKUs, suppliers, carriers, and guardrail thresholds."""
    return {
        "strategic_skus": list(SystemConfig.STRATEGIC_SKUS),
        "reserve_floor": SystemConfig.CRITICAL_STRATEGIC_RESERVE_FLOOR,
        "spending_ceiling_eur": SystemConfig.MAX_EXPRESS_PURCHASE_BUDGET_EUR,
        "emergency_ceiling_eur": SystemConfig.EMERGENCY_BUDGET_CEILING_EUR,
        "sanctioned_countries": list(SystemConfig.SANCTIONED_COUNTRIES),
        "suppliers": SUPPLIER_CATALOG,
        "carriers": CARRIER_CATALOG,
    }


@app.get("/api/graph")
async def get_graph_topology():
    """Returns the live Mermaid diagram generated directly by LangGraph's StateGraph."""
    return {
        "mermaid": supply_chain_app.get_graph().draw_mermaid(),
        "nodes": list(supply_chain_app.get_graph().nodes.keys()),
    }


class SimulationRequest(BaseModel):
    sku: str = "SKU-MED-901"
    starting_stock: int = 750
    prompt: str = ""


@app.post("/api/simulate")
async def start_simulation(request: SimulationRequest):
    """Streams LangGraph execution updates via Server-Sent Events (SSE) with MemorySaver checkpointing."""
    async def event_generator():
        thread_id = f"crisis-thread-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        config = {"configurable": {"thread_id": thread_id}}

        initial_messages = [HumanMessage(content=request.prompt)] if request.prompt else []
        initial_state = {
            "sku": request.sku,
            "sku_description": "Emergency Strategic Supplies & Critical Infrastructure",
            "current_inventory": request.starting_stock,
            "strategic_reserve_floor": SystemConfig.CRITICAL_STRATEGIC_RESERVE_FLOOR,
            "demand_forecast": {},
            "inventory_analysis": {},
            "risk_assessment": {},
            "procurement_proposals": [],
            "selected_procurement": None,
            "compliance_review": {},
            "logistics_plan": {},
            "orchestrator_decision": {},
            "agent_logs": [],
            "messages": initial_messages,
            "current_step": "INITIALIZED",
            "is_compliant": False,
            "is_completed": False,
        }

        await asyncio.sleep(0.3)

        for event in supply_chain_app.stream(initial_state, config=config, stream_mode="updates"):
            for node_name, node_output in event.items():
                if not isinstance(node_output, dict):
                    continue
                node_logs = node_output.get("agent_logs", [])
                node_messages = node_output.get("messages", [])
                latest_msg = ""
                if node_logs:
                    latest_msg = node_logs[-1]
                elif node_messages:
                    last_msg = node_messages[-1]
                    latest_msg = getattr(last_msg, "content", str(last_msg))

                payload = {
                    "thread_id": thread_id,
                    "node": node_name,
                    "message": latest_msg,
                    "state_update": {
                        k: v for k, v in node_output.items() if k not in ["messages", "agent_logs"]
                    },
                }
                yield f"data: {json.dumps(payload)}\n\n"
                await asyncio.sleep(0.6)

        yield f"data: {json.dumps({'node': 'END', 'thread_id': thread_id, 'message': 'Simulation completed and checkpointed.'})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
