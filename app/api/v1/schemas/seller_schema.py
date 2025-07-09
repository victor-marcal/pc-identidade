import re
from typing import Optional, List
from datetime import date
from pydantic import Field, field_validator, EmailStr
from app.models.enums import SellerStatus

from app.api.common.schemas import SchemaType
from app.models.enums import BrazilianState, AccountType, ProductCategory
from app.messages import (
    DESC_CNPJ,
    DESC_NOME_FANTASIA,
    DESC_SELLER_ID,
    MSG_CNPJ_FORMATO,
    MSG_CNPJ_FORMATO_REPLACE,
    MSG_NOME_FANTASIA_CURTO,
    MSG_SELLER_ID_FORMATO,
    MSG_SELLER_ID_OBRIGATORIO,
)

# Constantes para descrições
DESC_COMPANY_NAME = "Razão Social da empresa"
DESC_STATE_MUNICIPAL_REG = "Inscrição Estadual/Municipal"
DESC_CONTACT_PHONE = "Telefone de contato"
DESC_CONTACT_EMAIL = "E-mail de contato"
DESC_LEGAL_REP_FULL_NAME = "Nome completo do representante legal"
DESC_LEGAL_REP_CPF = "CPF do representante legal"
DESC_LEGAL_REP_RG_NUMBER = "Número do RG"
DESC_LEGAL_REP_RG_STATE = "Estado emissor do RG"
DESC_LEGAL_REP_BIRTH_DATE = "Data de nascimento"
DESC_LEGAL_REP_PHONE = "Telefone do representante legal"
DESC_LEGAL_REP_EMAIL = "E-mail do representante legal"
DESC_BANK_NAME = "Nome do banco"
DESC_AGENCY_ACCOUNT = "Agência e conta bancária"
DESC_ACCOUNT_TYPE = "Tipo de conta bancária"
DESC_ACCOUNT_HOLDER_NAME = "Nome do titular da conta"
DESC_PRODUCT_CATEGORIES = "Categorias de produtos"
DESC_BUSINESS_DESCRIPTION = "Descrição do negócio"

# Constantes para mensagens de erro
MSG_STATE_MUNICIPAL_REG_ERROR = "Inscrição Estadual/Municipal deve conter apenas números"
MSG_CPF_ERROR = "CPF deve conter exatamente 11 dígitos numéricos"
MSG_RG_ERROR = "RG deve conter apenas números"
MSG_BIRTH_DATE_ERROR = "Data de nascimento não pode ser futura"
MSG_CATEGORIES_ERROR = "Pelo menos uma categoria de produto deve ser selecionada"


class SellerBase(SchemaType):
    seller_id: str = Field(..., description=DESC_SELLER_ID)
    
    # Company Information
    company_name: str = Field(..., description=DESC_COMPANY_NAME)
    trade_name: str = Field(..., description=DESC_NOME_FANTASIA)  # Nome Fantasia
    cnpj: str = Field(..., description=DESC_CNPJ)
    state_municipal_registration: str = Field(..., description=DESC_STATE_MUNICIPAL_REG)
    commercial_address: str = Field(..., description="Endereço comercial da empresa")
    contact_phone: str = Field(..., description=DESC_CONTACT_PHONE)
    contact_email: EmailStr = Field(..., description=DESC_CONTACT_EMAIL)

    # Legal Representative
    legal_rep_full_name: str = Field(..., description=DESC_LEGAL_REP_FULL_NAME)
    legal_rep_cpf: str = Field(..., description=DESC_LEGAL_REP_CPF)
    legal_rep_rg_number: str = Field(..., description=DESC_LEGAL_REP_RG_NUMBER)
    legal_rep_rg_state: BrazilianState = Field(..., description=DESC_LEGAL_REP_RG_STATE)
    legal_rep_birth_date: date = Field(..., description=DESC_LEGAL_REP_BIRTH_DATE)
    legal_rep_phone: str = Field(..., description=DESC_LEGAL_REP_PHONE)
    legal_rep_email: EmailStr = Field(..., description=DESC_LEGAL_REP_EMAIL)

    # Banking Information
    bank_name: str = Field(..., description=DESC_BANK_NAME)
    agency_account: str = Field(..., description=DESC_AGENCY_ACCOUNT)
    account_type: AccountType = Field(..., description=DESC_ACCOUNT_TYPE)
    account_holder_name: str = Field(..., description=DESC_ACCOUNT_HOLDER_NAME)

    # Operational Data
    product_categories: List[ProductCategory] = Field(..., description=DESC_PRODUCT_CATEGORIES)
    business_description: str = Field(..., description=DESC_BUSINESS_DESCRIPTION)

    @field_validator('seller_id')
    def validar_seller_id(cls, v):
        if not v:
            raise ValueError(MSG_SELLER_ID_OBRIGATORIO)
        if not re.fullmatch(r"^[a-z0-9]+$", v):
            raise ValueError(MSG_SELLER_ID_FORMATO)
        return v

    @field_validator('trade_name')
    def validar_nome_fantasia(cls, v):
        if not v or len(v.strip()) < 3:
            raise ValueError(MSG_NOME_FANTASIA_CURTO)
        return v

    @field_validator('cnpj')
    def validar_cnpj(cls, v):
        if not v or not v.isdigit() or len(v) != 14:
            raise ValueError(MSG_CNPJ_FORMATO)
        return v

    @field_validator('state_municipal_registration')
    def validar_inscricao_estadual(cls, v):
        if v and not v.isdigit():
            raise ValueError(MSG_STATE_MUNICIPAL_REG_ERROR)
        return v

    @field_validator('legal_rep_cpf')
    def validar_cpf(cls, v):
        if not v or not v.isdigit() or len(v) != 11:
            raise ValueError(MSG_CPF_ERROR)
        return v

    @field_validator('legal_rep_rg_number')
    def validar_rg_numero(cls, v):
        if v and not v.isdigit():
            raise ValueError(MSG_RG_ERROR)
        return v

    @field_validator('legal_rep_birth_date')
    def validar_data_nascimento(cls, v):
        if v and v > date.today():
            raise ValueError(MSG_BIRTH_DATE_ERROR)
        return v

    @field_validator('contact_phone', 'legal_rep_phone')
    def validar_telefone(cls, v):
        # Remove caracteres não numéricos para armazenar apenas números
        if v:
            v = re.sub(r'\D', '', v)
        return v

    @field_validator('bank_name')
    def validar_nome_banco(cls, v):
        # Converte para lowercase conforme especificação
        return v.lower() if v else v

    @field_validator('product_categories')
    def validar_categorias(cls, v):
        if not v or len(v) == 0:
            raise ValueError(MSG_CATEGORIES_ERROR)
        return v


