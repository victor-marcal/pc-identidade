"""
Test health check exceptions following SOLID principles and clean code practices.
"""

import pytest

from app.services.health_check.exceptions import (
    HealthCheckException,
    InvalidConfigurationException,
    ServiceReturnedUnexpectedResult,
    ServiceUnavailable,
    ServiceWarning,
)


class TestHealthCheckException:
    """Test suite for HealthCheckException - follows Single Responsibility Principle"""

    def test_health_check_exception_init(self):
        """Test HealthCheckException initialization"""
        message = "Test error"
        exception = HealthCheckException(message)

        assert exception.message == message
        assert exception.message_type == "unknown error"

    def test_health_check_exception_str(self):
        """Test HealthCheckException string representation"""
        message = "Test error"
        exception = HealthCheckException(message)

        result = str(exception)

        assert result == "unknown error: Test error"

    def test_health_check_exception_inheritance(self):
        """Test HealthCheckException inherits from Exception"""
        exception = HealthCheckException("test")

        assert isinstance(exception, Exception)


class TestInvalidConfigurationException:
    """Test suite for InvalidConfigurationException - follows Open/Closed Principle"""

    def test_invalid_configuration_exception_init(self):
        """Test InvalidConfigurationException initialization"""
        message = "Invalid config"
        exception = InvalidConfigurationException(message)

        assert exception.message == message
        assert exception.message_type == "unexpected configuration"

    def test_invalid_configuration_exception_str(self):
        """Test InvalidConfigurationException string representation"""
        message = "Invalid config"
        exception = InvalidConfigurationException(message)

        result = str(exception)

        assert result == "unexpected configuration: Invalid config"

    def test_invalid_configuration_exception_inheritance(self):
        """Test InvalidConfigurationException inherits from HealthCheckException"""
        exception = InvalidConfigurationException("test")

        assert isinstance(exception, HealthCheckException)


class TestServiceWarning:
    """Test suite for ServiceWarning - follows Liskov Substitution Principle"""

    def test_service_warning_init(self):
        """Test ServiceWarning initialization"""
        message = "Service warning"
        exception = ServiceWarning(message)

        assert exception.message == message
        assert exception.message_type == "warning"

    def test_service_warning_str(self):
        """Test ServiceWarning string representation"""
        message = "Service warning"
        exception = ServiceWarning(message)

        result = str(exception)

        assert result == "warning: Service warning"

    def test_service_warning_inheritance(self):
        """Test ServiceWarning inherits from HealthCheckException"""
        exception = ServiceWarning("test")

        assert isinstance(exception, HealthCheckException)


class TestServiceUnavailable:
    """Test suite for ServiceUnavailable"""

    def test_service_unavailable_init(self):
        """Test ServiceUnavailable initialization"""
        message = "Service down"
        exception = ServiceUnavailable(message)

        assert exception.message == message
        assert exception.message_type == "unavailable"

    def test_service_unavailable_str(self):
        """Test ServiceUnavailable string representation"""
        message = "Service down"
        exception = ServiceUnavailable(message)

        result = str(exception)

        assert result == "unavailable: Service down"

    def test_service_unavailable_inheritance(self):
        """Test ServiceUnavailable inherits from HealthCheckException"""
        exception = ServiceUnavailable("test")

        assert isinstance(exception, HealthCheckException)


class TestServiceReturnedUnexpectedResult:
    """Test suite for ServiceReturnedUnexpectedResult"""

    def test_service_returned_unexpected_result_init(self):
        """Test ServiceReturnedUnexpectedResult initialization"""
        message = "Unexpected response"
        exception = ServiceReturnedUnexpectedResult(message)

        assert exception.message == message
        assert exception.message_type == "unexpected result"

    def test_service_returned_unexpected_result_str(self):
        """Test ServiceReturnedUnexpectedResult string representation"""
        message = "Unexpected response"
        exception = ServiceReturnedUnexpectedResult(message)

        result = str(exception)

        assert result == "unexpected result: Unexpected response"

    def test_service_returned_unexpected_result_inheritance(self):
        """Test ServiceReturnedUnexpectedResult inherits from HealthCheckException"""
        exception = ServiceReturnedUnexpectedResult("test")

        assert isinstance(exception, HealthCheckException)


class TestModuleExports:
    """Test module exports - follows Interface Segregation Principle"""

    def test_module_all_exports(self):
        """Test that all expected classes are exported in __all__"""
        from app.services.health_check import exceptions

        expected_exports = [
            "HealthCheckException",
            "ServiceWarning",
            "ServiceUnavailable",
            "ServiceReturnedUnexpectedResult",
        ]

        assert hasattr(exceptions, '__all__')
        assert all(export in exceptions.__all__ for export in expected_exports)

    def test_all_classes_accessible(self):
        """Test that all classes are accessible through the module"""
        from app.services.health_check import exceptions

        assert hasattr(exceptions, 'HealthCheckException')
        assert hasattr(exceptions, 'InvalidConfigurationException')
        assert hasattr(exceptions, 'ServiceWarning')
        assert hasattr(exceptions, 'ServiceUnavailable')
        assert hasattr(exceptions, 'ServiceReturnedUnexpectedResult')
