from typing import Dict, Any
from graph.state import AgentState

def generate_report_node(state: AgentState) -> Dict[str, Any]:
    """
    Final node that takes the highly ranked assets and compiles a clean markdown report.
    """
    print("\n--- AGENT ARCHITECT: Compiling Final R&D Briefing ---")
    ranked = state.get("ranked_results", [])
    
    report = f"# Technology Scout Insights Briefing\n"
    report += f"**Core Objective:** {state.get('query')}\n\n"
    report += "## Top Verified High-Value Assets\n"
    
    for idx, item in enumerate(ranked[:3], 1):  # Grab the top 3 best fits
        report += f"### {idx}. {item['title']}\n"
        report += f"- **Relevance Score:** {item['relevance_score']} | **Credibility:** {item['credibility_score']}\n"
        report += f"- **Source/URL:** [{item['url']}]({item['url']})\n"
        report += f"- **Analysis:** {item['reason']}\n\n"
        
    return {"final_report": report}