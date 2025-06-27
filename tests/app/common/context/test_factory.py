import pytest
from unittest.mock import patch
from contextvars import ContextVar
from app.common.context.factory import set_context, get_context, _app_context
from app.common.context.model import AppContext, AppContextScope
from app.common.exceptions import ForbiddenException


def test_set_context():
    """Test setting context in ContextVar"""
    context = AppContext(
        tenant="test-tenant",
        azp="test-azp",
        sub="test-sub",
        trace_id="test-trace-id",
        scope=AppContextScope.SELLER
    )
    
    set_context(context)
    
    # Verify context is set
    assert _app_context.get() == context


def test_get_context_success():
    """Test getting context when it exists"""
    context = AppContext(
        tenant="test-tenant",
        azp="test-azp",
        sub="test-sub",
        trace_id="test-trace-id",
        scope=AppContextScope.CHANNEL
    )
    
    set_context(context)
    
    retrieved_context = get_context()
    assert retrieved_context == context
    assert retrieved_context.tenant == "test-tenant"
    assert retrieved_context.azp == "test-azp"
    assert retrieved_context.sub == "test-sub"
    assert retrieved_context.trace_id == "test-trace-id"
    assert retrieved_context.scope == AppContextScope.CHANNEL


def test_get_context_raises_forbidden_when_no_context():
    """Test that get_context raises ForbiddenException when no context is set"""
    # Clear any existing context
    _app_context.set(None)
    
    with pytest.raises(ForbiddenException):
        get_context()


def test_context_var_default_value():
    """Test that ContextVar has correct default value"""
    # Reset context
    _app_context.set(None)
    
    assert _app_context.get() is None


def test_context_var_name():
    """Test ContextVar name"""
    assert _app_context.name == "_app_context"


def test_multiple_context_sets():
    """Test setting context multiple times"""
    context1 = AppContext(tenant="tenant1", scope=AppContextScope.SELLER)
    context2 = AppContext(tenant="tenant2", scope=AppContextScope.CHANNEL)
    
    set_context(context1)
    assert get_context().tenant == "tenant1"
    
    set_context(context2)
    assert get_context().tenant == "tenant2"


def test_context_isolation():
    """Test that context is properly isolated"""
    context = AppContext(
        tenant="isolated-tenant",
        azp="isolated-azp",
        sub="isolated-sub",
        trace_id="isolated-trace",
        scope=AppContextScope.SELLER
    )
    
    set_context(context)
    
    # Get context and verify all fields
    retrieved = get_context()
    assert retrieved.tenant == "isolated-tenant"
    assert retrieved.azp == "isolated-azp"
    assert retrieved.sub == "isolated-sub"
    assert retrieved.trace_id == "isolated-trace"
    assert retrieved.scope == AppContextScope.SELLER
