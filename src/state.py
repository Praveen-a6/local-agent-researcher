# src/state.py
from typing import TypedDict, List

class ResearcherState(TypedDict):
    # The initial research prompt or question submitted by the user
    task: str                  
    
    # Accumulated factual telemetry notes extracted by the researcher node
    research_notes: List[str]  
    
    # The final compiled technical report compiled by the editor node
    report: str                
    
    # Safety loop counter to prevent infinite recursive agent iterations
    revision_count: int        
    
    # Internal router signal flag ('researcher', 'writer', or 'finalize')
    next_step: str