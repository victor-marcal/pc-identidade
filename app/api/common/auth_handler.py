"""
'Camada' de segurança para a API
"""

from typing import TYPE_CHECKING, Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

from app.api.common.injector import get_seller_id_from_path
from app.common.exceptions import ForbiddenException, UnauthorizedException
from app.integrations.auth.keycloak_adapter import InvalidTokenException, OAuthException, TokenExpiredException
from app.models.base import UserModel

if TYPE_CHECKING:
    from app.container import Container
    from app.integrations.auth.keycloak_adapter import KeycloakAdapter


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class UserAuthInfo(BaseModel):
    user: UserModel
    trace_id: str | None
    sellers: list[str]

    @staticmethod
    def to_sellers(sellers: str | None) -> list[str]:
        return sellers.split(",") if sellers else []


@inject
async def do_auth(
    request: Request,
    token: Annotated[str, Depends(oauth2_scheme)],
    seller_id: str = Depends(get_seller_id_from_path),
    openid_adapter: "KeycloakAdapter" = Depends(Provide["keycloak_adapter"]),
) -> UserAuthInfo:
    try:
        info_token = await openid_adapter.validate_token(token)
    except TokenExpiredException as exception:
        raise UnauthorizedException(message="Seu token de acesso expirou.") from exception
    except InvalidTokenException as exception:
        raise UnauthorizedException(message="Seu token de acesso é inválido.") from exception
    except OAuthException as exception:
        raise UnauthorizedException(message="Falha na autenticação.") from exception

    user_info = UserAuthInfo(
        user=UserModel(
            name=info_token.get("sub"),
            server=info_token.get("iss"),
        ),
        trace_id=getattr(request.state, 'trace_id', None),
        sellers=UserAuthInfo.to_sellers(info_token.get("sellers")),
    )

    if seller_id not in user_info.sellers:
        raise ForbiddenException("Não autorizado para trabalhar com este seller")

    request.state.user = user_info
    return user_info


async def get_current_user(request: Request) -> UserAuthInfo:
    """
    Pega o usuário logado na 'sessão' da requisição.
    """
    return request.state.user
