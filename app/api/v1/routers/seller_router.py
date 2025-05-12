from typing import TYPE_CHECKING

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status

from app.api.common.schemas import ListResponse, Paginator, UuidType, get_request_pagination
from app.container import Container

from ..schemas.seller_schema import SellerCreate, SellerResponse, SellerUpdate
from . import SELLER_PREFIX

if TYPE_CHECKING:
    from app.services import SellerService


router = APIRouter(prefix=SELLER_PREFIX, tags=["Sellers"])


@router.get(
    "",
    response_model=ListResponse[SellerResponse],
    status_code=status.HTTP_200_OK,
)
@inject
async def get(
    paginator: Paginator = Depends(get_request_pagination),
    seller_service: "SellerService" = Depends(Provide[Container.seller_service]),
):
    results = await seller_service.find(paginator=paginator, filters={})
    return paginator.paginate(results=results)


@router.get(
    "/{seller_id}",
    response_model=SellerResponse,
    status_code=status.HTTP_200_OK,
)
@inject
async def get_by_id(
    seller_id: str,
    seller_service: "SellerService" = Depends(Provide[Container.seller_service]),
):
    return await seller_service.find_by_id(seller_id)


@router.post(
    "",
    response_model=SellerResponse,
    status_code=status.HTTP_201_CREATED,
)
@inject
async def create(
    seller: SellerCreate, seller_service: "SellerService" = Depends(Provide[Container.seller_service])
):
    return await seller_service.create(seller)


@router.patch(
    "/{seller_id}",
    response_model=SellerResponse,
    status_code=status.HTTP_200_OK,
)
@inject
async def update_by_id(
    seller_id: str,
    seller: SellerUpdate,
    seller_service: "SellerService" = Depends(Provide[Container.seller_service]),
):
    return await seller_service.update(seller_id, seller)


@router.delete("/{seller_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete(
    seller_id: str, seller_service: "SellerService" = Depends(Provide[Container.seller_service])
):
    await seller_service.delete_by_id(seller_id)
