# Grafana Dashboards

This directory contains Grafana dashboard configurations for monitoring the Case Study application.

## Available Dashboards

### Usage Analytics Dashboard

**File**: `usage-analytics-dashboard.json`

A comprehensive dashboard for analyzing user behavior and application usage patterns from the UsageAnalytics database table.

#### Dashboard Features

**Key Metrics (Top Row)**

- Total Page Views (24h) - Gauge showing total page views in the last 24 hours
- Unique Users (24h) - Number of unique users who visited the app
- Total Sessions (24h) - Number of unique user sessions
- Average Session Duration - How long users typically stay engaged

**Time Series Charts**

- Hourly Page Views Trend - View traffic patterns throughout the day
- Daily Active Users Trend (30d) - Track user engagement over the past month

**Distribution Charts**

- Action Types Distribution - Pie chart showing breakdown of user actions (page_view, button_click, form_submit, etc.)

**Data Tables**

- Top Pages by Views - Most visited routes with unique users and average time spent
- Top Active Users (7d) - Most engaged users based on page views and time spent
- Top Referrers - Traffic sources bringing users to the application

#### Metrics Source

The dashboard queries custom PostgreSQL metrics exposed through the postgres-exporter. These metrics are defined in `/backend/monitoring/postgres_exporter/queries.yaml` and include:

- `pg_usage_page_views` - Route-level page view statistics
- `pg_usage_daily_active_users` - Daily active user counts
- `pg_usage_hourly_views` - Hourly traffic patterns
- `pg_usage_top_users` - Most active users
- `pg_usage_actions` - Action type distribution
- `pg_usage_sessions` - Session metrics
- `pg_usage_referrers` - Referrer analysis

## Setup Instructions

### 1. Start the Monitoring Stack

The dashboards are automatically provisioned when you start the monitoring stack:

```bash
cd backend/docker
docker-compose --profile monitoring up -d
```

Or start the full stack (app + monitoring):

```bash
docker-compose --profile full up -d
```

### 2. Access Grafana

Open your browser and navigate to:

```
http://localhost:3001
```

Default credentials:

- Username: `admin`
- Password: `admin` (or value from `GRAFANA_PASSWORD` env var)

### 3. View the Dashboard

1. Click on the menu icon (three lines) in the top-left
2. Navigate to "Dashboards"
3. Select "Usage Analytics Dashboard"

Alternatively, you can directly access:

```
http://localhost:3001/d/usage-analytics
```

## Customization

### Adding New Panels

1. Click the "Add panel" button in the Grafana UI
2. Configure your query using the Prometheus data source
3. Available metrics follow the pattern: `pg_usage_*`
4. Save the dashboard when done

### Modifying Time Ranges

- Default refresh: 30 seconds
- Default time range: Last 24 hours
- Change using the time picker in the top-right corner

### Creating Custom Queries

To add new metrics:

1. Edit `/backend/monitoring/postgres_exporter/queries.yaml`
2. Add your custom PostgreSQL query following the existing pattern
3. Restart the postgres-exporter container:
   ```bash
   docker-compose restart postgres-exporter
   ```
4. New metrics will be available in Prometheus with the prefix `pg_` followed by your query name

## Troubleshooting

### Dashboard Shows No Data

1. Verify the monitoring stack is running:

   ```bash
   docker-compose ps
   ```

2. Check if postgres-exporter is collecting metrics:

   ```bash
   curl http://localhost:9187/metrics | grep pg_usage
   ```

3. Verify Prometheus is scraping the exporter:

   ```
   http://localhost:9090/targets
   ```

4. Check if UsageAnalytics table has data:
   ```sql
   SELECT COUNT(*) FROM usage_analytics;
   ```

### Metrics Not Updating

1. Check the postgres-exporter logs:

   ```bash
   docker-compose logs postgres-exporter
   ```

2. Verify the queries.yaml file is mounted correctly:

   ```bash
   docker exec case-study-postgres-exporter cat /etc/postgres_exporter/queries.yaml
   ```

3. Restart the postgres-exporter to reload queries:
   ```bash
   docker-compose restart postgres-exporter
   ```

## Dashboard Maintenance

### Exporting Dashboard Changes

If you modify the dashboard in the Grafana UI and want to save your changes:

1. Go to Dashboard Settings (gear icon)
2. Click "JSON Model"
3. Copy the JSON
4. Save it to `usage-analytics-dashboard.json`

### Version Control

This dashboard is version-controlled. Any changes should be committed to the repository so they persist across deployments.

## Related Documentation

- Main monitoring README: `/backend/monitoring/README.md`
- Custom queries configuration: `/backend/monitoring/postgres_exporter/queries.yaml`
- Prometheus configuration: `/backend/monitoring/prometheus/prometheus.yml`
- UsageAnalytics model: `/backend/api/app/models/usage_analytics.py`
