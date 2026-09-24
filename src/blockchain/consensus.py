import logging

logger = logging.getLogger(__name__)

class SimplifiedPBFT:
    """
    Simplified Practical Byzantine Fault Tolerance for a permissioned network.
    
    In this simulation, we simulate the logic of PBFT without the actual network roundtrips.
    We assume honest nodes automatically endorse blocks if they are valid.
    """
    
    def __init__(self, node_id: str, all_node_ids: list, pqc_handler):
        self.node_id = node_id
        self.all_nodes = all_node_ids
        self.pqc = pqc_handler
        self.quorum_size = (2 * len(all_node_ids)) // 3 + 1
        
    def propose_block(self, block) -> dict:
        """Simulate proposing a block."""
        return {
            'type': 'PROPOSAL',
            'block': block,
            'proposer': self.node_id
        }
        
    def handle_proposal(self, proposal, chain_validator) -> bool:
        """Validate proposal, return True if valid (simulate PREPARE/COMMIT)."""
        block = proposal['block']
        # Validate block
        if not chain_validator(block):
            return False
            
        # Simulate reaching quorum assuming 2/3 honest nodes
        # (In a real distributed system, we'd wait for network messages)
        return True
