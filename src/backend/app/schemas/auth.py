from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    first_name: str
    last_name: str
    role: str


class TokenResponse(BaseModel):
    token: str
    role: str
    user: UserResponse


class RegisterAdminRequest(BaseModel):
    username: str
    password: str
