import pytest
from pydantic import ValidationError

from app.common.error_schema import ErrorDetail, ErrorLocation, ErrorResponse

# Dicionário com constantes para evitar duplicação
TEST_ERROR_DATA = {
    "test_error_message": "Test error message",
    "test_error": "Test error",
    "detail_error_message": "Detail error message",
    "detail_error": "Detail error",
    "validation_error": "validation-error",
    "validation_failed": "Validation failed",
    "test_error_slug": "test-error",
    "username": "username",
    "body": "body",
    "query": "query",
    "path": "path",
    "header": "header",
    "invalid_location": "invalid_location",
}


def test_error_detail_creation():
    """Test ErrorDetail model creation with required fields"""
    error_detail = ErrorDetail(message=TEST_ERROR_DATA["test_error_message"])

    assert error_detail.message == TEST_ERROR_DATA["test_error_message"]
    assert error_detail.location is None
    assert error_detail.slug is None
    assert error_detail.field is None
    assert error_detail.ctx is None


def test_error_detail_with_all_fields():
    """Test ErrorDetail model creation with all fields"""
    error_detail = ErrorDetail(
        message=TEST_ERROR_DATA["test_error_message"],
        location=TEST_ERROR_DATA["body"],
        slug=TEST_ERROR_DATA["test_error_slug"],
        field=TEST_ERROR_DATA["username"],
        ctx={"min_length": 3},
    )

    assert error_detail.message == TEST_ERROR_DATA["test_error_message"]
    assert error_detail.location == TEST_ERROR_DATA["body"]
    assert error_detail.slug == TEST_ERROR_DATA["test_error_slug"]
    assert error_detail.field == TEST_ERROR_DATA["username"]
    assert error_detail.ctx == {"min_length": 3}


def test_error_detail_invalid_location():
    """Test ErrorDetail with invalid location"""
    with pytest.raises(ValidationError):
        ErrorDetail(message=TEST_ERROR_DATA["test_error"], location=TEST_ERROR_DATA["invalid_location"])  # type: ignore


def test_error_detail_valid_locations():
    """Test ErrorDetail with all valid locations"""
    valid_locations = [
        TEST_ERROR_DATA["query"],
        TEST_ERROR_DATA["path"],
        TEST_ERROR_DATA["body"],
        TEST_ERROR_DATA["header"],
    ]

    for location in valid_locations:
        error_detail = ErrorDetail(message=TEST_ERROR_DATA["test_error"], location=location)  # type: ignore
        assert error_detail.location == location


def test_error_response_creation():
    """Test ErrorResponse model creation with required fields"""
    error_response = ErrorResponse(
        slug=TEST_ERROR_DATA["test_error_slug"], message=TEST_ERROR_DATA["test_error_message"], details=None
    )

    assert error_response.slug == TEST_ERROR_DATA["test_error_slug"]
    assert error_response.message == TEST_ERROR_DATA["test_error_message"]
    assert error_response.details is None


def test_error_response_with_details():
    """Test ErrorResponse model creation with details"""
    error_detail = ErrorDetail(message=TEST_ERROR_DATA["detail_error_message"])
    error_response = ErrorResponse(
        slug=TEST_ERROR_DATA["test_error_slug"], message=TEST_ERROR_DATA["test_error_message"], details=[error_detail]
    )

    assert error_response.slug == TEST_ERROR_DATA["test_error_slug"]
    assert error_response.message == TEST_ERROR_DATA["test_error_message"]
    assert len(error_response.details) == 1
    assert error_response.details[0].message == TEST_ERROR_DATA["detail_error_message"]


def test_error_response_missing_required_fields():
    """Test ErrorResponse validation with missing required fields"""
    with pytest.raises(ValidationError):
        ErrorResponse()  # type: ignore


def test_error_response_json_serialization():
    """Test ErrorResponse JSON serialization"""
    error_detail = ErrorDetail(
        message=TEST_ERROR_DATA["detail_error"], location=TEST_ERROR_DATA["body"], field=TEST_ERROR_DATA["username"]
    )
    error_response = ErrorResponse(
        slug=TEST_ERROR_DATA["validation_error"], message=TEST_ERROR_DATA["validation_failed"], details=[error_detail]
    )

    json_data = error_response.model_dump()

    assert json_data["slug"] == TEST_ERROR_DATA["validation_error"]
    assert json_data["message"] == TEST_ERROR_DATA["validation_failed"]
    assert len(json_data["details"]) == 1
    assert json_data["details"][0]["message"] == TEST_ERROR_DATA["detail_error"]
    assert json_data["details"][0]["location"] == TEST_ERROR_DATA["body"]
    assert json_data["details"][0]["field"] == TEST_ERROR_DATA["username"]


def test_error_location_type():
    """Test ErrorLocation type definition"""
    # Test that we can create ErrorDetail with valid locations
    valid_locations = [
        TEST_ERROR_DATA["query"],
        TEST_ERROR_DATA["path"],
        TEST_ERROR_DATA["body"],
        TEST_ERROR_DATA["header"],
    ]

    for location in valid_locations:
        error_detail = ErrorDetail(message=TEST_ERROR_DATA["test_error"], location=location)  # type: ignore
        assert error_detail.location == location
