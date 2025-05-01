from pydantic import BaseModel, EmailStr
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str
    
class AuthData(BaseModel):
    username: str
    password: str