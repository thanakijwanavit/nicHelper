import pytest
from nicHelper.rsa import generate_password, generate_keypair, encrypt, decrypt

def test_password_generation():
    password = generate_password()
    assert isinstance(password, str)
    assert len(password) > 0

def test_keypair_generation():
    password = generate_password()
    pubkey, privkey = generate_keypair(password)
    assert pubkey is not None
    assert privkey is not None

def test_encryption_decryption():
    password = generate_password()
    pubkey, privkey = generate_keypair(password)
    original_data = "Hello, World!"
    
    encrypted_data = encrypt(pubkey, original_data)
    assert encrypted_data != original_data
    
    decrypted_data = decrypt(encrypted_data, password, privkey)
    assert decrypted_data == original_data