class SellerCreate(SellerBase):
    pass


class SellerUpdate(SchemaType):
    # Company Information
    company_name: Optional[str] = Field(None, description=DESC_COMPANY_NAME)
    trade_name: Optional[str] = Field(None, description=DESC_NOME_FANTASIA)
    cnpj: Optional[str] = Field(None, description=DESC_CNPJ)
    state_municipal_registration: Optional[str] = Field(None, description=DESC_STATE_MUNICIPAL_REG)
    commercial_address: Optional[str] = Field(None, description="Endereço comercial")
    contact_phone: Optional[str] = Field(None, description=DESC_CONTACT_PHONE)
    contact_email: Optional[EmailStr] = Field(None, description=DESC_CONTACT_EMAIL)

    # Legal Representative
    legal_rep_full_name: Optional[str] = Field(None, description=DESC_LEGAL_REP_FULL_NAME)
    legal_rep_cpf: Optional[str] = Field(None, description=DESC_LEGAL_REP_CPF)
    legal_rep_rg_number: Optional[str] = Field(None, description=DESC_LEGAL_REP_RG_NUMBER)
    legal_rep_rg_state: Optional[BrazilianState] = Field(None, description=DESC_LEGAL_REP_RG_STATE)
    legal_rep_birth_date: Optional[date] = Field(None, description=DESC_LEGAL_REP_BIRTH_DATE)
    legal_rep_phone: Optional[str] = Field(None, description=DESC_LEGAL_REP_PHONE)
    legal_rep_email: Optional[EmailStr] = Field(None, description=DESC_LEGAL_REP_EMAIL)

    # Banking Information
    bank_name: Optional[str] = Field(None, description=DESC_BANK_NAME)
    agency_account: Optional[str] = Field(None, description=DESC_AGENCY_ACCOUNT)
    account_type: Optional[AccountType] = Field(None, description=DESC_ACCOUNT_TYPE)
    account_holder_name: Optional[str] = Field(None, description=DESC_ACCOUNT_HOLDER_NAME)

    # Operational Data
    product_categories: Optional[List[ProductCategory]] = Field(None, description=DESC_PRODUCT_CATEGORIES)
    business_description: Optional[str] = Field(None, description=DESC_BUSINESS_DESCRIPTION)

    @field_validator('trade_name')
    def validar_nome_fantasia(cls, v):
        if v is not None and len(v.strip()) < 3:
            raise ValueError(MSG_NOME_FANTASIA_CURTO)
        return v

    @field_validator('cnpj')
    def validar_cnpj(cls, v):
        if v is not None and (not v.isdigit() or len(v) != 14):
            raise ValueError(MSG_CNPJ_FORMATO)
        return v

    @field_validator('state_municipal_registration')
    def validar_inscricao_estadual(cls, v):
        if v and not v.isdigit():
            raise ValueError(MSG_STATE_MUNICIPAL_REG_ERROR)
        return v

    @field_validator('legal_rep_cpf')
    def validar_cpf(cls, v):
        if v and (not v.isdigit() or len(v) != 11):
            raise ValueError(MSG_CPF_ERROR)
        return v

    @field_validator('legal_rep_rg_number')
    def validar_rg_numero(cls, v):
        if v and not v.isdigit():
            raise ValueError(MSG_RG_ERROR)
        return v

    @field_validator('legal_rep_birth_date')
    def validar_data_nascimento(cls, v):
        if v and v > date.today():
            raise ValueError(MSG_BIRTH_DATE_ERROR)
        return v

    @field_validator('contact_phone', 'legal_rep_phone')
    def validar_telefone(cls, v):
        if v:
            v = re.sub(r'\D', '', v)
        return v

    @field_validator('bank_name')
    def validar_nome_banco(cls, v):
        return v.lower() if v else v

    @field_validator('product_categories')
    def validar_categorias(cls, v):
        if v is not None and len(v) == 0:
            raise ValueError(MSG_CATEGORIES_ERROR)
        return v


