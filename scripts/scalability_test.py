import time
import logging
import pandas as pd
import psutil
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils import load_config
from src.testbed.node_manager import NodeManager
from src.crypto.pqc_handler import PQCHandler
from src.blockchain.chain import Blockchain
from src.blockchain.consensus import SimplifiedPBFT

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_system_metrics():
    """Get current host CPU and Memory usage."""
    return {
        'cpu_percent': psutil.cpu_percent(interval=1),
        'mem_used_mb': psutil.virtual_memory().used / (1024 * 1024)
    }

def run_scalability_test():
    config = load_config()
    os.makedirs('results/tables', exist_ok=True)
    os.makedirs('results/figures', exist_ok=True)
    
    steps = config['docker_testbed']['scalability_steps']
    logger.info(f"Starting scalability tests for steps: {steps}")
    
    pqc = PQCHandler(config)
    node_manager = NodeManager(config)
    
    results = []
    
    for num_nodes in steps:
        logger.info(f"\n--- Testing with {num_nodes} Nodes ---")
        
        # 1. Start Nodes
        t0 = time.time()
        node_manager.start_cluster(num_nodes)
        startup_time = time.time() - t0
        logger.info(f"Started {num_nodes} nodes in {startup_time:.2f}s")
        
        # 2. Get Host Resource Usage
        time.sleep(2) # Let containers settle
        metrics = get_system_metrics()
        
        # 3. Test Blockchain Consensus Scaling (Simulated)
        # As nodes increase, PBFT message complexity goes up (O(n^2))
        node_ids = list(node_manager.nodes.keys())
        consensus = SimplifiedPBFT(node_ids[0], node_ids, pqc)
        bc = Blockchain(config, pqc, consensus)
        
        t0 = time.perf_counter_ns()
        bc.add_event({'test': 'scalability', 'nodes': num_nodes})
        tx_latency_ms = (time.perf_counter_ns() - t0) / 1e6
        
        logger.info(f"System: CPU {metrics['cpu_percent']}%, Mem {metrics['mem_used_mb']:.0f}MB. Tx Latency: {tx_latency_ms:.2f}ms")
        
        results.append({
            'num_nodes': num_nodes,
            'startup_time_s': startup_time,
            'cpu_percent': metrics['cpu_percent'],
            'mem_used_mb': metrics['mem_used_mb'],
            'consensus_latency_ms': tx_latency_ms
        })
        
        # 4. Teardown before next step
        node_manager.teardown()
        time.sleep(2) # Give Docker a moment to clean up
        
    df = pd.DataFrame(results)
    df.to_csv('results/tables/scalability_results.csv', index=False)
    logger.info("Scalability tests complete. Saved to results/tables/scalability_results.csv")

if __name__ == "__main__":
    run_scalability_test()
