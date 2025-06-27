import pytest
from app.common.exceptions.application_exception import ApplicationException
from app.common.exceptions.unauthorized_exception import UnauthorizedException
from app.common.error_codes import ErrorCodes


def test_application_exception_with_error_info():
    """Test ApplicationException with ErrorInfo - follows Interface Segregation Principle"""
    error_info = ErrorCodes.BAD_REQUEST.value
    exception = ApplicationException(error_info)
    
    assert exception.slug == "BAD_REQUEST"
    assert exception.message == "Bad Request"
    assert exception.status_code == 400


def test_application_exception_with_custom_message():
    """Test ApplicationException with custom message"""
    error_info = ErrorCodes.BAD_REQUEST.value
    custom_message = "Custom error message"
    exception = ApplicationException(error_info, message=custom_message)
    
    assert exception.slug == "BAD_REQUEST"
    assert exception.message == custom_message
    assert exception.status_code == 400


def test_application_exception_with_details():
    """Test ApplicationException with details"""
    from app.api.common.schemas.response import ErrorDetail
    
    error_info = ErrorCodes.BAD_REQUEST.value
    details = [ErrorDetail(message="Field error", location="body", slug="field_error", field="name")]
    exception = ApplicationException(error_info, details=details)
    
    assert exception.details == details
    assert len(exception.details) == 1


def test_unauthorized_exception_default():
    """Test UnauthorizedException with default values - follows Open/Closed Principle"""
    exception = UnauthorizedException()
    
    assert exception.slug == "UNAUTHORIZED"
    assert exception.message == "Unauthorized"
    assert exception.status_code == 401


def test_unauthorized_exception_custom_message():
    """Test UnauthorizedException with custom message"""
    custom_message = "Custom authorization error"
    exception = UnauthorizedException(message=custom_message)
    
    assert exception.slug == "UNAUTHORIZED"
    assert exception.message == custom_message
    assert exception.status_code == 401


def test_unauthorized_exception_with_details():
    """Test UnauthorizedException with details"""
    from app.api.common.schemas.response import ErrorDetail
    
    details = [ErrorDetail(message="Token expired", location="header", slug="token_error", field="authorization")]
    exception = UnauthorizedException(details=details, message="Token validation failed")
    
    assert exception.details == details
    assert exception.message == "Token validation failed"
    assert exception.status_code == 401


def test_error_codes_properties():
    """Test ErrorCodes enum properties"""
    bad_request = ErrorCodes.BAD_REQUEST
    
    assert bad_request.slug == "BAD_REQUEST"
    assert bad_request.message == "Bad Request"
    assert bad_request.http_code == 400


def test_error_codes_unauthorized():
    """Test UNAUTHORIZED error code"""
    unauthorized = ErrorCodes.UNAUTHORIZED
    
    assert unauthorized.slug == "UNAUTHORIZED"
    assert unauthorized.message == "Unauthorized"
    assert unauthorized.http_code == 401


def test_error_codes_not_found():
    """Test NOT_FOUND error code"""
    not_found = ErrorCodes.NOT_FOUND
    
    assert not_found.slug == "NOT_FOUND"
    assert not_found.message == "Not found"
    assert not_found.http_code == 404
