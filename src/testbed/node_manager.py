import docker
import time
import requests
import logging

logger = logging.getLogger(__name__)

class NodeManager:
    """
    Orchestrates the Docker testbed from the host machine.
    """
    
    def __init__(self, config):
        try:
            self.client = docker.from_env()
        except Exception as e:
            logger.warning(f"Failed to connect to Docker daemon: {e}. Running in simulation mode.")
            self.client = None
            
        self.config = config['docker_testbed']
        self.nodes = {}  # node_id -> dict with container info
        self.network_name = "crypto_security_net"
        
        if self.client:
            try:
                self.client.networks.get(self.network_name)
            except docker.errors.NotFound:
                self.client.networks.create(self.network_name, driver="bridge")
    
    def start_cluster(self, num_nodes: int):
        """Start a heterogeneous cluster with `num_nodes` containers."""
        if not self.client:
            logger.info(f"[Simulated] Started cluster with {num_nodes} nodes")
            for i in range(num_nodes):
                self.nodes[f"node_{i}"] = {'ip': f'10.0.0.{i}', 'role': 'simulated'}
            return
            
        logger.info(f"Starting cluster with {num_nodes} nodes...")
        types = self.config['node_types']
        
        for i in range(num_nodes):
            node_id = f"node_{i}"
            # Distribute types: 40% web, 30% api, 30% db
            if i % 10 < 4:
                ntype = types[0] # web
            elif i % 10 < 7:
                ntype = types[1] # api
            else:
                ntype = types[2] # db
                
            # Assume images are built (done in setup script)
            try:
                container = self.client.containers.run(
                    f"crypto_{ntype['image']}",
                    name=node_id,
                    network=self.network_name,
                    detach=True,
                    nano_cpus=int(float(ntype['cpus']) * 1e9),
                    mem_limit=ntype['memory'],
                    labels={'role': ntype['name']}
                )
                
                # Get IP
                container.reload()
                ip = container.attrs['NetworkSettings']['Networks'][self.network_name]['IPAddress']
                
                self.nodes[node_id] = {
                    'container': container,
                    'ip': ip,
                    'role': ntype['name'],
                    'port': 5000
                }
            except Exception as e:
                logger.error(f"Failed to start {node_id}: {e}")
                
        time.sleep(2) # wait for APIs to start
        logger.info(f"Successfully started {len(self.nodes)} nodes.")
    
    def scale_to(self, num_nodes: int):
        """Scale cluster up or down to exactly `num_nodes`."""
        current = len(self.nodes)
        if num_nodes > current:
            # Scale up
            num_to_add = num_nodes - current
            logger.info(f"Scaling UP from {current} to {num_nodes} nodes...")
            if not self.client:
                for i in range(current, num_nodes):
                    self.nodes[f"node_{i}"] = {'ip': f'10.0.0.{i}', 'role': 'simulated'}
                return
            
            types = self.config['node_types']
            for i in range(current, num_nodes):
                node_id = f"node_{i}"
                ntype = types[i % len(types)]
                try:
                    container = self.client.containers.run(
                        f"crypto_{ntype['image']}",
                        name=node_id,
                        network=self.network_name,
                        detach=True,
                        nano_cpus=int(float(ntype['cpus']) * 1e9),
                        mem_limit=ntype['memory'],
                        labels={'role': ntype['name']}
                    )
                    container.reload()
                    ip = container.attrs['NetworkSettings']['Networks'][self.network_name]['IPAddress']
                    self.nodes[node_id] = {
                        'container': container,
                        'ip': ip,
                        'role': ntype['name'],
                        'port': 5000
                    }
                except Exception as e:
                    logger.error(f"Failed to start {node_id} during scale up: {e}")
            time.sleep(2)
        elif num_nodes < current:
            # Scale down
            logger.info(f"Scaling DOWN from {current} to {num_nodes} nodes...")
            keys = list(self.nodes.keys())
            to_remove = keys[num_nodes:]
            for node_id in to_remove:
                if self.client:
                    try:
                        self.nodes[node_id]['container'].remove(force=True)
                    except Exception as e:
                        logger.error(f"Error removing {node_id} during scale down: {e}")
                del self.nodes[node_id]
            
    def kill_node(self, node_id: str):
        """Kill a specific node (for dependability testing)."""
        if not self.client:
            logger.info(f"[Simulated] Killed node {node_id}")
            return
            
        if node_id in self.nodes:
            self.nodes[node_id]['container'].kill()
            logger.info(f"Killed node {node_id}")
            
    def restart_node(self, node_id: str):
        """Restart a killed node."""
        if not self.client:
            logger.info(f"[Simulated] Restarted node {node_id}")
            return
            
        if node_id in self.nodes:
            self.nodes[node_id]['container'].start()
            logger.info(f"Restarted node {node_id}")
            
    def get_all_metrics(self) -> dict:
        """Collect CPU/memory/network from all running nodes."""
        metrics = {}
        if not self.client:
            # Return dummy metrics
            for node_id in self.nodes:
                metrics[node_id] = {'cpu_percent': 10.0, 'memory_percent': 20.0}
            return metrics
            
        for node_id, info in self.nodes.items():
            try:
                # Ask the agent inside
                url = f"http://{info['ip']}:{info['port']}/metrics"
                resp = requests.get(url, timeout=1)
                metrics[node_id] = resp.json()
            except Exception:
                metrics[node_id] = {'status': 'down'}
        return metrics
        
    def inject_attack(self, node_id: str, attack_type: str):
        """Send attack command to a specific node."""
        if not self.client:
            logger.info(f"[Simulated] Injected {attack_type} into {node_id}")
            return
            
        if node_id in self.nodes:
            try:
                info = self.nodes[node_id]
                url = f"http://{info['ip']}:{info['port']}/inject_attack"
                requests.post(url, json={'attack_type': attack_type}, timeout=1)
                logger.info(f"Injected {attack_type} into {node_id}")
            except Exception as e:
                logger.error(f"Failed to inject attack on {node_id}: {e}")
                
    def throttle_node(self, node_id: str):
        if not self.client: return
        if node_id in self.nodes:
            # Update container to 10% CPU
            self.nodes[node_id]['container'].update(cpu_quota=10000, cpu_period=100000)
            
    def isolate_node(self, node_id: str):
        if not self.client: return
        if node_id in self.nodes:
            try:
                network = self.client.networks.get(self.network_name)
                network.disconnect(self.nodes[node_id]['container'])
            except Exception as e:
                logger.error(f"Failed to isolate {node_id}: {e}")
                
    def teardown(self):
        """Stop and remove all containers."""
        if not self.client:
            return
            
        logger.info("Tearing down cluster...")
        for node_id, info in self.nodes.items():
            try:
                info['container'].remove(force=True)
            except Exception as e:
                logger.error(f"Error removing {node_id}: {e}")
        self.nodes = {}
