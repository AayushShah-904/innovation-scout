import streamlit as st
import requests

st.set_page_config(page_title="Innovation Scout", layout="wide")

API_URL="http://localhost:8000"

st.title("Innovation Scout R&D Engine")

if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "stage" not in st.session_state:
    st.session_state.stage = "search_input"  
if "search_data" not in st.session_state:
    st.session_state.search_data = {}
if "final_report" not in st.session_state:
    st.session_state.final_report = ""

st.caption("Multi-Agent Knowledge Retrieval & Verification Engine Powered by LangGraph & Gemini") 

if st.session_state.stage == "search_input":
    query = st.text_input("Enter your research query:", placeholder="e.g. 'Eco-friendly bio-plastics for protective phone cases'")
    if st.button("Search") and query.strip():
        if not query.strip():
            st.error("Query cannot be empty.")
        # Trigger the backend to run our LangGraph agents in parallel across arXiv, local vector DB, and live web
        with st.spinner("Executing 3-Way Parallel Agent Scans (arXiv, Local DB, Live Web Grounding)"):
            try:
                response = requests.post(f"{API_URL}/search", json={"query": query})
                if response.status_code == 200:
                    data = response.json()
                    st.session_state.session_id = data["session_id"]
                    st.session_state.search_data = data
                    st.session_state.stage = "review"
                    st.rerun()
                else:
                    st.error(f"Backend Server Processing failed: {response.text}")
            except Exception as e:
                st.error(f"Connection error to FastAPI server: {e}")

# The LangGraph workflow pauses here at our Human-in-the-Loop checkpoint so the researcher can verify AI credibility scores before generating the final report
elif st.session_state.stage == "review":
    st.subheader("Review & Approve Search Results")
    st.info("The LangGraph state machine has paused execution. Evaluate the extracted data assets below to authorize report compilation.")

    keywords = st.session_state.search_data.get("keywords", [])
    st.write(f"**Expanded Agent Parsing Targets:** " + ", ".join([f"`{k}`" for k in keywords]))

    st.write("---")
    st.subheader("Top Ranked Scientific & Market Discoveries")
    
    ranked_items = st.session_state.search_data.get("ranked_results", [])

    if not ranked_items:
        st.error("No matching documents found across standard sources.")
    else:
        for idx, item in enumerate(ranked_items, 1):
                with st.container():
                    col1, col2 = st.columns([0.7, 0.3])
                    with col1:
                        st.markdown(f"### {idx}. [{item.get('title', 'Untitled')}]( {item.get('url', '#')} )")
                        st.write(f"**Source:** `{item.get('source', 'WEB').upper()}`")
                        st.write(f"**Analysis:** {item.get('reason', 'No reasoning text profile populated.')}")
                    with col2:
                        st.caption("Agent Evaluator Scores")
                        rel = float(item.get('relevance_score', 0.5))
                        crd = float(item.get('credibility_score', 0.5))
                        
                        st.write(f"Relevance: `{rel}`")
                        st.progress(rel)
                        st.write(f"Credibility: `{crd}`")
                        st.progress(crd)
                st.markdown("<br>", unsafe_allow_html=True)
    st.write("---")

    col_app, col_can = st.columns([0.5, 0.5])
    with col_app:
        # Once approved, we tell the backend to resume the LangGraph state machine and synthesize the final briefing
        if st.button("Approve & Compile Briefing Report", type="primary", use_container_width=True):
            with st.spinner("Authorizing state thread... Building final R&D report brief..."):
                payload = {"session_id": st.session_state.session_id, "approve": True}
                res = requests.post(f"{API_URL}/approve", json=payload)
                if res.status_code == 200:
                    st.session_state.final_report = res.json().get("final_report", "# Compilation Fault")
                    st.session_state.stage = "complete_screen"
                    st.rerun()
                else:
                    st.error("Error committing validation decision to graph background context.")
                    
    with col_can:
        if st.button("Reject & Clear Session", use_container_width=True):
            st.session_state.session_id = None
            st.session_state.stage = "search_input"
            st.session_state.search_data = {}
            st.rerun()

elif st.session_state.stage == "complete_screen":
    st.success("R&D Synthesis Briefing Generated Successfully!")
    
    if st.session_state.final_report:
        st.markdown(st.session_state.final_report)
    else:
        st.error(" Report compilation returned empty. Check backend logs for `final_report` key.")
    
    st.markdown("---")
    
    if st.button("Launch New Research Session", type="primary"):
        st.session_state.session_id = None
        st.session_state.stage = "search_input"
        st.session_state.search_data = {}
        st.session_state.final_report = ""
        st.rerun()