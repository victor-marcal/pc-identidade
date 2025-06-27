from enum import StrEnum

import pytest
from pydantic import ValidationError

from app.common.context.model import AppContext, AppContextScope


def test_app_context_scope_enum():
    """Test AppContextScope enum values"""
    assert AppContextScope.CHANNEL == "channel"
    assert AppContextScope.SELLER == "seller"

    # Test that it's a StrEnum
    assert issubclass(AppContextScope, StrEnum)


def test_app_context_creation_minimal():
    """Test AppContext creation with minimal data"""
    context = AppContext()

    assert context.tenant is None
    assert context.azp is None
    assert context.sub is None
    assert context.trace_id is None
    assert context.scope is None


def test_app_context_creation_full():
    """Test AppContext creation with all fields"""
    context = AppContext(
        tenant="test-tenant", azp="test-azp", sub="test-subject", trace_id="trace-123", scope=AppContextScope.SELLER
    )

    assert context.tenant == "test-tenant"
    assert context.azp == "test-azp"
    assert context.sub == "test-subject"
    assert context.trace_id == "trace-123"
    assert context.scope == AppContextScope.SELLER


def test_app_context_with_channel_scope():
    """Test AppContext with CHANNEL scope"""
    context = AppContext(tenant="channel-tenant", scope=AppContextScope.CHANNEL)

    assert context.tenant == "channel-tenant"
    assert context.scope == AppContextScope.CHANNEL


def test_app_context_with_seller_scope():
    """Test AppContext with SELLER scope"""
    context = AppContext(tenant="seller-tenant", scope=AppContextScope.SELLER)

    assert context.tenant == "seller-tenant"
    assert context.scope == AppContextScope.SELLER


def test_app_context_json_serialization():
    """Test AppContext JSON serialization"""
    context = AppContext(
        tenant="json-tenant",
        azp="json-azp",
        sub="json-subject",
        trace_id="json-trace-123",
        scope=AppContextScope.SELLER,
    )

    json_data = context.model_dump()

    assert json_data["tenant"] == "json-tenant"
    assert json_data["azp"] == "json-azp"
    assert json_data["sub"] == "json-subject"
    assert json_data["trace_id"] == "json-trace-123"
    assert json_data["scope"] == "seller"


def test_app_context_json_with_nulls():
    """Test AppContext JSON serialization with null values"""
    context = AppContext(tenant="only-tenant")

    json_data = context.model_dump()

    assert json_data["tenant"] == "only-tenant"
    assert json_data["azp"] is None
    assert json_data["sub"] is None
    assert json_data["trace_id"] is None
    assert json_data["scope"] is None


def test_app_context_from_dict():
    """Test AppContext creation from dictionary"""
    data = {
        "tenant": "dict-tenant",
        "azp": "dict-azp",
        "sub": "dict-subject",
        "trace_id": "dict-trace-456",
        "scope": "channel",
    }

    context = AppContext(**data)

    assert context.tenant == "dict-tenant"
    assert context.azp == "dict-azp"
    assert context.sub == "dict-subject"
    assert context.trace_id == "dict-trace-456"
    assert context.scope == AppContextScope.CHANNEL


def test_app_context_invalid_scope():
    """Test AppContext with invalid scope"""
    with pytest.raises(ValidationError):
        AppContext(scope="invalid_scope")  # type: ignore


def test_app_context_equality():
    """Test AppContext equality comparison"""
    context1 = AppContext(tenant="same-tenant", azp="same-azp", scope=AppContextScope.SELLER)

    context2 = AppContext(tenant="same-tenant", azp="same-azp", scope=AppContextScope.SELLER)

    context3 = AppContext(tenant="different-tenant", azp="same-azp", scope=AppContextScope.SELLER)

    assert context1 == context2
    assert context1 != context3


def test_app_context_string_fields():
    """Test that string fields accept various string values"""
    context = AppContext(
        tenant="tenant-with-dashes", azp="azp_with_underscores", sub="sub.with.dots", trace_id="trace-id-123-abc"
    )

    assert context.tenant == "tenant-with-dashes"
    assert context.azp == "azp_with_underscores"
    assert context.sub == "sub.with.dots"
    assert context.trace_id == "trace-id-123-abc"


def test_app_context_scope_values():
    """Test all valid scope values"""
    # Test CHANNEL
    context_channel = AppContext(scope=AppContextScope.CHANNEL)
    assert context_channel.scope == "channel"

    # Test SELLER
    context_seller = AppContext(scope=AppContextScope.SELLER)
    assert context_seller.scope == "seller"
