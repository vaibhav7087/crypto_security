import time
import random
import logging
import threading
import requests

logger = logging.getLogger(__name__)

class WorkloadGenerator:
    """
    Generates synthetic traffic and orchestrates attacks.
    """
    
    def __init__(self, config, node_manager):
        self.config = config['workloads']
        self.attack_config = config['attacks']
        self.node_manager = node_manager
        self._stop_flag = False
        
    def _get_target_nodes(self):
        return [info for info in self.node_manager.nodes.values() if info.get('ip')]
        
    def generate_normal_traffic(self):
        """Simulate normal background traffic to all nodes."""
        targets = self._get_target_nodes()
        if not targets:
            return
            
        rate = random.choice(self.config['normal_traffic']['requests_per_second'])
        sleep_time = 1.0 / rate if rate > 0 else 0.1
        
        while not self._stop_flag:
            try:
                target = random.choice(targets)
                url = f"http://{target['ip']}:{target['port']}/health"
                # Fire and forget request
                requests.get(url, timeout=0.5)
            except:
                pass
            time.sleep(sleep_time)
            
    def trigger_attack(self, attack_name: str, target_node_id: str):
        """Trigger an attack on a specific node."""
        logger.warning(f"Triggering {attack_name} on {target_node_id}")
        self.node_manager.inject_attack(target_node_id, attack_name)
        
    def stop_attack(self, target_node_id: str):
        """Stop an attack on a specific node."""
        logger.info(f"Stopping attack on {target_node_id}")
        try:
            info = self.node_manager.nodes[target_node_id]
            url = f"http://{info['ip']}:{info['port']}/stop_attack"
            requests.post(url, timeout=1)
        except Exception as e:
            logger.error(f"Failed to stop attack on {target_node_id}: {e}")
            
    def run_scenario(self, scenario_name: str, duration: int):
        """Run a predefined scenario for `duration` seconds."""
        self._stop_flag = False
        t_bg = threading.Thread(target=self.generate_normal_traffic, daemon=True)
        t_bg.start()
        
        start_time = time.time()
        
        if scenario_name == 'bursty':
            while time.time() - start_time < duration:
                # Random bursts
                if random.random() < 0.1: # 10% chance per second
                    # Simulate burst by spawning a temporary high-rate thread
                    pass
                time.sleep(1)
        elif scenario_name == 'attack_mixed':
            nodes = list(self.node_manager.nodes.keys())
            if nodes:
                # Normal for 5s
                time.sleep(5)
                # Attack node 0
                target = nodes[0]
                self.trigger_attack('ddos_flood', target)
                time.sleep(10)
                self.stop_attack(target)
                time.sleep(5)
        else:
            # Steady state
            time.sleep(duration)
            
        self._stop_flag = True
        t_bg.join(timeout=1.0)
