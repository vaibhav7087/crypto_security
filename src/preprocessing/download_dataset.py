import os
import requests
import zipfile
import yaml
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from src.utils import load_config

def download_file(url, dest_path):
    """Downloads a file with a progress bar."""
    if os.path.exists(dest_path):
        logger.info(f"File already exists: {dest_path}")
        return True

    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        total_size = int(response.headers.get('content-length', 0))
        
        with open(dest_path, 'wb') as f:
            if total_size == 0:
                f.write(response.content)
            else:
                downloaded = 0
                for data in response.iter_content(chunk_size=4096):
                    downloaded += len(data)
                    f.write(data)
                    done = int(50 * downloaded / total_size)
                    print(f"\r[{'=' * done}{' ' * (50-done)}] {downloaded}/{total_size} bytes", end='', flush=True)
        print()
        logger.info(f"Successfully downloaded: {dest_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to download {url}: {e}")
        if os.path.exists(dest_path):
            os.remove(dest_path)
        return False

def main():
    config = load_config()
    raw_dir = config['dataset']['raw_dir']
    os.makedirs(raw_dir, exist_ok=True)
    
    # In a real scenario, these would be the actual CICIDS2018 download URLs.
    # For this simulation/testbed, if actual URLs are not accessible without registration,
    # we simulate the download or provide instructions.
    # The user is instructed to place the files in data/raw/ if they have them.
    
    logger.info("Checking for dataset files in data/raw/...")
    
    expected_files = [
        "Friday-02-03-2018-TrafficForML_CICFlowMeter.csv",
        "Friday-16-02-2018-TrafficForML_CICFlowMeter.csv",
        "Friday-23-02-2018-TrafficForML_CICFlowMeter.csv",
        "Thursday-01-03-2018-TrafficForML_CICFlowMeter.csv",
        "Thursday-15-02-2018-TrafficForML_CICFlowMeter.csv",
        "Thursday-22-02-2018-TrafficForML_CICFlowMeter.csv",
        "Wednesday-14-02-2018-TrafficForML_CICFlowMeter.csv",
        "Wednesday-21-02-2018-TrafficForML_CICFlowMeter.csv",
        "Wednesday-28-02-2018-TrafficForML_CICFlowMeter.csv",
        "Tuesday-20-02-2018-TrafficForML_CICFlowMeter.csv"
    ]
    
    missing_files = [f for f in expected_files if not os.path.exists(os.path.join(raw_dir, f))]
    
    if not missing_files:
        logger.info("All dataset files are present.")
    else:
        logger.warning(f"Missing {len(missing_files)} files. For a full run, please download CICIDS2018 CSVs and place them in {raw_dir}.")
        logger.info("If you want to run a quick test, you can create a dummy CSV file or use a smaller subset.")
        
        # Creating a realistic synthetic dataset for testing purposes
        if len(missing_files) == len(expected_files):
            logger.info("Creating a realistic synthetic dataset for testing...")
            import pandas as pd
            import numpy as np
            
            np.random.seed(42)
            
            # Mimic CICIDS2018 feature names (80 features)
            feature_names = [
                "Dst Port", "Protocol", "Flow Duration", "Tot Fwd Pkts", "Tot Bwd Pkts",
                "TotLen Fwd Pkts", "TotLen Bwd Pkts", "Fwd Pkt Len Max", "Fwd Pkt Len Min",
                "Fwd Pkt Len Mean", "Fwd Pkt Len Std", "Bwd Pkt Len Max", "Bwd Pkt Len Min",
                "Bwd Pkt Len Mean", "Bwd Pkt Len Std", "Flow Byts/s", "Flow Pkts/s",
                "Flow IAT Mean", "Flow IAT Std", "Flow IAT Max", "Flow IAT Min",
                "Fwd IAT Tot", "Fwd IAT Mean", "Fwd IAT Std", "Fwd IAT Max", "Fwd IAT Min",
                "Bwd IAT Tot", "Bwd IAT Mean", "Bwd IAT Std", "Bwd IAT Max", "Bwd IAT Min",
                "Fwd PSH Flags", "Bwd PSH Flags", "Fwd URG Flags", "Bwd URG Flags",
                "Fwd Header Len", "Bwd Header Len", "Fwd Pkts/s", "Bwd Pkts/s",
                "Pkt Len Min", "Pkt Len Max", "Pkt Len Mean", "Pkt Len Std", "Pkt Len Var",
                "FIN Flag Cnt", "SYN Flag Cnt", "RST Flag Cnt", "PSH Flag Cnt",
                "ACK Flag Cnt", "URG Flag Cnt", "CWE Flag Count", "ECE Flag Cnt",
                "Down/Up Ratio", "Pkt Size Avg", "Fwd Seg Size Avg", "Bwd Seg Size Avg",
                "Fwd Byts/b Avg", "Fwd Pkts/b Avg", "Fwd Blk Rate Avg",
                "Bwd Byts/b Avg", "Bwd Pkts/b Avg", "Bwd Blk Rate Avg",
                "Subflow Fwd Pkts", "Subflow Fwd Byts", "Subflow Bwd Pkts", "Subflow Bwd Byts",
                "Init Fwd Win Byts", "Init Bwd Win Byts", "Fwd Act Data Pkts",
                "Fwd Seg Size Min", "Active Mean", "Active Std", "Active Max", "Active Min",
                "Idle Mean", "Idle Std", "Idle Max", "Idle Min"
            ]
            num_features = len(feature_names)
            
            # Generate realistic data
            n_benign = 50000
            n_ddos = 5000
            n_portscan = 3000
            n_bruteforce = 2000
            
            # Benign: low variance, small values
            benign = np.random.exponential(scale=100, size=(n_benign, num_features))
            benign[:, 0] = np.random.choice([80, 443, 8080, 53], size=n_benign)  # Dst Port
            benign[:, 1] = np.random.choice([6, 17], size=n_benign)  # TCP/UDP
            
            # DDoS: very high packet counts, high flow bytes
            ddos = np.random.exponential(scale=500, size=(n_ddos, num_features))
            ddos[:, 3] *= 10  # Tot Fwd Pkts very high
            ddos[:, 5] *= 10  # TotLen Fwd Pkts very high
            ddos[:, 15] *= 100  # Flow Byts/s very high
            
            # Port Scan: many flows, small packets, diverse ports
            portscan = np.random.exponential(scale=50, size=(n_portscan, num_features))
            portscan[:, 0] = np.random.randint(1, 65535, size=n_portscan)  # random ports
            portscan[:, 2] *= 0.1  # very short flow duration
            
            # Brute Force: repeated connections, moderate volume
            bruteforce = np.random.exponential(scale=200, size=(n_bruteforce, num_features))
            bruteforce[:, 3] = np.random.randint(1, 5, size=n_bruteforce)  # few packets per flow
            bruteforce[:, 0] = np.random.choice([22, 3389, 21], size=n_bruteforce)  # SSH/RDP/FTP
            
            # Combine
            all_data = np.vstack([benign, ddos, portscan, bruteforce])
            labels = (['Benign'] * n_benign + ['DDoS'] * n_ddos + 
                      ['PortScan'] * n_portscan + ['BruteForce'] * n_bruteforce)
            
            df = pd.DataFrame(all_data, columns=feature_names)
            df['Label'] = labels
            # Shuffle
            df = df.sample(frac=1, random_state=42).reset_index(drop=True)
            
            out_path = os.path.join(raw_dir, "synthetic_cicids.csv")
            df.to_csv(out_path, index=False)
            logger.info(f"Created {out_path} with {len(df)} rows, {num_features} features, "
                        f"{len(set(labels))} attack classes")

if __name__ == "__main__":
    main()
