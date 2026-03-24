# API Reliability Monitor

Monitors availability and response time of HTTP services.
Exposes Prometheus-compatible metrics endpoint for observability.

## Run with Docker
```bash
git clone https://github.com/Gatraj/api-reliability-monitor.git
cd api-reliability-monitor
docker build -t api-reliability-monitor .
docker run -p 5003:5001 api-reliability-monitor
```

Visit http://localhost:5003

## Endpoints

| Route | Description |
|-------|-------------|
| `GET /` | Health dashboard |
| `GET /health` | Kubernetes liveness probe |
| `GET /metrics` | Prometheus scrape endpoint |

## Stack

- Python, Flask, Gunicorn
- Docker (multi-stage build)

## Roadmap

- [ ] GitHub Actions CI/CD pipeline
- [ ] Terraform — AWS EKS provisioning
- [ ] Kubernetes deployment
- [ ] ArgoCD GitOps
- [ ] Prometheus + Grafana observability
- [ ] AI-powered log analysis
