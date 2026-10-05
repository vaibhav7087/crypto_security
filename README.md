# Hybrid Decentralized Security Framework for Heterogeneous Cloud Computing Environments

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-Deep%20Learning-red.svg)](https://pytorch.org/)
[![NIST PQC](https://img.shields.io/badge/NIST%20PQC-Kyber768%20%7C%20Dilithium3-brightgreen.svg)](https://csrc.nist.gov/projects/post-quantum-cryptography)
[![Blockchain](https://img.shields.io/badge/Blockchain-PBFT%20%7C%20Merkle%20Tree-orange.svg)]()
[![Dataset](https://img.shields.io/badge/Dataset-CICIDS2018-purple.svg)](https://www.unb.ca/cic/datasets/ids-2018.html)

A production-grade, zero-trust cloud security architecture integrating **Deep Unsupervised Neural Networks (Autoencoder & Sequential LSTM)**, **NIST Round-3 Post-Quantum Cryptography (CRYSTALS-Kyber768 & CRYSTALS-Dilithium3)**, and a **Permissioned Byzantine Fault Tolerant (PBFT) Blockchain** for autonomous anomaly detection, dynamic reputation management, and tamper-proof forensic auditing across heterogeneous cloud containers.

---

## Quick Start: How to Run (At a Glance)

### Prerequisites
* **Python 3.10+** (64-bit)
* Windows PowerShell / CMD or Linux/macOS Bash
* Minimum 8 GB RAM (16 GB recommended)

### 1. Environment Setup
Clone the repository and install all dependencies:

```bash
# Clone the repository
git clone https://github.com/vaibhav7087/crypto_security.git
cd crypto_security

# Create and activate virtual environment
python -m venv venv

# Windows (PowerShell):
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1

# Windows (CMD):
venv\Scripts\activate.bat

# Linux / macOS:
source venv/bin/activate

# Install required dependencies
pip install -r requirements.txt
```

---

### 2. Available Run Options

#### Option A: Interactive Web Simulation Dashboard (Recommended)
Launches the full interactive browser dashboard demonstrating live PyTorch forward passes, PQC key generation, blockchain block minting, and closed-loop autonomous mitigation in real time.

```bash
# Windows (PowerShell or CMD):
python web_server.py

# Or directly with virtualenv python:
.\venv\Scripts\python.exe web_server.py
```

* **Access the Dashboard:** Open your browser and navigate to **[http://localhost:8080](http://localhost:8080)**.
* **Dashboard Features:**
  * **Live Mesh Stream:** Real-time execution of the 8-step defense lifecycle across heterogeneous nodes.
  * **Manual Step Mode:** Use `Next Step ⏭️` to inspect intermediate mathematical tensors, reconstruction errors, and trust updates.
  * **Interactive Tamper Experiment:** Click `🚨 Tamper with Block #1 History` to test SHA3-256 Merkle root verification and observe real-time cryptographic failure detection.
  * **Node Inspector:** Click any container card to inspect its live NIST Kyber-768 public key, Dilithium-3 signature identity, and firewall isolation rules.

---

#### Option B: Full CLI Pipeline & Reproducibility Suite (`run_all.py`)
Executes the headless end-to-end research pipeline, including data preparation, neural network training/evaluation against 4 baselines, PQC latency benchmarks, multi-node scalability simulations, and automated publication figure generation.

```bash
# Run the entire pipeline end-to-end:
python run_all.py --all

# Or run specific pipeline stages:
python run_all.py --train      # Train and evaluate Autoencoder, LSTM, CNN, Isolation Forest, and One-Class SVM
python run_all.py --crypto     # Benchmark NIST Kyber-768/Dilithium-3 against classical RSA/ECDH
python run_all.py --scale      # Execute cluster scalability tests from 5 to 30 nodes
python run_all.py --figures    # Regenerate all high-resolution publication charts in results/figures/
python run_all.py --testbed    # Run end-to-end cloud testbed simulation
```

---

#### Option C: Automated Verification & Unit Tests
Verify model forward passes, PQC key encapsulation/signatures, and PBFT consensus integrity:

```bash
python -m pytest tests/ -v
```

---

### Using the Real Official CICIDS2018 Dataset (Optional / PhD Evaluation)

This repository comes pre-packaged with preprocessed data matrices in `data/processed/` and pre-trained model weights in `results/`, allowing you to run the interactive dashboard and benchmark evaluations immediately.

If an academic advisor, committee, or research reviewer requires running the pipeline directly on the **original, full-scale CICIDS2018 PCAP/CSV captures**:

1. **Download the Official Dataset:**
   * Download the daily traffic CSV captures from the official [UNB Canadian Institute for Cybersecurity Portal](https://www.unb.ca/cic/datasets/ids-2018.html) (or via AWS Open Data: `s3://cse-cic-ids2018/`).
2. **Place CSVs in the Raw Directory:**
   * Drop the downloaded CSV files directly into:
     ```
     crypto_security/data/raw/
     ```
3. **Execute the Automated Data Processing Pipeline:**
   ```bash
   python run_all.py --data
   ```
   * The automated cleaner (`src/preprocessing/clean_data.py`) will automatically scan `data/raw/`, clean infinite/NaN values, strip whitespace, remove duplicates, extract the 80 flow features, normalize values, and partition the data into `data/processed/`.

---

## Research Objectives & Implementation Mapping

This framework directly addresses and satisfies the three core research objectives:

### Objective 1: ANN-Based Adaptive Security Framework
> *"To provide an ANN-based security framework that is adaptive, self-learning, and capable of autonomous response, threat prediction, and real-time anomaly detection in heterogeneous cloud computing environments."*

| Feature | Implementation | Implementation File | Verification & Evidence |
| :--- | :--- | :--- | :--- |
| **Real-Time Anomaly Detection** | Deep Unsupervised Autoencoder ($77 \to 64 \to 32 \to 16 \to 8 \to 16 \to 32 \to 64 \to 77$) evaluating reconstruction loss against calibrated threshold $\tau = 0.000784$. | [`src/models/autoencoder.py`](src/models/autoencoder.py) | **Accuracy: 96.92%**, **Precision: 90.75%**, **Recall: 90.75%**, **F1-Score: 0.9075**, Latency: **5.99 ms**. Checkpoint: `results/autoencoder_best.pth`. |
| **Threat Prediction** | Sequential Recurrent Neural Network (LSTM) forecasting multi-step attack escalation before payload detonation. | [`src/models/lstm_predictor.py`](src/models/lstm_predictor.py) | `results/lstm_best.pth`, Sequence evaluation in `results/tables/model_comparison.csv`. |
| **Adaptive Self-Learning** | Sliding-window FIFO buffer (5,000 samples) fine-tuning model weights incrementally on verified clean flows to defeat **concept drift**. | [`src/detection/adaptive_retrainer.py`](src/detection/adaptive_retrainer.py) | Pipeline Step 8 in `web_server.py`, recalibrates manifold without full retrain. |
| **Autonomous Response** | Sub-second closed-loop policy engine executing graduated actions: **Traffic Throttling (10% ingress)** for moderate suspicion vs. **Container Isolation (CNI firewall drop)** for critical threats. | [`src/detection/response_engine.py`](src/detection/response_engine.py) | Pipeline Step 7 in `web_server.py`, response latency $< 1.0\text{ ms}$. |
| **Heterogeneous Cloud** | Multi-tier container cluster modeling distinct compute profiles (API Gateway, Worker Pods, Database Master, Auth Microservice, Redis Cache). | [`docker/`](docker/) & [`cloud_deployment_guide/`](cloud_deployment_guide/) | Scalability validation across 5 to 30 nodes. |

---

### Objective 2: Hybrid Decentralized Security Architecture (PQC + Blockchain)
> *"To create and implement a hybrid decentralized security architecture that combines quantum-resistant cryptographic techniques with blockchain-enabled trust management to guarantee improved data integrity, confidentiality, tamper-proof auditing, and secure communication across dispersed cloud infrastructures."*

| Feature | Implementation | Implementation File | Verification & Evidence |
| :--- | :--- | :--- | :--- |
| **Quantum-Resistant KEM** | **NIST CRYSTALS-Kyber768 (ML-KEM)** key encapsulation deriving 256-bit symmetric keys in **0.85 ms** (1,088-byte ciphertext). | [`src/crypto/pqc_handler.py`](src/crypto/pqc_handler.py) | Only +6% latency overhead over classical ECDH secp256r1. Table: `results/tables/crypto_benchmark.csv`. |
| **Quantum-Resistant Signatures** | **NIST CRYSTALS-Dilithium3 (ML-DSA)** lattice digital signatures for event signing and block endorsement in **1.45 ms** (3,293-byte signature). | [`src/crypto/pqc_handler.py`](src/crypto/pqc_handler.py) | Faster than classical RSA-2048 (1.50 ms). |
| **Blockchain Trust Engine** | Dynamic reputation manager updating node trust based on anomaly margins, uptime, and signature validity; logged immutably to ledger. | [`src/blockchain/trust_manager.py`](src/blockchain/trust_manager.py) | Trajectories recorded in `results/tables/trust_node_*.csv`, visualized in `results/figures/trust_trajectories.png`. |
| **Tamper-Proof Auditing** | **SHA3-256 Merkle Trees** combined with hash-chained blocks. Altering a single transaction invalidates all descendant blocks immediately. | [`src/blockchain/chain.py`](src/blockchain/chain.py), [`src/blockchain/block.py`](src/blockchain/block.py) | Tested via `tamper_test()` and interactive dashboard tamper button. |
| **Decentralized Consensus** | **Simplified PBFT** requiring $\ge 2/3$ validator quorum to commit blocks without central single point of failure. | [`src/blockchain/consensus.py`](src/blockchain/consensus.py) | Sub-second consensus latency across cluster nodes. |
| **Data Confidentiality** | **AES-256-GCM** authenticated symmetric encryption with PBKDF2 key derivation for container data at rest. | [`src/crypto/aes_handler.py`](src/crypto/aes_handler.py) | Benchmark in `results/tables/aes_benchmark.csv`. |

---

### Objective 3: Robustness, Scalability & Empirical Verification
> *"To verify the robustness and practical application of the hybrid decentralized security framework by thoroughly assessing its efficacy, scalability, dependability, and computing efficiency using benchmark datasets, actual cloud workloads, and simulated attack scenarios."*

| Feature | Implementation | Implementation File | Verification & Evidence |
| :--- | :--- | :--- | :--- |
| **Benchmark Dataset** | Evaluated on **60,000 real network flows** from the Canadian Institute for Cybersecurity (**CICIDS2018**). | [`data/`](data/) | Standardized 77/80 features in `data/processed/`. |
| **Baseline Comparisons** | Benchmarked against **4 distinct paradigms**: Isolation Forest, One-Class SVM, LSTM Predictor, and CNN-1D. | [`src/models/classical_baselines.py`](src/models/classical_baselines.py), [`src/models/cnn_baseline.py`](src/models/cnn_baseline.py) | Deep Autoencoder demonstrates superior F1 (0.9075 vs 0.6313 IF and 0.6319 OCSVM). Table: `results/tables/model_comparison.csv`. |
| **Statistical Rigor** | **5-Fold Stratified Cross-Validation** and **Paired Student's $t$-test** demonstrating statistical significance. | [`src/evaluation/statistical_tests.py`](src/evaluation/statistical_tests.py) | $F_1 = 0.9067 \pm 0.0051$, $t = 16.37$, $p = 0.0001 < 0.05$ (Null hypothesis rejected). File: `results/tables/statistical_test.json`. |
| **Scalability Assessment** | Multi-node stress testing from **5 to 30 nodes**, logging PBFT consensus time, memory overhead, and throughput. | [`scripts/scalability_test.py`](scripts/scalability_test.py) | Linear scaling profile documented in `results/tables/scalability_results.csv` and `results/figures/scalability.png`. |
| **Simulated Attack Suite** | Synthetic and real multi-vector attack generation (DDoS SYN Flood, Port Scan Sweeps, Zero-Day anomalous distributions). | [`src/testbed/attack_simulator.py`](src/testbed/attack_simulator.py) | Validated across automated tests and real-time dashboard injections. |

---

## Project Structure & Navigation

```
crypto_security/
├── config/                         # Centralized configuration profiles
│   └── config.yaml                 # Model hyperparameters, PQC algorithms, trust & blockchain thresholds
├── data/                           # CICIDS2018 datasets & preprocessed matrices
│   ├── raw/                        # Raw source network captures (CSV)
│   └── processed/                  # Cleaned arrays (X_train.npy, X_test.npy, y_test_binary.npy, etc.)
├── docker/                         # Containerization testbed definitions
│   ├── Dockerfile.alpine           # Lightweight node image (Alpine Linux)
│   ├── Dockerfile.debian           # Database/Worker node image
│   ├── Dockerfile.ubuntu           # Gateway node image
│   └── node_entrypoint.py          # Container runtime bootstrap & telemetry forwarder
├── cloud_deployment_guide/         # Production cloud orchestration specifications
│   ├── kubernetes/                 # Kubernetes manifests (deployments, services, CNI network policies)
│   └── terraform/                  # Terraform Infrastructure as Code (AWS EKS provisioning)
├── results/                        # Generated experimental artifacts, weights & figures
│   ├── autoencoder_best.pth        # Trained PyTorch Autoencoder weights & threshold metadata
│   ├── lstm_best.pth               # Trained PyTorch Sequential LSTM weights
│   ├── tables/                     # CSV empirical benchmarks (model comparisons, cross-validation, PQC latency)
│   └── figures/                    # High-resolution publication plots (ROC curves, confusion matrices, scalability)
├── scripts/                        # Automation & evaluation routines
│   ├── train_and_evaluate.py       # Trains all 5 models and compiles comparative metrics
│   ├── scalability_test.py         # Multi-node benchmark runner (5 to 30 nodes)
│   └── generate_all_figures.py     # Compiles and renders publication-ready plots
├── src/                            # Core Framework Implementation Source Code
│   ├── blockchain/                 # Permissioned PQC Blockchain & Trust Engine
│   │   ├── block.py                # Block data structure, SHA3 hashing, Proof-of-Work
│   │   ├── chain.py                # Hash-chained ledger, chain validation, tamper auditing
│   │   ├── consensus.py            # Simplified PBFT consensus algorithm (2/3 quorum)
│   │   ├── merkle_tree.py          # SHA3-256 binary Merkle tree implementation
│   │   ├── transaction.py          # Dilithium-signed security event transaction model
│   │   └── trust_manager.py        # Dynamic reputation scoring & mathematical penalty engine
│   ├── crypto/                     # Post-Quantum & Classical Cryptographic Suite
│   │   ├── aes_handler.py          # AES-256-GCM symmetric authenticated encryption
│   │   ├── classical_crypto.py     # Classical baseline algorithms (RSA-2048, ECDH secp256r1)
│   │   ├── pqc_handler.py          # NIST Round-3 CRYSTALS-Kyber768 (KEM) & Dilithium3 (Signatures)
│   │   └── secure_channel.py       # Hybrid PQC-authenticated TLS-like channel wrapper
│   ├── detection/                  # Real-Time Threat Handling & Adaptation
│   │   ├── adaptive_retrainer.py   # FIFO sliding-window retraining engine (defeats concept drift)
│   │   └── response_engine.py      # Autonomous closed-loop mitigation (Throttling / Quarantine)
│   ├── evaluation/                 # Metrics & Statistical Validation
│   │   ├── benchmarks.py           # Cryptographic execution timing engine
│   │   ├── end_to_end.py           # End-to-end framework test pipeline
│   │   ├── metrics.py              # Precision, Recall, F1, ROC-AUC, FPR, FNR computation
│   │   └── statistical_tests.py    # 5-fold CV & paired t-test statistical validation
│   ├── models/                     # Deep Neural Network Implementations
│   │   ├── autoencoder.py          # Unsupervised PyTorch Anomaly Autoencoder
│   │   ├── classical_baselines.py  # Isolation Forest and One-Class SVM wrappers
│   │   ├── cnn_baseline.py         # 1D Convolutional Neural Network baseline
│   │   ├── lstm_predictor.py       # Sequential Recurrent Neural Network (LSTM Threat Predictor)
│   │   └── trainer.py              # PyTorch training loops, early stopping, and validation loss tracking
│   ├── preprocessing/              # Data Pipeline & Feature Extraction
│   │   ├── clean_data.py           # Cleans infinite/NaN values and parses CICIDS2018 records
│   │   ├── data_loader.py          # PyTorch Dataset and DataLoader generators
│   │   ├── download_dataset.py     # Automated dataset retrieval and verification
│   │   └── feature_engineering.py  # Normalization, MinMax scaling, and one-hot encoding
│   └── testbed/                    # Cluster Simulation Utilities
│       ├── attack_simulator.py     # Multi-threat attack generator (SYN flood, port sweeps, zero-day)
│       ├── node_manager.py         # Node state manager & role assigner
│       └── workload_generator.py   # Simulates realistic microservice background HTTP/RPC traffic
├── tests/                          # Automated PyTest Test Suite
│   └── test_smoke.py               # Smoke tests for AE, LSTM, PQC, and Blockchain consensus
├── web/                            # Front-End Web Application Assets
│   ├── index.html                  # Responsive multi-tab dashboard interface
│   ├── style.css                   # Custom modern dark-mode glassmorphic design system
│   └── app.js                      # Real-time state polling, client stepper logic, and terminal rendering
├── requirements.txt                # Python package dependency list
├── run_all.py                      # Unified CLI entry point for full pipeline execution
└── web_server.py                   # Multi-threaded HTTP backend streaming live telemetry to web UI
```

---

## Technical Specifications & Parameter Summary

### Deep Autoencoder Architecture
* **Input Layer:** 77 normalized network features (CICIDS2018)
* **Encoder:** Linear(77 $\to$ 64) $\to$ BatchNorm $\to$ LeakyReLU $\to$ Linear(64 $\to$ 32) $\to$ BatchNorm $\to$ LeakyReLU $\to$ Linear(32 $\to$ 16) $\to$ Linear(16 $\to$ 8)
* **Latent Bottleneck:** 8 dimensions
* **Decoder:** Linear(8 $\to$ 16) $\to$ LeakyReLU $\to$ Linear(16 $\to$ 32) $\to$ BatchNorm $\to$ LeakyReLU $\to$ Linear(32 $\to$ 64) $\to$ BatchNorm $\to$ Linear(64 $\to$ 77)
* **Reconstruction Loss:** $\mathcal{L}_{\text{MSE}}(x, \hat{x}) = \frac{1}{D} \sum_{i=1}^{D} (x_i - \hat{x}_i)^2$
* **Calibrated Decision Boundary:** $\tau = 0.000784$

### Cryptographic Parameters
* **Key Encapsulation:** NIST FIPS 203 CRYSTALS-Kyber768 (Public Key: 1,184 B, Secret Key: 2,400 B, Ciphertext: 1,088 B)
* **Digital Signatures:** NIST FIPS 204 CRYSTALS-Dilithium3 (Public Key: 1,952 B, Secret Key: 4,000 B, Signature: 3,293 B)
* **Symmetric Encryption:** AES-256-GCM with 96-bit IV and 128-bit authentication tag
* **Hash Functions:** SHA3-256 (Merkle tree hashing and block header proof-of-work)

### Blockchain Consensus Parameters
* **Consensus Algorithm:** Simplified Practical Byzantine Fault Tolerance (PBFT)
* **Proof-of-Work Target:** Difficulty $d = 2$ (`00...` prefix)
* **Block Capacity:** 10 signed security transactions per block
* **Quorum Threshold:** $\ge \lfloor \frac{2N}{3} \rfloor + 1$ validator agreement

---

## License & Handover Documentation

This project has been implemented, validated, and formatted for academic research, doctoral defense, and industrial cloud deployment. All benchmark outputs, model weights, and visualization charts are reproducible using `python run_all.py --all`.
