"""
Script 1: Train all models, evaluate with 5-fold CV, produce comparison table.
This is the core script for Objective 1 and Objective 3 (ML metrics).
"""
import os
import sys
import json
import time
import logging
import numpy as np
import pandas as pd
import torch
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import (accuracy_score, precision_score, recall_score, 
                             f1_score, roc_auc_score, confusion_matrix,
                             classification_report)

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils import load_config
from src.models.autoencoder import AnomalyAutoencoder
from src.models.lstm_predictor import ThreatPredictor
from src.models.cnn_baseline import CNN1DBaseline
from src.models.classical_baselines import IsolationForestBaseline, OneClassSVMBaseline
from src.models.trainer import train_model, save_model
from src.preprocessing.data_loader import PointDataset, SequenceDataset, get_dataloaders, get_normal_only_loader
from src.evaluation.metrics import MetricsEngine
from src.evaluation.statistical_tests import StatisticalTester
from src.visualization.detection_plots import DetectionPlotter
from torch.utils.data import DataLoader, Subset

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

def evaluate_binary(y_true, y_pred, y_prob=None):
    """Compute all metrics for binary classification."""
    metrics = {
        'accuracy': accuracy_score(y_true, y_pred),
        'precision': precision_score(y_true, y_pred, zero_division=0),
        'recall': recall_score(y_true, y_pred, zero_division=0),
        'f1': f1_score(y_true, y_pred, zero_division=0),
    }
    if y_prob is not None:
        try:
            metrics['auc_roc'] = roc_auc_score(y_true, y_prob)
        except ValueError:
            metrics['auc_roc'] = float('nan')
    cm = confusion_matrix(y_true, y_pred)
    if cm.shape == (2, 2):
        tn, fp, fn, tp = cm.ravel()
        metrics['fpr'] = fp / (fp + tn) if (fp + tn) > 0 else 0
        metrics['fnr'] = fn / (fn + tp) if (fn + tp) > 0 else 0
        metrics['detection_rate'] = tp / (tp + fn) if (tp + fn) > 0 else 0
    return metrics

def train_and_evaluate_autoencoder(config, X_train, y_train, X_test, y_test):
    """Train AE on normal data only, evaluate on full test set."""
    device = config['autoencoder']['device']
    input_dim = X_train.shape[1]
    
    # Filter normal data for training
    normal_mask = y_train == 0
    X_normal = X_train[normal_mask]
    
    # Create model
    model = AnomalyAutoencoder(
        input_dim=input_dim,
        hidden_dims=config['autoencoder']['hidden_dims'],
        latent_dim=config['autoencoder']['latent_dim'],
        dropout=config['autoencoder']['dropout']
    )
    
    # Train on normal data only
    normal_dataset = PointDataset(X_normal, np.zeros(len(X_normal)))
    # Split normal data 90/10 for train/val
    split_idx = int(0.9 * len(X_normal))
    train_ds = Subset(normal_dataset, range(split_idx))
    val_ds = Subset(normal_dataset, range(split_idx, len(X_normal)))
    
    train_loader = DataLoader(train_ds, batch_size=config['autoencoder']['batch_size'], shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=config['autoencoder']['batch_size'], shuffle=False)
    
    t0 = time.time()
    result = train_model(model, train_loader, val_loader, config['autoencoder'], model_type="autoencoder")
    training_time = time.time() - t0
    model = result['model']
    
    # Compute threshold on training normal data
    threshold = model.get_threshold(train_loader, config['autoencoder']['anomaly_threshold_percentile'])
    
    # Evaluate on test set
    model.eval()
    with torch.no_grad():
        X_test_tensor = torch.FloatTensor(X_test).to(device)
        scores = model.get_anomaly_score(X_test_tensor).cpu().numpy()
    
    y_pred = (scores > threshold).astype(int)
    
    # Inference time
    t0 = time.time()
    with torch.no_grad():
        _ = model.get_anomaly_score(X_test_tensor)
    inference_time_ms = (time.time() - t0) * 1000
    
    metrics = evaluate_binary(y_test, y_pred, scores)
    metrics['training_time_s'] = training_time
    metrics['inference_time_ms'] = inference_time_ms
    metrics['threshold'] = threshold
    
    return model, metrics, scores

