# core/crypto_engine.py
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization, hashes
import base64

class CipherEngine:
    @staticmethod
    def import_identity(key_path: str):
        """Loads the private RSA identity from a file."""
        with open(key_path, "rb") as key_file:
            return serialization.load_pem_private_key(key_file.read(), password=None)

    @staticmethod
    def reveal_secret(encoded_blob: str, identity_key) -> str:
        """Decodes Base64 and decrypts the blob using the identity key."""
        try:
            binary_blob = base64.b64decode(encoded_blob)
            
            plain_bytes = identity_key.decrypt(
                binary_blob,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            return plain_bytes.decode('utf-8')
        except Exception as error:
            raise RuntimeError(f"Vault unlock failed: {error}")