# utilities/retrieve_secret.py
import requests
import json
import os

# --- VAULT CONFIGURATION ---
VAULT_ID = "23A91A6160"
VAULT_REPO = "https://github.com/karthikthorlapati/pki-2fa-microservice"
GATEWAY_URL = "https://eajeyq4r3zljoq4rpovy2nthda0vtjqf.lambda-url.ap-south-1.on.aws/"
# ---------------------------

def execute_retrieval():
    try:
        # Check if the public key exists
        if not os.path.exists("student_public.pem"):
            print("❌ Error: student_public.pem not found. Make sure you generated keys.")
            return

        # Load the Public Identity
        with open("student_public.pem", "r") as key_file:
            public_identity_data = key_file.read()

        # Prepare the payload
        payload = {
            "student_id": VAULT_ID,
            "github_repo_url": VAULT_REPO,
            "public_key": public_identity_data
        }

        print(f"Authenticating Vault ID {VAULT_ID}...")
        response = requests.post(GATEWAY_URL, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            if "encrypted_seed" in data:
                # Save to the filename expected by the Docker instructions
                with open("encrypted_seed.txt", "w") as secret_file:
                    secret_file.write(data["encrypted_seed"])
                print("✅ Success: Encrypted seed saved to 'encrypted_seed.txt'")
            else:
                print("!! Gateway Error:", data)
        else:
            print(f"!! Connection Error {response.status_code}: {response.text}")

    except Exception as error:
        print(f"!! System Failure: {error}")

if __name__ == "__main__":
    execute_retrieval()