from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.api.common.error_handlers import add_error_handlers, extract_error_detail, extract_error_detail_body

DEFAULT_MENSAGE = {
    "msgfield": "field required",
    "error": "test error",
    "msgValidation": "validation error",
    "msgTest": "test message",
}

DEFAULT_PAGINATION = {
    "request_path": "/test",
}


def test_extract_error_detail():
    """Test extract_error_detail function"""
    error = {
        "msg": DEFAULT_MENSAGE["msgfield"],
        "type": "missing",
        "loc": ["query", "field_name"],
        "ctx": {"error": ValueError(DEFAULT_MENSAGE["error"])},
    }

    result = extract_error_detail(error)

    assert result.message == DEFAULT_MENSAGE["msgfield"]
    assert result.location == "query"
    assert result.slug == "missing"
    assert result.field == "field_name"
    assert result.ctx["error"] == DEFAULT_MENSAGE["error"]


def test_extract_error_detail_body_location():
    """Test extract_error_detail with body location"""
    error = {
        "msg": DEFAULT_MENSAGE["msgValidation"],
        "type": "value_error",
        "loc": ["body", "field1", "subfield"],
        "ctx": {},
    }

    result = extract_error_detail(error)

    assert result.location == "body"
    assert result.field == "field1, subfield"


def test_extract_error_detail_invalid_location():
    """Test extract_error_detail with invalid location defaults to body"""
    error = {
        "msg": DEFAULT_MENSAGE["msgValidation"],
        "type": "value_error",
        "loc": ["invalid_location", "field_name"],
        "ctx": {},
    }

    result = extract_error_detail(error)

    assert result.location == "body"
    assert result.field == "field_name"


def test_extract_error_detail_empty_loc():
    """Test extract_error_detail with empty location"""
    error = {"msg": DEFAULT_MENSAGE["msgValidation"], "type": "value_error", "loc": [], "ctx": {}}

    result = extract_error_detail(error)

    assert result.location == "body"
    assert result.field == ""


def test_extract_error_detail_body():
    """Test extract_error_detail_body function"""
    error = {
        "msg": DEFAULT_MENSAGE["msgfield"],
        "type": "missing",
        "loc": ["field_name", "subfield"],
        "ctx": {"error": DEFAULT_MENSAGE["error"]},
    }

    result = extract_error_detail_body(error)

    assert result.message == DEFAULT_MENSAGE["msgfield"]
    assert result.location == "body"
    assert result.slug == "missing"
    assert result.field == "subfield"  # extract_error_detail_body skips first element for field


def test_extract_error_detail_body_with_value_error():
    """Test extract_error_detail_body with ValueError in context"""
    error = {
        "msg": "invalid value",
        "type": "value_error",
        "loc": ["field_name"],
        "ctx": {"error": ValueError("Invalid input")},
    }

    result = extract_error_detail_body(error)

    assert result.message == "invalid value"
    assert result.location == "body"
    assert result.slug == "value_error"
    assert result.ctx["error"] == "Invalid input"  # ValueError converted to string


def test_extract_error_detail_body_empty_loc():
    """Test extract_error_detail_body with empty location"""
    error = {"msg": DEFAULT_MENSAGE["msgValidation"], "type": "value_error", "loc": [], "ctx": {}}

    result = extract_error_detail_body(error)

    assert result.location == "body"
    assert result.field == ""


def test_http_exception_handler():
    """Test HTTP exception handler"""
    app = FastAPI()
    add_error_handlers(app)

    @app.get("/test")
    def test_endpoint():
        raise HTTPException(status_code=400, detail="Bad Request")

    client = TestClient(app)
    response = client.get(DEFAULT_PAGINATION["request_path"])

    assert response.status_code == 400
    # The handler returns a structured error response


def test_validation_error_handler():
    """Test validation error handler integration"""
    app = FastAPI()
    add_error_handlers(app)

    @app.post("/test")
    def test_endpoint(data: dict):
        return data

    client = TestClient(app)
    response = client.post(DEFAULT_PAGINATION["request_path"], json="invalid")

    assert response.status_code == 422


def test_add_error_handlers():
    """Test that error handlers are properly added to app"""
    app = FastAPI()

    # Before adding handlers
    initial_handlers = len(app.exception_handlers)

    add_error_handlers(app)

    # After adding handlers - should have more handlers
    assert len(app.exception_handlers) > initial_handlers


def test_extract_error_detail_with_valueerror_ctx():
    """Test extract_error_detail with ValueError in ctx - covers isinstance branch"""
    error = {
        "msg": DEFAULT_MENSAGE["msgTest"],
        "loc": ["query", "param"],
        "type": "value_error",
        "ctx": {"error": ValueError(DEFAULT_MENSAGE["error"])},
    }

    result = extract_error_detail(error)

    assert result.message == DEFAULT_MENSAGE["msgTest"]
    assert result.location == "query"
    assert result.slug == "value_error"
    assert result.field == "param"
    assert result.ctx["error"] == DEFAULT_MENSAGE["error"]  # ValueError converted to string


def test_extract_error_detail_with_non_valueerror_ctx():
    """Test extract_error_detail with non-ValueError in ctx - covers else branch"""
    error = {
        "msg": DEFAULT_MENSAGE["msgTest"],
        "loc": ["query", "param"],
        "type": "value_error",
        "ctx": {"error": "string error"},
    }

    result = extract_error_detail(error)

    assert result.message == DEFAULT_MENSAGE["msgTest"]
    assert result.location == "query"
    assert result.slug == "value_error"
    assert result.field == "param"
    assert result.ctx["error"] == "string error"


