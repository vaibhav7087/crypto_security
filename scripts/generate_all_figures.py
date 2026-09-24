import os
import sys
import logging
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils import load_config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def plot_model_comparison(config):
    csv_path = 'results/tables/model_comparison.csv'
    if not os.path.exists(csv_path):
        logger.warning(f"{csv_path} not found. Skip model comparison plot.")
        return
        
    df = pd.read_csv(csv_path)
    
    # Melt for seaborn grouped bar chart
    df_melt = pd.melt(df, id_vars=['Model'], value_vars=['f1', 'precision', 'recall'],
                      var_name='Metric', value_name='Score')
                      
    plt.figure(figsize=config['visualization']['figsize'])
    sns.set_style(config['visualization']['style'])
    
    ax = sns.barplot(x='Model', y='Score', hue='Metric', data=df_melt, palette=config['visualization']['color_palette'])
    plt.title('Model Comparison: F1, Precision, and Recall', fontsize=14)
    plt.ylim(0, 1.1)
    plt.xticks(rotation=15)
    plt.legend(loc='lower right')
    
    out_path = os.path.join(config['visualization']['output_dir'], 'model_comparison_bar.png')
    plt.savefig(out_path, dpi=config['visualization']['dpi'], bbox_inches='tight')
    plt.close()
    logger.info(f"Saved {out_path}")

def plot_crypto_latency(config):
    csv_path = 'results/tables/crypto_benchmark.csv'
    if not os.path.exists(csv_path):
        logger.warning(f"{csv_path} not found. Skip crypto latency plot.")
        return
        
    df = pd.read_csv(csv_path)
    
    # Filter only latency metrics
    df_lat = df[df['Metric'].str.endswith('_ms')].copy()
    
    df_melt = pd.melt(df_lat, id_vars=['Metric'], value_vars=['PQC', 'Classical'],
                      var_name='Algorithm', value_name='Latency (ms)')
                      
    plt.figure(figsize=config['visualization']['figsize'])
    sns.barplot(x='Metric', y='Latency (ms)', hue='Algorithm', data=df_melt, palette='Set1')
    plt.title('Cryptographic Operations Latency: PQC vs Classical', fontsize=14)
    plt.yscale('log')
    plt.ylabel('Latency (ms) [Log Scale]')
    
    out_path = os.path.join(config['visualization']['output_dir'], 'crypto_latency.png')
    plt.savefig(out_path, dpi=config['visualization']['dpi'], bbox_inches='tight')
    plt.close()
    logger.info(f"Saved {out_path}")

def plot_e2e_latency(config):
    csv_path = 'results/tables/e2e_latency.csv'
    if not os.path.exists(csv_path):
        logger.warning(f"{csv_path} not found. Skip e2e latency plot.")
        return
        
    df = pd.read_csv(csv_path)
    
    plt.figure(figsize=config['visualization']['figsize'])
    
    # Stacked bar/area plot for components
    df_plot = df[['collect_ms', 'inference_ms', 'response_ms']]
    df_plot.plot.area(figsize=config['visualization']['figsize'], colormap='viridis', alpha=0.7)
    
    plt.title('End-to-End Latency Breakdown over Time', fontsize=14)
    plt.xlabel('Simulation Round')
    plt.ylabel('Latency (ms)')
    
    out_path = os.path.join(config['visualization']['output_dir'], 'e2e_latency_breakdown.png')
    plt.savefig(out_path, dpi=config['visualization']['dpi'], bbox_inches='tight')
    plt.close()
    logger.info(f"Saved {out_path}")

def plot_trust_trajectories(config):
    tables_dir = 'results/tables'
    trust_files = [f for f in os.listdir(tables_dir) if f.startswith('trust_') and f.endswith('.csv')]
    
    if not trust_files:
        logger.warning("No trust trajectory files found. Skip trust plot.")
        return
        
    plt.figure(figsize=config['visualization']['figsize'])
    
    for f in trust_files:
        node_id = f.replace('trust_', '').replace('.csv', '')
        df = pd.read_csv(os.path.join(tables_dir, f))
        
        # Convert timestamp to relative seconds
        if len(df) > 0:
            df['rel_time'] = df['timestamp'] - df['timestamp'].iloc[0]
            plt.plot(df['rel_time'], df['score'], marker='o', label=node_id)
            
    plt.axhline(y=config['trust']['isolation_threshold'], color='r', linestyle='--', label='Isolation Threshold')
    plt.title('Node Trust Score Trajectories', fontsize=14)
    plt.xlabel('Time (seconds)')
    plt.ylabel('Trust Score')
    plt.ylim(0, 1.1)
    plt.legend()
    
    out_path = os.path.join(config['visualization']['output_dir'], 'trust_trajectories.png')
    plt.savefig(out_path, dpi=config['visualization']['dpi'], bbox_inches='tight')
    plt.close()
    logger.info(f"Saved {out_path}")

def plot_scalability(config):
    csv_path = 'results/tables/scalability_results.csv'
    if not os.path.exists(csv_path):
        logger.warning(f"{csv_path} not found. Skip scalability plot.")
        return
        
    df = pd.read_csv(csv_path)
    
    fig, ax1 = plt.subplots(figsize=config['visualization']['figsize'])
    
    color = 'tab:blue'
    ax1.set_xlabel('Number of Nodes')
    ax1.set_ylabel('CPU Usage (%)', color=color)
    ax1.plot(df['num_nodes'], df['cpu_percent'], marker='o', color=color, label='CPU')
    ax1.tick_params(axis='y', labelcolor=color)
    
    ax2 = ax1.twinx()
    color = 'tab:red'
    ax2.set_ylabel('Memory Used (MB)', color=color)
    ax2.plot(df['num_nodes'], df['mem_used_mb'], marker='s', color=color, label='Memory')
    ax2.tick_params(axis='y', labelcolor=color)
    
    fig.tight_layout()
    plt.title('Testbed Scalability: Resource Usage vs Active Nodes', fontsize=14)
    
    out_path = os.path.join(config['visualization']['output_dir'], 'scalability.png')
    plt.savefig(out_path, dpi=config['visualization']['dpi'], bbox_inches='tight')
    plt.close()
    logger.info(f"Saved {out_path}")

def plot_cv_boxplot(config):
    csv_path = 'results/tables/cross_validation.csv'
    if not os.path.exists(csv_path):
        logger.warning(f"{csv_path} not found. Skip CV boxplot.")
        return
        
    df = pd.read_csv(csv_path)
    
    plt.figure(figsize=(6, 8))
    sns.boxplot(y='f1', data=df, color='skyblue')
    sns.swarmplot(y='f1', data=df, color='black', alpha=0.6)
    
    plt.title('Autoencoder F1 Score across 5 Folds', fontsize=14)
    plt.ylabel('F1 Score')
    plt.ylim(0, 1.1)
    
    out_path = os.path.join(config['visualization']['output_dir'], 'cv_boxplot.png')
    plt.savefig(out_path, dpi=config['visualization']['dpi'], bbox_inches='tight')
    plt.close()
    logger.info(f"Saved {out_path}")

def main():
    config = load_config()
    os.makedirs(config['visualization']['output_dir'], exist_ok=True)
    
    logger.info("Generating all visualization figures...")
    plot_model_comparison(config)
    plot_crypto_latency(config)
    plot_e2e_latency(config)
    plot_trust_trajectories(config)
    plot_scalability(config)
    plot_cv_boxplot(config)
    logger.info("Visualization complete.")

if __name__ == "__main__":
    main()
