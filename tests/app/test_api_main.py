"""
Testes completos para app.api_main.py
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from fastapi import FastAPI, Request
from fastapi.responses import Response
import os
import time
import logging


class TestApiMain:
    """Testes para o módulo api_main.py"""
    
    def test_init_creates_fastapi_app(self):
        """Test that init() creates a FastAPI application"""
        from app.api_main import init

        app = init()

        assert isinstance(app, FastAPI)
        assert hasattr(app, 'container')

    def test_app_is_fastapi_instance(self):
        """Test that the app variable is a FastAPI instance"""
        from app.api_main import app

        assert isinstance(app, FastAPI)
        assert hasattr(app, 'container')
    
    @patch('app.api_main.dotenv.load_dotenv')
    @patch('app.api_main.LoggingBuilder.init')
    @patch('app.api_main.logging.basicConfig')
    def test_module_initialization(self, mock_basicConfig, mock_logging_init, mock_load_dotenv):
        """Testa inicialização do módulo api_main"""
        # Reimportar para trigger da inicialização
        import importlib
        import app.api_main
        importlib.reload(app.api_main)
        
        # Verificar se as funções foram chamadas
        mock_logging_init.assert_called_once()
        mock_basicConfig.assert_called_once()
        mock_load_dotenv.assert_called_once()
    
    @patch.dict(os.environ, {"ENV": "dev"})
    @patch('app.api_main.dotenv.load_dotenv')
    def test_dev_environment_dotenv_override(self, mock_load_dotenv):
        """Testa se em ambiente dev o dotenv é carregado com override"""
        import importlib
        import app.api_main
        importlib.reload(app.api_main)
        
        mock_load_dotenv.assert_called_once_with(override=True)
    
    @patch.dict(os.environ, {"ENV": "production"})
    @patch('app.api_main.dotenv.load_dotenv')
    def test_production_environment_dotenv_no_override(self, mock_load_dotenv):
        """Testa se em ambiente production o dotenv é carregado sem override"""
        import importlib
        import app.api_main
        importlib.reload(app.api_main)
        
        mock_load_dotenv.assert_called_once_with(override=False)
    
    @patch.dict(os.environ, {}, clear=True)
    @patch('app.api_main.dotenv.load_dotenv')
    def test_default_environment_dotenv_no_override(self, mock_load_dotenv):
        """Testa se sem ENV definido o default é production"""
        import importlib
        import app.api_main
        importlib.reload(app.api_main)
        
        mock_load_dotenv.assert_called_once_with(override=False)
    
    @pytest.mark.asyncio
    async def test_log_requests_middleware_success(self):
        """Testa middleware de log para requisições bem-sucedidas"""
        from app.api_main import log_requests_middleware
        
        # Mock request
        request = Mock(spec=Request)
        request.method = "GET"
        request.url.path = "/test"
        
        # Mock response
        response = Mock(spec=Response)
        response.status_code = 200
        
        # Mock call_next
        call_next = AsyncMock(return_value=response)
        
        # Mock logger
        with patch('app.api_main.logger') as mock_logger:
            result = await log_requests_middleware(request, call_next)
            
            assert result is response
            call_next.assert_called_once_with(request)
            
            # Verificar logs
            assert mock_logger.info.call_count == 2
            mock_logger.info.assert_any_call("Requisição recebida: GET /test")
            
            # Verificar log de finalização (deve conter duração)
            final_log_call = mock_logger.info.call_args_list[1]
            assert "Requisição finalizada: GET /test - Status: 200 - Duração:" in final_log_call[0][0]
            assert "ms" in final_log_call[0][0]
    
    @pytest.mark.asyncio
    async def test_log_requests_middleware_error(self):
        """Testa middleware de log para requisições com erro"""
        from app.api_main import log_requests_middleware
        
        # Mock request
        request = Mock(spec=Request)
        request.method = "POST"
        request.url.path = "/error"
        
        # Mock response com erro
        response = Mock(spec=Response)
        response.status_code = 500
        
        # Mock call_next
        call_next = AsyncMock(return_value=response)
        
        # Mock logger
        with patch('app.api_main.logger') as mock_logger:
            result = await log_requests_middleware(request, call_next)
            
            assert result is response
            call_next.assert_called_once_with(request)
            
            # Verificar logs
            assert mock_logger.info.call_count == 2
            mock_logger.info.assert_any_call("Requisição recebida: POST /error")
            
            # Verificar log de finalização com status 500
            final_log_call = mock_logger.info.call_args_list[1]
            assert "Requisição finalizada: POST /error - Status: 500 - Duração:" in final_log_call[0][0]
    
    @patch('app.api.api_application.create_app')
    @patch('app.api_main.Container')
    @patch('app.api_main.api_settings')
    def test_init_function(self, mock_api_settings, mock_container_class, mock_create_app):
        """Testa função init()"""
        from app.api_main import init
        
        # Mock container instance
        mock_container = Mock()
        mock_container_class.return_value = mock_container
        
        # Mock app
        mock_app = Mock(spec=FastAPI)
        mock_create_app.return_value = mock_app
        
        # Mock api_routes
        with patch('app.api.router.routes') as mock_api_routes:
            result = init()
            
            # Verificar se container foi criado
            mock_container_class.assert_called_once()
            
            # Verificar se config foi definida
            mock_container.config.from_pydantic.assert_called_once_with(mock_api_settings)
            
            # Verificar se app foi criada
            mock_create_app.assert_called_once_with(mock_api_settings, mock_api_routes)
            
            # Verificar se container foi atribuído ao app
            assert mock_app.container is mock_container
            
            # Verificar se middleware foi adicionado
            mock_app.add_middleware.assert_called_once()
            
            # Verificar se wiring foi feito
            assert mock_container.wire.call_count == 4
            
            # Verificar se resultado é o app mockado
            assert result is mock_app
    
    def test_logger_creation(self):
        """Testa se o logger é criado corretamente"""
        from app.api_main import logger
        
        assert logger is not None
        assert isinstance(logger, logging.Logger)
        assert logger.name == "app.api_main"
    
    def test_env_variable_handling(self):
        """Testa tratamento da variável ENV"""
        from app.api_main import ENV, is_dev
        
        # ENV deve ser string
        assert isinstance(ENV, str)
        
        # is_dev deve ser boolean
        assert isinstance(is_dev, bool)
        
        # is_dev deve ser True apenas se ENV == "dev"
        if ENV == "dev":
            assert is_dev is True
        else:
            assert is_dev is False


@patch.dict('os.environ', {'ENV': 'dev'})
@patch('app.api_main.dotenv.load_dotenv')
def test_dev_environment_loads_dotenv_with_override(mock_load_dotenv):
    """Test that in dev environment, dotenv is loaded with override=True"""
    # Need to reload the module to test dotenv loading behavior
    import importlib

    import app.api_main

    importlib.reload(app.api_main)

    mock_load_dotenv.assert_called_once_with(override=True)


@patch.dict('os.environ', {'ENV': 'production'})
@patch('app.api_main.dotenv.load_dotenv')
def test_production_environment_loads_dotenv_without_override(mock_load_dotenv):
    """Test that in production environment, dotenv is loaded with override=False"""
    # Need to reload the module to test dotenv loading behavior
    import importlib

    import app.api_main

    importlib.reload(app.api_main)

    mock_load_dotenv.assert_called_once_with(override=False)


@patch.dict('os.environ', {}, clear=True)
@patch('app.api_main.dotenv.load_dotenv')
def test_default_environment_is_production(mock_load_dotenv):
    """Test that when ENV is not set, it defaults to production"""
    # Need to reload the module to test dotenv loading behavior
    import importlib

    import app.api_main

    importlib.reload(app.api_main)

    mock_load_dotenv.assert_called_once_with(override=False)


def test_container_wiring():
    """Test that the container is properly wired with the expected modules"""
    from app.api_main import init

    app = init()
    container = app.container

    # Verify container exists and has config
    assert hasattr(container, 'config')
    assert hasattr(container, 'wire')
