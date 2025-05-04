import hashlib


def generate_hash(data: str) -> str:  # pragma: no cover
    hasher256 = getattr(hashlib, "sha256")
    hash_result = hasher256(data.encode()).hexdigest()
    return hash_result
