from langgraph.graph import StateGraph,START,END
from IPython.display import Image, display
from langgraph.checkpoint.memory import MemorySaver

from graph.state import AgentState

from agents.query_parser import parse_query_node
from agents.searcher import parallel_search_node
from agents.ranker import rank_results_node
from agents.human_review import human_review_node
from agents.reporter import generate_report_node


def build_graph():

    workflow=StateGraph(AgentState)
    
    workflow.add_node("parser",parse_query_node)
    workflow.add_node("searcher",parallel_search_node)
    workflow.add_node("ranker",rank_results_node)
    workflow.add_node("review",human_review_node)
    workflow.add_node("reporter",generate_report_node)


    workflow.add_edge(START,"parser")
    workflow.add_edge("parser","searcher")
    workflow.add_edge("searcher","ranker")
    workflow.add_edge("ranker","review")
    workflow.add_edge("review","reporter")
    workflow.add_edge("reporter",END)

    return workflow.compile(checkpointer=MemorySaver(),interrupt_before=["review"])


if __name__ == "__main__":
    print("--- Testing Integrated LangGraph Pipeline App ---")
    app = build_graph()
    
    initial_inputs = {
        "query": "Eco-friendly bio-plastics for protective phone cases"
    }
    
    final_state = app.invoke(initial_inputs)
    
    print("\n FINAL GENERATED REPORT ")
    print(final_state.get("final_report"))
    print("========================================================")
    display(Image(app.get_graph().draw_mermaid_png()))