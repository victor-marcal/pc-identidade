import pytest
from pydantic import ValidationError

from app.common.error_schema import ErrorDetail, ErrorLocation, ErrorResponse


def test_error_detail_creation():
    """Test ErrorDetail model creation with required fields"""
    error_detail = ErrorDetail(message="Test error message")

    assert error_detail.message == "Test error message"
    assert error_detail.location is None
    assert error_detail.slug is None
    assert error_detail.field is None
    assert error_detail.ctx is None


def test_error_detail_with_all_fields():
    """Test ErrorDetail model creation with all fields"""
    error_detail = ErrorDetail(
        message="Test error message", location="body", slug="test-error", field="username", ctx={"min_length": 3}
    )

    assert error_detail.message == "Test error message"
    assert error_detail.location == "body"
    assert error_detail.slug == "test-error"
    assert error_detail.field == "username"
    assert error_detail.ctx == {"min_length": 3}


def test_error_detail_invalid_location():
    """Test ErrorDetail with invalid location"""
    with pytest.raises(ValidationError):
        ErrorDetail(message="Test error", location="invalid_location")  # type: ignore


def test_error_detail_valid_locations():
    """Test ErrorDetail with all valid locations"""
    valid_locations = ["query", "path", "body", "header"]

    for location in valid_locations:
        error_detail = ErrorDetail(message="Test error", location=location)  # type: ignore
        assert error_detail.location == location


def test_error_response_creation():
    """Test ErrorResponse model creation with required fields"""
    error_response = ErrorResponse(slug="test-error", message="Test error message", details=None)

    assert error_response.slug == "test-error"
    assert error_response.message == "Test error message"
    assert error_response.details is None


def test_error_response_with_details():
    """Test ErrorResponse model creation with details"""
    error_detail = ErrorDetail(message="Detail error message")
    error_response = ErrorResponse(slug="test-error", message="Test error message", details=[error_detail])

    assert error_response.slug == "test-error"
    assert error_response.message == "Test error message"
    assert len(error_response.details) == 1
    assert error_response.details[0].message == "Detail error message"


def test_error_response_missing_required_fields():
    """Test ErrorResponse validation with missing required fields"""
    with pytest.raises(ValidationError):
        ErrorResponse()  # type: ignore


def test_error_response_json_serialization():
    """Test ErrorResponse JSON serialization"""
    error_detail = ErrorDetail(message="Detail error", location="body", field="username")
    error_response = ErrorResponse(slug="validation-error", message="Validation failed", details=[error_detail])

    json_data = error_response.model_dump()

    assert json_data["slug"] == "validation-error"
    assert json_data["message"] == "Validation failed"
    assert len(json_data["details"]) == 1
    assert json_data["details"][0]["message"] == "Detail error"
    assert json_data["details"][0]["location"] == "body"
    assert json_data["details"][0]["field"] == "username"


def test_error_location_type():
    """Test ErrorLocation type definition"""
    # Test that we can create ErrorDetail with valid locations
    valid_locations = ["query", "path", "body", "header"]

    for location in valid_locations:
        error_detail = ErrorDetail(message="Test error", location=location)  # type: ignore
        assert error_detail.location == location
