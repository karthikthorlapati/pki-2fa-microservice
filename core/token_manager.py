# core/token_manager.py
import pyotp
import base64
import time

class TokenController:
    # FIX: Added double underscores before and after 'init'
    def __init__(self, raw_hex_seed: str):
        self.seed_hex = raw_hex_seed.strip()
        self.encoded_seed = self._transcode_seed()
        self.otp_engine = pyotp.TOTP(self.encoded_seed)

    def _transcode_seed(self):
        """Transform Hex -> Binary -> Base32 for PyOTP compatibility."""
        # Check for empty seed to prevent crash
        if not self.seed_hex:
            raise ValueError("Seed cannot be empty")
            
        binary_data = bytes.fromhex(self.seed_hex)
        return base64.b32encode(binary_data).decode('utf-8')

    def fetch_active_token(self):
        """Returns the current OTP and seconds remaining in the cycle."""
        current_time = time.time()
        # Determine seconds left in the current 30s cycle
        time_left = int(self.otp_engine.interval - (current_time % self.otp_engine.interval))
        return self.otp_engine.now(), time_left

    def check_validity(self, provided_token: str):
        """Validates a token with a grace period of +/- 1 step."""
        return self.otp_engine.verify(provided_token, valid_window=1)