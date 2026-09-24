// PQC-ANN CloudShield - Real-Time Dashboard Client Connected to Python Backend

class CloudSecuritySimulator {
    constructor() {
        this.numNodes = 10;
        this.totalRounds = 5;
        this.currentRound = 1;
        this.currentStep = 1;
        this.attackType = "DDoS SYN Flood";
        this.targetNode = 3;
        this.realtimeActive = false;
        this.autoScroll = true;
        this.pollInterval = null;
        this.chainTampered = false;

        this.initDOM();
        this.initEventListeners();
        this.fetchInitialState();
        this.startStatePolling();
    }

    initDOM() {
        // Controls
        this.sliderNodes = document.getElementById('input-nodes');
        this.sliderRounds = document.getElementById('input-rounds');
        this.labelNodes = document.getElementById('label-nodes');
        this.labelRounds = document.getElementById('label-rounds');
        this.selectAttack = document.getElementById('select-attack');
        this.selectTarget = document.getElementById('select-target');
        this.btnNextStep = document.getElementById('btn-next-step');
        this.btnAutoPlay = document.getElementById('btn-auto-play');
        this.btnReset = document.getElementById('btn-reset');

        // Stepper & Spotlight
        this.progressFill = document.getElementById('step-progress-fill');
        this.stepItems = document.querySelectorAll('.step-item');
        this.spotlightBadge = document.getElementById('spotlight-badge');
        this.roundIndicator = document.getElementById('round-indicator');
        this.spotlightTitle = document.getElementById('spotlight-title');
        this.spotlightDesc = document.getElementById('spotlight-desc');
        this.spotlightFormula = document.getElementById('spotlight-formula');
        this.pillThreat = document.getElementById('pill-threat');
        this.pillTarget = document.getElementById('pill-target');
        this.pillDur = document.getElementById('pill-dur');
        this.pillSyn = document.getElementById('pill-syn');

        // Workspace
        this.nodesContainer = document.getElementById('nodes-container');
        this.terminalBody = document.getElementById('terminal-body');
        this.btnClearTerm = document.getElementById('btn-clear-term');
        this.btnToggleScroll = document.getElementById('btn-toggle-scroll');
        this.clusterHealthText = document.getElementById('cluster-health-text');

        // Blockchain & Tamper
        this.blocksContainer = document.getElementById('blocks-container');
        this.btnTamperChain = document.getElementById('btn-tamper-chain');
        this.btnRestoreChain = document.getElementById('btn-restore-chain');
        this.tamperAlert = document.getElementById('tamper-status-alert');

        // Modal
        this.nodeModal = document.getElementById('node-modal');
        this.modalClose = document.getElementById('modal-close');
        this.modalTitle = document.getElementById('modal-node-title');
        this.modalBody = document.getElementById('modal-node-body');

        // Tabs
        this.navTabs = document.querySelectorAll('.nav-tab');
        this.tabPanes = document.querySelectorAll('.tab-pane');
    }

    initEventListeners() {
        // Tab switching
        this.navTabs.forEach(tab => {
            tab.addEventListener('click', () => {
                this.navTabs.forEach(t => t.classList.remove('active'));
                this.tabPanes.forEach(p => p.classList.remove('active'));
                tab.classList.add('active');
                const targetPane = document.getElementById(tab.dataset.tab);
                if (targetPane) targetPane.classList.add('active');
            });
        });

        // Sliders & Selects
        this.sliderNodes.addEventListener('input', (e) => {
            this.numNodes = parseInt(e.target.value);
            this.labelNodes.textContent = `${this.numNodes} Nodes`;
            this.updateTargetDropdown();
            this.sendReset();
        });

        this.sliderRounds.addEventListener('input', (e) => {
            this.totalRounds = parseInt(e.target.value);
            this.labelRounds.textContent = `${this.totalRounds} Rounds`;
            this.roundIndicator.textContent = `Simulation Round: ${this.currentRound} / ${this.totalRounds}`;
        });

        this.selectAttack.addEventListener('change', (e) => {
            this.attackType = e.target.value;
            this.sendReset();
        });

        this.selectTarget.addEventListener('change', (e) => {
            this.targetNode = parseInt(e.target.value);
            this.sendReset();
        });

        // Real Execution Actions
        this.btnNextStep.addEventListener('click', () => this.executeRealStep());
        this.btnAutoPlay.addEventListener('click', () => this.toggleRealtimeEngine());
        this.btnReset.addEventListener('click', () => this.sendReset());

        // Terminal controls
        this.btnClearTerm.addEventListener('click', () => {
            this.terminalBody.innerHTML = '';
        });

        this.btnToggleScroll.addEventListener('click', () => {
            this.autoScroll = !this.autoScroll;
            this.btnToggleScroll.classList.toggle('active', this.autoScroll);
            this.btnToggleScroll.textContent = `Auto-Scroll: ${this.autoScroll ? 'ON' : 'OFF'}`;
        });

        // Tamper Proofing
        if (this.btnTamperChain) {
            this.btnTamperChain.addEventListener('click', () => this.triggerRealTamper());
        }
        if (this.btnRestoreChain) {
            this.btnRestoreChain.addEventListener('click', () => this.sendReset());
        }

        // Modal Close
        this.modalClose.addEventListener('click', () => this.nodeModal.classList.add('hidden'));
        this.nodeModal.addEventListener('click', (e) => {
            if (e.target === this.nodeModal) this.nodeModal.classList.add('hidden');
        });
    }

