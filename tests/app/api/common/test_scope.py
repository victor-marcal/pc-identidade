from enum import StrEnum

import pytest

from app.api.common.scope import Scope


def test_scope_is_str_enum():
    """Test that Scope is a StrEnum"""
    assert issubclass(Scope, StrEnum)


def test_scope_class_exists():
    """Test that Scope class can be imported and instantiated"""
    assert Scope is not None
    assert hasattr(Scope, '__name__')
    assert Scope.__name__ == 'Scope'


def test_scope_docstring():
    """Test that Scope has the expected docstring"""
    assert Scope.__doc__ is not None
    assert "Escopos" in Scope.__doc__
