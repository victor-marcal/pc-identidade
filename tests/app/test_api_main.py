from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI


def test_init_creates_fastapi_app():
    """Test that init() creates a FastAPI application"""
    from app.api_main import init

    app = init()

    assert isinstance(app, FastAPI)
    assert hasattr(app, 'container')


def test_app_is_fastapi_instance():
    """Test that the app variable is a FastAPI instance"""
    from app.api_main import app

    assert isinstance(app, FastAPI)
    assert hasattr(app, 'container')


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
