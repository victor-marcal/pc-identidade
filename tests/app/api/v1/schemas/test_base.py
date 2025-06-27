from datetime import datetime
from uuid import UUID, uuid4

import pytest
from pydantic import BaseModel, ValidationError

from app.api.v1.schemas.base import ModelSchema, TimestampMixinSchema, UuidMixinSchema


def test_model_schema_alias():
    """Test ModelSchema is an alias for BaseModel"""
    assert ModelSchema is BaseModel


def test_uuid_mixin_schema_creation():
    """Test UuidMixinSchema creation with valid UUID"""
    test_uuid = uuid4()

    schema = UuidMixinSchema(id=test_uuid)

    assert schema.id == test_uuid
    assert isinstance(schema.id, UUID)


def test_uuid_mixin_schema_none_id():
    """Test UuidMixinSchema creation with None id"""
    schema = UuidMixinSchema()

    assert schema.id is None


def test_uuid_mixin_schema_string_uuid():
    """Test UuidMixinSchema creation with string UUID"""
    test_uuid_str = str(uuid4())

    schema = UuidMixinSchema(id=test_uuid_str)

    assert isinstance(schema.id, UUID)
    assert str(schema.id) == test_uuid_str


def test_uuid_mixin_schema_invalid_uuid():
    """Test UuidMixinSchema with invalid UUID string"""
    with pytest.raises(ValidationError):
        UuidMixinSchema(id="invalid-uuid-string")


def test_uuid_mixin_schema_inheritance():
    """Test UuidMixinSchema inherits from BaseModel"""
    assert issubclass(UuidMixinSchema, BaseModel)


def test_uuid_mixin_schema_field_description():
    """Test UuidMixinSchema id field has correct description"""
    field_info = UuidMixinSchema.model_fields['id']
    assert field_info.description == "Identificador do objeto"


def test_timestamp_mixin_schema_creation():
    """Test TimestampMixinSchema creation with datetime values"""
    now = datetime.now()
    earlier = datetime.now()

    schema = TimestampMixinSchema(created_at=earlier, updated_at=now)

    assert schema.created_at == earlier
    assert schema.updated_at == now
    assert isinstance(schema.created_at, datetime)
    assert isinstance(schema.updated_at, datetime)


def test_timestamp_mixin_schema_none_values():
    """Test TimestampMixinSchema creation with None values"""
    schema = TimestampMixinSchema()

    assert schema.created_at is None
    assert schema.updated_at is None


def test_timestamp_mixin_schema_only_created_at():
    """Test TimestampMixinSchema with only created_at"""
    now = datetime.now()

    schema = TimestampMixinSchema(created_at=now)

    assert schema.created_at == now
    assert schema.updated_at is None


def test_timestamp_mixin_schema_only_updated_at():
    """Test TimestampMixinSchema with only updated_at"""
    now = datetime.now()

    schema = TimestampMixinSchema(updated_at=now)

    assert schema.created_at is None
    assert schema.updated_at == now


def test_timestamp_mixin_schema_inheritance():
    """Test TimestampMixinSchema inherits from BaseModel"""
    assert issubclass(TimestampMixinSchema, BaseModel)


def test_timestamp_mixin_schema_field_descriptions():
    """Test TimestampMixinSchema fields have correct descriptions"""
    fields = TimestampMixinSchema.model_fields

    assert fields['created_at'].description == "Data e hora da criação"
    assert fields['updated_at'].description == "Data e hora da atualização"


def test_combined_mixins():
    """Test using both mixins together"""

    class CombinedSchema(UuidMixinSchema, TimestampMixinSchema):
        name: str

    test_uuid = uuid4()
    now = datetime.now()

    schema = CombinedSchema(id=test_uuid, created_at=now, updated_at=now, name="Test")

    assert schema.id == test_uuid
    assert schema.created_at == now
    assert schema.updated_at == now
    assert schema.name == "Test"


def test_mixin_schemas_json_serialization():
    """Test mixin schemas JSON serialization"""
    test_uuid = uuid4()
    now = datetime.now()

    uuid_schema = UuidMixinSchema(id=test_uuid)
    timestamp_schema = TimestampMixinSchema(created_at=now, updated_at=now)

    uuid_json = uuid_schema.model_dump()
    timestamp_json = timestamp_schema.model_dump()

    assert uuid_json["id"] == test_uuid  # Pydantic keeps UUID objects in model_dump()
    assert "created_at" in timestamp_json
    assert "updated_at" in timestamp_json


def test_uuid_mixin_with_dict():
    """Test UuidMixinSchema creation from dictionary"""
    test_uuid = uuid4()
    data = {"id": str(test_uuid)}

    schema = UuidMixinSchema(**data)

    assert schema.id == test_uuid


def test_timestamp_mixin_with_dict():
    """Test TimestampMixinSchema creation from dictionary"""
    now = datetime.now()
    data = {"created_at": now.isoformat(), "updated_at": now.isoformat()}

    schema = TimestampMixinSchema(**data)

    assert isinstance(schema.created_at, datetime)
    assert isinstance(schema.updated_at, datetime)
