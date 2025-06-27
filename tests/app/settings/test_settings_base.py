import pytest
from unittest.mock import patch
from enum import StrEnum
from app.settings.base import EnvironmentEnum, BaseSettings, ENV_FILE, ENV_FILES


def test_environment_enum_values():
    """Test EnvironmentEnum values"""
    assert EnvironmentEnum.DEVELOPMENT == "dev"
    assert EnvironmentEnum.PRODUCTION == "prod"
    assert EnvironmentEnum.TEST == "test"
    
    # Test that it's a StrEnum
    assert issubclass(EnvironmentEnum, StrEnum)


def test_environment_enum_properties():
    """Test EnvironmentEnum properties"""
    # Test is_test
    assert EnvironmentEnum.TEST.is_test is True
    assert EnvironmentEnum.DEVELOPMENT.is_test is False
    assert EnvironmentEnum.PRODUCTION.is_test is False
    
    # Test is_production
    assert EnvironmentEnum.PRODUCTION.is_production is True
    assert EnvironmentEnum.DEVELOPMENT.is_production is False
    assert EnvironmentEnum.TEST.is_production is False
    
    # Test is_development
    assert EnvironmentEnum.DEVELOPMENT.is_development is True
    assert EnvironmentEnum.PRODUCTION.is_development is False
    assert EnvironmentEnum.TEST.is_development is False


def test_env_files_mapping():
    """Test ENV_FILES mapping"""
    assert ENV_FILES["dev"] == "dotenv.dev"
    assert ENV_FILES["prod"] == "dotenv.prod"
    assert ENV_FILES["test"] == "dotenv.test"


@patch.dict('os.environ', {'ENV': 'dev'})
def test_env_file_dev():
    """Test ENV_FILE generation for dev environment"""
    from importlib import reload
    from app.settings import base
    reload(base)
    
    assert base.ENV_FILE == "devtools/dotenv.dev"


@patch.dict('os.environ', {'ENV': 'test'})
def test_env_file_test():
    """Test ENV_FILE generation for test environment"""
    from importlib import reload
    from app.settings import base
    reload(base)
    
    assert base.ENV_FILE == "devtools/dotenv.test"


@patch.dict('os.environ', {'ENV': 'prod'})
def test_env_file_prod():
    """Test ENV_FILE generation for prod environment"""
    from importlib import reload
    from app.settings import base
    reload(base)
    
    assert base.ENV_FILE == "devtools/dotenv.prod"


def test_base_settings_default_values():
    """Test BaseSettings default values"""
    # When ENV=test, the environment should be TEST
    settings = BaseSettings()
    
    # In test environment, env should be TEST
    assert settings.env == EnvironmentEnum.TEST
    assert isinstance(settings.env_file, str)


def test_base_settings_env_override():
    """Test BaseSettings with environment override"""
    settings = BaseSettings(env=EnvironmentEnum.PRODUCTION)
    
    assert settings.env == EnvironmentEnum.PRODUCTION


def test_base_settings_model_config():
    """Test BaseSettings model configuration"""
    config = BaseSettings.model_config
    
    assert config["env_file_encoding"] == "utf-8"
    assert config["env_nested_delimiter"] == "__"
    assert config["validate_default"] is True
    assert config["extra"] == "ignore"


def test_base_settings_sources_customization():
    """Test settings sources customization"""
    from pydantic_settings import PydanticBaseSettingsSource
    from unittest.mock import MagicMock
    
    # Mock the source objects
    init_settings = MagicMock(spec=PydanticBaseSettingsSource)
    env_settings = MagicMock(spec=PydanticBaseSettingsSource)
    dotenv_settings = MagicMock(spec=PydanticBaseSettingsSource)
    file_secret_settings = MagicMock(spec=PydanticBaseSettingsSource)
    
    sources = BaseSettings.settings_customise_sources(
        BaseSettings,
        init_settings,
        env_settings,
        dotenv_settings,
        file_secret_settings
    )
    
    # Verify the order of sources
    assert sources[0] == init_settings
    assert sources[1] == env_settings
    assert sources[2] == dotenv_settings
    assert sources[3] == file_secret_settings


def test_base_settings_with_env_file():
    """Test BaseSettings with custom env_file"""
    settings = BaseSettings(env_file="custom.env")
    
    assert settings.env_file == "custom.env"


def test_base_settings_inheritance():
    """Test that BaseSettings can be inherited"""
    class CustomSettings(BaseSettings):
        custom_field: str = "default_value"
    
    settings = CustomSettings()
    
    assert hasattr(settings, 'env')
    assert hasattr(settings, 'env_file')
    assert hasattr(settings, 'custom_field')
    assert settings.custom_field == "default_value"


@patch.dict('os.environ', {'ENV': 'invalid'}, clear=True)
def test_invalid_env_raises_error():
    """Test that invalid ENV raises ValueError"""
    with pytest.raises(ValueError, match="ENV must be either 'dev', 'prod' or 'test'"):
        from importlib import reload
        from app.settings import base
        reload(base)
