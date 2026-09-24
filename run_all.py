import sys
import logging
import argparse
import time

# Preprocessing
from src.preprocessing.download_dataset import main as download_dataset
from src.preprocessing.clean_data import clean_data
from src.preprocessing.feature_engineering import feature_engineering

# Evaluation & ML
from src.evaluation.end_to_end import run_end_to_end
from src.evaluation.benchmarks import CryptoBenchmark
from src.evaluation.metrics import MetricsEngine
from src.utils import load_config
from scripts.train_and_evaluate import main as train_evaluate
from scripts.scalability_test import run_scalability_test
from scripts.generate_all_figures import main as generate_figures

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_data_pipeline():
    logger.info("=== Starting Data Pipeline ===")
    download_dataset()
    clean_data()
    feature_engineering()
    logger.info("=== Data Pipeline Complete ===")

def run_crypto_benchmarks():
    logger.info("=== Starting Crypto Benchmarks ===")
    config = load_config()
    benchmark = CryptoBenchmark(config)
    benchmark.run_all()
    logger.info("=== Crypto Benchmarks Complete ===")

def run_ml_training():
    logger.info("=== Starting ML Training & Evaluation ===")
    train_evaluate()
    logger.info("=== ML Training Complete ===")
    
def run_scalability():
    logger.info("=== Starting Scalability Tests ===")
    run_scalability_test()
    logger.info("=== Scalability Tests Complete ===")

def generate_visualizations():
    logger.info("=== Generating Visualizations ===")
    generate_figures()
    logger.info("=== Visualizations Complete ===")

def main():
    parser = argparse.ArgumentParser(description="Hybrid Decentralized ANN-Based Security Framework")
    parser.add_argument('--all', action='store_true', help="Run the entire pipeline sequentially")
    parser.add_argument('--data', action='store_true', help="Run data pipeline (download, clean, feature eng)")
    parser.add_argument('--train', action='store_true', help="Run ML training and evaluation (AE, LSTM, etc)")
    parser.add_argument('--crypto', action='store_true', help="Run cryptography benchmarks")
    parser.add_argument('--testbed', action='store_true', help="Run the testbed end-to-end simulation")
    parser.add_argument('--scale', action='store_true', help="Run the scalability test script")
    parser.add_argument('--figures', action='store_true', help="Generate all visualization figures")
    
    args = parser.parse_args()
    
    if not any(vars(args).values()):
        parser.print_help()
        sys.exit(1)
        
    start_time = time.time()
        
    if args.data or args.all:
        run_data_pipeline()
        
    if args.train or args.all:
        run_ml_training()
        
    if args.crypto or args.all:
        run_crypto_benchmarks()
        
    if args.testbed or args.all:
        run_end_to_end()
        
    if args.scale or args.all:
        run_scalability()
        
    if args.figures or args.all:
        generate_visualizations()
        
    logger.info(f"Total Execution Time: {time.time() - start_time:.2f} seconds")

if __name__ == "__main__":
    main()
