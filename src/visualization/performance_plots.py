import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import os
import logging

logger = logging.getLogger(__name__)

class PerformancePlotter:
    def __init__(self, config):
        self.config = config['visualization']
        self.out_dir = self.config['output_dir']
        os.makedirs(self.out_dir, exist_ok=True)
        sns.set_theme(style=self.config['style'])
        
    def plot_latency_comparison(self, crypto_benchmark_csv="results/tables/crypto_benchmark.csv"):
        """Plot latency comparison (PQC vs Classical)."""
        if not os.path.exists(crypto_benchmark_csv):
            logger.error(f"Cannot find {crypto_benchmark_csv}")
            return
            
        df = pd.read_csv(crypto_benchmark_csv)
        
        # Filter latency metrics
        latency_df = df[df['Metric'].str.contains('ms')]
        
        # Melt for seaborn barplot
        melted = latency_df.melt(id_vars=['Metric'], value_vars=['PQC', 'Classical'], 
                                var_name='Type', value_name='Latency (ms)')
                                
        plt.figure(figsize=self.config['figsize'])
        sns.barplot(data=melted, x='Metric', y='Latency (ms)', hue='Type', palette=self.config['color_palette'])
        plt.title('Cryptographic Latency Comparison')
        plt.xticks(rotation=45)
        plt.yscale('log') # Log scale is usually better since keygen and encap differ vastly
        
        out_path = os.path.join(self.out_dir, f'crypto_latency.{self.config["format"]}')
        plt.savefig(out_path, dpi=self.config['dpi'], bbox_inches='tight')
        plt.close()
        logger.info(f"Saved latency comparison to {out_path}")