def test_extract_error_detail_empty_location():
    """Test extract_error_detail with empty location - covers empty loc branch"""
    error = {"msg": DEFAULT_MENSAGE["msgTest"], "loc": [], "type": "value_error", "ctx": {}}

    result = extract_error_detail(error)

    assert result.location == "body"  # Default when loc is empty
    assert result.field == ""


def test_extract_error_detail_invalid_location():
    """Test extract_error_detail with invalid location - covers invalid location branch"""
    error = {"msg": DEFAULT_MENSAGE["msgTest"], "loc": ["invalid_location", "param"], "type": "value_error", "ctx": {}}

    result = extract_error_detail(error)

    assert result.location == "body"  # Default when location not in VALID_LOCATIONS
    assert result.field == "param"


def test_extract_error_detail_body_with_valueerror():
    """Test extract_error_detail_body with ValueError in ctx - covers isinstance branch"""
    error = {
        "msg": DEFAULT_MENSAGE["msgTest"],
        "loc": ["query", "param"],
        "type": "value_error",
        "ctx": {"error": ValueError("Body error")},
    }

    result = extract_error_detail_body(error)

    assert result.message == DEFAULT_MENSAGE["msgTest"]
    assert result.location == "body"  # Always body in this function
    assert result.slug == "value_error"
    assert result.ctx["error"] == "Body error"  # ValueError converted to string


def test_extract_error_detail_body_without_valueerror():
    """Test extract_error_detail_body without ValueError in ctx - covers else branch"""
    error = {
        "msg": DEFAULT_MENSAGE["msgTest"],
        "loc": ["query", "param"],
        "type": "value_error",
        "ctx": {"error": "regular error"},
    }

    result = extract_error_detail_body(error)

    assert result.message == DEFAULT_MENSAGE["msgTest"]
    assert result.location == "body"
    assert result.slug == "value_error"
    assert result.ctx["error"] == "regular error"  # String remains as string


# Additional tests for comprehensive coverage


@pytest.mark.asyncio
async def test_application_error_handler_with_headers():
    """Test application error handler with custom headers"""
    from fastapi import Request

    from app.api.common.error_handlers import add_error_handlers
    from app.common.error_codes import ErrorCodes
    from app.common.exceptions.application_exception import ApplicationException

    app = FastAPI()
    add_error_handlers(app)
    client = TestClient(app)

    @app.get("/test")
    async def test_endpoint():
        exc = ApplicationException(ErrorCodes.UNPROCESSABLE_ENTITY)
        exc.headers = {"X-Custom-Header": "test-value"}
        raise exc

    response = client.get(DEFAULT_PAGINATION["request_path"])
    assert response.status_code == 422


def test_extract_error_detail_with_complex_ctx():
    """Test extract_error_detail with complex context containing nested objects"""
    error = {
        "msg": "field validation failed",
        "type": "value_error",
        "loc": ["query", "complex_field"],
        "ctx": {
            "error": ValueError("nested error"),
            "nested_dict": {"key": "value"},
            "nested_list": [1, 2, 3],
            "string_value": "test",
        },
    }

    result = extract_error_detail(error)

    assert result.message == "field validation failed"
    assert result.location == "query"
    assert result.slug == "value_error"
    assert result.field == "complex_field"
    assert result.ctx["error"] == "nested error"
    assert result.ctx["nested_dict"] == {"key": "value"}
    assert result.ctx["nested_list"] == [1, 2, 3]
    assert result.ctx["string_value"] == "test"


def test_extract_error_detail_with_none_ctx():
    """Test extract_error_detail when ctx is None"""
    error = {"msg": "required field missing", "type": "missing", "loc": ["body", "required_field"], "ctx": None}

    result = extract_error_detail(error)

    assert result.message == "required field missing"
    assert result.location == "body"
    assert result.slug == "missing"
    assert result.field == "required_field"
    assert result.ctx == {}


def test_extract_error_detail_body_with_deep_nesting():
    """Test extract_error_detail_body with deeply nested fields"""
    error = {
        "msg": "validation failed",
        "type": "value_error",
        "loc": ["body", "level1", "level2", "level3", "deep_field"],
        "ctx": {"limit_value": 100},
    }

    result = extract_error_detail_body(error)

    assert result.message == "validation failed"
    assert result.location == "body"
    assert result.slug == "value_error"
    assert result.field == "level1, level2, level3, deep_field"
    assert result.ctx["limit_value"] == 100


def test_extract_error_detail_body_single_field():
    """Test extract_error_detail_body with single field in body"""
    error = {
        "msg": "invalid format",
        "type": "format_error",
        "loc": ["body", "single_field"],
        "ctx": {"pattern": "^[A-Z]+$"},
    }

    result = extract_error_detail_body(error)

    assert result.message == "invalid format"
    assert result.location == "body"
    assert result.slug == "format_error"
    assert result.field == "single_field"
    assert result.ctx["pattern"] == "^[A-Z]+$"


def test_extract_error_detail_empty_loc():
    """Test extract_error_detail with empty location list"""
    error = {"msg": "generic error", "type": "generic", "loc": [], "ctx": {}}

    result = extract_error_detail(error)

    assert result.message == "generic error"
    assert result.location == "body"  # Default fallback
    assert result.slug == "generic"
    assert result.field == ""
    assert result.ctx == {}
