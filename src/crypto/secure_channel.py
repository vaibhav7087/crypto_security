import time
import os
import logging
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes

logger = logging.getLogger(__name__)

class SecureChannel:
    """
    Secure communication channel using PQC key exchange.
    
    Protocol:
    1. Node A generates Kyber keypair, sends public key to Node B
    2. Node B encapsulates a shared secret using A's public key
    3. Node B sends ciphertext to Node A
    4. Node A decapsulates to get the same shared secret
    5. Both derive an AES-256-GCM key from the shared secret
    6. All subsequent messages are encrypted with AES-256-GCM
    7. All messages are also signed with Dilithium for authenticity
    """
    
    def __init__(self, pqc_handler):
        self.pqc = pqc_handler
        self.session_key = None
        self.my_sig_pk, self.my_sig_sk = self.pqc.generate_sig_keypair()
        self.peer_sig_pk = None
        
        # Temp state for handshake
        self._temp_kem_sk = None
    
    def initiate_handshake(self):
        """Node A: Generate keypair, return public key and signature public key."""
        kem_pk, kem_sk = self.pqc.generate_kem_keypair()
        self._temp_kem_sk = kem_sk
        return {
            'kem_pk': kem_pk,
            'sig_pk': self.my_sig_pk
        }
    
    def respond_to_handshake(self, peer_handshake_msg):
        """Node B: Encapsulate shared secret, return ciphertext."""
        peer_kem_pk = peer_handshake_msg['kem_pk']
        self.peer_sig_pk = peer_handshake_msg['sig_pk']
        
        ciphertext, shared_secret = self.pqc.encapsulate(peer_kem_pk)
        
        # Derive AES key
        self._derive_session_key(shared_secret)
        
        return {
            'ciphertext': ciphertext,
            'sig_pk': self.my_sig_pk
        }
    
    def complete_handshake(self, peer_response_msg):
        """Node A: Decapsulate to derive shared secret."""
        ciphertext = peer_response_msg['ciphertext']
        self.peer_sig_pk = peer_response_msg['sig_pk']
        
        shared_secret = self.pqc.decapsulate(self._temp_kem_sk, ciphertext)
        self._temp_kem_sk = None # clear temp key
        
        # Derive AES key
        self._derive_session_key(shared_secret)
        return True
        
    def _derive_session_key(self, shared_secret: bytes):
        """Derive AES-256 key from shared secret using HKDF."""
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=b'handshake data',
        )
        self.session_key = hkdf.derive(shared_secret)
        self.aesgcm = AESGCM(self.session_key)
    
    def encrypt_message(self, plaintext: bytes) -> dict:
        """Encrypt with AES-256-GCM using session key, and sign."""
        if not self.session_key:
            raise RuntimeError("Handshake not completed")
            
        # Encrypt
        nonce = os.urandom(12)
        ciphertext = self.aesgcm.encrypt(nonce, plaintext, None)
        
        # Sign the ciphertext + nonce
        signature = self.pqc.sign(self.my_sig_sk, nonce + ciphertext)
        
        return {
            'nonce': nonce,
            'ciphertext': ciphertext,
            'signature': signature
        }
    
    def decrypt_message(self, encrypted_msg: dict) -> bytes:
        """Verify signature and decrypt with AES-256-GCM."""
        if not self.session_key:
            raise RuntimeError("Handshake not completed")
            
        nonce = encrypted_msg['nonce']
        ciphertext = encrypted_msg['ciphertext']
        signature = encrypted_msg['signature']
        
        # Verify signature first
        if not self.pqc.verify(self.peer_sig_pk, nonce + ciphertext, signature):
            raise ValueError("Invalid signature on message")
            
        # Decrypt
        plaintext = self.aesgcm.decrypt(nonce, ciphertext, None)
        return plaintext
    
    def measure_handshake_latency(self, iterations=50):
        """
        Measure full handshake time.
        Returns: mean_ms, std_ms
        """
        times = []
        for _ in range(iterations):
            # We need two channels to simulate A and B
            node_b = SecureChannel(self.pqc)
            
            t0 = time.perf_counter_ns()
            # Node A initiates
            msg_a = self.initiate_handshake()
            
            # Node B responds
            msg_b = node_b.respond_to_handshake(msg_a)
            
            # Node A completes
            self.complete_handshake(msg_b)
            t1 = time.perf_counter_ns()
            
            times.append((t1 - t0) / 1e6) # ms
            
        import numpy as np
        return np.mean(times), np.std(times)
