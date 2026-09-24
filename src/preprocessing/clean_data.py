import os
import glob
import json
import logging
import pandas as pd
import numpy as np
import yaml

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from src.utils import load_config

def clean_data():
    config = load_config()
    raw_dir = config['dataset']['raw_dir']
    processed_dir = config['dataset']['processed_dir']
    
    os.makedirs(processed_dir, exist_ok=True)
    
    csv_files = glob.glob(os.path.join(raw_dir, "*.csv"))
    if not csv_files:
        logger.error(f"No CSV files found in {raw_dir}")
        return
    
    logger.info(f"Found {len(csv_files)} CSV files. Loading and concatenating...")
    
    df_list = []
    for file in csv_files:
        logger.info(f"Loading {file}...")
        try:
            # low_memory=False helps with mixed types in large files
            df = pd.read_csv(file, low_memory=False)
            df_list.append(df)
        except Exception as e:
            logger.error(f"Failed to read {file}: {e}")
            
    if not df_list:
        logger.error("No data loaded.")
        return
        
    full_df = pd.concat(df_list, ignore_index=True)
    logger.info(f"Total shape after concatenation: {full_df.shape}")
    
    # Strip whitespace from column names
    logger.info("Stripping whitespace from column names...")
    full_df.columns = full_df.columns.str.strip()
    
    # Remove duplicates
    initial_rows = len(full_df)
    full_df.drop_duplicates(inplace=True)
    logger.info(f"Removed {initial_rows - len(full_df)} duplicate rows. New shape: {full_df.shape}")
    
    # Handle Infinity values
    if config['preprocessing']['handle_inf']:
        logger.info("Replacing Inf with NaN...")
        # Select numeric columns to avoid issues with string columns
        numeric_cols = full_df.select_dtypes(include=[np.number]).columns
        full_df[numeric_cols] = full_df[numeric_cols].replace([np.inf, -np.inf], np.nan)
        
    # Handle NaN values
    logger.info("Handling NaN values...")
    # Drop columns with >50% NaN
    nan_threshold = len(full_df) * 0.5
    full_df.dropna(thresh=nan_threshold, axis=1, inplace=True)
    logger.info(f"Shape after dropping columns with >50% NaN: {full_df.shape}")
    
    nan_strategy = config['preprocessing']['handle_nan']
    if nan_strategy == 'drop':
        full_df.dropna(inplace=True)
    else:
        # Fill numeric NaNs
        numeric_cols = full_df.select_dtypes(include=[np.number]).columns
        if nan_strategy == 'median':
            full_df[numeric_cols] = full_df[numeric_cols].fillna(full_df[numeric_cols].median())
        elif nan_strategy == 'mean':
            full_df[numeric_cols] = full_df[numeric_cols].fillna(full_df[numeric_cols].mean())
            
    logger.info(f"Shape after handling NaN: {full_df.shape}")
    
    # Remove constant columns
    logger.info("Removing constant columns...")
    nunique = full_df.nunique()
    cols_to_drop = nunique[nunique == 1].index
    full_df.drop(cols_to_drop, axis=1, inplace=True)
    logger.info(f"Dropped {len(cols_to_drop)} constant columns. New shape: {full_df.shape}")
    
    # Label encoding
    logger.info("Encoding labels...")
    if 'Label' not in full_df.columns:
        logger.error("'Label' column not found! Check dataset format.")
        return
        
    # Binary Label: 0 = Benign, 1 = Attack
    full_df['label_binary'] = (full_df['Label'] != 'Benign').astype(int)
    
    # Multiclass Label
    labels = full_df['Label'].unique()
    # Ensure Benign is always 0
    labels = sorted(labels, key=lambda x: (x != 'Benign', x))
    label_map = {label: idx for idx, label in enumerate(labels)}
    
    full_df['label_multiclass'] = full_df['Label'].map(label_map)
    
    # Save label mapping
    mapping_path = os.path.join(processed_dir, 'label_mapping.json')
    with open(mapping_path, 'w') as f:
        json.dump(label_map, f, indent=4)
    logger.info(f"Saved label mapping to {mapping_path}")
    
    # Print stats
    logger.info("--- Data Statistics ---")
    logger.info(f"Total Rows: {len(full_df)}")
    logger.info("Class Distribution:")
    counts = full_df['Label'].value_counts()
    for label, count in counts.items():
        logger.info(f"  {label}: {count} ({(count/len(full_df))*100:.2f}%)")
        
    # Save cleaned data
    out_path = os.path.join(processed_dir, 'cleaned_data.csv')
    logger.info(f"Saving cleaned data to {out_path}...")
    full_df.to_csv(out_path, index=False)
    logger.info("Data cleaning complete.")

if __name__ == "__main__":
    clean_data()
