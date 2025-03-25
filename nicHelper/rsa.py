from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import rsa
import base64
import secrets, string


def encrypt(pubkey: str, data: str) -> str:
    """
    Encrypts data using the provided public key.

    Args:
        pubkey: PEM-encoded public key
        data: String data to encrypt

    Returns:
        Base64-encoded encrypted data
    """
    public_key = serialization.load_pem_public_key(
        pubkey.encode(), backend=default_backend()
    )

    encrypted_data = public_key.encrypt(
        data.encode(),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )

    # Convert binary data to base64 string for easier handling
    return base64.b64encode(encrypted_data).decode("utf-8")


def decrypt(encrypted_data: str, password: str, privkey: str) -> str:
    """
    Decrypts data using the provided private key.

    Args:
        encrypted_data: Base64-encoded encrypted data
        password: Password to decrypt the private key
        privkey: PEM-encoded private key protected with password

    Returns:
        Decrypted string data
    """
    # Convert base64 string back to binary
    encrypted_binary = base64.b64decode(encrypted_data)

    private_key = serialization.load_pem_private_key(
        privkey.encode(),
        password=password.encode(),
        backend=default_backend(),
    )

    decrypted_data = private_key.decrypt(
        encrypted_binary,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )

    return decrypted_data.decode("utf-8")



def generate_keypair(password: str) -> tuple[str, str]:
    """
    Generate an RSA key pair, with the private key protected by a password.

    Args:
        password: Password to protect the private key

    Returns:
        A tuple of (encryption_key, decryption_key) as strings, where:
        - encryption_key is the PEM-encoded public key
        - decryption_key is the PEM-encoded private key protected with the password
    """
    # Generate private key (which contains the public key)
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    # Extract public key (encryption key)
    public_key = private_key.public_key()
    encryption_key = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode("utf-8")

    # Protect the private key (decryption key) with password
    decryption_key = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.BestAvailableEncryption(password.encode()),
    ).decode("utf-8")

    return encryption_key, decryption_key


def generate_password(length: int = 100) -> str:
    """Generate a secure random password."""

    return "".join(
        secrets.choice(string.ascii_letters + string.digits + "!@#$%^&*()_-+=<>?")
        for _ in range(length)
    )

if __name__ == "__main__":
    password = generate_password()
    print(f"Password: {password}")
    pubkey, privkey = generate_keypair(password)
    data = "Hello, World!"
    encrypted_data = encrypt(pubkey, data)
    decrypted_data = decrypt(encrypted_data, password, privkey)
    print(f"Original data: {data}")
    print(f"Encrypted data: {encrypted_data}")
    print(f"Decrypted data: {decrypted_data}")