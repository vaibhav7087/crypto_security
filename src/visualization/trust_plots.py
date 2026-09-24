import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import os
import logging

logger = logging.getLogger(__name__)

class TrustPlotter:
    def __init__(self, config):
        self.config = config['visualization']
        self.out_dir = self.config['output_dir']
        os.makedirs(self.out_dir, exist_ok=True)
        sns.set_theme(style=self.config['style'])
        
    def plot_trust_trajectories(self, trust_manager):
        """Plot the trust score of all nodes over time."""
        plt.figure(figsize=self.config['figsize'])
        
        for node_id in trust_manager.trust_history.keys():
            df = trust_manager.get_trust_trajectory(node_id)
            if not df.empty:
                # Normalize timestamp to start at 0
                df['time_rel'] = df['timestamp'] - df['timestamp'].min()
                plt.plot(df['time_rel'], df['score'], label=node_id, marker='o', markersize=4)
                
        plt.axhline(y=trust_manager.config['isolation_threshold'], color='r', linestyle='--', label='Isolation Threshold')
        plt.ylim([-0.05, 1.05])
        plt.xlabel('Time (seconds)')
        plt.ylabel('Trust Score')
        plt.title('Node Trust Scores Over Time')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        out_path = os.path.join(self.out_dir, f'trust_trajectories.{self.config["format"]}')
        plt.savefig(out_path, dpi=self.config['dpi'], bbox_inches='tight')
        plt.close()
        logger.info(f"Saved trust trajectories to {out_path}")
