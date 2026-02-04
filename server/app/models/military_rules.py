from pydantic import BaseModel
from typing import List, Optional

class MilitaryRule(BaseModel):
    id: int
    title: str
    content: str
    category: str
    description: Optional[str] = None

class MilitaryRuleResponse(BaseModel):
    rules: List[MilitaryRule]
    total: int
