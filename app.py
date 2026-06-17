# app.py
import streamlit as st
from src.graph import compiled_graph

st.set_page_config(page_title="Agentic Researcher", page_icon="🤖", layout="centered")

st.title("Autonomous Multi-Agent Research Studio")
st.caption("Powered by LangGraph Loop Architecture & Local Ollama Inference")

st.write("---")

task_input = st.text_input(
    "Enter a technical topic for the Agent team to analyze:", 
    placeholder="e.g., Explain quantization benefits"
)

if st.button("Launch Autonomous Agents"):
    if task_input.strip():
        # 1. Initialize our clean starting state dictionary layout
        initial_state = {
            "task": task_input,
            "research_notes": [],
            "report": "",
            "revision_count": 0,
            "next_step": ""
        }
        
        # 2. Setup visual container monitoring blocks
        with st.spinner("Initializing graph state machine execution loops..."):
            status_box = st.empty()
            notes_expander = st.expander("📚 Live Agent Memory Ledger (Shared State)")
            
            # 3. Stream the graph updates state-by-state
            # .stream() lets us capture data the moment a node completes its work
            for output in compiled_graph.stream(initial_state):
                for node_name, state_snapshot in output.items():
                    
                    if node_name == "researcher":
                        status_box.warning("🔍 **Researcher Agent** is scraping documentation and logging discovered telemetry...")
                        if state_snapshot.get("research_notes"):
                            notes_expander.code(state_snapshot["research_notes"][-1], language="text")
                            
                    elif node_name == "writer":
                        # If next_step is set to researcher, it means the quality gate failed and it's looping back
                        if state_snapshot.get("next_step") == "researcher":
                            status_box.error(f"⚠️ **Editor Agent flagged draft quality constraint violation** (Revision {state_snapshot.get('revision_count')}). Routing back for secondary data harvesting.")
                        else:
                            status_box.success("✅ **Editor Agent** has validated the synthesis metrics against engineering guidelines.")

            # 4. Extract and print the final state values
            final_result = compiled_graph.invoke(initial_state)
            
            st.write("---")
            st.subheader("📝 Final Compiled Executive Report")
            st.info(final_result["report"])
            
    else:
        st.warning("Please enter a valid research topic.")