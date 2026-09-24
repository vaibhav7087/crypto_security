import time
import logging
import pandas as pd
import numpy as np
import torch
import os

from src.crypto.pqc_handler import PQCHandler
from src.crypto.aes_handler import AESDataAtRestHandler
from src.blockchain.chain import Blockchain
from src.blockchain.consensus import SimplifiedPBFT
from src.blockchain.trust_manager import TrustManager
from src.testbed.node_manager import NodeManager
from src.testbed.workload_generator import WorkloadGenerator
from src.testbed.attack_simulator import AttackSimulator
from src.models.autoencoder import AnomalyAutoencoder
from src.utils import load_config
import pickle

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def collect_node_features(node_manager, scaler, num_features):
    """Simulates collecting a feature vector for each active node."""
    # In a real system, this would gather metrics (CPU, net io, etc) and format them.
    # Here, we generate realistic feature vectors matching the input dim.
    num_nodes = len(node_manager.nodes)
    if num_nodes == 0:
        return np.array([])
    # Generate benign-like features
    raw_features = np.random.exponential(scale=100, size=(num_nodes, num_features))
    # Add random anomaly to one node occasionally (10% chance)
    if np.random.rand() < 0.1:
        raw_features[0, :] *= 10  # simulate attack spike
    return scaler.transform(raw_features)

class ResponseEngine:
    def __init__(self, config, trust_manager, node_manager):
        self.config = config['response']
        self.trust = trust_manager
        self.nodes = node_manager
        
    def process_anomaly(self, node_id, anomaly_score, context):
        """Determine action based on anomaly severity and update trust."""
        # Penalize trust
        if anomaly_score > self.config['severity_thresholds']['low']:
            self.trust.penalize(node_id, anomaly_score)
            
        # Determine active response
        if anomaly_score > self.config['severity_thresholds']['critical']:
            logger.warning(f"[CRITICAL] Isolating node {node_id} (Score: {anomaly_score:.3f})")
            return "isolate"
        elif anomaly_score > self.config['severity_thresholds']['high']:
            logger.warning(f"[HIGH] Restarting/Isolating node {node_id} (Score: {anomaly_score:.3f})")
            return "isolate"
        elif anomaly_score > self.config['severity_thresholds']['medium']:
            logger.info(f"[MEDIUM] Throttling traffic for node {node_id} (Score: {anomaly_score:.3f})")
            return "throttle"
        return "log"

def run_end_to_end():
    config = load_config()
    os.makedirs('results/tables', exist_ok=True)
    os.makedirs('results/figures', exist_ok=True)
    
    logger.info("Starting End-to-End Integrated Testbed Pipeline")
    
    # 0. Load trained model & scaler
    model_path = 'results/autoencoder_best.pth'
    scaler_path = os.path.join(config['dataset']['processed_dir'], 'scaler.pkl')
    
    if not os.path.exists(model_path) or not os.path.exists(scaler_path):
        logger.error("Model or scaler not found. Run --train pipeline first.")
        return
        
    logger.info("0. Loading trained Autoencoder and Scaler")
    checkpoint = torch.load(model_path, map_location=config['autoencoder']['device'], weights_only=False)
    # The config now has the exact input_dim
    input_dim = config['autoencoder']['input_dim']
    ae_model = AnomalyAutoencoder(
        input_dim=input_dim,
        hidden_dims=config['autoencoder']['hidden_dims'],
        latent_dim=config['autoencoder']['latent_dim']
    )
    ae_model.load_state_dict(checkpoint['model_state_dict'])
    ae_model.to(config['autoencoder']['device'])
    ae_model.eval()
    ae_threshold = checkpoint.get('threshold', 0.5) # Fallback if not in dict
    
    with open(scaler_path, 'rb') as f:
        scaler = pickle.load(f)
    
    # 1. Initialize PQC & AES
    logger.info("1. Initializing Cryptographic Layers")
    pqc = PQCHandler(config)
    aes = AESDataAtRestHandler("master_password_123", config)
    
    # 2. Initialize Blockchain & Trust
    logger.info("2. Initializing Blockchain and Trust Manager")
    consensus = SimplifiedPBFT("master", ["master", "node_1", "node_2"], pqc)
    blockchain = Blockchain(config, pqc, consensus)
    trust_manager = TrustManager(config, blockchain)
    
    # 3. Initialize Docker Testbed
    logger.info("3. Starting Docker Testbed")
    node_manager = NodeManager(config)
    node_manager.start_cluster(3)  # start small for quick test
    
    for node_id in node_manager.nodes.keys():
        trust_manager.register_node(node_id)
        
    response_engine = ResponseEngine(config, trust_manager, node_manager)
    
    # 4. Traffic & Attacks
    logger.info("4. Initializing Workload & Attack Simulators")
    workload_gen = WorkloadGenerator(config, node_manager)
    attack_sim = AttackSimulator(config, node_manager, workload_gen)
    
    # 5. Run Scenario Loop
    logger.info("5. Running Monitoring Loop (Metrics -> Inference -> Response)")
    num_rounds = 20
    latency_records = []
    
    device = config['autoencoder']['device']
    
    for round_num in range(num_rounds):
        node_ids = list(node_manager.nodes.keys())
        if not node_ids:
            break
            
        t_start = time.perf_counter_ns()
        
        # A. Collect features
        features = collect_node_features(node_manager, scaler, input_dim)
        if len(features) == 0:
            continue
            
        t_collect = time.perf_counter_ns()
        
        # B. Inference
        with torch.no_grad():
            x_tensor = torch.FloatTensor(features).to(device)
            scores = ae_model.get_anomaly_score(x_tensor).cpu().numpy()
        t_inference = time.perf_counter_ns()
        
        # C. Response Engine & Trust
        for i, node_id in enumerate(node_ids):
            action = response_engine.process_anomaly(node_id, float(scores[i]), {})
            # Simulate a valid signature reward periodically
            if round_num % 5 == 0:
                trust_manager.reward_signature(node_id)
        t_response = time.perf_counter_ns()
        
        # Log latency
        latency_records.append({
            'round': round_num,
            'collect_ms': (t_collect - t_start) / 1e6,
            'inference_ms': (t_inference - t_collect) / 1e6,
            'response_ms': (t_response - t_inference) / 1e6,
            'total_ms': (t_response - t_start) / 1e6
        })
        time.sleep(0.1) # Simulate time passing
    
    # Save latency results
    latency_df = pd.DataFrame(latency_records)
    latency_df.to_csv('results/tables/e2e_latency.csv', index=False)
    logger.info(f"End-to-End latency saved to results/tables/e2e_latency.csv")
    
    # Save trust trajectories
    for node_id in node_manager.nodes.keys():
        traj = trust_manager.get_trust_trajectory(node_id)
        traj.to_csv(f'results/tables/trust_{node_id}.csv', index=False)
        
    logger.info(f"Blockchain height: {len(blockchain.chain)}")
    valid, msg = blockchain.verify_chain()
    logger.info(f"Blockchain validation: {valid} ({msg})")
    
    # 6. Teardown
    logger.info("6. Tearing down testbed")
    node_manager.teardown()
    
    logger.info("End-to-End Pipeline Complete.")

if __name__ == "__main__":
    run_end_to_end()
