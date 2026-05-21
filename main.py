import uuid
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict
import uvicorn
import traceback
from dotenv import load_dotenv
from graph.pipeline import build_graph
from tools.init_db import init_database

load_dotenv()

init_database()

app = FastAPI(title="Innovation Scout R&D Engine")

# Allow requests from any origin (Render frontend URL, local dev, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

graph_app=build_graph()

# Stores active LangGraph thread configurations in memory so we can resume them after human review
SESSION_STORE:Dict[str,dict]={}

class SearchRequest(BaseModel):
    query: str

class ApproveRequest(BaseModel):
    session_id:str
    approve:bool

@app.get("/")
def read_root():
    return {"status":"online","health":"ok"}

@app.post("/search")
async def search(request:SearchRequest):

    if not request.query.strip():
        raise HTTPException(status_code=400,detail="Query cannot be empty")

    session_id=str(uuid.uuid4())
    config={"configurable":{"thread_id":session_id}}

    SESSION_STORE[session_id]=config

    try:
        print(f"Starting search session {session_id} for query: {request.query}")

        # Start the LangGraph workflow; it will automatically pause when it reaches the human review checkpoint
        graph_app.invoke({"query":request.query},config)

        snapshot=graph_app.get_state(config)
        state_data=snapshot.values

        return {
            "session_id":session_id,
            "status":"review",
            "keywords":state_data.get("keywords",[]),
            "ranked_results":state_data.get("ranked_results",[]),
        }
    except Exception as e:
        print(f"Error during search: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500,detail="Internal server error during search")
    
@app.post("/approve")
async def human_review(request:ApproveRequest):
    config = SESSION_STORE.get(request.session_id)

    if not config:
        raise HTTPException(status_code=404,detail="Session not found")
    
    try:
        # Update the paused graph state with the researcher's approval decision, then resume execution to build the final report
        graph_app.update_state(
            config,
            {"review_approved":request.approve}
        )

        final_state=graph_app.invoke(input=None,config=config)
        print("Final state keys:", final_state.keys()) 
        
        if request.session_id in SESSION_STORE:
            del SESSION_STORE[request.session_id]
        
        return {
            "session_id":request.session_id,
            "status":"completed",
            "final_report":final_state.get("final_report")
        }
    
    except Exception as e:
        print(f"Error during human review: {e}")
        traceback.print_exc()
        if request.session_id in SESSION_STORE:
            del SESSION_STORE[request.session_id]
        raise HTTPException(status_code=500, detail="Internal server error during review")

    
if __name__ == "__main__":

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)