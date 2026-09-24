"""Quick smoke test to verify all imports work and basic operations succeed."""
import pytest
import numpy as np

def test_autoencoder_forward():
    from src.models.autoencoder import AnomalyAutoencoder
    import torch
    model = AnomalyAutoencoder(input_dim=10, hidden_dims=[8, 4], latent_dim=2, dropout=0.1)
    x = torch.randn(5, 10)
    out, latent = model(x)
    assert out.shape == (5, 10)
    assert latent.shape == (5, 2)

def test_lstm_forward():
    from src.models.lstm_predictor import ThreatPredictor
    import torch
    model = ThreatPredictor(input_dim=10, hidden_dim=8, num_layers=1, dropout=0.1)
    x = torch.randn(3, 5, 10)  # batch=3, seq=5, features=10
    out = model(x)
    assert out.shape == (3, 1)

def test_pqc_handler():
    from src.crypto.pqc_handler import PQCHandler
    config = {'pqc': {'kem_algorithm': 'Kyber768', 'sig_algorithm': 'Dilithium3'}}
    pqc = PQCHandler(config)
    pk, sk = pqc.generate_kem_keypair()
    assert len(pk) > 0

def test_blockchain():
    from src.crypto.pqc_handler import PQCHandler
    from src.blockchain.chain import Blockchain
    from src.blockchain.consensus import SimplifiedPBFT
    config = {
        'pqc': {'kem_algorithm': 'Kyber768', 'sig_algorithm': 'Dilithium3'},
        'blockchain': {'block_size': 2, 'difficulty': 1, 'consensus': 'PBFT', 'min_validators': 3, 'merkle_hash': 'sha3_256'}
    }
    pqc = PQCHandler(config)
    consensus = SimplifiedPBFT("n1", ["n1", "n2", "n3"], pqc)
    bc = Blockchain(config, pqc, consensus)
    tx_id = bc.add_event({'type': 'TEST', 'node_id': 'n1'})
    assert tx_id is not None
