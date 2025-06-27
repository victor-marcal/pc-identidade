import pytest
from unittest.mock import MagicMock, patch
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from pydantic import ValidationError
from app.api.common.error_handlers import (
    add_error_handlers, 
    extract_error_detail, 
    extract_error_detail_body
)


def test_extract_error_detail():
    """Test extract_error_detail function"""
    error = {
        "msg": "field required",
        "type": "missing",
        "loc": ["query", "field_name"],
        "ctx": {"error": ValueError("test error")}
    }
    
    result = extract_error_detail(error)
    
    assert result.message == "field required"
    assert result.location == "query"
    assert result.slug == "missing"
    assert result.field == "field_name"
    assert result.ctx["error"] == "test error"


def test_extract_error_detail_body_location():
    """Test extract_error_detail with body location"""
    error = {
        "msg": "validation error",
        "type": "value_error",
        "loc": ["body", "field1", "subfield"],
        "ctx": {}
    }
    
    result = extract_error_detail(error)
    
    assert result.location == "body"
    assert result.field == "field1, subfield"


def test_extract_error_detail_invalid_location():
    """Test extract_error_detail with invalid location defaults to body"""
    error = {
        "msg": "validation error",
        "type": "value_error",
        "loc": ["invalid_location", "field_name"],
        "ctx": {}
    }
    
    result = extract_error_detail(error)
    
    assert result.location == "body"
    assert result.field == "field_name"


def test_extract_error_detail_empty_loc():
    """Test extract_error_detail with empty location"""
    error = {
        "msg": "validation error",
        "type": "value_error",
        "loc": [],
        "ctx": {}
    }
    
    result = extract_error_detail(error)
    
    assert result.location == "body"
    assert result.field == ""


def test_extract_error_detail_body():
    """Test extract_error_detail_body function"""
    error = {
        "msg": "field required",
        "type": "missing",
        "loc": ["field_name", "subfield"],
        "ctx": {"error": "test error"}
    }
    
    result = extract_error_detail_body(error)
    
    assert result.message == "field required"
    assert result.location == "body"
    assert result.slug == "missing"
    assert result.field == "subfield"  # extract_error_detail_body skips first element for field


def test_extract_error_detail_body_with_value_error():
    """Test extract_error_detail_body with ValueError in context"""
    error = {
        "msg": "invalid value",
        "type": "value_error",
        "loc": ["field_name"],
        "ctx": {"error": ValueError("Invalid input")}
    }
    
    result = extract_error_detail_body(error)
    
    assert result.message == "invalid value"
    assert result.location == "body"
    assert result.slug == "value_error"
    assert result.ctx["error"] == "Invalid input"  # ValueError converted to string


def test_extract_error_detail_body_empty_loc():
    """Test extract_error_detail_body with empty location"""
    error = {
        "msg": "validation error",
        "type": "value_error",
        "loc": [],
        "ctx": {}
    }
    
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
    response = client.get("/test")
    
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
    response = client.post("/test", json="invalid")
    
    assert response.status_code == 422
    # Should return structured validation error


def test_add_error_handlers():
    """Test that error handlers are properly added to app"""
    app = FastAPI()
    
    # Before adding handlers
    initial_handlers = len(app.exception_handlers)
    
    add_error_handlers(app)
    
    # After adding handlers - should have more handlers
    assert len(app.exception_handlers) > initial_handlers