    updateTargetDropdown() {
        this.selectTarget.innerHTML = '';
        for (let i = 0; i < this.numNodes; i++) {
            const opt = document.createElement('option');
            opt.value = i;
            opt.textContent = `Node-${String(i).padStart(2, '0')}`;
            if (i === 3) opt.selected = true;
            this.selectTarget.appendChild(opt);
        }
        this.targetNode = Math.min(this.targetNode, this.numNodes - 1);
    }

    async fetchInitialState() {
        try {
            const res = await fetch('/api/state');
            if (res.ok) {
                const data = await res.json();
                this.renderState(data);
            }
        } catch (e) {
            console.warn("Backend not reached, running in standalone mode:", e);
        }
    }

    startStatePolling() {
        // Poll backend state every 900ms to stay synchronized with live Python execution
        this.pollInterval = setInterval(async () => {
            if (this.realtimeActive) {
                try {
                    const res = await fetch('/api/state');
                    if (res.ok) {
                        const data = await res.json();
                        this.renderState(data);
                    }
                } catch (e) {
                    // Ignore transient network errors
                }
            }
        }, 900);
    }

    async executeRealStep() {
        try {
            const res = await fetch('/api/step', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    num_nodes: this.numNodes,
                    rounds: this.totalRounds,
                    attack: this.attackType,
                    target: this.targetNode
                })
            });
            if (res.ok) {
                const data = await res.json();
                this.currentStep = data.step;
                this.currentRound = data.round;
                this.renderStepDetails(data.details, data.step);
                this.renderNodes(data.nodes);
                this.renderBlocks(data.blocks);
                this.renderLogs(data.latest_logs);
                this.updateStepUI();
            }
        } catch (e) {
            console.error("Failed to execute real step on Python backend:", e);
        }
    }

    async toggleRealtimeEngine() {
        this.realtimeActive = !this.realtimeActive;
        const endpoint = this.realtimeActive ? '/api/start-realtime' : '/api/stop-realtime';
        
        try {
            await fetch(endpoint, { method: 'POST' });
        } catch (e) {
            console.warn("Backend call failed:", e);
        }

        if (this.realtimeActive) {
            this.btnAutoPlay.innerHTML = '<span>Pause Real-Time</span> ⏸️';
            this.btnAutoPlay.className = 'btn btn-outline';
            this.clusterHealthText.textContent = "Cluster Mesh: LIVE STREAMING (Real PyTorch + PQC)";
            this.clusterHealthText.style.color = "#00f2fe";
        } else {
            this.btnAutoPlay.innerHTML = '<span>Live Stream Engine</span> ⚡';
            this.btnAutoPlay.className = 'btn btn-accent';
            this.clusterHealthText.textContent = "Cluster Mesh: Healthy";
            this.clusterHealthText.style.color = "#10b981";
        }
    }

    async sendReset() {
        try {
            const res = await fetch('/api/reset', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    num_nodes: this.numNodes,
                    rounds: this.totalRounds,
                    attack: this.attackType,
                    target: this.targetNode
                })
            });
            if (res.ok) {
                const data = await res.json();
                this.currentStep = 1;
                this.currentRound = 1;
                this.chainTampered = false;
                this.tamperAlert.className = 'tamper-alert alert-success';
                this.tamperAlert.innerHTML = `
                    <span class="alert-icon">✓</span>
                    <span class="alert-text">Hash Chain Status: 100% Cryptographically Valid across all blocks.</span>
                `;
                this.fetchInitialState();
            }
        } catch (e) {
            console.warn("Reset error:", e);
        }
    }

    async triggerRealTamper() {
        try {
            const res = await fetch('/api/tamper', { method: 'POST' });
            if (res.ok) {
                const data = await res.json();
                this.chainTampered = true;
                this.tamperAlert.className = 'tamper-alert alert-danger';
                this.tamperAlert.innerHTML = `
                    <span class="alert-icon">❌</span>
                    <span class="alert-text">CRITICAL INTEGRITY BREACH: Block #1 modified! SHA-256 Hash Chaining Failed. Chain Valid: FALSE!</span>
                `;
                this.fetchInitialState();
            }
        } catch (e) {
            console.warn("Tamper error:", e);
        }
    }

    renderState(data) {
        if (!data) return;
        this.currentStep = data.current_step;
        this.currentRound = data.current_round;
        this.renderNodes(data.nodes);
        this.renderBlocks(data.blocks);
        this.renderLogs(data.logs);
        this.updateStepUI();
    }

    renderStepDetails(details, step) {
        if (!details) return;
        this.spotlightTitle.textContent = details.title || `Step ${step}`;
        this.spotlightDesc.textContent = details.description || '';
        
        if (details.formula) {
            this.spotlightFormula.innerHTML = `<code>${details.formula}</code>`;
        } else if (details.features) {
            let featHtml = "<code>Features: ";
            for (let [k, v] of Object.entries(details.features)) {
                featHtml += `${k}=${v} | `;
            }
            featHtml = featHtml.slice(0, -3) + "</code>";
            this.spotlightFormula.innerHTML = featHtml;
        }

        // Update pills
        this.pillThreat.textContent = this.attackType;
        this.pillTarget.textContent = `Node-${String(this.targetNode).padStart(2, '0')}`;
        if (details.loss) this.pillDur.textContent = `Loss: ${details.loss}`;
        if (details.inference_time) this.pillSyn.textContent = details.inference_time;
    }

    updateStepUI() {
        this.progressFill.style.width = `${(this.currentStep / 8) * 100}%`;
        this.stepItems.forEach(item => {
            const stepNum = parseInt(item.dataset.step);
            item.classList.toggle('active', stepNum === this.currentStep);
            item.classList.toggle('completed', stepNum < this.currentStep);
        });

        this.spotlightBadge.textContent = `STEP ${this.currentStep} OF 8 • ACTIVE REAL-TIME PHASE`;
        this.roundIndicator.textContent = `Simulation Round: ${this.currentRound} / ${this.totalRounds}`;
    }

    renderNodes(nodes) {
        if (!nodes || !this.nodesContainer) return;
        this.nodesContainer.innerHTML = '';
        let hasQuarantined = false;

        nodes.forEach(node => {
            if (node.status === 'quarantined') hasQuarantined = true;

            const card = document.createElement('div');
            card.className = `node-card status-${node.status}`;
            card.addEventListener('click', () => this.showNodeModal(node));

            let meterClass = 'high';
            const trustVal = node.trust_score !== undefined ? node.trust_score : node.trust;
            if (trustVal < 0.4) meterClass = 'low';
            else if (trustVal < 0.7) meterClass = 'med';

            card.innerHTML = `
                <div class="node-card-top">
                    <span class="node-name">${node.name}</span>
                    <span class="node-role-badge">${node.role}</span>
                </div>
                <div class="node-trust-meter">
                    <div class="trust-meter-label">
                        <span>Trust Score</span>
                        <strong class="${meterClass === 'low' ? 'text-alert' : ''}">${trustVal.toFixed(3)}</strong>
                    </div>
                    <div class="trust-bar">
                        <div class="trust-fill ${meterClass}" style="width: ${trustVal * 100}%;"></div>
                    </div>
                </div>
                <div style="font-size: 9px; color: #64748b; margin-top: 2px;">
                    ${node.cpu} • ${node.ram}
                </div>
            `;
            this.nodesContainer.appendChild(card);
        });

        if (!this.realtimeActive) {
            if (hasQuarantined) {
                this.clusterHealthText.textContent = "Cluster Mesh: Threat Quarantined";
                this.clusterHealthText.parentElement.style.borderColor = "rgba(239, 68, 68, 0.4)";
                this.clusterHealthText.style.color = "#f87171";
            } else {
                this.clusterHealthText.textContent = "Cluster Mesh: Healthy";
                this.clusterHealthText.parentElement.style.borderColor = "rgba(16, 185, 129, 0.25)";
                this.clusterHealthText.style.color = "#10b981";
            }
        }
    }

    renderBlocks(blocks) {
        if (!blocks || !this.blocksContainer) return;
        this.blocksContainer.innerHTML = '';
        
        blocks.forEach(b => {
            const card = document.createElement('div');
            card.className = `block-card ${this.chainTampered && b.index > 0 ? 'tampered' : ''}`;
            card.innerHTML = `
                <div class="block-header">
                    <span>Block #${b.index}</span>
                    <span style="font-size: 10px; color: #94a3b8;">${b.timestamp}</span>
                </div>
                <div class="block-hash">
                    <span style="color: #64748b;">Hash:</span> ${b.hash ? b.hash.substring(0, 18) : '0x00'}...
                </div>
                <div class="block-hash">
                    <span style="color: #64748b;">Prev:</span> ${b.prevHash ? b.prevHash.substring(0, 18) : '0x00'}...
                </div>
                <div style="color: #cbd5e1; font-size: 10px; margin-top: 4px; border-top: 1px solid rgba(255,255,255,0.06); padding-top: 4px;">
                    ${b.tx || 'Transactions verified'}
                </div>
            `;
            this.blocksContainer.appendChild(card);
        });
    }

    renderLogs(logs) {
        if (!logs || !this.terminalBody) return;
        this.terminalBody.innerHTML = '';
        
        logs.forEach(log => {
            const line = document.createElement('div');
            line.className = 'term-line';
            line.innerHTML = `
                <span class="term-time">[${log.time}]</span>
                <span class="term-tag ${log.tag}">[${log.tag}]</span>
                <span class="term-msg ${log.level}">${log.msg}</span>
            `;
            this.terminalBody.appendChild(line);
        });

        if (this.autoScroll) {
            this.terminalBody.scrollTop = this.terminalBody.scrollHeight;
        }
    }

    showNodeModal(node) {
        const trustVal = node.trust_score !== undefined ? node.trust_score : node.trust;
        this.modalTitle.textContent = `${node.name} — Technical Telemetry & PQC Credentials`;
        this.modalBody.innerHTML = `
            <div><strong>Role:</strong> ${node.role} (${node.cpu}, ${node.ram})</div>
            <div><strong>Status:</strong> <span class="badge badge-${node.status === 'normal' ? 'green' : (node.status === 'throttled' ? 'primary' : 'secondary')}">${node.status.toUpperCase()}</span></div>
            <div><strong>Live Trust Score:</strong> ${trustVal.toFixed(4)} (Isolation Cutoff: 0.4000)</div>
            <div><strong>Latest Anomaly Loss:</strong> ${(node.anomaly_score || 0.00018).toFixed(6)} (Threshold: 0.000784)</div>
            <hr style="border: none; border-top: 1px solid rgba(255,255,255,0.08); margin: 6px 0;">
            <div><strong>NIST Kyber-768 Public Key (KEM):</strong></div>
            <code style="font-family: monospace; color: #38bdf8; font-size: 10px; word-break: break-all;">${node.kyber_pk}</code>
            <div style="margin-top: 6px;"><strong>NIST Dilithium-3 Public Key (Signature):</strong></div>
            <code style="font-family: monospace; color: #a78bfa; font-size: 10px; word-break: break-all;">${node.dilithium_pk}</code>
            <hr style="border: none; border-top: 1px solid rgba(255,255,255,0.08); margin: 6px 0;">
            <div><strong>Firewall Policy:</strong> ${node.status === 'quarantined' ? 'Ingress Ports Blocked / Node Quarantined' : (node.status === 'throttled' ? 'Ingress Throttled 90%' : 'Normal Ingress Allowed')}</div>
        `;
        this.nodeModal.classList.remove('hidden');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.app = new CloudSecuritySimulator();
});
