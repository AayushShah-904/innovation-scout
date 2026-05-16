from typing import TypedDict,List,Dict,Any

class AgentState(TypedDict):
    query: str                      # The original messy R&D statement from the user
    keywords: List[str]             # Expanded keywords from the Query Parser
    raw_results: List[Dict[str, Any]] # Combined list from arXiv, pgvector, and Web
    ranked_results: List[Dict[str, Any]] # Scored and sorted results from the Ranker
    review_approved: bool           # Flag to check if human approved the results
    final_report: str               # The finalized research summary piece