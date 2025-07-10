import os

import logging

from fastapi import HTTPException, status
from pydantic import ValidationError

from app.api.common.auth_handler import UserAuthInfo
from app.clients.keycloak_admin_client import KeycloakAdminClient
from app.common.datetime import utcnow
from app.common.exceptions import BadRequestException, NotFoundException
from app.messages import (
    MSG_NOME_FANTASIA_JA_CADASTRADO,
    MSG_SELLER_CNPJ_NAO_ENCONTRADO,
    MSG_SELLER_ID_JA_CADASTRADO,
    MSG_SELLER_NAO_ENCONTRADO,
)
from app.models.seller_model import Seller
from app.models.seller_patch_model import SellerPatch
from app.repositories.seller_repository import SellerRepository
from app.services.publisher import publish_seller_message
from app.services.webhook_service import WebhookService
from ..api.v1.schemas.seller_schema import SellerResponse
from app.models.enums import SellerStatus

from ..models import Seller
from ..repositories import SellerRepository
from .base import CrudService

DEFAULT_USER = "system"

logger = logging.getLogger(__name__)



class SellerService(CrudService[Seller, str]):
    def __init__(self, repository: SellerRepository, keycloak_client: KeycloakAdminClient):
        super().__init__(repository)
        self.repository: SellerRepository = repository
        self.keycloak_client: KeycloakAdminClient = keycloak_client
        self.webhook_service = WebhookService()

    async def create(self, data: Seller, auth_info: UserAuthInfo) -> Seller:
        logger.info(f"Iniciando processo de criação para o seller_id: {data.seller_id}")
        # Verifica se seller_id já existe
        if await self.repository.find_by_id(data.seller_id):
            logger.warning(f"Tentativa de criar seller com ID duplicado: {data.seller_id}")
            raise BadRequestException(message=MSG_SELLER_ID_JA_CADASTRADO)

        # Verifica se trade_name já existe
        if await self.repository.find_by_trade_name(data.trade_name):
            logger.warning(f"Tentativa de criar seller com trade_name duplicado: {data.seller_id}")
            raise BadRequestException(message=MSG_NOME_FANTASIA_JA_CADASTRADO)

        user_identifier = f"{auth_info.user.server}:{auth_info.user.name}"

        now = utcnow()

        seller_to_create = Seller(
            seller_id=data.seller_id,
            company_name=data.company_name,
            trade_name=data.trade_name,
            cnpj=data.cnpj,
            state_municipal_registration=data.state_municipal_registration,
            commercial_address=data.commercial_address,
            contact_phone=data.contact_phone,
            contact_email=data.contact_email,
            legal_rep_full_name=data.legal_rep_full_name,
            legal_rep_cpf=data.legal_rep_cpf,
            legal_rep_rg_number=data.legal_rep_rg_number,
            legal_rep_rg_state=data.legal_rep_rg_state,
            legal_rep_birth_date=data.legal_rep_birth_date,
            legal_rep_phone=data.legal_rep_phone,
            legal_rep_email=data.legal_rep_email,
            bank_name=data.bank_name,
            agency_account=data.agency_account,
            account_type=data.account_type,
            account_holder_name=data.account_holder_name,
            product_categories=data.product_categories,
            business_description=data.business_description,
            created_at=now,
            updated_at=now,
            created_by=user_identifier,
            updated_by=user_identifier,
            audit_created_at=now,
            audit_updated_at=now,
        )

        user_keycloak_id = auth_info.user.name
        logger.debug(f"Tentando associar o novo seller '{data.seller_id}' ao usuário '{user_keycloak_id}' no Keycloak.")
        await self.keycloak_client.add_seller_to_user(
            user_id=user_keycloak_id,
            seller_to_add=data.seller_id
        )
        logger.info("Associação no Keycloak bem-sucedida.")

        logger.debug(f"Salvando o seller '{data.seller_id}' no repositório.")
        created_seller = await self.repository.create(seller_to_create)
        logger.info(f"Seller '{data.seller_id}' e associação de usuário criados com sucesso.")

        try:
            seller_dict = created_seller.model_dump()
            logger.debug(f"Dados do seller para publicação: {seller_dict}")
            publish_seller_message(seller_dict)
            logger.info(f"Mensagem do seller '{data.seller_id}' publicada com sucesso no RabbitMQ.")
        except Exception as e:
            logger.error(f"Falha ao publicar mensagem do seller '{data.seller_id}' no RabbitMQ: {str(e)}")
            # Não falha a operação principal, apenas loga o erro

        # Enviar notificação webhook
        try:
            await self.webhook_service.send_update_message(
                message=f"Seller '{data.seller_id}' foi criado",
                changes={"operation": "created", "seller_id": data.seller_id}
            )
        except Exception as e:
            logger.error(f"Falha ao enviar notificação webhook para seller criado '{data.seller_id}': {str(e)}")

        return created_seller

    async def find(self, paginator, filters: dict) -> list[Seller]:
        """
                Busca sellers, adicionando um filtro padrão para retornar apenas os ativos.
        """
        # Adiciona o filtro de status 'Ativo' por padrão
        if 'status' not in filters:
            filters['status'] = SellerStatus.ACTIVE

        return await self.repository.find(
            filters=filters, limit=paginator.limit, offset=paginator.offset, sort=paginator.get_sort_order()
        )

    async def delete_by_id(self, entity_id: str, auth_info: UserAuthInfo) -> Seller:
        """
        Realiza um 'soft delete' alterando o status do seller para 'Inativo'.
        """
        user_identifier = f"{auth_info.user.server}:{auth_info.user.name}"
        logger.info(f"Usuário '{user_identifier}' iniciando exclusão lógica para o seller_id: {entity_id}")

        current_seller = await self.repository.find_by_id(entity_id)
        if not current_seller or current_seller.status == SellerStatus.INACTIVE:
            raise NotFoundException(message=MSG_SELLER_NAO_ENCONTRADO.format(entity_id=entity_id))

        now = utcnow()
        update_data = {
            "status": SellerStatus.INACTIVE,
            "updated_at": now,
            "updated_by": user_identifier,
            "audit_updated_at": now,
        }

        updated_seller = await self.repository.patch(entity_id, update_data)
        logger.info(f"Seller '{entity_id}' marcado como 'Inativo' com sucesso pelo usuário '{user_identifier}'.")

        try:
            await self.webhook_service.send_update_message(
                message=f"Seller '{entity_id}' foi marcado como inativo",
                changes={"operation": "deleted", "seller_id": entity_id}
            )
        except Exception as e:
            logger.error(f"Falha ao enviar notificação webhook para seller excluído '{entity_id}': {str(e)}")

        try:
            user_keycloak_id = auth_info.user.name  # 'name' é o 'sub' (ID do usuário)
            await self.keycloak_client.remove_seller_from_user(
                user_id=user_keycloak_id,
                seller_to_remove=entity_id
            )
        except Exception:
            # Se a atualização do Keycloak falhar, o seller já foi inativado.
            logger.error(
                f"ALERTA: O seller '{entity_id}' foi inativado no banco, mas a remoção "
                f"do atributo no Keycloak para o usuário '{user_identifier}' FALHOU. "
                "O acesso pode precisar ser revogado manualmente.",
                exc_info=True
            )

        return updated_seller

    async def find_by_cnpj(self, cnpj: str) -> Seller:
        seller = await self.repository.find_by_cnpj(cnpj)
        if not seller:
            raise NotFoundException(message=MSG_SELLER_CNPJ_NAO_ENCONTRADO.format(cnpj=cnpj))
        return seller

    async def update(self, entity_id: str, data: SellerPatch, auth_info: UserAuthInfo) -> Seller:
        user_identifier = f"{auth_info.user.server}:{auth_info.user.name}"
        logger.info(f"Usuário '{user_identifier}' iniciando atualização (PATCH) para o seller_id: {entity_id}")
        current = await self.repository.find_by_id(entity_id)
        if not current:
            logger.warning(f"Usuário '{user_identifier}' tentou atualizar um seller inexistente: {entity_id}")
            raise NotFoundException(message=MSG_SELLER_NAO_ENCONTRADO.format(entity_id=entity_id))

        update_data = data.model_dump(exclude_unset=True)

        if not update_data:
            logger.info(f"Nenhum campo para atualizar no seller_id: {entity_id}. Nenhuma ação realizada.")
            return current

        if "trade_name" in update_data:
            existing = await self.repository.find_by_trade_name(update_data["trade_name"])
            if existing and existing.seller_id != entity_id:
                logger.warning(f"Tentativa de atualizar seller '{entity_id}' com trade_name que já está em uso.")
                raise BadRequestException(message=MSG_NOME_FANTASIA_JA_CADASTRADO)

        now = utcnow()

        update_data["updated_at"] = now
        update_data["updated_by"] = user_identifier
        update_data["audit_updated_at"] = now

        updated_seller = await self.repository.patch(entity_id, update_data)
        logger.info(f"Seller '{entity_id}' atualizado com sucesso pelo usuário '{user_identifier}'.")

        # Enviar notificação webhook
        try:
            changes_made = {key: value for key, value in update_data.items() if key not in ['updated_at', 'updated_by', 'audit_updated_at']}
            await self.webhook_service.send_update_message(
                message=f"Seller '{entity_id}' foi atualizado",
                changes={"operation": "updated", "seller_id": entity_id, "fields_changed": changes_made}
            )
        except Exception as e:
            logger.error(f"Falha ao enviar notificação webhook para seller atualizado '{entity_id}': {str(e)}")
            # Não falha a operação principal, apenas loga o erro

        return updated_seller

    async def replace(self, entity_id: str, data: Seller, auth_info: UserAuthInfo) -> Seller:
        user_identifier = f"{auth_info.user.server}:{auth_info.user.name}"
        logger.info(f"Usuário '{user_identifier}' iniciando substituição (PUT) para o seller_id: {entity_id}")
        existing = await self.repository.find_by_id(entity_id)
        if not existing:
            logger.warning(f"Usuário '{user_identifier}' tentou substituir um seller inexistente: {entity_id}")
            raise NotFoundException(message=MSG_SELLER_NAO_ENCONTRADO.format(entity_id=entity_id))

        if await self.repository.find_by_trade_name(data.trade_name):
            if data.trade_name != existing.trade_name:
                logger.warning(
                    f"Conflito de nome fantasia ao tentar substituir o seller '{entity_id}'. "
                    f"O nome '{data.trade_name}' já está em uso."
                )
                raise BadRequestException(message=MSG_NOME_FANTASIA_JA_CADASTRADO)

        now = utcnow()

        logger.debug(f"Montando objeto de substituição para o seller '{entity_id}'.")
        updated_seller = Seller(
            seller_id=entity_id,
            company_name=data.company_name,
            trade_name=data.trade_name,
            cnpj=data.cnpj,
            state_municipal_registration=data.state_municipal_registration,
            commercial_address=data.commercial_address,
            contact_phone=data.contact_phone,
            contact_email=data.contact_email,
            legal_rep_full_name=data.legal_rep_full_name,
            legal_rep_cpf=data.legal_rep_cpf,
            legal_rep_rg_number=data.legal_rep_rg_number,
            legal_rep_rg_state=data.legal_rep_rg_state,
            legal_rep_birth_date=data.legal_rep_birth_date,
            legal_rep_phone=data.legal_rep_phone,
            legal_rep_email=data.legal_rep_email,
            bank_name=data.bank_name,
            agency_account=data.agency_account,
            account_type=data.account_type,
            account_holder_name=data.account_holder_name,
            product_categories=data.product_categories,
            business_description=data.business_description,
            created_at=existing.created_at,
            created_by=existing.created_by,
            updated_at=now,
            updated_by=user_identifier,
            audit_created_at=existing.audit_created_at,
            audit_updated_at=now,
        )

        result = await self.repository.update(entity_id, updated_seller)

        logger.info(f"Seller '{entity_id}' substituído com sucesso pelo usuário '{user_identifier}'.")

        # Enviar notificação webhook
        try:
            await self.webhook_service.send_update_message(
                message=f"Seller '{entity_id}' foi substituído completamente",
                changes={"operation": "replaced", "seller_id": entity_id}
            )
        except Exception as e:
            logger.error(f"Falha ao enviar notificação webhook para seller substituído '{entity_id}': {str(e)}")
            # Não falha a operação principal, apenas loga o erro

        return result

    async def find_by_id(self, seller_id: str) -> Seller | None:
        seller = await self.repository.find_by_id(seller_id)
        if not seller or seller.status != "Ativo":
            return None
        return seller
