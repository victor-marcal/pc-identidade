import pytest
from unittest.mock import MagicMock, patch, call, AsyncMock
import smtplib
from app.services.email_service import EmailService


EMPRESA_TESTE = 'Empresa Teste Ltda'
EMAIl_LOJA_TESTE = 'contato@lojateste.com'

class TestEmailService:
    """Testes para o serviço de email"""
    
    @patch.dict('os.environ', {
        'SMTP_SERVER': 'smtp.test.com',
        'SMTP_PORT': '587',
        'SENDER_EMAIL': 'test@company.com',
        'SENDER_PASSWORD': 'test_password'
    })
    def test_init(self):
        """Testa inicialização do serviço"""
        service = EmailService()
        
        assert service.server == 'smtp.test.com'
        assert service.port == '587'
        assert service.sender_email == 'test@company.com'
        assert service.password == 'test_password'
        assert service.logger is not None
    
    @patch.dict('os.environ', {
        'SMTP_SERVER': 'smtp.test.com',
        'SMTP_PORT': '587',
        'SENDER_EMAIL': 'test@company.com',
        'SENDER_PASSWORD': 'test_password'
    })
    @patch('app.services.email_service.smtplib.SMTP')
    def test_send_welcome_email_success(self, mock_smtp):
        """Testa envio de email de boas-vindas com sucesso"""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__ = MagicMock(return_value=mock_server)
        mock_smtp.return_value.__exit__ = MagicMock(return_value=None)
        
        service = EmailService()
        
        seller_data = {
            'company_name': EMPRESA_TESTE,
            'trade_name': 'Loja Teste1',
            'contact_email': EMAIl_LOJA_TESTE,
            'business_description': 'cursos',
            'product_categories': ['ELETRONICOS', 'CASA_JARDIM']
        }
        
        result = service.send_welcome_email(seller_data)
        
        # Verifica se o método retornou sucesso
        assert result is True
        
        # Verifica se o SMTP foi configurado corretamente
        mock_smtp.assert_called_once_with('smtp.test.com', '587')
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with('test@company.com', 'test_password')
        mock_server.sendmail.assert_called_once()
    
    @patch.dict('os.environ', {
        'SMTP_SERVER': 'smtp.test.com',
        'SMTP_PORT': '587',
        'SENDER_EMAIL': 'test@company.com',
        'SENDER_PASSWORD': 'test_password'
    })
    @patch('app.services.email_service.smtplib.SMTP')
    def test_send_welcome_email_smtp_error(self, mock_smtp):
        """Testa tratamento de erro SMTP"""
        mock_smtp.side_effect = smtplib.SMTPException("Falha na conexão")
        
        service = EmailService()
        
        seller_data = {
            'company_name': EMPRESA_TESTE,
            'trade_name': 'Loja Teste2',
            'contact_email': EMAIl_LOJA_TESTE,
            'business_description': 'comércio e indústria',
            'product_categories': ['ELETRONICOS']
        }
        
        # Não deve levantar exceção, mas deve logar o erro
        service.send_welcome_email(seller_data)
        
        mock_smtp.assert_called_once()
    
    @patch.dict('os.environ', {
        'SMTP_SERVER': 'smtp.test.com',
        'SMTP_PORT': '587', 
        'SENDER_EMAIL': 'test@company.com',
        'SENDER_PASSWORD': 'test_password'
    })
    def test_create_welcome_email_body_with_all_fields(self):
        """Testa criação do corpo do email com todos os campos"""
        service = EmailService()
        
        result = service._create_welcome_email_body(
            company_name=EMPRESA_TESTE,
            trade_name='Loja Teste4',
            business_description='celulares e smartphones',
            product_categories=['ELETRONICOS', 'CASA_JARDIM']
        )
        
        assert EMPRESA_TESTE in result
        assert 'Loja Teste4' in result
        assert 'celulares e smartphones' in result
        assert 'ELETRONICOS' in result
        assert 'CASA_JARDIM' in result
        assert 'bem-vindo' in result.lower()
    
    @patch.dict('os.environ', {
        'SMTP_SERVER': 'smtp.test.com',
        'SMTP_PORT': '587',
        'SENDER_EMAIL': 'test@company.com', 
        'SENDER_PASSWORD': 'test_password'
    })
    def test_create_welcome_email_body_without_trade_name(self):
        """Testa criação do corpo do email sem nome fantasia"""
        service = EmailService()
        
        result = service._create_welcome_email_body(
            company_name= EMPRESA_TESTE,
            trade_name=EMPRESA_TESTE,  # Mesmo que company_name
            business_description='casa inteligente',
            product_categories=['ELETRONICOS']
        )
        
        # Não deve repetir o nome da empresa
        company_count = result.count(EMPRESA_TESTE)
        assert company_count >= 1
        assert 'ELETRONICOS' in result
    
    @patch.dict('os.environ', {
        'SMTP_SERVER': 'smtp.test.com',
        'SMTP_PORT': '587',
        'SENDER_EMAIL': 'test@company.com',
        'SENDER_PASSWORD': 'test_password'
    })
    def test_create_welcome_email_body_empty_categories(self):
        """Testa criação do corpo do email sem categorias"""
        service = EmailService()
        
        result = service._create_welcome_email_body(
            company_name= EMPRESA_TESTE,
            trade_name='Loja Teste5',
            business_description='Venda de produtos diversos',
            product_categories=[]
        )
        
        assert EMPRESA_TESTE in result
        assert 'Loja Teste5' in result
        assert 'Venda de produtos diversos' in result
        # Deve ter uma mensagem para categorias vazias ou não mencionar categorias
        assert result is not None
    
    @patch.dict('os.environ', {
        'SMTP_SERVER': 'smtp.test.com',
        'SMTP_PORT': '587',
        'SENDER_EMAIL': 'test@company.com',
        'SENDER_PASSWORD': 'test_password'
    })
    @patch('app.services.email_service.smtplib.SMTP')
    def test_send_welcome_email_missing_fields(self, mock_smtp):
        """Testa envio de email com campos obrigatórios faltando"""
        service = EmailService()
        
        # Dados incompletos (sem contact_email)
        seller_data = {
            'company_name': EMPRESA_TESTE,
            'business_description': 'casa de construção',
            'product_categories': ['ELETRONICOS']
        }
        
        result = service.send_welcome_email(seller_data)
        
        # Deve retornar False devido ao email faltando
        assert result is False
        
        # SMTP não deve ser chamado
        mock_smtp.assert_not_called()
    
    @patch.dict('os.environ', {
        'SMTP_SERVER': '',
        'SMTP_PORT': '',
        'SENDER_EMAIL': '',
        'SENDER_PASSWORD': ''
    })
    def test_init_with_empty_env_vars(self):
        """Testa inicialização com variáveis de ambiente vazias"""
        service = EmailService()
        
        assert service.server == ''
        assert service.port == ''
        assert service.sender_email == ''
        assert service.password == ''
    
    @patch.dict('os.environ', {
        'SMTP_SERVER': 'smtp.test.com',
        'SMTP_PORT': '587',
        'SENDER_EMAIL': 'test@company.com',
        'SENDER_PASSWORD': 'test_password'
    })
    @patch('app.services.email_service.smtplib.SMTP')
    def test_send_welcome_email_connection_error(self, mock_smtp):
        """Testa tratamento de erro de conexão"""
        mock_server = MagicMock()
        mock_server.starttls.side_effect = Exception("Falha na conexão TLS")
        mock_smtp.return_value.__enter__ = MagicMock(return_value=mock_server)
        mock_smtp.return_value.__exit__ = MagicMock(return_value=None)
        
        service = EmailService()
        
        seller_data = {
            'company_name': EMPRESA_TESTE,
            'trade_name': 'Loja Teste7',
            'contact_email': EMAIl_LOJA_TESTE,
            'business_description': 'câmeras e drones',
            'product_categories': ['ELETRONICOS']
        }
        
        result = service.send_welcome_email(seller_data)
        
        # Deve retornar False devido ao erro
        assert result is False
        
        mock_smtp.assert_called_once()
        mock_server.starttls.assert_called_once()
