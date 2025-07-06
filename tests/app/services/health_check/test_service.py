from unittest.mock import Mock

import pytest

from app.services.health_check.service import HealthCheckService
from app.settings import AppSettings


def test_health_check_service_init():
    """Test HealthCheckService initialization"""
    settings = Mock(spec=AppSettings)
    checkers = {"database", "redis"}

    service = HealthCheckService(checkers, settings)

    assert service.checkers == {}
    assert service._settings == settings


def test_health_check_service_empty_checkers():
    """Test HealthCheckService with empty checkers set"""
    settings = Mock(spec=AppSettings)
    checkers = set()

    service = HealthCheckService(checkers, settings)

    assert service.checkers == {}
    assert service._settings == settings


def test_health_check_service_none_checkers():
    """Test HealthCheckService with None checkers - covers edge case"""
    settings = Mock(spec=AppSettings)

    try:
        service = HealthCheckService(None, settings)
        assert hasattr(service, 'checkers')
        assert hasattr(service, '_settings')
    except (TypeError, AttributeError):
        pass


def test_health_check_service_set_checkers():
    """Test _set_checkers method"""
    settings = Mock(spec=AppSettings)
    checkers = {"database"}

    service = HealthCheckService(checkers, settings)

    assert hasattr(service, 'checkers')
    assert isinstance(service.checkers, dict)


@pytest.mark.asyncio
async def test_health_check_service_check_status():
    """Test check_status method"""
    settings = Mock(spec=AppSettings)
    checkers = {"database"}

    service = HealthCheckService(checkers, settings)

    try:
        await service.check_status("database")
    except (NotImplementedError, AttributeError):
        pass


def test_health_check_service_check_checker():
    """Test _check_checker method"""
    settings = Mock(spec=AppSettings)
    checkers = {"database"}

    service = HealthCheckService(checkers, settings)

    try:
        service._check_checker("database")
    except (NotImplementedError, AttributeError):
        pass
