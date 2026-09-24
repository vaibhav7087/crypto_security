import time
import os
import logging
from cryptography.hazmat.primitives.asymmetric import ec, rsa, padding
from cryptography.hazmat.primitives import hashes, serialization

logger = logging.getLogger(__name__)

class ClassicalCryptoHandler:
    """
    Classical cryptography baseline for comparison with PQC.
    
    Implements:
    - ECDH (P-256) key exchange
    - RSA-2048 signatures
    """
    
    def __init__(self, config):
        self.ecdh_curve = ec.SECP256R1()
        self.rsa_key_size = config['classical_crypto']['rsa_key_size']
        
    def generate_kem_keypair(self):
        """Generate ECDH key pair."""
        private_key = ec.generate_private_key(self.ecdh_curve)
        public_key = private_key.public_key()
        
        # Serialize for sizing
        sk_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        pk_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.X509,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return pk_bytes, sk_bytes
        
    def encapsulate(self, public_key_bytes):
        """Simulate encapsulation with ECDH: generate ephemeral key and derive secret."""
        # Load peer public key
        peer_public_key = serialization.load_pem_public_key(public_key_bytes)
        
        # Generate ephemeral key
        ephemeral_private = ec.generate_private_key(self.ecdh_curve)
        ephemeral_public = ephemeral_private.public_key()
        
        # Derive shared secret
        shared_secret = ephemeral_private.exchange(ec.ECDH(), peer_public_key)
        
        # Serialize ephemeral public key as the "ciphertext"
        ct = ephemeral_public.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return ct, shared_secret
        
    def decapsulate(self, secret_key_bytes, ciphertext_bytes):
        """Simulate decapsulation: load private key and ephemeral public key, derive secret."""
        private_key = serialization.load_pem_private_key(secret_key_bytes, password=None)
        ephemeral_public = serialization.load_pem_public_key(ciphertext_bytes)
        
        shared_secret = private_key.exchange(ec.ECDH(), ephemeral_public)
        return shared_secret
        
    def generate_sig_keypair(self):
        """Generate RSA signing key pair."""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=self.rsa_key_size
        )
        public_key = private_key.public_key()
        
        sk_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        )
        pk_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return pk_bytes, sk_bytes
        
    def sign(self, secret_key_bytes, message: bytes):
        """Sign a message with RSA."""
        private_key = serialization.load_pem_private_key(secret_key_bytes, password=None)
        signature = private_key.sign(
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return signature
        
    def verify(self, public_key_bytes, message: bytes, signature: bytes):
        """Verify an RSA signature."""
        public_key = serialization.load_pem_public_key(public_key_bytes)
        try:
            public_key.verify(
                signature,
                message,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception:
            return False
            
    def benchmark_all(self, iterations=10):
        """Benchmark all operations."""
        results = {}
        
        # KEM Keygen
        t0 = time.time()
        for _ in range(iterations):
            self.generate_kem_keypair()
        results['kem_keygen_ms'] = (time.time() - t0) * 1000 / iterations
        
        pk, sk = self.generate_kem_keypair()
        results['public_key_size'] = len(pk)
        results['secret_key_size'] = len(sk)
        
        # Encaps
        t0 = time.time()
        for _ in range(iterations):
            self.encapsulate(pk)
        results['kem_encaps_ms'] = (time.time() - t0) * 1000 / iterations
        
        ct, ss = self.encapsulate(pk)
        results['ciphertext_size'] = len(ct)
        
        # Decaps
        t0 = time.time()
        for _ in range(iterations):
            self.decapsulate(sk, ct)
        results['kem_decaps_ms'] = (time.time() - t0) * 1000 / iterations
        
        # Sig Keygen
        t0 = time.time()
        for _ in range(iterations):
            self.generate_sig_keypair()
        results['sig_keygen_ms'] = (time.time() - t0) * 1000 / iterations
        
        spk, ssk = self.generate_sig_keypair()
        msg = b"test message"
        
        # Sign
        t0 = time.time()
        for _ in range(iterations):
            self.sign(ssk, msg)
        results['sig_sign_ms'] = (time.time() - t0) * 1000 / iterations
        
        sig = self.sign(ssk, msg)
        results['signature_size'] = len(sig)
        
        # Verify
        t0 = time.time()
        for _ in range(iterations):
            self.verify(spk, msg, sig)
        results['sig_verify_ms'] = (time.time() - t0) * 1000 / iterations
        
        return results