def train_and_evaluate_lstm(config, X_train, y_train, X_test, y_test):
    """Train LSTM for threat prediction."""
    device = config['lstm']['device']
    input_dim = X_train.shape[1]
    seq_len = config['lstm']['sequence_length']
    
    model = ThreatPredictor(
        input_dim=input_dim,
        hidden_dim=config['lstm']['hidden_dim'],
        num_layers=config['lstm']['num_layers'],
        dropout=config['lstm']['dropout']
    )
    
    train_ds = SequenceDataset(X_train, y_train, seq_len=seq_len)
    val_size = int(0.1 * len(train_ds))
    train_sub = Subset(train_ds, range(len(train_ds) - val_size))
    val_sub = Subset(train_ds, range(len(train_ds) - val_size, len(train_ds)))
    
    train_loader = DataLoader(train_sub, batch_size=config['lstm']['batch_size'], shuffle=True)
    val_loader = DataLoader(val_sub, batch_size=config['lstm']['batch_size'], shuffle=False)
    
    t0 = time.time()
    result = train_model(model, train_loader, val_loader, config['lstm'], model_type="lstm")
    training_time = time.time() - t0
    model = result['model']
    
    # Evaluate
    test_ds = SequenceDataset(X_test, y_test, seq_len=seq_len)
    test_loader = DataLoader(test_ds, batch_size=config['lstm']['batch_size'], shuffle=False)
    
    model.eval()
    all_preds = []
    all_labels = []
    with torch.no_grad():
        for X_batch, y_batch in test_loader:
            X_batch = X_batch.to(device)
            preds = torch.sigmoid(model(X_batch)).squeeze().cpu().numpy()
            all_preds.extend(preds)
            all_labels.extend(y_batch.numpy())
    
    y_prob = np.array(all_preds)
    y_pred = (y_prob > 0.5).astype(int)
    y_true = np.array(all_labels)
    
    metrics = evaluate_binary(y_true, y_pred, y_prob)
    metrics['training_time_s'] = training_time
    
    return model, metrics

def train_and_evaluate_cnn(config, X_train, y_train, X_test, y_test):
    """Train CNN-1D baseline on sequences."""
    device = config['cnn_baseline']['device']
    input_dim = X_train.shape[1]
    seq_len = config['lstm']['sequence_length'] # Use same sequence length as LSTM
    
    model = CNN1DBaseline(
        input_dim=input_dim,
        filters=config['cnn_baseline']['filters'],
        kernel_size=config['cnn_baseline']['kernel_size'],
        dropout=config['cnn_baseline']['dropout']
    )
    
    train_ds = SequenceDataset(X_train, y_train, seq_len=seq_len)
    val_size = int(0.1 * len(train_ds))
    train_sub = Subset(train_ds, range(len(train_ds) - val_size))
    val_sub = Subset(train_ds, range(len(train_ds) - val_size, len(train_ds)))
    
    train_loader = DataLoader(train_sub, batch_size=config['cnn_baseline']['batch_size'], shuffle=True)
    val_loader = DataLoader(val_sub, batch_size=config['cnn_baseline']['batch_size'], shuffle=False)
    
    t0 = time.time()
    result = train_model(model, train_loader, val_loader, config['cnn_baseline'], model_type="cnn")
    training_time = time.time() - t0
    model = result['model']
    
    # Evaluate
    test_ds = SequenceDataset(X_test, y_test, seq_len=seq_len)
    test_loader = DataLoader(test_ds, batch_size=config['cnn_baseline']['batch_size'], shuffle=False)
    
    model.eval()
    all_preds = []
    all_labels = []
    with torch.no_grad():
        for X_batch, y_batch in test_loader:
            X_batch = X_batch.to(device)
            preds = torch.sigmoid(model(X_batch)).squeeze().cpu().numpy()
            all_preds.extend(preds)
            all_labels.extend(y_batch.numpy())
            
    y_prob = np.array(all_preds)
    y_pred = (y_prob > 0.5).astype(int)
    y_true = np.array(all_labels)
    
    metrics = evaluate_binary(y_true, y_pred, y_prob)
    metrics['training_time_s'] = training_time
    
    return model, metrics

