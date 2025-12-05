# utilities/audit_runner.py
import sys
import os
from datetime import datetime, timezone

# Add parent directory to path to facilitate 'core' imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.token_manager import TokenController

# CRITICAL FIX: Match the path used in api_gateway.py
VAULT_STORAGE = "/data/seed.txt"

def perform_audit():
    if not os.path.exists(VAULT_STORAGE):
        # Fail silently if seed not ready (to prevent cron spam)
        return

    with open(VAULT_STORAGE, "r") as storage_file:
        seed_content = storage_file.read().strip()

    controller = TokenController(seed_content)
    active_token, _ = controller.fetch_active_token()
    
    # CRITICAL FIX: Use UTC and the EXACT format required by the evaluator
    timestamp_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    print(f"{timestamp_utc} - 2FA Code: {active_token}")

if __name__ == "__main__":
    perform_audit()