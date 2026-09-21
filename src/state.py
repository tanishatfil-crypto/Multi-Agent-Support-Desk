from typing import TypedDict, Annotated, List
import operator

class SupportState(TypedDict):
    # Customer's and Agent's conversation history
    messages: Annotated[List[dict], operator.add]
    
    # Classification category: "billing", "tech", or "general"
    category: str
    
    # Flag: Approval needed from Human Manager or not
    requires_human_approval: bool
    
    # Final ticket output summary
    resolution: str