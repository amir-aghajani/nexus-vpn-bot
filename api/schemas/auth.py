from pydantic import BaseModel


class LoginModel(BaseModel):
    username: str
    password: str


class TokenModel(BaseModel):
    accessToken: str
    tokenType: str = "bearer"
