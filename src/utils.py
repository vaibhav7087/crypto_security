import yaml
import torch
import logging

logger = logging.getLogger(__name__)

def load_config(config_path='config/config.yaml'):
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Auto-detect device
    if torch.cuda.is_available():
        device = 'cuda'
        logger.info(f"CUDA available: {torch.cuda.get_device_name(0)}")
    else:
        device = 'cpu'
        logger.info("CUDA not available, using CPU")
    
    # Override all device fields
    for section in ['autoencoder', 'lstm', 'cnn_baseline']:
        if section in config:
            config[section]['device'] = device
    
    return config
