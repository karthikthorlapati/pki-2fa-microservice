# utilities/identity_gen.py
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

# System Configuration
KEY_EXPONENT = 65537
KEY_STRENGTH = 4096

print(f"Initializing {KEY_STRENGTH}-bit Vault Identity...")

# Generate the master identity (RSA Pair)
vault_identity = rsa.generate_private_key(
    public_exponent=KEY_EXPONENT,
    key_size=KEY_STRENGTH
)

# Serialize and Save Private Identity
with open("identity_secret.pem", "wb") as secret_io:
    secret_io.write(vault_identity.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ))

# Serialize and Save Public Identity
with open("identity_public.pem", "wb") as public_io:
    public_io.write(vault_identity.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ))

print("Vault identity established successfully.")