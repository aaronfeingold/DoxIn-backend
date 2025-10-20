# Case Study Monitoring Infrastructure

This directory contains the complete monitoring stack configuration for the Case Study Invoice Intelligence System.

## Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   NextJS Admin  │◄──►│  Flask API       │◄──►│ Prometheus      │
│   Dashboard     │    │  /metrics        │    │ :9090           │
│   :3000         │    │  :8000           │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                         │
                                ▼                         ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │ Celery Workers   │    │    Grafana      │
                       │ + Flower :5555   │    │    :3001        │
                       └──────────────────┘    └─────────────────┘
                                │                         │
                                ▼                         ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │ PostgreSQL :5433 │    │ AlertManager    │
                       │ Redis :6379      │    │ :9093           │
                       └──────────────────┘    └─────────────────┘
```

## Quick Start

### 1. Start Monitoring Stack Only
```bash
./scripts/start-monitoring.sh
```

### 2. Start Complete System (App + Monitoring)
```bash
cd docker/
docker-compose --profile full up -d
```

### 3. Access Monitoring Interfaces
- **Grafana Dashboard**: http://localhost:3001 (admin/admin)
- **Prometheus**: http://localhost:9090
- **AlertManager**: http://localhost:9093
- **Celery Flower**: http://localhost:5555

## Configuration Files

### Prometheus (`prometheus/`)
- `prometheus.yml` - Main Prometheus configuration with scrape targets
- `alert_rules.yml` - Alerting rules for critical system events

### Grafana (`grafana/`)
- `datasources/prometheus.yml` - Prometheus data source configuration
- `dashboards/dashboard.yml` - Dashboard provisioning configuration
- `dashboards/usage-analytics-dashboard.json` - Usage analytics visualization dashboard

### PostgreSQL Exporter (`postgres_exporter/`)
- `queries.yaml` - Custom SQL queries for usage analytics metrics

### AlertManager (`alertmanager/`)
- `alertmanager.yml` - Alert routing and notification configuration

## Monitoring Components

### Core Metrics Collection
| Service | Port | Purpose |
|---------|------|---------|
| Prometheus | 9090 | Metrics storage and querying |
| Grafana | 3001 | Dashboard and visualization |
| AlertManager | 9093 | Alert handling and notifications |

### System Exporters
| Exporter | Port | Metrics |
|----------|------|---------|
| Node Exporter | 9100 | CPU, memory, disk, network |
| PostgreSQL Exporter | 9187 | Database performance and health |
| Redis Exporter | 9121 | Cache performance and memory |

### Application Metrics
| Service | Endpoint | Metrics |
|---------|----------|---------|
| Flask API | :8000/metrics | Request rates, response times, business metrics |
| Celery Flower | :5555 | Task queue status, worker health |

## Alert Configuration

### Critical Alerts (Immediate Response)
- Service downtime (> 2 minutes)
- High error rates (> 5% over 5 minutes)
- Resource exhaustion (> 95% CPU/memory)
- Database connection failures

### Warning Alerts (Investigate Within Hours)
- Performance degradation (> 2s response times)
- Growing task queues (> 100 jobs for 15 minutes)
- Storage issues (< 20% disk space)
- High processing job failure rates

### Notification Channels
- **Webhook**: Sends alerts to NextJS admin API at `/api/admin/alerts/webhook`
- **Email**: Configurable SMTP notifications
- **Custom**: Extend AlertManager configuration for Slack, PagerDuty, etc.

## Grafana Dashboards

### Usage Analytics Dashboard
**Location**: `grafana/dashboards/usage-analytics-dashboard.json`  
**URL**: http://localhost:3001/d/usage-analytics

Comprehensive user behavior and application usage visualization:
- Real-time page view metrics and trends
- Daily and hourly active user tracking
- Session duration and engagement analysis
- Top visited routes with performance metrics
- Most active users and their behavior patterns
- Traffic source analysis (referrers)
- User action type distribution

See `grafana/dashboards/README.md` for detailed usage instructions.

### Executive Overview
- System health at a glance
- Service availability status
- Key performance indicators

### Technical Dashboard
- Detailed performance metrics
- Resource utilization trends
- Error rate analysis

### Business Intelligence
- Invoice processing analytics
- Extraction accuracy metrics
- Revenue processing trends

## Health Check Endpoints

### Direct Container Health Checks
```bash
# PostgreSQL
pg_isready -h localhost -p 5433 -U case-study

# Redis
redis-cli -p 6379 ping

# Flask API
curl -f http://localhost:8000/api/health

# Prometheus
curl -f http://localhost:9090/-/healthy

# Grafana
curl -f http://localhost:3001/api/health
```

### Integrated Health via Flask API
```bash
# Basic health
curl http://localhost:8000/api/health

# Database health
curl http://localhost:8000/api/health/database

