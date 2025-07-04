"""
Testes unitários para os schemas de usuário (user_schema.py).
"""
import pytest
from pydantic import ValidationError

from app.api.v1.schemas.user_schema import UserCreate, UserPatch, UserResponse

# --- Testes para o schema UserCreate ---


def test_user_create_success():
    """Testa a criação bem-sucedida de UserCreate com todos os campos."""
    data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "a_strong_password",
        "first_name": "Test",
        "last_name": "User"
    }
    schema = UserCreate(**data)
    assert schema.username == data["username"]
    assert schema.email == data["email"]
    assert schema.password == data["password"]
    assert schema.first_name == data["first_name"]
    assert schema.last_name == data["last_name"]


def test_user_create_only_required_fields():
    """Testa a criação bem-sucedida de UserCreate apenas com campos obrigatórios."""
    data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "a_strong_password"
    }
    schema = UserCreate(**data)
    assert schema.username == data["username"]
    assert schema.email == data["email"]
    assert schema.first_name is None
    assert schema.last_name is None


@pytest.mark.parametrize("invalid_data, expected_error_msg", [
    ({"username": "a", "email": "test@example.com", "password": "a_strong_password"}, "at least 3 characters"),
    ({"username": "testuser", "email": "invalid-email", "password": "a_strong_password"}, "value is not a valid email address"),
    ({"username": "testuser", "email": "test@example.com", "password": "short"}, "at least 8 characters"),
])
def test_user_create_validation_error(invalid_data, expected_error_msg):
    """Testa se UserCreate levanta ValidationError para dados inválidos."""
    with pytest.raises(ValidationError) as exc_info:
        UserCreate(**invalid_data)
    assert expected_error_msg in str(exc_info.value)


# --- Testes para o schema UserResponse ---

def test_user_response_success():
    """Testa a criação bem-sucedida de UserResponse."""
    data = {
        "id": "user_id_123",
        "username": "testuser",
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User",
        "enabled": True,
        "attributes": {"sellers": ["seller_a"]}
    }
    schema = UserResponse(**data)
    assert schema.id == data["id"]
    assert schema.username == data["username"]
    assert schema.first_name == data["first_name"]
    assert schema.attributes["sellers"] == ["seller_a"]


def test_user_response_missing_required_field():
    """Testa se UserResponse levanta erro para campos obrigatórios ausentes."""
    invalid_data = {
        "id": "user_id_123",
        "username": "testuser",
    }
    with pytest.raises(ValidationError):
        UserResponse(**invalid_data)


# --- Testes para o schema UserPatch ---

def test_user_patch_success_partial_data():
    """Testa a criação bem-sucedida de UserPatch com dados parciais."""
    data = {"first_name": "NewFirstName"}
    schema = UserPatch(**data)
    assert schema.first_name == "NewFirstName"
    assert schema.email is None
    assert schema.password is None


def test_user_patch_success_all_fields():
    """Testa a criação bem-sucedida de UserPatch com todos os campos."""
    data = {
        "email": "new@example.com",
        "first_name": "NewFirst",
        "last_name": "NewLast",
        "password": "new_secure_password"
    }
    schema = UserPatch(**data)
    assert schema.email == data["email"]
    assert schema.password == data["password"]


def test_user_patch_empty_data():
    """Testa se UserPatch pode ser instanciado sem dados, pois todos os campos são opcionais."""
    schema = UserPatch()
    assert schema.model_dump(exclude_unset=True) == {}


@pytest.mark.parametrize("invalid_data, expected_error_msg", [
    ({"email": "not-an-email"}, "value is not a valid email address"),
    ({"password": "short"}, "at least 8 characters"),
])
def test_user_patch_validation_error(invalid_data, expected_error_msg):
    """Testa se UserPatch levanta ValidationError para dados inválidos."""
    with pytest.raises(ValidationError) as exc_info:
        UserPatch(**invalid_data)
    assert expected_error_msg in str(exc_info.value)
