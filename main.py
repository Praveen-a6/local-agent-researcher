# main.py
from src.graph import compiled_graph

def execute_autonomous_agent():
    print("================================================================")
    print("STARTING STATEFUL MULTI-AGENT RUNTIME ENGINE")
    print("================================================================")
    
    # Define our clean starting clipboard structure
    initial_state = {
        "task": "Explain quantization benefits",
        "research_notes": [],
        "report": "",
        "revision_count": 0,
        "next_step": ""
    }
    
    # Execute the workflow. LangGraph runs through the nodes and loops autonomously.
    final_output = compiled_graph.invoke(initial_state)
    
    print("\n================ FINAL COMPILED REPORT ================")
    print(final_output["report"])
    print("========================================================\n")

if __name__ == "__main__":
    execute_autonomous_agent()