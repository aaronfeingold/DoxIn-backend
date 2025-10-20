# Usage Analytics Dashboard Setup Guide

This guide walks you through setting up and using the new Grafana dashboard for visualizing UsageAnalytics data.

## What Was Added

### 1. Custom PostgreSQL Exporter Queries

**File**: `postgres_exporter/queries.yaml`

Custom SQL queries that expose UsageAnalytics table metrics to Prometheus:

- Page views by route (24h)
- Daily active users (30d)
- Hourly page views (24h)
- Top active users (7d)
- Action type distribution
- Session metrics
- Referrer analysis

### 2. Grafana Dashboard

**File**: `grafana/dashboards/usage-analytics-dashboard.json`

A comprehensive dashboard with 10 visualization panels:

- 4 gauge panels for key metrics (total views, unique users, sessions, avg duration)
- 2 time series charts (hourly views, daily active users)
- 1 pie chart (action types)
- 3 data tables (top pages, top users, top referrers)

### 3. Docker Compose Update

**File**: `docker/docker-compose.yml`

Added volume mount to the postgres-exporter service to load custom queries.

## Quick Start

### Step 1: Start the Monitoring Stack

If you already have the monitoring stack running, restart it to pick up the new configuration:

```bash
cd backend/docker
docker-compose --profile monitoring down
docker-compose --profile monitoring up -d
```

Or start for the first time:

```bash
cd backend/docker
docker-compose --profile monitoring up -d
```

### Step 2: Verify Services Are Running

Check that all monitoring services are healthy:

```bash
docker-compose ps
```

You should see:

- `case-study-prometheus` (running)
- `case-study-grafana` (running)
- `case-study-postgres-exporter` (running)
- `case-study-alertmanager` (running)

### Step 3: Verify Metrics Are Being Collected

Check that the postgres-exporter is exposing custom metrics:

```bash
curl http://localhost:9187/metrics | grep pg_usage
```

You should see metrics like:

- `pg_usage_page_views_views`
- `pg_usage_daily_active_users_active_users`
- `pg_usage_hourly_views_views`
- etc.

### Step 4: Verify Prometheus Is Scraping

Open Prometheus and check the targets:

1. Go to http://localhost:9090/targets
2. Find the `postgres-exporter` job
3. Verify it shows "UP" status

### Step 5: Access the Dashboard

1. Open Grafana: http://localhost:3001
2. Login with credentials:
   - Username: `admin`
   - Password: `admin` (or your `GRAFANA_PASSWORD` env var)
3. Navigate to Dashboards → Usage Analytics Dashboard

Or directly access: http://localhost:3001/d/usage-analytics

## Dashboard Features

### Top Row - Key Metrics (Gauges)

- **Total Page Views (24h)**: Sum of all page views in the last 24 hours
- **Unique Users (24h)**: Number of distinct users who visited
- **Total Sessions (24h)**: Number of unique user sessions
- **Avg Session Duration**: Average time users spend in a session

### Time Series Charts

- **Hourly Page Views Trend**: Traffic patterns throughout the day
- **Daily Active Users Trend**: User engagement over the past 30 days

### Distribution Chart

- **Action Types Distribution**: Breakdown of user actions (page_view, button_click, etc.)

### Data Tables

- **Top Pages by Views**: Most visited routes with engagement metrics
- **Top Active Users**: Most engaged users by activity (7-day window)
- **Top Referrers**: Traffic sources bringing users to the app

## Customization

### Changing Time Windows

The queries are currently configured with these time windows:

- Page views: Last 24 hours
- Daily active users: Last 30 days
- Hourly views: Last 24 hours
- Top users: Last 7 days
- Sessions: Last 24 hours
- Referrers: Last 24 hours

To modify, edit `postgres_exporter/queries.yaml` and change the `INTERVAL` values in the SQL queries.

### Adding New Metrics

1. Edit `postgres_exporter/queries.yaml`
2. Add a new query following this pattern:

```yaml
pg_usage_your_metric_name:
  query: |
    SELECT 
      your_column as label_name,
      COUNT(*) as metric_value
    FROM usage_analytics
    WHERE viewed_at >= NOW() - INTERVAL '24 hours'
    GROUP BY your_column
  master: true
  metrics:
    - label_name:
        usage: "LABEL"
        description: "Your label description"
    - metric_value:
        usage: "GAUGE"
        description: "Your metric description"
```

3. Restart the postgres-exporter:

```bash
docker-compose restart postgres-exporter
```

4. Add a new panel in Grafana using your metric: `pg_usage_your_metric_name_metric_value`

### Dashboard Refresh Rate

