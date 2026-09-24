# Cloud Deployment Guide
## Hybrid Decentralized ANN-Based Security Framework

This guide outlines how to take the local Docker-based testbed and deploy it to a real-world cloud environment (e.g., AWS, GCP) using Terraform and Kubernetes.

### Architecture
- **Infrastructure as Code (IaC)**: Terraform is used to provision EKS (Elastic Kubernetes Service) on AWS.
- **Container Orchestration**: Kubernetes manages the scaling, networking, and resilience of the nodes.
- **Node Types**: The same Docker images (`crypto_ubuntu`, `crypto_alpine`, `crypto_debian`) are used but deployed as K8s Pods.

### Prerequisites
1. [Terraform](https://www.terraform.io/downloads.html) installed.
2. [kubectl](https://kubernetes.io/docs/tasks/tools/) installed.
3. AWS CLI configured with appropriate credentials (`aws configure`).
4. Docker images built and pushed to a container registry (e.g., ECR or Docker Hub).

### Step 1: Provision Infrastructure (AWS)
1. Navigate to the Terraform directory:
   ```bash
   cd terraform/aws
   ```
2. Initialize and apply:
   ```bash
   terraform init
   terraform apply -auto-approve
   ```
3. Update your kubeconfig:
   ```bash
   aws eks --region us-east-1 update-kubeconfig --name crypto-security-cluster
   ```

### Step 2: Deploy to Kubernetes
1. Push your local images to a registry (assuming Docker Hub `yourusername/`):
   ```bash
   docker tag crypto_ubuntu yourusername/crypto_ubuntu:latest
   docker push yourusername/crypto_ubuntu:latest
   # repeat for alpine and debian
   ```
2. Apply the Kubernetes manifests:
   ```bash
   cd ../../kubernetes
   kubectl apply -f namespace.yaml
   kubectl apply -f deployment.yaml
   kubectl apply -f service.yaml
   ```

### Step 3: Verify and Scale
1. Check running pods:
   ```bash
   kubectl get pods -n crypto-security
   ```
2. Scale the cluster to 100 nodes:
   ```bash
   kubectl scale deployment crypto-node-ubuntu --replicas=40 -n crypto-security
   kubectl scale deployment crypto-node-alpine --replicas=30 -n crypto-security
   kubectl scale deployment crypto-node-debian --replicas=30 -n crypto-security
   ```

### Notes on Cloud Implementation
- The **NodeManager** class in our testbed codebase (`src/testbed/node_manager.py`) would need to be updated to use the Kubernetes API Python client (`kubernetes` package) instead of the Docker SDK.
- **Blockchain Consensus** in a real distributed environment would use actual network RPCs (e.g., gRPC) between pods instead of simulated memory-level consensus.
- **Resource Limits**: Ensure your K8s node groups have sufficient capacity to handle the PQC cryptographic overhead.
