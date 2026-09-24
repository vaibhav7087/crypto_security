import argparse
import time
import os
import threading
import psutil
from flask import Flask, jsonify, request

app = Flask(__name__)

# Node state
state = {
    'role': 'unknown',
    'status': 'healthy',
    'start_time': time.time(),
    'trust_score': 0.5,
    'attack_active': False,
    'attack_type': None
}

def attack_worker():
    """Background thread to simulate attack behavior."""
    while True:
        if state['attack_active']:
            # Simulate CPU spike for DDoS
            if state['attack_type'] == 'ddos_flood':
                [x**2 for x in range(10000)]
        time.sleep(0.1)

@app.route('/health')
def health():
    return jsonify({
        'status': state['status'],
        'uptime': time.time() - state['start_time'],
        'role': state['role']
    })

@app.route('/metrics')
def metrics():
    return jsonify({
        'cpu_percent': psutil.cpu_percent(),
        'memory_percent': psutil.virtual_memory().percent,
        'bytes_sent': psutil.net_io_counters().bytes_sent,
        'bytes_recv': psutil.net_io_counters().bytes_recv
    })

@app.route('/inject_attack', methods=['POST'])
def inject_attack():
    data = request.json or {}
    state['attack_active'] = True
    state['attack_type'] = data.get('attack_type', 'ddos_flood')
    return jsonify({'status': 'Attack started', 'type': state['attack_type']})

@app.route('/stop_attack', methods=['POST'])
def stop_attack():
    state['attack_active'] = False
    state['attack_type'] = None
    return jsonify({'status': 'Attack stopped'})

@app.route('/trust', methods=['GET', 'POST'])
def trust():
    if request.method == 'POST':
        data = request.json or {}
        state['trust_score'] = data.get('score', state['trust_score'])
        return jsonify({'status': 'Trust updated'})
    return jsonify({'trust_score': state['trust_score']})

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--role', default='worker')
    args = parser.parse_args()
    state['role'] = args.role
    
    # Start attack worker thread
    t = threading.Thread(target=attack_worker, daemon=True)
    t.start()
    
    # Run API
    app.run(host='0.0.0.0', port=5000)
