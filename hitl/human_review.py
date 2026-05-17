from typing import Dict, Any
from graph.state import AgentState

def human_review_node(state: AgentState) -> Dict[str, Any]:
    """
    Temporary placeholder for the human-in-the-loop gate.
    In the final app, this will pause execution for Streamlit input.
    """
    print("\n--- GATE: Pausing for Human-in-the-Loop Review ---")
    # Check if the researcher has clicked Approve in the Streamlit UI to authorize continuing the workflow
    approved = state.get("review_approved", False)
    
    if approved:
        print("Result Status: Human Approved the assets. Moving to Report Generation.")
    else:
        print("Result Status: Human Rejected or Requested Re-search. Halted.")
        
    return {"review_approved": approved}
