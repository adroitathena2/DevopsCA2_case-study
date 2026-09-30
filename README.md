# DevOps Case Study - Amazon (Q2)

## Overview
This project demonstrates the implementation of modern DevOps principles to address the challenges of monolithic architectures, modeled after Amazon's transition to microservices and "two-pizza teams."

The project containerizes a Flask microservice, orchestrates it with Kubernetes, automates configuration with Ansible, implements a CI/CD pipeline with GitHub Actions, and sets up observability with Prometheus and Grafana.

## Architecture
Developer -> GitHub Actions -> Docker Build -> GitHub Container Registry -> Kubernetes Cluster -> Prometheus -> Grafana

## Tech Stack
- Application: Python (Flask)
- Containerization: Docker
- Orchestration: Kubernetes (Docker Desktop)
- CI/CD: GitHub Actions
- Configuration Management: Ansible
- Monitoring & Logging: Prometheus & Grafana

## Repository Structure
- `.github/workflows/deploy.yml` - Task 1: CI/CD Pipeline
- `ansible/inventory.ini` - Task 2: Ansible Inventory
- `ansible/playbook.yml` - Task 2: Configuration Management
- `k8s/deployment.yaml` - Task 3: Kubernetes Deployment
- `k8s/service.yaml` - Task 3: Kubernetes Service
- `k8s/servicemonitor.yaml` - Task 4: Prometheus ServiceMonitor
- `app.py` - Flask Application
- `requirements.txt` - Python Dependencies
- `Dockerfile` - Task 3: Dockerization

## Pipeline Flow
1. Developer pushes code to the `main` branch.
2. GitHub Actions triggers the pipeline.
3. Job 1 (Test): Installs Python, dependencies, and runs tests.
4. Job 2 (Build & Push): Builds the Docker image and pushes to GitHub Container Registry.
5. Kubernetes pulls the latest image and performs a zero-downtime rolling update.
6. Prometheus scrapes metrics and Grafana visualizes uptime, latency, and error rates.

## Challenges Faced
- Windows/WSL Complexity: Ansible requires a Linux environment; we utilized WSL 2 (Ubuntu).
- Kubernetes Port Conflicts: Port 8080 was in use by Jenkins; resolved by mapping to port 9090.
- Prometheus Metric Naming: The `prometheus-flask-exporter` prefixes metrics with `flask_`, requiring adjusted PromQL queries.
- Resource Constraints: Docker Desktop (WSL2) needed extra memory via a `.wslconfig` file for the monitoring stack.
- Passwordless Sudo in WSL: Required to allow Ansible's `become` task to work in WSL.

## Lessons Learned
- Shift-Left: Catching errors early in the pipeline reduces rework and speeds up delivery.
- Automation: Ansible, GitHub Actions, and Kubernetes eliminate manual errors.
- Observability: Prometheus and Grafana provide instant insight into service health.
- Resilience: Kubernetes Rolling Updates and Rollbacks enable zero-downtime deployments.
- Microservices Fit DevOps: Independently deployable services directly enable Amazon's two-pizza team model.

## Connection to Amazon Case Study
Amazon's monolithic architecture caused frequent outages and slow feature releases. By adopting microservices and a "two-pizza team" culture, they enabled autonomous teams to deploy code every 11.7 seconds.

This project demonstrates how that transformation works in practice. By containerizing the app, automating configuration with Ansible, orchestrating with Kubernetes, and setting up robust monitoring, we have created a system capable of rapid, reliable, and independent deployments—the exact foundation of Amazon's continuous innovation culture.