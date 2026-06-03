import uuid
import os
import traceback
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict
import uvicorn
from dotenv import load_dotenv

load_dotenv()

# ── Lifespan: runs startup logic AFTER the server is already bound to a port ──
# This prevents "Exited with status 1" crashes caused by DB/graph init failures
# at module level (before uvicorn can even bind the port).
@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── DB Init ──────────────────────────────────────────────────────────────
    try:
        from tools.init_db import init_database
        init_database()
        print("✅ Database initialized successfully.")
    except Exception as e:
        print(f"⚠️  Database init failed (non-fatal): {e}")
        print("    The app will still start. DB-dependent features may not work.")
        print("    Check that DATABASE_URL is set correctly in Render environment variables.")

    # ── LangGraph Pipeline ───────────────────────────────────────────────────
    try:
        from graph.pipeline import build_graph
        app.state.graph_app = build_graph()
        print("✅ LangGraph pipeline built successfully.")
    except Exception as e:
        print(f"⚠️  LangGraph pipeline build failed: {e}")
        traceback.print_exc()
        app.state.graph_app = None

    yield  # Server runs here

    print("🛑 Shutting down Innovation Scout.")


app = FastAPI(title="Innovation Scout R&D Engine", lifespan=lifespan)

# Configure CORS to allow the React frontend to communicate with this backend
origins = [
    "http://localhost:5173",    # React local dev server
    "http://127.0.0.1:5173",
    # Add your production frontend URL here later, e.g., "https://app.innovationscout.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Stores active LangGraph thread configurations in memory so we can resume them after human review
SESSION_STORE: Dict[str, dict] = {}

class SearchRequest(BaseModel):
    query: str

class ApproveRequest(BaseModel):
    session_id: str
    approve: bool

@app.get("/")
def read_root():
    return {"status": "online", "health": "ok"}

@app.post("/search")
async def search(request: SearchRequest):
    graph_app = app.state.graph_app
    if graph_app is None:
        raise HTTPException(status_code=503, detail="LangGraph pipeline failed to initialize. Check server logs.")

    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    session_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": session_id}}

    SESSION_STORE[session_id] = config

    try:
        print(f"Starting search session {session_id} for query: {request.query}")

        # Start the LangGraph workflow; it will automatically pause when it reaches the human review checkpoint
        graph_app.invoke({"query": request.query}, config)

        snapshot = graph_app.get_state(config)
        state_data = snapshot.values

        return {
            "session_id": session_id,
            "status": "review",
            "keywords": state_data.get("keywords", []),
            "ranked_results": state_data.get("ranked_results", []),
        }
    except Exception as e:
        print(f"Error during search: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error during search")

@app.post("/approve")
async def human_review(request: ApproveRequest):
    graph_app = app.state.graph_app
    if graph_app is None:
        raise HTTPException(status_code=503, detail="LangGraph pipeline failed to initialize. Check server logs.")

    config = SESSION_STORE.get(request.session_id)

    if not config:
        raise HTTPException(status_code=404, detail="Session not found")

    try:
        # Update the paused graph state with the researcher's approval decision, then resume execution to build the final report
        graph_app.update_state(
            config,
            {"review_approved": request.approve}
        )

        final_state = graph_app.invoke(input=None, config=config)
        print("Final state keys:", final_state.keys())

        if request.session_id in SESSION_STORE:
            del SESSION_STORE[request.session_id]

        return {
            "session_id": request.session_id,
            "status": "completed",
            "final_report": final_state.get("final_report")
        }

    except Exception as e:
        print(f"Error during human review: {e}")
        traceback.print_exc()
        if request.session_id in SESSION_STORE:
            del SESSION_STORE[request.session_id]
        raise HTTPException(status_code=500, detail="Internal server error during review")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)), reload=True)