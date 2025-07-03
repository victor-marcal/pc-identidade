from pydantic import BaseModel, Field, EmailStr


class UserCreate(BaseModel):
    """
    Schema para criação de um novo usuário no Keycloak.
    """
    username: str = Field(..., description="Nome de usuário único.", min_length=3)
    email: EmailStr = Field(..., description="Email do usuário.")
    password: str = Field(..., description="Senha do usuário.", min_length=8)
    first_name: str | None = Field(None, description="Primeiro nome do usuário.")
    last_name: str | None = Field(None, description="Sobrenome do usuário.")


class UserResponse(BaseModel):
    """
    Schema para a resposta de dados de um usuário do Keycloak.
    """
    id: str = Field(..., description="ID do usuário no Keycloak.")
    username: str = Field(..., description="Nome de usuário.")
    email: EmailStr = Field(..., description="Email do usuário.")
    first_name: str | None = Field(None, description="Primeiro nome.")
    last_name: str | None = Field(None, description="Sobrenome.")
    enabled: bool = Field(..., description="Indica se o usuário está ativo.")
    attributes: dict | None = Field(None, description="Atributos personalizados do usuário, como 'sellers'.")