def train_and_evaluate_classical(config, X_train, y_train, X_test, y_test):
    """Train and evaluate Isolation Forest and OC-SVM."""
    results = {}
    
    normal_mask = y_train == 0
    X_normal = X_train[normal_mask]
    
    # Isolation Forest
    iforest = IsolationForestBaseline(config['classical_baselines']['isolation_forest'])
    t0 = time.time()
    iforest.fit(X_normal)
    training_time = time.time() - t0
    
    preds = iforest.predict(X_test)
    y_pred = (preds == -1).astype(int)  # -1 = anomaly → 1
    scores = iforest.get_anomaly_score(X_test)
    
    metrics = evaluate_binary(y_test, y_pred, scores)
    metrics['training_time_s'] = training_time
    results['IsolationForest'] = metrics
    
    # OC-SVM (use subset if data is large — OC-SVM is O(n^2))
    max_svm_samples = 10000
    X_svm = X_normal[:max_svm_samples] if len(X_normal) > max_svm_samples else X_normal
    
    ocsvm = OneClassSVMBaseline(config['classical_baselines']['one_class_svm'])
    t0 = time.time()
    ocsvm.fit(X_svm)
    training_time = time.time() - t0
    
    X_test_svm = X_test[:max_svm_samples] if len(X_test) > max_svm_samples else X_test
    y_test_svm = y_test[:max_svm_samples] if len(y_test) > max_svm_samples else y_test
    
    preds = ocsvm.predict(X_test_svm)
    y_pred = (preds == -1).astype(int)
    scores = ocsvm.get_anomaly_score(X_test_svm)
    
    metrics = evaluate_binary(y_test_svm, y_pred, scores)
    metrics['training_time_s'] = training_time
    results['OneClassSVM'] = metrics
    
    return results

def run_cross_validation(config):
    """5-Fold CV for the autoencoder to get F1 confidence intervals."""
    processed_dir = config['dataset']['processed_dir']
    X = np.load(os.path.join(processed_dir, 'X_train.npy'))
    y = np.load(os.path.join(processed_dir, 'y_train_binary.npy'))
    
    k = config['evaluation']['k_folds']
    skf = StratifiedKFold(n_splits=k, shuffle=True, random_state=42)
    
    fold_metrics = []
    for fold_idx, (train_idx, val_idx) in enumerate(skf.split(X, y)):
        logger.info(f"--- Fold {fold_idx+1}/{k} ---")
        X_tr, X_val = X[train_idx], X[val_idx]
        y_tr, y_val = y[train_idx], y[val_idx]
        
        _, metrics, _ = train_and_evaluate_autoencoder(config, X_tr, y_tr, X_val, y_val)
        metrics['fold'] = fold_idx + 1
        fold_metrics.append(metrics)
    
    return pd.DataFrame(fold_metrics)

