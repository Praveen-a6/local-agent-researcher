# src/graph.py
from langgraph.graph import StateGraph, END
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage
from src.state import ResearcherState
from src.tools import web_search_tool
from src.config import settings

llm = ChatOllama(
    base_url=settings.OLLAMA_BASE_URL, 
    model=settings.OLLAMA_MODEL, 
    temperature=0.2
)

def researcher_node(state: ResearcherState) -> dict:
    """Fetches documents and appends facts to the state memory ledger."""
    print("\n[Node: Researcher] Scanning system logs and documentation...")
    task_query = state["task"]
    
    # Fire our deterministic tool function
    extracted_fact = web_search_tool(task_query)
    
    # We must return ONLY the keys we want to update. LangGraph merges it automatically.
    updated_notes = list(state.get("research_notes", []))
    updated_notes.append(extracted_fact)
    
    return {
        "research_notes": updated_notes,
        "next_step": "writer"
    }

def writer_node(state: ResearcherState) -> dict:
    """Compiles facts into a brief and runs an internal quality check."""
    print("[Node: Writer/Editor] Reading notes and synthesizing executive report...")
    
    accumulated_notes = "\n".join(state["research_notes"])
    current_revisions = state.get("revision_count", 0) + 1
    
    prompt = f"""You are a senior systems engineer writing an executive technical summary.
    Based strictly on these notes, write a professional 2-sentence summary brief:
    {accumulated_notes}
    """
    
    # Invoke the local model
    response = llm.invoke([HumanMessage(content=prompt)])
    generated_report = response.content.strip()
    
    # Quality Control Gate: If the LLM generates an incomplete/short draft, force a cycle
    if len(generated_report) < 60 and current_revisions < 3:
        print(f"⚠️ [Quality Alert] Report is too short ({len(generated_report)} chars). Routing back to Researcher.")
        return {
            "report": generated_report,
            "revision_count": current_revisions,
            "next_step": "researcher"
        }
    
    print("✅ [Quality Check Passed] Report meets engineering standards.")
    return {
        "report": generated_report,
        "revision_count": current_revisions,
        "next_step": "finalize"
    }

def router_logic(state: ResearcherState) -> str:
    """The traffic cop inspecting the state clipboard to route the next step."""
    return state["next_step"]

# -------------------------------------------------------------
# Constructing the State Machine Graph
# -------------------------------------------------------------

# Initialize the workflow graph with our strict clipboard schema
workflow = StateGraph(ResearcherState)

# 1. Register our operational workers (Nodes)
workflow.add_node("researcher", researcher_node)
workflow.add_node("writer", writer_node)

# 2. Establish where the data pipeline begins execution
workflow.set_entry_point("researcher")

# 3. Inject the conditional routing layout rules
workflow.add_conditional_edges(
    "researcher",
    router_logic,
    {
        "writer": "writer"
    }
)

workflow.add_conditional_edges(
    "writer",
    router_logic,
    {
        "researcher": "researcher",  # Allows loop cycling backward
        "finalize": END              # Safely terminates the graph execution
    }
)

# Compile the blueprint state machine into a single runtime engine asset
compiled_graph = workflow.compile()