# Comprehensive health
curl http://localhost:8000/api/health/detailed
```

## Troubleshooting

### Container Mount Issues

**Problem**: Monitoring services fail to start with mount errors like "Are you trying to mount a directory onto a file (or vice-versa)?"

**Root Cause**: Configuration files exist as directories instead of files, typically caused by Docker creating directories when mounting non-existent files.

**Diagnosis**:
```bash
# Check if config files are actually directories
ls -la ../docker/monitoring/prometheus/
ls -la ../docker/monitoring/alertmanager/

# Compare with correct structure
ls -la monitoring/prometheus/
ls -la monitoring/alertmanager/
```

**Solution**:
```bash
# Stop all containers
cd ../docker
docker-compose down

# Remove incorrect directories (may need Docker for root-owned files)
docker run --rm -v "$(pwd)/monitoring:/monitoring" alpine sh -c "rm -rf /monitoring/prometheus/prometheus.yml /monitoring/prometheus/alert_rules.yml /monitoring/alertmanager/alertmanager.yml"

# Verify Docker Compose uses correct mount paths
# Should be: ../monitoring/prometheus/prometheus.yml (not ./monitoring/)

# Restart services
docker-compose --profile monitoring up -d
```

### AlertManager Configuration Issues

**Problem**: AlertManager crashes with "field subject not found" or "field body not found" errors.

**Solution**: Update email configuration format for newer AlertManager versions:
```yaml
# Old format (doesn't work)
email_configs:
  - to: 'admin@example.com'
    subject: 'Alert'
    body: 'Alert content'

# New format (works)
email_configs:
  - to: 'admin@example.com'
    html: 'Alert content'
```

### Common Issues

1. **Services won't start**
   ```bash
   # Check Docker resources
   docker system df
   docker system prune

   # Check logs for specific errors
   docker-compose logs prometheus
   docker-compose logs grafana
   docker-compose logs alertmanager
   ```

2. **Metrics not appearing**
   ```bash
   # Verify Prometheus targets
   curl http://localhost:9090/api/v1/targets

   # Check Flask API metrics endpoint
   curl http://localhost:8000/metrics
   ```

3. **Grafana dashboards empty**
   ```bash
   # Verify Prometheus data source
   curl http://localhost:3001/api/datasources

   # Check Prometheus connectivity from Grafana
   docker exec case-study-grafana wget -qO- http://prometheus:9090/api/v1/targets
   ```

4. **Permission issues with monitoring files**
   ```bash
   # If files are owned by root from Docker
   sudo chown -R $USER:$USER monitoring/

   # Or use Docker to fix permissions
   docker run --rm -v "$(pwd):/data" alpine chown -R $(id -u):$(id -g) /data/monitoring
   ```

### Log Locations
- **Application logs**: `./logs/` directory
- **Container logs**: `docker-compose logs [service-name]`
- **Monitoring data**: Docker volumes (`prometheus_data`, `grafana_data`)

## Production Deployment

### Azure Container Instances
The monitoring stack is designed to work with Azure Container Instances:

```bash
# Deploy infrastructure
cd ../terraform/
terraform apply -var-file="production.tfvars"
```

### Environment Variables
```bash
# Required for production
POSTGRES_PASSWORD=<secure-password>
GRAFANA_PASSWORD=<admin-password>
SMTP_HOST=<email-server>
ALERT_WEBHOOK_URL=<nextjs-admin-url>
```

## Development

### Adding Custom Metrics
1. **Flask API**: Add Prometheus metrics in your Flask routes
2. **Grafana**: Create custom dashboards via the UI
3. **Alerts**: Add rules to `prometheus/alert_rules.yml`

### Testing Alerts
```bash
# Trigger a test alert
docker stop case-study-postgres

# Check AlertManager
curl http://localhost:9093/api/v1/alerts
```

## Security Considerations

- **Network isolation**: All services run in `case-study-network`
- **No external exposure**: Only necessary ports are exposed
- **Authentication**: Grafana requires admin credentials
- **Data retention**: Prometheus data retained for 30 days
- **Webhook security**: AlertManager webhook uses internal Docker network

## Backup and Recovery

### Data Backup
```bash
# Backup monitoring data
docker run --rm -v case-study_prometheus_data:/data -v $(pwd):/backup alpine tar czf /backup/prometheus-backup.tar.gz /data
docker run --rm -v case-study_grafana_data:/data -v $(pwd):/backup alpine tar czf /backup/grafana-backup.tar.gz /data
```

### Configuration Backup
All configuration files are version controlled in this repository.

## Support

For issues with the monitoring stack:
1. Check the troubleshooting section above
2. Review Docker logs: `docker-compose logs [service-name]`
3. Verify network connectivity between containers
4. Ensure all required ports are available
