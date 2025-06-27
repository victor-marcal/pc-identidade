import pytest

from app.api.common.schemas.pagination import Paginator


def test_paginator_basic():
    """Test basic paginator functionality"""
    paginator = Paginator(request_path="/test", limit=10, offset=0)

    assert paginator.limit == 10
    assert paginator.offset == 0
    assert paginator.sort is None
    assert paginator.request_path == "/test"


def test_paginator_with_sort():
    """Test paginator with sort parameter"""
    paginator = Paginator(request_path="/test", limit=5, offset=10, sort="name:asc,date:desc")

    assert paginator.limit == 5
    assert paginator.offset == 10
    assert paginator.sort == "name:asc,date:desc"


def test_paginator_get_sort_dict_none():
    """Test get_sort_order returns None when no sort"""
    paginator = Paginator(request_path="/test", limit=10, offset=0)

    result = paginator.get_sort_order()
    assert result is None


def test_paginator_get_sort_dict_empty():
    """Test get_sort_order with empty sort string"""
    paginator = Paginator(request_path="/test", limit=10, offset=0, sort="")

    result = paginator.get_sort_order()
    assert result is None


def test_paginator_get_sort_dict_single_field_asc():
    """Test get_sort_order with single ascending field"""
    paginator = Paginator(request_path="/test", limit=10, offset=0, sort="name")

    result = paginator.get_sort_order()
    assert result == {"name": 1}


def test_paginator_get_sort_dict_single_field_desc():
    """Test get_sort_order with single descending field"""
    paginator = Paginator(request_path="/test", limit=10, offset=0, sort="name:desc")

    result = paginator.get_sort_order()
    assert result == {"name": -1}


def test_paginator_get_sort_dict_multiple_fields():
    """Test get_sort_order with multiple fields"""
    paginator = Paginator(request_path="/test", limit=10, offset=0, sort="name:asc,date:desc,id")

    result = paginator.get_sort_order()
    assert result == {"name": 1, "date": -1, "id": 1}


def test_paginator_get_sort_dict_with_empty_fields():
    """Test get_sort_order filters out empty fields"""
    paginator = Paginator(request_path="/test", limit=10, offset=0, sort="name,,date:desc,")

    result = paginator.get_sort_order()
    assert result == {"name": 1, "date": -1}


def test_paginator_get_sort_dict_invalid_format():
    """Test get_sort_order with invalid sort format"""
    paginator = Paginator(request_path="/test", limit=10, offset=0, sort="name:invalid")

    result = paginator.get_sort_order()
    # Should default to ascending (1) for invalid order
    assert result == {"name": 1}
