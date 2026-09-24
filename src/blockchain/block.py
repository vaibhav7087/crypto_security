import json
import hashlib
from dataclasses import dataclass
from typing import List
from src.blockchain.transaction import Transaction
from src.blockchain.merkle_tree import MerkleTree

@dataclass
class Block:
    """
    A block in the blockchain.
    """
    index: int
    timestamp: float
    transactions: List[Transaction]
    previous_hash: str
    merkle_root: str
    nonce: int
    hash: str
    
    @staticmethod
    def create(index: int, timestamp: float, transactions: List[Transaction], previous_hash: str, difficulty: int = 2):
        """
        Create a new block with proof-of-work.
        """
        merkle_tree = MerkleTree(transactions)
        merkle_root = merkle_tree.root
        
        nonce = 0
        block_hash = ""
        target = "0" * difficulty
        
        while True:
            header = f"{index}{timestamp}{previous_hash}{merkle_root}{nonce}"
            block_hash = hashlib.sha3_256(header.encode('utf-8')).hexdigest()
            if block_hash.startswith(target):
                break
            nonce += 1
            
        return Block(
            index=index,
            timestamp=timestamp,
            transactions=transactions,
            previous_hash=previous_hash,
            merkle_root=merkle_root,
            nonce=nonce,
            hash=block_hash
        )
        
    def verify(self, difficulty: int = 2) -> bool:
        """Verify block hash, nonce and merkle root."""
        header = f"{self.index}{self.timestamp}{self.previous_hash}{self.merkle_root}{self.nonce}"
        computed_hash = hashlib.sha3_256(header.encode('utf-8')).hexdigest()
        
        if computed_hash != self.hash:
            return False
            
        if not self.hash.startswith("0" * difficulty):
            return False
            
        computed_merkle = MerkleTree(self.transactions).root
        if computed_merkle != self.merkle_root:
            return False
            
        return True
