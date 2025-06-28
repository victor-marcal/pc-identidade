import hashlib

import pytest

from app.common.hash_utils import generate_hash


def test_generate_hash_basic():
    """Test basic hash generation"""
    data = "test_string"
    result = generate_hash(data)

    # Verify it returns a string
    assert isinstance(result, str)

    # Verify it's a valid SHA256 hash (64 characters)
    assert len(result) == 64

    # Verify it's hexadecimal
    assert all(c in '0123456789abcdef' for c in result)


def test_generate_hash_consistency():
    """Test that the same input always produces the same hash"""
    data = "consistent_test_string"

    hash1 = generate_hash(data)
    hash2 = generate_hash(data)

    assert hash1 == hash2


def test_generate_hash_different_inputs():
    """Test that different inputs produce different hashes"""
    data1 = "input1"
    data2 = "input2"

    hash1 = generate_hash(data1)
    hash2 = generate_hash(data2)

    assert hash1 != hash2


def test_generate_hash_empty_string():
    """Test hash generation with empty string"""
    data = ""
    result = generate_hash(data)

    assert isinstance(result, str)
    assert len(result) == 64

    # Verify it matches the expected SHA256 of empty string
    expected = hashlib.sha256("".encode()).hexdigest()
    assert result == expected


def test_generate_hash_unicode():
    """Test hash generation with unicode characters"""
    data = "héllo wørld 🌍"
    result = generate_hash(data)

    assert isinstance(result, str)
    assert len(result) == 64

    # Verify it matches direct hashlib computation
    expected = hashlib.sha256(data.encode()).hexdigest()
    assert result == expected


def test_generate_hash_long_string():
    """Test hash generation with long string"""
    data = "a" * 10000
    result = generate_hash(data)

    assert isinstance(result, str)
    assert len(result) == 64


def test_generate_hash_special_characters():
    """Test hash generation with special characters"""
    data = "!@#$%^&*()_+-=[]{}|;':\",./<>?"
    result = generate_hash(data)

    assert isinstance(result, str)
    assert len(result) == 64

    # Verify it matches direct hashlib computation
    expected = hashlib.sha256(data.encode()).hexdigest()
    assert result == expected


def test_generate_hash_matches_direct_sha256():
    """Test that generate_hash produces the same result as direct SHA256"""
    test_cases = [
        "hello",
        "world",
        "test123",
        "Python testing",
        "UPPERCASE",
        "lowercase",
        "Mix3d C4s3",
    ]

    for data in test_cases:
        result = generate_hash(data)
        expected = hashlib.sha256(data.encode()).hexdigest()
        assert result == expected
