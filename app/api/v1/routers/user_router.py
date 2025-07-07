from typing import List
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status, Path, HTTPException

from app.api.common.auth_handler import get_current_user_info, UserAuthInfo, require_admin_user
from app.common.exceptions import ForbiddenException
from app.container import Container
from app.services.user_service import UserService
from app.api.v1.schemas.user_schema import UserCreate, UserResponse, UserPatch


router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cria um novo usuário no Keycloak",
)
@inject
async def create_user(
    user_data: UserCreate,
    user_service: UserService = Depends(Provide[Container.user_service]),
):
    """
    Cria um novo usuário no sistema de identidade (Keycloak).
    Este usuário poderá posteriormente criar um ou mais sellers.
    """
    return await user_service.create_user(user_data)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Busca um usuário por ID",
)
@inject
async def get_user(
    user_id: str,
    auth_info: UserAuthInfo = Depends(get_current_user_info),
    user_service: UserService = Depends(Provide[Container.user_service]),
):
    """
    Retorna os detalhes de um usuário específico do Keycloak.
    """
    realm_access = auth_info.info_token.get("realm_access", {})
    realm_roles = realm_access.get("roles", [])
    is_admin = "realm-admin" in realm_roles

    if not is_admin and auth_info.user.name != user_id:
        raise ForbiddenException(message="Você só pode consultar seus próprios dados.")

    return await user_service.get_user_by_id(user_id)


@router.get(
    "",
    response_model=List[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="Lista todos os usuários",
    dependencies=[Depends(require_admin_user)],
)
@inject
async def list_users(
    user_service: UserService = Depends(Provide[Container.user_service]),
):
    """
    Retorna uma lista de todos os usuários cadastrados no Keycloak.
    """
    return await user_service.get_all_users()


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deleta um usuário",
)
@inject
async def delete_user(
    user_id: str,
    auth_info: UserAuthInfo = Depends(get_current_user_info),
    user_service: UserService = Depends(Provide[Container.user_service]),
):
    """
    Remove um usuário permanentemente.
    Acessível pelo próprio usuário para deletar sua conta ou por um administrador.
    """
    realm_access = auth_info.info_token.get("realm_access", {})
    realm_roles = realm_access.get("roles", [])
    is_admin = "realm-admin" in realm_roles

    # Regra: Se não for admin, só pode deletar a si mesmo.
    if not is_admin and auth_info.user.name != user_id:
        raise ForbiddenException(message="Você não tem permissão para deletar este usuário.")

    await user_service.delete_user(user_id)


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Atualiza dados de um usuário (parcial)"
)
@inject
async def patch_user(
        patch_data: UserPatch,
        user_id: str = Path(..., description="ID do usuário a ser atualizado"),
        auth_info: UserAuthInfo = Depends(get_current_user_info),
        user_service: UserService = Depends(Provide[Container.user_service]),
):
    """
    Permite que um usuário autenticado atualize seus próprios dados
    (email, nome, sobrenome e/ou senha).
    """
    # Regra de negócio: um usuário só pode alterar seus próprios dados
    if auth_info.user.name != user_id:
        raise ForbiddenException(message="Você só pode alterar seus próprios dados.")

    return await user_service.patch_user(user_id, patch_data)
