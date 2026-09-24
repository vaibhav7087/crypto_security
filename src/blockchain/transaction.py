import json
import uuid
from dataclasses import dataclass

@dataclass
class Transaction:
    """
    A single event recorded on the blockchain.
    """
    tx_id: str
    timestamp: float
    event_type: str
    node_id: str
    data: dict
    signature: bytes = b''
    signer_public_key: bytes = b''
    
    @classmethod
    def create(cls, timestamp: float, event_type: str, node_id: str, data: dict, pqc_handler, sig_sk, sig_pk):
        tx_id = str(uuid.uuid4())
        tx = cls(
            tx_id=tx_id,
            timestamp=timestamp,
            event_type=event_type,
            node_id=node_id,
            data=data,
            signer_public_key=sig_pk
        )
        # Sign the transaction data
        tx.signature = pqc_handler.sign(sig_sk, tx.to_bytes())
        return tx
    
    def to_bytes(self) -> bytes:
        """Serialize transaction for hashing/signing (excluding signature)."""
        tx_dict = {
            'tx_id': self.tx_id,
            'timestamp': self.timestamp,
            'event_type': self.event_type,
            'node_id': self.node_id,
            'data': self.data,
            # we don't include signature in the bytes to be signed
        }
        # Use stable JSON serialization
        return json.dumps(tx_dict, sort_keys=True).encode('utf-8')
        
    def to_dict(self):
        """Full representation including signature (hex encoded for JSON)."""
        import binascii
        return {
            'tx_id': self.tx_id,
            'timestamp': self.timestamp,
            'event_type': self.event_type,
            'node_id': self.node_id,
            'data': self.data,
            'signature': binascii.hexlify(self.signature).decode('utf-8') if self.signature else '',
            'signer_public_key': binascii.hexlify(self.signer_public_key).decode('utf-8') if self.signer_public_key else ''
        }
    
    def verify_signature(self, pqc_handler) -> bool:
        """Verify this transaction's Dilithium signature."""
        if not self.signature or not self.signer_public_key:
            return False
        return pqc_handler.verify(self.signer_public_key, self.to_bytes(), self.signature)
