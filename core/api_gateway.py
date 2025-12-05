# core/api_gateway.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from core.crypto_engine import CipherEngine
from core.token_manager import TokenController

gateway = FastAPI()

# System Paths & Storage Configuration
# Corresponds to volume mounts in Docker
VAULT_STORAGE = "/vault_data/plain_seed.hex"
IDENTITY_PATH = "/app/identity_secret.pem"

# Data Transfer Objects (DTOs)
class EncryptedBlob(BaseModel):
    encrypted_seed: str

class TokenInput(BaseModel):
    token: str

# Internal Utility
def _retrieve_stored_seed():
    """Reads the decrypted seed from the secure volume."""
    if not os.path.exists(VAULT_STORAGE):
        return None
    with open(VAULT_STORAGE, "r") as storage_file:
        return storage_file.read().strip()

# --- Gateway Endpoints ---

@gateway.post("/vault/unlock")
def process_unlock(payload: EncryptedBlob):
    """
    Receives the encrypted seed, decrypts it using the private identity,
    and stores the raw hex seed in the secure volume.
    """
    try:
        # Load the Vault Identity (Private Key)
        identity = CipherEngine.import_identity(IDENTITY_PATH)
        
        # Decrypt the incoming blob
        raw_seed = CipherEngine.reveal_secret(payload.encrypted_seed, identity)
        
        # Persist the raw seed to the secure volume
        with open(VAULT_STORAGE, "w") as storage_file:
            storage_file.write(raw_seed)
            
        return {"status": "Vault Unlocked"}
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))

@gateway.get("/vault/token")
def process_token_request():
    """Generates a current time-based token."""
    master_seed = _retrieve_stored_seed()
    if not master_seed:
        raise HTTPException(status_code=500, detail="Vault Locked: Seed not available")
    
    controller = TokenController(master_seed)
    current_token, time_left = controller.fetch_active_token()
    
    return {
        "access_token": current_token, 
        "expires_in_seconds": time_left
    }

@gateway.post("/vault/validate")
def process_validation(input_data: TokenInput):
    """Verifies if a provided token is valid."""
    master_seed = _retrieve_stored_seed()
    if not master_seed:
        raise HTTPException(status_code=500, detail="Vault Locked: Seed not available")
        
    controller = TokenController(master_seed)
    is_legit = controller.check_validity(input_data.token)
    
    return {"is_valid": is_legit}