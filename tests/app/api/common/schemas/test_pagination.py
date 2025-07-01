import pytest

from app.api.common.schemas.pagination import Paginator

# Valores padrão para evitar repetição nos testes
DEFAULT_PAGINATION = {"request_path": "/test", "limit": 10, "offset": 0}


def test_paginator_basic():
    """Test basic paginator functionality"""
    paginator = Paginator(**DEFAULT_PAGINATION)

    assert paginator.limit == DEFAULT_PAGINATION["limit"]
    assert paginator.offset == DEFAULT_PAGINATION["offset"]
    assert paginator.sort is None
    assert paginator.request_path == DEFAULT_PAGINATION["request_path"]


def test_paginator_with_sort():
    """Test paginator with sort parameter"""
    paginator = Paginator(
        request_path=DEFAULT_PAGINATION["request_path"], limit=5, offset=10, sort="name:asc,date:desc"
    )

    assert paginator.limit == 5
    assert paginator.offset == 10
    assert paginator.sort == "name:asc,date:desc"


def test_paginator_get_sort_dict_none():
    """Test get_sort_order returns None when no sort"""
    paginator = Paginator(**DEFAULT_PAGINATION)

    result = paginator.get_sort_order()
    assert result is None


def test_paginator_get_sort_dict_empty():
    """Test get_sort_order with empty sort string"""
    paginator = Paginator(**DEFAULT_PAGINATION, sort="")

    result = paginator.get_sort_order()
    assert result is None


def test_paginator_get_sort_dict_single_field_asc():
    """Test get_sort_order with single ascending field"""
    paginator = Paginator(**DEFAULT_PAGINATION, sort="name")

    result = paginator.get_sort_order()
    assert result == {"name": 1}


def test_paginator_get_sort_dict_single_field_desc():
    """Test get_sort_order with single descending field"""
    paginator = Paginator(**DEFAULT_PAGINATION, sort="name:desc")

    result = paginator.get_sort_order()
    assert result == {"name": -1}


def test_paginator_get_sort_dict_multiple_fields():
    """Test get_sort_order with multiple fields"""
    paginator = Paginator(**DEFAULT_PAGINATION, sort="name:asc,date:desc,id")

    result = paginator.get_sort_order()
    assert result == {"name": 1, "date": -1, "id": 1}


def test_paginator_get_sort_dict_with_empty_fields():
    """Test get_sort_order filters out empty fields"""
    paginator = Paginator(**DEFAULT_PAGINATION, sort="name,,date:desc,")

    result = paginator.get_sort_order()
    assert result == {"name": 1, "date": -1}


def test_paginator_get_sort_dict_invalid_format():
    """Test get_sort_order with invalid sort format"""
    paginator = Paginator(**DEFAULT_PAGINATION, sort="name:invalid")

    result = paginator.get_sort_order()
    # Should default to ascending (1) for invalid order
    assert result == {"name": 1}
