from typing import Optional, List
from datetime import date
from pydantic import BaseModel, Field, field_validator, EmailStr
from .enums import BrazilianState, AccountType, ProductCategory
import re


class SellerPatch(BaseModel):
    # Company Information
    company_name: Optional[str] = Field(None, description="Razão Social da empresa")
    trade_name: Optional[str] = Field(None, description="Nome fantasia exclusivo no sistema")
    cnpj: Optional[str] = Field(None, description="CNPJ com exatamente 14 dígitos numéricos, sem pontuação")
    state_municipal_registration: Optional[str] = Field(None, description="Inscrição Estadual/Municipal")
    commercial_address: Optional[str] = Field(None, description="Endereço comercial")
    contact_phone: Optional[str] = Field(None, description="Telefone de contato")
    contact_email: Optional[EmailStr] = Field(None, description="E-mail de contato")

    # Legal Representative
    legal_rep_full_name: Optional[str] = Field(None, description="Nome completo do representante legal")
    legal_rep_cpf: Optional[str] = Field(None, description="CPF do representante legal")
    legal_rep_rg_number: Optional[str] = Field(None, description="Número do RG")
    legal_rep_rg_state: Optional[BrazilianState] = Field(None, description="Estado emissor do RG")
    legal_rep_birth_date: Optional[date] = Field(None, description="Data de nascimento")
    legal_rep_phone: Optional[str] = Field(None, description="Telefone do representante legal")
    legal_rep_email: Optional[EmailStr] = Field(None, description="E-mail do representante legal")

    # Banking Information
    bank_name: Optional[str] = Field(None, description="Nome do banco")
    agency_account: Optional[str] = Field(None, description="Agência e conta bancária")
    account_type: Optional[AccountType] = Field(None, description="Tipo de conta bancária")
    account_holder_name: Optional[str] = Field(None, description="Nome do titular da conta")

    # Operational Data
    product_categories: Optional[List[ProductCategory]] = Field(None, description="Categorias de produtos")
    business_description: Optional[str] = Field(None, description="Descrição do negócio")

    @field_validator("trade_name")
    def validar_nome_fantasia(cls, v):
        if v is not None and len(v.strip()) < 3:
            raise ValueError("O nome_fantasia deve conter ao menos 3 caracteres.")
        return v

    @field_validator("cnpj")
    def validar_cnpj(cls, v):
        if v is not None and (not v.isdigit() or len(v) != 14):
            raise ValueError("O CNPJ deve conter exatamente 14 dígitos numéricos.")
        return v

    @field_validator('state_municipal_registration')
    def validar_inscricao_estadual(cls, v):
        if v and not v.isdigit():
            raise ValueError("Inscrição Estadual/Municipal deve conter apenas números")
        return v

    @field_validator('legal_rep_cpf')
    def validar_cpf(cls, v):
        if v and (not v.isdigit() or len(v) != 11):
            raise ValueError("CPF deve conter exatamente 11 dígitos numéricos")
        return v

    @field_validator('legal_rep_rg_number')
    def validar_rg_numero(cls, v):
        if v and not v.isdigit():
            raise ValueError("RG deve conter apenas números")
        return v

    @field_validator('legal_rep_birth_date')
    def validar_data_nascimento(cls, v):
        if v and v > date.today():
            raise ValueError("Data de nascimento não pode ser futura")
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
            raise ValueError("Pelo menos uma categoria de produto deve ser selecionada")
        return v
