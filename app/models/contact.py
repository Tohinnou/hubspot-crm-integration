from pydantic import BaseModel, EmailStr
from typing import Optional

class ContactCreate(BaseModel):
    firstname: str
    lastname: str
    email: EmailStr
    phone: Optional[str] = None
    lead_source_custom: Optional[str] = None
  
  
class ContactResponse(BaseModel):
    id: str
    firstname: str
    lastname: str
    email: str
    lead_score_custom: Optional[int] = None