Default: 30 seconds

To change:

1. Open the dashboard
2. Click the refresh icon (top-right)
3. Select a different interval or disable auto-refresh

## Troubleshooting

### No Data in Dashboard

**Problem**: Dashboard panels show "No data"

**Solutions**:

1. Check if UsageAnalytics table has data:

```sql
SELECT COUNT(*) FROM usage_analytics;
```

2. Verify postgres-exporter can query the database:

```bash
docker-compose logs postgres-exporter
```

3. Check if queries.yaml is mounted correctly:

```bash
docker exec case-study-postgres-exporter cat /etc/postgres_exporter/queries.yaml
```

4. Verify Prometheus is scraping:

```bash
curl http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | select(.job=="postgres-exporter")'
```

### Metrics Not Updating

**Problem**: Metrics are stale or not updating

**Solutions**:

1. Check Prometheus scrape interval (default: 30s):

```yaml
# In prometheus.yml
- job_name: "postgres-exporter"
  scrape_interval: 30s
```

2. Restart the postgres-exporter:

```bash
docker-compose restart postgres-exporter
```

3. Force Prometheus to reload config:

```bash
curl -X POST http://localhost:9090/-/reload
```

### Query Errors

**Problem**: postgres-exporter shows SQL errors in logs

**Solutions**:

1. Check the exporter logs:

```bash
docker-compose logs -f postgres-exporter
```

2. Verify the SQL syntax in `queries.yaml`
3. Test the query directly in PostgreSQL:

```bash
docker exec -it case-study-postgres psql -U case-study -d case-study
```

4. Common issues:
   - Missing tables (run migrations)
   - Column type mismatches
   - Incorrect interval syntax

### Dashboard Permissions

**Problem**: Can't edit or save dashboard changes

**Solutions**:

1. Check you're logged in as admin
2. Verify dashboard is not marked as read-only
3. Check the provisioning settings in `dashboards/dashboard.yml`:

```yaml
allowUiUpdates: true # Should be true to allow edits
```

## Performance Considerations

### Query Performance

The custom queries run every 30 seconds (Prometheus scrape interval). For large datasets:

1. Consider adding indexes to the UsageAnalytics table:

```sql
CREATE INDEX idx_usage_viewed_at ON usage_analytics(viewed_at);
CREATE INDEX idx_usage_route ON usage_analytics(route);
CREATE INDEX idx_usage_user_id ON usage_analytics(user_id);
CREATE INDEX idx_usage_session_id ON usage_analytics(session_id);
```

2. Use the PageViewSummary materialized view for pre-aggregated data
3. Increase the scrape interval for less frequent updates:

```yaml
# In prometheus.yml
- job_name: "postgres-exporter"
  scrape_interval: 60s # Increase from 30s
```

### Data Retention

Prometheus default retention: 15 days

To change:

```yaml
# In docker-compose.yml, prometheus service
command:
  - "--storage.tsdb.retention.time=30d" # Keep for 30 days
```

For longer retention, consider:

1. Exporting to a time-series database
2. Using Grafana's built-in alerting to save historical snapshots
3. Implementing data aggregation at the database level

## Next Steps

### Integration with Admin Dashboard

The metrics can also be consumed by your NextJS admin dashboard:

1. Query Prometheus API directly:

```typescript
const response = await fetch(
  "http://localhost:9090/api/v1/query?query=pg_usage_page_views_views"
);
const data = await response.json();
```

2. Or use the existing Flask API endpoint:

```typescript
const response = await fetch("/api/admin/usage-analytics?days=30");
```

### Setting Up Alerts

Create alerts based on usage patterns:

1. Edit `prometheus/alert_rules.yml`
2. Add usage-based alerts:

```yaml
- alert: LowUserActivity
  expr: sum(pg_usage_hourly_views_unique_users) < 5
  for: 1h
  annotations:
    summary: "Low user activity detected"
    description: "Less than 5 unique users in the past hour"

- alert: HighBounceRate
  expr: avg(pg_usage_page_views_avg_duration_seconds) < 10
  for: 5m
  annotations:
    summary: "High bounce rate detected"
    description: "Average page duration is very low"
```

3. Restart Prometheus to load new alerts:

```bash
docker-compose restart prometheus
```

## Additional Resources

- Grafana Dashboard Documentation: `grafana/dashboards/README.md`
- Main Monitoring README: `monitoring/README.md`
- Custom Queries: `postgres_exporter/queries.yaml`
- Prometheus Configuration: `prometheus/prometheus.yml`
- UsageAnalytics Model: `../api/app/models/usage_analytics.py`
