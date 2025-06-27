import pytest
from typing import Optional
from pydantic import BaseModel, Field
from app.models.query_model import QueryModel, _query_mapper


def test_query_mapper_values():
    """Test the query mapper dictionary"""
    assert _query_mapper["__ge"] == "$gte"
    assert _query_mapper["__gt"] == "$gt"
    assert _query_mapper["__le"] == "$lte"
    assert _query_mapper["__lt"] == "$lt"


def test_query_model_inheritance():
    """Test QueryModel inherits from BaseModel"""
    assert issubclass(QueryModel, BaseModel)


def test_query_model_docstring():
    """Test QueryModel has proper docstring"""
    assert QueryModel.__doc__ is not None
    assert "Modelo para pesquisas" in QueryModel.__doc__
    assert "__ge" in QueryModel.__doc__
    assert "__gt" in QueryModel.__doc__
    assert "__le" in QueryModel.__doc__
    assert "__lt" in QueryModel.__doc__


def test_to_query_dict_simple_fields():
    """Test to_query_dict with simple fields"""
    class TestQuery(QueryModel):
        name: Optional[str] = None
        age: Optional[int] = None
        active: Optional[bool] = None
    
    query = TestQuery(name="John", age=30, active=True)
    result = query.to_query_dict()
    
    assert result == {
        "name": "John",
        "age": 30,
        "active": True
    }


def test_to_query_dict_with_ge_operator():
    """Test to_query_dict with __ge operator"""
    class TestQuery(QueryModel):
        age__ge: Optional[int] = None
        name: Optional[str] = None
    
    query = TestQuery(age__ge=18, name="John")
    result = query.to_query_dict()
    
    assert result == {
        "age": {"$gte": 18},
        "name": "John"
    }


def test_to_query_dict_with_gt_operator():
    """Test to_query_dict with __gt operator"""
    class TestQuery(QueryModel):
        score__gt: Optional[float] = None
        category: Optional[str] = None
    
    query = TestQuery(score__gt=85.5, category="A")
    result = query.to_query_dict()
    
    assert result == {
        "score": {"$gt": 85.5},
        "category": "A"
    }


def test_to_query_dict_with_le_operator():
    """Test to_query_dict with __le operator"""
    class TestQuery(QueryModel):
        price__le: Optional[float] = None
        product: Optional[str] = None
    
    query = TestQuery(price__le=100.0, product="laptop")
    result = query.to_query_dict()
    
    assert result == {
        "price": {"$lte": 100.0},
        "product": "laptop"
    }


def test_to_query_dict_with_lt_operator():
    """Test to_query_dict with __lt operator"""
    class TestQuery(QueryModel):
        weight__lt: Optional[int] = None
        item: Optional[str] = None
    
    query = TestQuery(weight__lt=50, item="package")
    result = query.to_query_dict()
    
    assert result == {
        "weight": {"$lt": 50},
        "item": "package"
    }


def test_to_query_dict_multiple_operators_same_field():
    """Test to_query_dict with multiple operators on same field"""
    class TestQuery(QueryModel):
        age__ge: Optional[int] = None
        age__le: Optional[int] = None
        name: Optional[str] = None
    
    query = TestQuery(age__ge=18, age__le=65, name="John")
    result = query.to_query_dict()
    
    assert result == {
        "age": {"$gte": 18, "$lte": 65},
        "name": "John"
    }


def test_to_query_dict_all_operators():
    """Test to_query_dict with all operators"""
    class TestQuery(QueryModel):
        min_score__ge: Optional[int] = None
        max_score__le: Optional[int] = None
        threshold__gt: Optional[int] = None
        limit__lt: Optional[int] = None
        category: Optional[str] = None
    
    query = TestQuery(
        min_score__ge=10,
        max_score__le=100,
        threshold__gt=50,
        limit__lt=90,
        category="test"
    )
    result = query.to_query_dict()
    
    assert result == {
        "min_score": {"$gte": 10},
        "max_score": {"$lte": 100},
        "threshold": {"$gt": 50},
        "limit": {"$lt": 90},
        "category": "test"
    }


def test_to_query_dict_exclude_none_values():
    """Test to_query_dict excludes None values"""
    class TestQuery(QueryModel):
        name: Optional[str] = None
        age__ge: Optional[int] = None
        active: Optional[bool] = None
    
    query = TestQuery(name="John", active=True)  # age__ge is None
    result = query.to_query_dict()
    
    assert result == {
        "name": "John",
        "active": True
    }
    assert "age" not in result


def test_to_query_dict_empty_model():
    """Test to_query_dict with empty model"""
    class TestQuery(QueryModel):
        name: Optional[str] = None
        age: Optional[int] = None
    
    query = TestQuery()  # All fields are None
    result = query.to_query_dict()
    
    assert result == {}


def test_to_query_dict_complex_field_names():
    """Test to_query_dict with complex field names containing underscores"""
    class TestQuery(QueryModel):
        user_name: Optional[str] = None
        user_age__ge: Optional[int] = None
        full_name__le: Optional[str] = None
    
    query = TestQuery(
        user_name="john_doe",
        user_age__ge=25,
        full_name__le="John Doe"
    )
    result = query.to_query_dict()
    
    assert result == {
        "user_name": "john_doe",
        "user_age": {"$gte": 25},
        "full_name": {"$lte": "John Doe"}
    }


def test_to_query_dict_with_mixed_types():
    """Test to_query_dict with mixed data types"""
    class TestQuery(QueryModel):
        name: Optional[str] = None
        age__ge: Optional[int] = None
        salary__le: Optional[float] = None
        active: Optional[bool] = None
        tags: Optional[list] = None
    
    query = TestQuery(
        name="Alice",
        age__ge=30,
        salary__le=75000.50,
        active=True,
        tags=["python", "fastapi"]
    )
    result = query.to_query_dict()
    
    assert result == {
        "name": "Alice",
        "age": {"$gte": 30},
        "salary": {"$lte": 75000.50},
        "active": True,
        "tags": ["python", "fastapi"]
    }


def test_to_query_dict_with_default_values():
    """Test to_query_dict with default values"""
    class TestQuery(QueryModel):
        status: str = "active"
        priority__ge: int = 1
        category: Optional[str] = None
    
    query = TestQuery(category="important")
    result = query.to_query_dict()
    
    assert result == {
        "status": "active",
        "priority": {"$gte": 1},
        "category": "important"
    }
