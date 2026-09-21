from typing import TypedDict, Annotated, List
import operator

class SupportState(TypedDict):
    # Customer aur Agent ki saari conversation history
    messages: Annotated[List[dict], operator.add]
    
    # Classification category: "billing", "tech", ya "general"
    category: str
    
    # Flag: Human manager ka approval chahiye ya nahi
    requires_human_approval: bool
    
    # Final ticket output summary
    resolution: str