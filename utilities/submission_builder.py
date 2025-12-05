# utilities/submission_builder.py
import base64
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

# === CONFIGURATION: UPDATE POST-COMMIT ===
COMMIT_ID = "PASTE_HASH_HERE"
# =========================================

def build_submission():
    try:
        # 1. Load the Vault Identity (Private Key)
        # Matches output from utilities/identity_gen.py
        with open("identity_secret.pem", "rb") as secret_file:
            signer_key = serialization.load_pem_private_key(
                secret_file.read(), 
                password=None
            )

        # 2. Sign the Commit Hash
        # Creates a digital signature proving ownership
        digital_signature = signer_key.sign(
            COMMIT_ID.encode('utf-8'),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

        # 3. Load the Authority's Public Key (Instructor/Verifier)
        # You must rename your instructor's key to 'authority_public.pem'
        with open("authority_public.pem", "rb") as pub_file:
            verifier_key = serialization.load_pem_public_key(pub_file.read())

        # 4. Encrypt the Signature (Seal the Proof)
        sealed_proof = verifier_key.encrypt(
            digital_signature,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        print("\n[Sealed Submission Proof]:")
        print(base64.b64encode(sealed_proof).decode('utf-8'))
        print("")

    except FileNotFoundError:
        print("Error: Missing key files. Ensure 'identity_secret.pem' and 'authority_public.pem' exist.")
    except Exception as error:
        print(f"Submission Build Failed: {error}")

if _name_ == "_main_":
    build_submission()