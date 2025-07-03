from typing import List
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status, HTTPException
from app.container import Container
from app.services.user_service import UserService
from app.api.v1.schemas.user_schema import UserCreate, UserResponse
# from app.api.common.auth_handler import do_auth # TODO: PROTEGER ROTAS DE ATUALIZAÇÃO E DELEÇÃO

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
    # dependencies=[Depends(do_auth)] # Proteger se necessário
)
@inject
async def get_user(
    user_id: str,
    user_service: UserService = Depends(Provide[Container.user_service]),
):
    """
    Retorna os detalhes de um usuário específico do Keycloak.
    """
    return await user_service.get_user_by_id(user_id)


@router.get(
    "",
    response_model=List[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="Lista todos os usuários",
    # dependencies=[Depends(do_auth)] # Proteger se necessário
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
    # dependencies=[Depends(do_auth)] # Proteger se necessário
)
@inject
async def delete_user(
    user_id: str,
    user_service: UserService = Depends(Provide[Container.user_service]),
):
    """
    Remove um usuário do Keycloak permanentemente.
    """
    await user_service.delete_user(user_id)