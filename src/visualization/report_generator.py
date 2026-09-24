import os
import markdown
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ReportGenerator:
    """
    Generates a Markdown and HTML summary report of all experiments.
    """
    def __init__(self, config):
        self.config = config['visualization']
        self.out_dir = "results/"
        
    def generate(self, title="Hybrid Decentralized ANN-Based Security Framework - Experiment Report"):
        md_content = f"# {title}\n"
        md_content += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        md_content += "## 1. Machine Learning Performance\n"
        md_content += "*(Insert Metrics Table Here)*\n\n"
        
        md_content += "### ROC Curves\n"
        md_content += "![ROC Curve](figures/roc_curve_Autoencoder.png)\n\n"
        
        md_content += "## 2. Cryptographic Latency (PQC vs Classical)\n"
        md_content += "![Crypto Latency](figures/crypto_latency.png)\n\n"
        
        md_content += "## 3. Trust Management Trajectories\n"
        md_content += "![Trust Trajectories](figures/trust_trajectories.png)\n\n"
        
        md_content += "## 4. Testbed Scalability\n"
        md_content += "![Scalability](figures/scalability.png)\n\n"
        
        # Save Markdown
        md_path = os.path.join(self.out_dir, "final_report.md")
        with open(md_path, 'w') as f:
            f.write(md_content)
            
        # Optional: Save HTML
        try:
            html = markdown.markdown(md_content)
            html_path = os.path.join(self.out_dir, "final_report.html")
            with open(html_path, 'w') as f:
                f.write(html)
        except Exception as e:
            logger.warning(f"Failed to generate HTML report: {e}")
            
        logger.info(f"Final reports saved to {self.out_dir}")
