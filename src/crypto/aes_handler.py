import os
import time
import logging
import numpy as np
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.exceptions import InvalidTag

logger = logging.getLogger(__name__)

class AESDataAtRestHandler:
    """
    AES-256-GCM encryption for data stored on each cloud node.
    """
    
    def __init__(self, node_password: str, config: dict):
        self.iterations = config['aes']['iterations']
        # In a real system, salt would be stored alongside the encrypted data
        self.salt = os.urandom(16)
        self.key = self._derive_key(node_password)
        self.aesgcm = AESGCM(self.key)
    
    def _derive_key(self, password: str) -> bytes:
        """Derive a 256-bit AES key from a password using PBKDF2."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=self.iterations
        )
        return kdf.derive(password.encode())
    
    def encrypt_data(self, plaintext: bytes) -> bytes:
        """Encrypt data with AES-256-GCM. Returns nonce + ciphertext."""
        nonce = os.urandom(12)
        ciphertext = self.aesgcm.encrypt(nonce, plaintext, None)
        return nonce + ciphertext
    
    def decrypt_data(self, encrypted_data: bytes) -> bytes:
        """Decrypt data. Raises InvalidTag if tampered."""
        if len(encrypted_data) < 12:
            raise ValueError("Encrypted data too short")
        nonce = encrypted_data[:12]
        ciphertext = encrypted_data[12:]
        try:
            plaintext = self.aesgcm.decrypt(nonce, ciphertext, None)
            return plaintext
        except InvalidTag:
            logger.error("Integrity check failed: Data was tampered with!")
            raise

    encrypt = encrypt_data
    decrypt = decrypt_data
    
    def encrypt_file(self, input_path: str, output_path: str):
        """Encrypt an entire file."""
        with open(input_path, 'rb') as f:
            plaintext = f.read()
        encrypted = self.encrypt_data(plaintext)
        with open(output_path, 'wb') as f:
            f.write(encrypted)
    
    def decrypt_file(self, input_path: str, output_path: str):
        """Decrypt an entire file."""
        with open(input_path, 'rb') as f:
            encrypted = f.read()
        plaintext = self.decrypt_data(encrypted)
        with open(output_path, 'wb') as f:
            f.write(plaintext)
            
    def benchmark(self, data_sizes_bytes=[1024, 10240, 102400, 1048576], iterations=50):
        """
        Benchmark encryption/decryption speed.
        Returns: dict mapping size -> {encrypt_ms, decrypt_ms}
        """
        results = {}
        for size in data_sizes_bytes:
            data = os.urandom(size)
            
            # Encrypt
            t0 = time.perf_counter_ns()
            for _ in range(iterations):
                enc = self.encrypt_data(data)
            enc_time_ms = ((time.perf_counter_ns() - t0) / 1e6) / iterations
            
            # Decrypt
            t0 = time.perf_counter_ns()
            for _ in range(iterations):
                self.decrypt_data(enc)
            dec_time_ms = ((time.perf_counter_ns() - t0) / 1e6) / iterations
            
            # Throughput in MB/s
            throughput_mb_s = (size / 1024 / 1024) / (enc_time_ms / 1000)
            
            results[size] = {
                'encrypt_ms': enc_time_ms,
                'decrypt_ms': dec_time_ms,
                'throughput_mb_s': throughput_mb_s
            }
            
        return results
