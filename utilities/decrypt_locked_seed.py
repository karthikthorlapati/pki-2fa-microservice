#!/usr/bin/env python3
# utilities/decrypt_locked_seed.py
import base64
from pathlib import Path
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
import sys

LOCKED_PATH = Path("locked_seed.dat")
PRIVATE_KEY_PATH = Path("student_private.pem")
OUT_PLAIN = Path("decrypted_seed.txt")       # local plain seed (DO NOT COMMIT)
OUT_ENC_B64 = Path("encrypted_seed.txt")     # optional: base64-encoded ciphertext (if needed)

def load_private_key(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"Private key not found: {path}")
    data = path.read_bytes()
    return serialization.load_pem_private_key(data, password=None)

def read_locked(path: Path) -> bytes:
    if not path.exists():
        raise FileNotFoundError(f"Locked file not found: {path}")
    raw = path.read_bytes()
    # If file is ASCII base64, decode it; otherwise treat as raw bytes.
    try:
        s = raw.decode('ascii').strip()
        # if looks like base64 (only base64 chars and length > 0), decode
        if all(c in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=\n\r" for c in s) and len(s) > 0:
            try:
                return base64.b64decode(s)
            except Exception:
                return raw
        else:
            return raw
    except Exception:
        return raw

def decrypt(ciphertext: bytes, private_key) -> str:
    try:
        plain = private_key.decrypt(
            ciphertext,
            padding.OAEP(
                mgf=padding.MGF1(hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
    except Exception as e:
        raise RuntimeError("RSA/OAEP decryption failed: " + str(e))
    try:
        s = plain.decode("utf-8").strip().lower()
    except Exception as e:
        raise RuntimeError("UTF-8 decode of plaintext failed: " + str(e))
    # validate 64 hex chars
    if len(s) != 64 or any(c not in "0123456789abcdef" for c in s):
        raise ValueError("Decrypted text is not a 64-character hex seed. Value: {!r}".format(s))
    return s

def main():
    try:
        priv = load_private_key(PRIVATE_KEY_PATH)
        ct = read_locked(LOCKED_PATH)
        seed_hex = decrypt(ct, priv)
        OUT_PLAIN.write_text(seed_hex + "\n")
        print("Decrypted seed written to:", OUT_PLAIN)
        # also save base64-encoded ciphertext to encrypted_seed.txt for use with /decrypt-seed endpoint (optional)
        try:
            OUT_ENC_B64.write_text(base64.b64encode(ct).decode('ascii') + "\n")
            print("Raw ciphertext base64 saved to:", OUT_ENC_B64)
        except Exception:
            pass
        # quick success summary
        print("Seed (first 8 chars):", seed_hex[:8], " ... length:", len(seed_hex))
    except Exception as e:
        print("ERROR:", e)
        sys.exit(1)

if __name__ == "__main__":
    main()
