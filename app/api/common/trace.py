import secrets


def get_trace_id() -> str:
    trace_id = secrets.token_hex(16)  # 32-char hex string
    return trace_id
