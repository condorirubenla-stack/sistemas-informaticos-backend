from pydantic import BaseModel, EmailStr
from typing import List, Optional

class UsuarioCreate(BaseModel):
    nombre: str
    apellido: str
    email: EmailStr
    password: str
    rol: str = "estudiante"

    class Config:
        from_attributes = True

class UsuarioResponse(BaseModel):
    id: int
    nombre: str
    apellido: str
    email: str
    rol: str

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UsuarioResponse

class TokenData(BaseModel):
    username: Optional[str] = None
