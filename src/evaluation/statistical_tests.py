import numpy as np
import scipy.stats as stats
import logging

logger = logging.getLogger(__name__)

class StatisticalTester:
    """
    Performs statistical significance testing (e.g., T-tests) to compare the proposed model 
    against baselines.
    """
    
    def __init__(self, confidence_level=0.95):
        self.confidence_level = confidence_level
        self.alpha = 1.0 - confidence_level
        
    def compare_f1_scores(self, f1_scores_proposed: list, f1_scores_baseline: list):
        """
        Paired T-test to compare F1 scores across multiple cross-validation folds.
        Null Hypothesis (H0): The means of both groups are equal.
        """
        t_stat, p_value = stats.ttest_rel(f1_scores_proposed, f1_scores_baseline)
        
        significant = p_value < self.alpha
        logger.info(f"F1 Comparison: t-stat={t_stat:.4f}, p-value={p_value:.4f}, significant={significant}")
        
        return {
            't_statistic': t_stat,
            'p_value': p_value,
            'significant': significant,
            'alpha': self.alpha
        }
        
    def compare_latencies(self, latency_proposed: list, latency_baseline: list):
        """
        Independent T-test to compare latency (e.g. Kyber vs ECDH).
        Null Hypothesis (H0): The means of both groups are equal.
        """
        # We might have different variances, use Welch's t-test
        t_stat, p_value = stats.ttest_ind(latency_proposed, latency_baseline, equal_var=False)
        
        significant = p_value < self.alpha
        logger.info(f"Latency Comparison: t-stat={t_stat:.4f}, p-value={p_value:.4f}, significant={significant}")
        
        return {
            't_statistic': t_stat,
            'p_value': p_value,
            'significant': significant,
            'alpha': self.alpha
        }
