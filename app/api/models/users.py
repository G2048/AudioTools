from pydantic import BaseModel


class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None


class UserLogin(BaseModel):
    username: str
    password: str
    grant_type: str = "password"

    def to_url_form(self):
        return f"grant_type={self.grant_type}&&username={self.username}&password={self.password}"


class Token(BaseModel):
    access_token: str
    token_type: str
