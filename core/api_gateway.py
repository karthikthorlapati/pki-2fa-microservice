# core/api_gateway.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from core.crypto_engine import CipherEngine
from core.token_manager import TokenController

gateway = FastAPI()

# --- CRITICAL CONFIGURATION FIXES ---
# Must map to Docker volume /data
VAULT_STORAGE = "/data/seed.txt"
# Must match the renamed private key
IDENTITY_PATH = "/app/student_private.pem"

class EncryptedBlob(BaseModel):
    encrypted_seed: str

class VerifyInput(BaseModel):
    code: str

def _retrieve_stored_seed():
    if not os.path.exists(VAULT_STORAGE):
        return None
    with open(VAULT_STORAGE, "r") as storage_file:
        return storage_file.read().strip()

# --- FIXED ENDPOINTS ---

@gateway.post("/decrypt-seed")
def decrypt_seed_endpoint(payload: EncryptedBlob):
    try:
        identity = CipherEngine.import_identity(IDENTITY_PATH)
        raw_seed = CipherEngine.reveal_secret(payload.encrypted_seed, identity)
        
        # Ensure directory exists before writing
        os.makedirs(os.path.dirname(VAULT_STORAGE), exist_ok=True)
        
        with open(VAULT_STORAGE, "w") as storage_file:
            storage_file.write(raw_seed)
            
        return {"status": "ok"}
    except Exception as error:
        raise HTTPException(status_code=500, detail="Decryption failed")

@gateway.get("/generate-2fa")
def generate_2fa_endpoint():
    master_seed = _retrieve_stored_seed()
    if not master_seed:
        raise HTTPException(status_code=500, detail="Seed not decrypted yet")
    
    controller = TokenController(master_seed)
    current_token, time_left = controller.fetch_active_token()
    
    return {
        "code": current_token,
        "valid_for": time_left
    }

@gateway.post("/verify-2fa")
def verify_2fa_endpoint(input_data: VerifyInput):
    master_seed = _retrieve_stored_seed()
    if not master_seed:
        raise HTTPException(status_code=500, detail="Seed not decrypted yet")
        
    controller = TokenController(master_seed)
    is_legit = controller.check_validity(input_data.code)
    
    return {"valid": is_legit}