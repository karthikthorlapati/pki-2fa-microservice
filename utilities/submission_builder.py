# utilities/submission_builder.py
import base64
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

# === CONFIGURATION ===
# Run 'git log -1 --format=%H' to get this
COMMIT_ID = "bb1e47335b06e357be662dbb52350224510f05d1"
# =====================

def build_submission():
    try:
        # 1. Load Student Private Key
        with open("student_private.pem", "rb") as secret_file:
            signer_key = serialization.load_pem_private_key(
                secret_file.read(), 
                password=None
            )

        # 2. Sign the Commit Hash (RSA-PSS)
        digital_signature = signer_key.sign(
            COMMIT_ID.encode('utf-8'),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

        # 3. Load Instructor Public Key
        with open("instructor_public.pem", "rb") as pub_file:
            verifier_key = serialization.load_pem_public_key(pub_file.read())

        # 4. Encrypt the Signature (RSA-OAEP)
        sealed_proof = verifier_key.encrypt(
            digital_signature,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        print("\n[Sealed Submission Proof (Base64 Single Line)]:")
        print(base64.b64encode(sealed_proof).decode('utf-8'))
        print("")

    except Exception as error:
        print(f"Submission Build Failed: {error}")

if __name__ == "__main__":
    build_submission()