class SellerReplace(SchemaType):
    # Company Information
    company_name: str = Field(..., description=DESC_COMPANY_NAME)
    trade_name: str = Field(..., description=DESC_NOME_FANTASIA)
    cnpj: str = Field(..., description=DESC_CNPJ)
    state_municipal_registration: str = Field(..., description=DESC_STATE_MUNICIPAL_REG)
    commercial_address: str = Field(..., description="Endereço comercial")
    contact_phone: str = Field(..., description=DESC_CONTACT_PHONE)
    contact_email: EmailStr = Field(..., description=DESC_CONTACT_EMAIL)

    # Legal Representative
    legal_rep_full_name: str = Field(..., description=DESC_LEGAL_REP_FULL_NAME)
    legal_rep_cpf: str = Field(..., description=DESC_LEGAL_REP_CPF)
    legal_rep_rg_number: str = Field(..., description=DESC_LEGAL_REP_RG_NUMBER)
    legal_rep_rg_state: BrazilianState = Field(..., description=DESC_LEGAL_REP_RG_STATE)
    legal_rep_birth_date: date = Field(..., description=DESC_LEGAL_REP_BIRTH_DATE)
    legal_rep_phone: str = Field(..., description=DESC_LEGAL_REP_PHONE)
    legal_rep_email: EmailStr = Field(..., description=DESC_LEGAL_REP_EMAIL)

    # Banking Information
    bank_name: str = Field(..., description=DESC_BANK_NAME)
    agency_account: str = Field(..., description=DESC_AGENCY_ACCOUNT)
    account_type: AccountType = Field(..., description=DESC_ACCOUNT_TYPE)
    account_holder_name: str = Field(..., description=DESC_ACCOUNT_HOLDER_NAME)

    # Operational Data
    product_categories: List[ProductCategory] = Field(..., description=DESC_PRODUCT_CATEGORIES)
    business_description: str = Field(..., description=DESC_BUSINESS_DESCRIPTION)

    @field_validator("trade_name")
    def validar_nome_fantasia(cls, v):
        if not v or len(v.strip()) < 3:
            raise ValueError(MSG_NOME_FANTASIA_CURTO)
        return v

    @field_validator("cnpj")
    def validar_cnpj(cls, v):
        if not v.isdigit() or len(v) != 14:
            raise ValueError(MSG_CNPJ_FORMATO_REPLACE)
        return v

    @field_validator('state_municipal_registration')
    def validar_inscricao_estadual(cls, v):
        if v and not v.isdigit():
            raise ValueError(MSG_STATE_MUNICIPAL_REG_ERROR)
        return v

    @field_validator('legal_rep_cpf')
    def validar_cpf(cls, v):
        if not v or not v.isdigit() or len(v) != 11:
            raise ValueError(MSG_CPF_ERROR)
        return v

    @field_validator('legal_rep_rg_number')
    def validar_rg_numero(cls, v):
        if v and not v.isdigit():
            raise ValueError(MSG_RG_ERROR)
        return v

    @field_validator('legal_rep_birth_date')
    def validar_data_nascimento(cls, v):
        if v and v > date.today():
            raise ValueError(MSG_BIRTH_DATE_ERROR)
        return v

    @field_validator('contact_phone', 'legal_rep_phone')
    def validar_telefone(cls, v):
        if v:
            v = re.sub(r'\D', '', v)
        return v

    @field_validator('bank_name')
    def validar_nome_banco(cls, v):
        return v.lower() if v else v

    @field_validator('product_categories')
    def validar_categorias(cls, v):
        if not v or len(v) == 0:
            raise ValueError(MSG_CATEGORIES_ERROR)
        return v


class SellerResponse(SellerBase):
    status: SellerStatus = Field(description="Status atual do seller")

