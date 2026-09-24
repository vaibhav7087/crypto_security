import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import os
import logging

logger = logging.getLogger(__name__)

class ScalabilityPlotter:
    def __init__(self, config):
        self.config = config['visualization']
        self.out_dir = self.config['output_dir']
        os.makedirs(self.out_dir, exist_ok=True)
        sns.set_theme(style=self.config['style'])
        
    def plot_cpu_memory_scalability(self, scalability_csv="results/tables/scalability_results.csv"):
        """Plot CPU and Memory usage as cluster scales."""
        if not os.path.exists(scalability_csv):
            logger.error(f"Cannot find {scalability_csv}")
            return
            
        df = pd.read_csv(scalability_csv)
        
        fig, ax1 = plt.subplots(figsize=self.config['figsize'])
        
        color = 'tab:blue'
        ax1.set_xlabel('Number of Nodes')
        ax1.set_ylabel('CPU Usage (%)', color=color)
        ax1.plot(df['nodes'], df['avg_cpu'], marker='o', color=color, label='CPU')
        ax1.tick_params(axis='y', labelcolor=color)
        
        ax2 = ax1.twinx()
        color = 'tab:orange'
        ax2.set_ylabel('Memory Usage (MB)', color=color)
        ax2.plot(df['nodes'], df['avg_mem_mb'], marker='s', color=color, label='Memory')
        ax2.tick_params(axis='y', labelcolor=color)
        
        plt.title('Testbed Scalability (Resource Usage)')
        
        out_path = os.path.join(self.out_dir, f'scalability.{self.config["format"]}')
        plt.savefig(out_path, dpi=self.config['dpi'], bbox_inches='tight')
        plt.close()
        logger.info(f"Saved scalability plot to {out_path}")
