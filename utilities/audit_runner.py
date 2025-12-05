# utilities/audit_runner.py
import sys
import os
from datetime import datetime, timezone

# Add parent directory to path to facilitate 'core' imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(_file_), '..')))

from core.token_manager import TokenController

# Must match the volume path defined in core/api_gateway.py
VAULT_STORAGE = "/vault_data/plain_seed.hex"

def perform_audit():
    """Reads the seed from secure storage and logs a generated token."""
    if not os.path.exists(VAULT_STORAGE):
        # Fail silently or log error if seed isn't ready yet
        print(f"Audit Skipped: No seed found at {VAULT_STORAGE}")
        return

    with open(VAULT_STORAGE, "r") as storage_file:
        seed_content = storage_file.read().strip()

    # Initialize the controller
    controller = TokenController(seed_content)
    
    # Generate token
    active_token, _ = controller.fetch_active_token()
    
    # Log with UTC Timestamp
    timestamp_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    print(f"{timestamp_utc} - Vault Token: {active_token}")

if _name_ == "_main_":
    perform_audit()