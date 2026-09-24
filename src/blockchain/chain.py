import time
import logging
from typing import List, Tuple
from src.blockchain.transaction import Transaction
from src.blockchain.block import Block

logger = logging.getLogger(__name__)

class Blockchain:
    """
    The full blockchain: chain of blocks + validation + querying.
    """
    
    def __init__(self, config, pqc_handler, consensus):
        self.config = config['blockchain']
        self.pqc = pqc_handler
        self.consensus = consensus
        
        # We need a signing key for the node generating transactions
        self.my_node_id = "master_node"
        self.my_sig_pk, self.my_sig_sk = self.pqc.generate_sig_keypair()
        
        self.chain: List[Block] = [self._create_genesis_block()]
        self.pending_transactions: List[Transaction] = []
        
    def _create_genesis_block(self) -> Block:
        return Block.create(
            index=0,
            timestamp=0.0,
            transactions=[],
            previous_hash="0",
            difficulty=self.config['difficulty']
        )
        
    def add_event(self, event_data: dict) -> str:
        """Create a signed transaction from an event dict and add to pending pool."""
        tx = Transaction.create(
            timestamp=time.time(),
            event_type=event_data.get('type', 'GENERIC'),
            node_id=event_data.get('node_id', 'unknown'),
            data=event_data,
            pqc_handler=self.pqc,
            sig_sk=self.my_sig_sk,
            sig_pk=self.my_sig_pk
        )
        self.pending_transactions.append(tx)
        
        if len(self.pending_transactions) >= self.config['block_size']:
            self.mine_block()
            
        return tx.tx_id
        
    def mine_block(self) -> Block:
        """Bundle pending transactions into a block, run consensus, add to chain."""
        if not self.pending_transactions:
            return None
            
        txs_to_mine = self.pending_transactions[:self.config['block_size']]
        
        t0 = time.time()
        new_block = Block.create(
            index=len(self.chain),
            timestamp=time.time(),
            transactions=txs_to_mine,
            previous_hash=self.chain[-1].hash,
            difficulty=self.config['difficulty']
        )
        
        # Simulate Consensus
        proposal = self.consensus.propose_block(new_block)
        approved = self.consensus.handle_proposal(proposal, self._validate_proposed_block)
        
        if approved:
            self.chain.append(new_block)
            self.pending_transactions = self.pending_transactions[len(txs_to_mine):]
            logger.info(f"Mined and appended block {new_block.index} with {len(txs_to_mine)} txs in {time.time()-t0:.3f}s")
            return new_block
        else:
            logger.error("Consensus failed for new block")
            return None
            
    def _validate_proposed_block(self, block: Block) -> bool:
        if block.previous_hash != self.chain[-1].hash:
            return False
        if block.index != len(self.chain):
            return False
        return block.verify(self.config['difficulty'])
        
    def verify_chain(self) -> Tuple[bool, str]:
        """Verify entire chain integrity."""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]
            if not current_block.verify(self.config['difficulty']):
                return False, f"Block {i} verification failed"
                
            if current_block.previous_hash != previous_block.hash:
                return False, f"Block {i} previous_hash mismatch"
                
            # Check signatures
            for tx in current_block.transactions:
                if not tx.verify_signature(self.pqc):
                    return False, f"Invalid signature in Block {i}, tx {tx.tx_id}"
                    
        return True, "Chain is valid"
        
    def tamper_test(self, block_index: int, tx_index: int) -> dict:
        """
        Intentionally modify a past transaction and demonstrate detection.
        """
        if block_index >= len(self.chain) or block_index == 0:
            return {'error': 'Invalid block index'}
            
        block = self.chain[block_index]
        if tx_index >= len(block.transactions):
            return {'error': 'Invalid tx index'}
            
        # Original state
        valid_before, msg_before = self.verify_chain()
        original_hash = block.hash
        original_merkle = block.merkle_root
        
        # Tamper
        import copy
        tampered_data = copy.deepcopy(block.transactions[tx_index].data)
        tampered_data['tampered'] = True
        block.transactions[tx_index].data = tampered_data
        
        # Check
        valid_after, msg_after = self.verify_chain()
        
        # Restore
        del block.transactions[tx_index].data['tampered']
        
        return {
            'valid_before': valid_before,
            'original_hash': original_hash,
            'original_merkle': original_merkle,
            'tampered': True,
            'valid_after': valid_after,
            'error_message': msg_after
        }
