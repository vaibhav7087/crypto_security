import os
import json
import logging
import pandas as pd
import numpy as np
import yaml
import pickle
from sklearn.preprocessing import MinMaxScaler, StandardScaler, RobustScaler
from sklearn.model_selection import train_test_split

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from src.utils import load_config

def feature_engineering():
    config = load_config()
    processed_dir = config['dataset']['processed_dir']
    clean_data_path = os.path.join(processed_dir, 'cleaned_data.csv')
    
    if not os.path.exists(clean_data_path):
        logger.error(f"{clean_data_path} not found. Run clean_data.py first.")
        return
        
    logger.info(f"Loading {clean_data_path}...")
    df = pd.read_csv(clean_data_path)
    
    # Drop non-numeric identifiers (as configured)
    cols_to_drop = config['dataset'].get('drop_columns', [])
    # Add other typical non-numeric identifiers if present
    default_drops = ['Flow ID', 'Src IP', 'Dst IP', 'Label']
    for col in default_drops:
        if col not in cols_to_drop and col in df.columns:
            cols_to_drop.append(col)
            
    # Keep target labels separate
    y_binary = df['label_binary'].values
    y_multi = df['label_multiclass'].values
    
    # Actually drop them
    drop_actual = [c for c in cols_to_drop if c in df.columns]
    logger.info(f"Dropping columns: {drop_actual}")
    df.drop(drop_actual, axis=1, inplace=True, errors='ignore')
    
    # Also drop label_binary and label_multiclass from features
    df.drop(['label_binary', 'label_multiclass'], axis=1, inplace=True, errors='ignore')
    
    # Ensure all remaining are numeric
    non_numeric = df.select_dtypes(exclude=[np.number]).columns
    if len(non_numeric) > 0:
        logger.warning(f"Found non-numeric columns remaining: {non_numeric.tolist()}. Dropping them.")
        df.drop(non_numeric, axis=1, inplace=True)
        
    X = df.values
    feature_names = df.columns.tolist()
    logger.info(f"Feature matrix shape before variance filter: {X.shape}")
    
    # Variance Threshold feature selection
    method = config['preprocessing']['feature_selection']['method']
    threshold = config['preprocessing']['feature_selection']['threshold']
    
    if method == 'variance':
        logger.info(f"Applying variance threshold: {threshold}")
        # Need to normalize temporarily or compute variance on raw data?
        # Usually variance on min-max scaled data is best
        temp_scaler = MinMaxScaler()
        X_temp = temp_scaler.fit_transform(X)
        variances = np.var(X_temp, axis=0)
        
        keep_idx = np.where(variances >= threshold)[0]
        drop_idx = np.where(variances < threshold)[0]
        
        logger.info(f"Dropping {len(drop_idx)} low variance features.")
        X = X[:, keep_idx]
        feature_names = [feature_names[i] for i in keep_idx]
        
    logger.info(f"Final feature matrix shape: {X.shape}")
    
    # Save final feature names
    feature_names_path = os.path.join(processed_dir, 'feature_names.json')
    with open(feature_names_path, 'w') as f:
        json.dump(feature_names, f, indent=4)
        
    # Normalization
    norm_type = config['preprocessing']['normalization']
    logger.info(f"Applying {norm_type} normalization...")
    
    if norm_type == 'minmax':
        scaler = MinMaxScaler()
    elif norm_type == 'standard':
        scaler = StandardScaler()
    elif norm_type == 'robust':
        scaler = RobustScaler()
    else:
        scaler = MinMaxScaler() # default
        
    X_scaled = scaler.fit_transform(X)
    
    # Save scaler for inference later
    scaler_path = os.path.join(processed_dir, 'scaler.pkl')
    with open(scaler_path, 'wb') as f:
        pickle.dump(scaler, f)
        
    # Stratified Train/Val/Test Split
    test_split = config['dataset']['test_split']
    val_split = config['dataset']['val_split']
    seed = config['dataset']['random_seed']
    
    # First split into train_temp and test
    X_temp, X_test, y_bin_temp, y_bin_test, y_multi_temp, y_multi_test = train_test_split(
        X_scaled, y_binary, y_multi, 
        test_size=test_split, 
        stratify=y_multi, 
        random_state=seed
    )
    
    # Calculate relative val split proportion
    # e.g., if test=0.2, val=0.1, we have 0.8 left. Val is 0.1/0.8 = 0.125 of remaining
    rel_val_split = val_split / (1.0 - test_split)
    
    X_train, X_val, y_bin_train, y_bin_val, y_multi_train, y_multi_val = train_test_split(
        X_temp, y_bin_temp, y_multi_temp,
        test_size=rel_val_split,
        stratify=y_multi_temp,
        random_state=seed
    )
    
    logger.info("--- Split Statistics ---")
    logger.info(f"Train: {X_train.shape[0]} samples ({(X_train.shape[0]/len(X))*100:.1f}%)")
    logger.info(f"Val:   {X_val.shape[0]} samples ({(X_val.shape[0]/len(X))*100:.1f}%)")
    logger.info(f"Test:  {X_test.shape[0]} samples ({(X_test.shape[0]/len(X))*100:.1f}%)")
    
    # Save splits
    logger.info("Saving numpy arrays...")
    np.save(os.path.join(processed_dir, 'X_train.npy'), X_train)
    np.save(os.path.join(processed_dir, 'y_train_binary.npy'), y_bin_train)
    np.save(os.path.join(processed_dir, 'y_train_multi.npy'), y_multi_train)
    
    np.save(os.path.join(processed_dir, 'X_val.npy'), X_val)
    np.save(os.path.join(processed_dir, 'y_val_binary.npy'), y_bin_val)
    np.save(os.path.join(processed_dir, 'y_val_multi.npy'), y_multi_val)
    
    np.save(os.path.join(processed_dir, 'X_test.npy'), X_test)
    np.save(os.path.join(processed_dir, 'y_test_binary.npy'), y_bin_test)
    np.save(os.path.join(processed_dir, 'y_test_multi.npy'), y_multi_test)
    
    # Update config with input_dim dynamically
    # Load config file content, replace 'input_dim: null' with actual dim
    with open('config/config.yaml', 'r') as f:
        config_content = f.read()
    
    import re
    config_content = re.sub(r'input_dim:\s*null', f'input_dim: {X.shape[1]}', config_content)
    
    with open('config/config.yaml', 'w') as f:
        f.write(config_content)
    logger.info(f"Updated config.yaml input_dim to {X.shape[1]}")
    logger.info("Feature engineering complete.")

if __name__ == "__main__":
    feature_engineering()
