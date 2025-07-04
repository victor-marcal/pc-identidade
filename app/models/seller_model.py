from . import PersistableEntity
from .enums import BrazilianState, AccountType, ProductCategory
from typing import List
from datetime import date


class Seller(PersistableEntity):
    seller_id: str
    
    # Company Information
    company_name: str  # Razão Social
    trade_name: str  # Nome Fantasia (nome_fantasia existente)
    cnpj: str  # CNPJ (já existente)
    state_municipal_registration: str # Inscrição Estadual/Municipal
    commercial_address: str  # Endereço Comercial
    contact_phone: str  # Telefone de Contato
    contact_email: str  # E-mail de Contato

    # Legal Representative
    legal_rep_full_name: str  # Nome Completo
    legal_rep_cpf: str  # CPF
    legal_rep_rg_number: str  # RG (Número)
    legal_rep_rg_state: BrazilianState  # RG (Estado)
    legal_rep_birth_date: date  # Data de Nascimento
    legal_rep_phone: str  # Telefone
    legal_rep_email: str  # E-mail

    # Banking Information
    bank_name: str  # Nome do Banco
    agency_account: str  # Agência / Conta
    account_type: AccountType  # Tipo de Conta
    account_holder_name: str  # Nome do Titular

    # Operational Data
    product_categories: List[ProductCategory] # Categorias de Produtos
    business_description: str  # Descrição do Negócio