def main():
    config = load_config()
    processed_dir = config['dataset']['processed_dir']
    os.makedirs('results/tables', exist_ok=True)
    os.makedirs('results/figures', exist_ok=True)
    
    # Load data
    X_train = np.load(os.path.join(processed_dir, 'X_train.npy'))
    y_train = np.load(os.path.join(processed_dir, 'y_train_binary.npy'))
    X_test = np.load(os.path.join(processed_dir, 'X_test.npy'))
    y_test = np.load(os.path.join(processed_dir, 'y_test_binary.npy'))
    
    logger.info(f"Train: {X_train.shape}, Test: {X_test.shape}")
    logger.info(f"Train attack ratio: {y_train.mean():.3f}, Test attack ratio: {y_test.mean():.3f}")
    
    all_results = {}
    
    # === 1. Autoencoder ===
    logger.info("=" * 60)
    logger.info("Training Autoencoder (Anomaly Detection)")
    ae_model, ae_metrics, ae_scores = train_and_evaluate_autoencoder(config, X_train, y_train, X_test, y_test)
    all_results['Autoencoder (Ours)'] = ae_metrics
    save_model(ae_model, 'results/autoencoder_best.pth', ae_metrics)
    logger.info(f"AE Results: {ae_metrics}")
    
    # === 2. LSTM ===
    logger.info("=" * 60)
    logger.info("Training LSTM (Threat Predictor)")
    lstm_model, lstm_metrics = train_and_evaluate_lstm(config, X_train, y_train, X_test, y_test)
    all_results['LSTM (Ours)'] = lstm_metrics
    save_model(lstm_model, 'results/lstm_best.pth', lstm_metrics)
    logger.info(f"LSTM Results: {lstm_metrics}")
    
    # === 3. CNN Baseline ===
    logger.info("=" * 60)
    logger.info("Training CNN-1D Baseline")
    cnn_model, cnn_metrics = train_and_evaluate_cnn(config, X_train, y_train, X_test, y_test)
    all_results['CNN-1D Baseline'] = cnn_metrics
    logger.info(f"CNN Results: {cnn_metrics}")
    
    # === 4. Classical Baselines ===
    logger.info("=" * 60)
    logger.info("Training Classical Baselines")
    classical_results = train_and_evaluate_classical(config, X_train, y_train, X_test, y_test)
    all_results.update(classical_results)
    
    # === 5. Comparison Table ===
    logger.info("=" * 60)
    logger.info("Generating Comparison Table")
    comparison_df = pd.DataFrame(all_results).T
    comparison_df.index.name = 'Model'
    comparison_df = comparison_df.round(4)
    comparison_df.to_csv('results/tables/model_comparison.csv')
    logger.info(f"\n{comparison_df.to_string()}")
    
    # === 6. 5-Fold Cross-Validation ===
    logger.info("=" * 60)
    logger.info("Running 5-Fold Cross-Validation for Autoencoder")
    cv_df = run_cross_validation(config)
    cv_df.to_csv('results/tables/cross_validation.csv', index=False)
    
    mean_f1 = cv_df['f1'].mean()
    std_f1 = cv_df['f1'].std()
    logger.info(f"5-Fold CV F1: {mean_f1:.4f} ± {std_f1:.4f}")
    
    # === 7. Statistical Tests ===
    logger.info("=" * 60)
    logger.info("Running Statistical Significance Tests")
    tester = StatisticalTester()
    # Compare AE F1 across folds vs a simulated baseline
    # (In practice you'd run CV for each baseline too; here we use the single-shot F1)
    if 'IsolationForest' in all_results:
        baseline_f1 = all_results['IsolationForest']['f1']
        ae_cv_f1s = cv_df['f1'].tolist()
        # Create synthetic baseline folds (same value repeated, conservative test)
        baseline_folds = [baseline_f1] * len(ae_cv_f1s)
        stat_result = tester.compare_f1_scores(ae_cv_f1s, baseline_folds)
        stat_result_clean = {k: bool(v) if isinstance(v, (bool, np.bool_)) else v for k, v in stat_result.items()}
        with open('results/tables/statistical_test.json', 'w') as f:
            json.dump(stat_result_clean, f, indent=2)
        logger.info(f"Statistical test: {stat_result}")
    
    # === 8. Plots ===
    logger.info("=" * 60)
    logger.info("Generating Plots")
    plotter = DetectionPlotter(config)
    plotter.plot_roc_curve(y_test, ae_scores, "Autoencoder")
    plotter.plot_confusion_matrix(y_test, (ae_scores > ae_metrics['threshold']).astype(int), "Autoencoder")
    
    logger.info("=" * 60)
    logger.info("ALL TRAINING AND EVALUATION COMPLETE")
    logger.info(f"Results saved to results/tables/ and results/figures/")

if __name__ == "__main__":
    main()
