from pydantic import BaseModel


class CreateUserRequest(BaseModel):
    username: str
    password: str
    first_name: str
    last_name: str
