import hashlib

def hash_string(text: str) -> str:
    hash_hex = hashlib.sha256(text.encode()).hexdigest()
    return hash_hex
