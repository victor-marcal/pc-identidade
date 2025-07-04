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


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)


class UserAuthInfo(BaseModel):
    """
    Modelo para armazenar informações do usuário autenticado.
    """
    user: UserModel
    trace_id: str | None
    sellers: list[str]
    info_token: dict

    @staticmethod
    def to_sellers(sellers_attr: str | list[str] | None) -> list[str]:
        """Converte o atributo 'sellers' do token para uma lista de strings."""
        if isinstance(sellers_attr, list):
            return sellers_attr
        if isinstance(sellers_attr, str):
            return sellers_attr.split(",") if sellers_attr else []
        return []


@inject
async def get_current_user_info(
        request: Request,
        token: Annotated[str, Depends(oauth2_scheme)],
        openid_adapter: "KeycloakAdapter" = Depends(Provide["keycloak_adapter"]),
) -> UserAuthInfo:
    """
    Dependência FastAPI para validar o token e retornar as informações do usuário.
    Esta função será o único ponto de entrada para autenticação nas rotas.
    """
    if token is None:
        raise UnauthorizedException(message="Não autenticado. É necessário fornecer um token de acesso válido.")

    try:
        info_token = await openid_adapter.validate_token(token)
    except TokenExpiredException as e:
        raise UnauthorizedException(message="Seu token de acesso expirou.") from e
    except InvalidTokenException as e:
        raise UnauthorizedException(message="Seu token de acesso é inválido.") from e
    except Exception as e:
        raise UnauthorizedException(message=f"Falha na autenticação: {e}") from e

    user_info = UserAuthInfo(
        user=UserModel(
            name=info_token.get("sub"),
            server=info_token.get("iss"),
        ),
        trace_id=getattr(request.state, 'trace_id', None),
        sellers=UserAuthInfo.to_sellers(info_token.get("sellers")),
        info_token=info_token
    )

    request.state.user = user_info

    return user_info


def require_seller_permission(seller_id: str, auth_info: UserAuthInfo = Depends(get_current_user_info)):
    """
    Dependência para verificar se o usuário autenticado tem permissão para um seller_id específico.
    Use isto em rotas que operam em um seller existente (GET, PATCH, DELETE).
    """
    if seller_id not in auth_info.sellers:
        raise ForbiddenException(message="Você não tem permissão para acessar este seller.")
    return auth_info


def require_admin_user(auth_info: UserAuthInfo = Depends(get_current_user_info)):
    """
    Dependência que verifica se o usuário autenticado possui a role de administrador
    do realm. Lança uma exceção ForbiddenException caso contrário.
    """
    token_payload = auth_info.info_token
    is_admin = False

    resource_access = token_payload.get("resource_access", {})
    if "realm-management" in resource_access:
        realm_management_roles = resource_access["realm-management"].get("roles", [])
        if "realm-admin" in realm_management_roles:
            is_admin = True

    if not is_admin:
        realm_access = token_payload.get("realm_access", {})
        realm_roles = realm_access.get("roles", [])
        if "realm-admin" in realm_roles:
            is_admin = True

    if not is_admin:
        raise ForbiddenException(message="Esta ação requer privilégios de administrador.")

    return auth_info


@inject
async def do_auth(
    request: Request,
    token: Annotated[str, Depends(oauth2_scheme)],
    seller_id: str = Depends(get_seller_id_from_path),
    openid_adapter: "KeycloakAdapter" = Depends(Provide["keycloak_adapter"]),
) -> None:
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
        raise ForbiddenException(message="Você não tem permissão para acessar este seller.")

    request.state.user = user_info


async def get_current_user(request: Request) -> UserAuthInfo:
    """
    Pega o usuário logado na 'sessão' da requisição.
    """
    return request.state.user
