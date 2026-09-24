import hashlib
import json

class MerkleTree:
    """
    Binary Merkle tree for transaction integrity in each block.
    """
    
    def __init__(self, transactions: list):
        self.transactions = transactions
        self.root = self._build_tree()
    
    def _hash(self, data: bytes) -> str:
        """Hash using SHA3-256 (quantum-resistant hash function)."""
        return hashlib.sha3_256(data).hexdigest()
    
    def _build_tree(self) -> str:
        """Build the tree bottom-up, return root hash."""
        if not self.transactions:
            return self._hash(b'empty')
        
        # Leaf level: hash each transaction
        current_level = [self._hash(tx.to_bytes()) for tx in self.transactions]
        
        # Build up: pair and hash
        while len(current_level) > 1:
            next_level = []
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                right = current_level[i+1] if i+1 < len(current_level) else left
                combined = self._hash((left + right).encode('utf-8'))
                next_level.append(combined)
            current_level = next_level
            
        return current_level[0]
