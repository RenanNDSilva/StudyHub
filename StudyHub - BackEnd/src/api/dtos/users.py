from typing import Optional
from pydantic import BaseModel

class UserRegistration(BaseModel):
    name: str
    email: str
    password: str
    
class UserLogin(BaseModel):
    email: str
    password: str

class UserUpdate(BaseModel):
    name: str
    

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    
    




class UserOut(BaseModel):
    id: int
    name: Optional[str]
    email: str

    class Config:
        from_attributes = True