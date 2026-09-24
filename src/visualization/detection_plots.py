import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import os
import logging

logger = logging.getLogger(__name__)

class DetectionPlotter:
    def __init__(self, config):
        self.config = config['visualization']
        self.out_dir = self.config['output_dir']
        os.makedirs(self.out_dir, exist_ok=True)
        sns.set_theme(style=self.config['style'])
        
    def plot_roc_curve(self, y_true, y_prob, model_name="Autoencoder"):
        from sklearn.metrics import roc_curve, auc
        fpr, tpr, _ = roc_curve(y_true, y_prob)
        roc_auc = auc(fpr, tpr)
        
        plt.figure(figsize=self.config['figsize'])
        plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (area = {roc_auc:.2f})')
        plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title(f'Receiver Operating Characteristic - {model_name}')
        plt.legend(loc="lower right")
        
        out_path = os.path.join(self.out_dir, f'roc_curve_{model_name}.{self.config["format"]}')
        plt.savefig(out_path, dpi=self.config['dpi'])
        plt.close()
        logger.info(f"Saved ROC curve to {out_path}")
        
    def plot_confusion_matrix(self, y_true, y_pred, model_name="Autoencoder"):
        from sklearn.metrics import confusion_matrix
        cm = confusion_matrix(y_true, y_pred)
        
        plt.figure(figsize=(6, 5))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                    xticklabels=['Normal', 'Attack'], yticklabels=['Normal', 'Attack'])
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')
        plt.title(f'Confusion Matrix - {model_name}')
        
        out_path = os.path.join(self.out_dir, f'cm_{model_name}.{self.config["format"]}')
        plt.savefig(out_path, dpi=self.config['dpi'], bbox_inches='tight')
        plt.close()
        logger.info(f"Saved Confusion Matrix to {out_path}")
