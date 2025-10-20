# Advanced Analysis Reports API

## Overview

The Advanced Reports API provides comprehensive business intelligence and profit analysis capabilities adapted from the original CSV discovery scripts. These admin-only endpoints generate detailed visualizations and metrics for business decision-making.

## Available Report Types

### 1. Business Intelligence Report

Comprehensive multi-chart analysis covering:

- Monthly revenue and profit trends
- Revenue by product category
- Profit margins by category
- Product performance matrix
- Sales by territory
- Customer value analysis
- Seasonal sales patterns
- Product category lifecycle

### 2. Profit Margin & Break-Even Analysis

Detailed cost analysis including:

- Raw material cost vs customer pricing scatter plot
- Profit margins by product category
- Break-even analysis (units to sell)
- Cost structure breakdown (where revenue goes)

## API Endpoints

### Generate Business Intelligence Report

**POST** `/api/reports/generate/business-intelligence`

**Auth Required:** Yes (Admin only)

**Request Body:**

```json
{
  "start_date": "2023-01-01", // optional - defaults to all data
  "end_date": "2023-12-31" // optional - defaults to all data
}
```

**Response:**

```json
{
  "id": "report-uuid",
  "status": "completed",
  "file_path": "/tmp/reports/business_sales_analysis_20231201_143022.png",
  "additional_files": [
    {
      "path": "/tmp/reports/operational_insights_20231201_143022.png",
      "name": "operational_insights_20231201_143022.png"
    }
  ],
  "metrics": {
    "financial": {
      "total_revenue": 29358677.22,
      "total_profit": 12345678.9,
      "overall_margin": 42.1,
      "yoy_growth": 15.3
    },
    "operational": {
      "total_customers": 847,
      "total_orders": 3421,
      "avg_order_value": 8582.14,
      "revenue_per_customer": 34654.02
    },
    "categories_analyzed": 4,
    "products_analyzed": 295,
    "date_range": {
      "start": "2023-01-01",
      "end": "2023-12-31"
    }
  },
  "message": "Business intelligence report generated successfully"
}
```

### Generate Profit Margin Report

**POST** `/api/reports/generate/profit-margin`

**Auth Required:** Yes (Admin only)

**Request Body:**

```json
{
  "start_date": "2023-01-01", // optional
  "end_date": "2023-12-31" // optional
}
```

**Response:**

```json
{
  "id": "report-uuid",
  "status": "completed",
  "file_path": "/tmp/reports/profit_margin_analysis_20231201_143022.png",
  "metrics": {
    "overall_performance": {
      "total_revenue": 29358677.22,
      "total_cost": 16987234.12,
      "total_profit": 12371443.1,
      "overall_margin": 42.14
    },
    "category_analysis": {
      "best_margin": {
        "category": "Bikes",
        "margin": 45.2
      },
      "worst_margin": {
        "category": "Accessories",
        "margin": 38.1
      }
    },
    "products_analyzed": 295,
    "categories_analyzed": 4,
    "date_range": {
      "start": "2023-01-01",
      "end": "2023-12-31"
    }
  },
  "message": "Profit margin analysis report generated successfully"
}
```

### Get Report Files

**GET** `/api/reports/{report_id}/files`

**Auth Required:** Yes (Admin only)

Returns all files associated with a report (useful for multi-file reports).

**Response:**

```json
{
  "report_id": "report-uuid",
  "report_type": "business_intelligence",
  "files": [
    {
      "name": "business_sales_analysis_20231201_143022.png",
      "path": "/tmp/reports/business_sales_analysis_20231201_143022.png",
      "type": "main",
      "download_url": "/api/reports/report-uuid/download"
    },
    {
      "name": "operational_insights_20231201_143022.png",
      "path": "/tmp/reports/operational_insights_20231201_143022.png",
      "type": "additional",
      "download_url": "/api/reports/report-uuid/download/operational_insights_20231201_143022.png"
    }
  ],
  "total_files": 2
}
```

### Download Report File

**GET** `/api/reports/{report_id}/download`

**Auth Required:** Yes (Admin only)

Downloads the main report file.

**Response:** PNG image file

### Download Specific Report File

**GET** `/api/reports/{report_id}/download/{filename}`

**Auth Required:** Yes (Admin only)

Downloads a specific file from a multi-file report.

**Response:** PNG image file

## Usage Examples

### Using curl

```bash
# Generate Business Intelligence Report
curl -X POST http://localhost:5000/api/reports/generate/business-intelligence \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "start_date": "2023-01-01",
    "end_date": "2023-12-31"
  }'

# Generate Profit Margin Report
curl -X POST http://localhost:5000/api/reports/generate/profit-margin \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "start_date": "2023-01-01",
    "end_date": "2023-12-31"
  }'

# Get all files for a report
curl http://localhost:5000/api/reports/{report_id}/files \
  -H "Authorization: Bearer YOUR_TOKEN"

# Download main report file
curl http://localhost:5000/api/reports/{report_id}/download \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o report.png

# Download specific file
curl http://localhost:5000/api/reports/{report_id}/download/operational_insights_20231201_143022.png \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o operational_insights.png
```

### Using Python

```python
import requests

API_URL = "http://localhost:5000/api"
TOKEN = "your-jwt-token"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Generate Business Intelligence Report
response = requests.post(
    f"{API_URL}/reports/generate/business-intelligence",
    json={
        "start_date": "2023-01-01",
        "end_date": "2023-12-31"
    },
    headers=headers
)

report_data = response.json()
print(f"Report generated: {report_data['id']}")
print(f"Total Revenue: ${report_data['metrics']['financial']['total_revenue']:,.2f}")
print(f"Profit Margin: {report_data['metrics']['financial']['overall_margin']:.1f}%")

# Get all files
files_response = requests.get(
    f"{API_URL}/reports/{report_data['id']}/files",
    headers=headers
)

files = files_response.json()

# Download each file
for file_info in files['files']:
    download_url = file_info['download_url']
    filename = file_info['name']

    file_response = requests.get(
        f"{API_URL}{download_url}",
        headers=headers
    )

    with open(filename, 'wb') as f:
        f.write(file_response.content)

    print(f"Downloaded: {filename}")
```

### Using JavaScript/TypeScript

```typescript
const API_URL = "http://localhost:5000/api";
const TOKEN = "your-jwt-token";

// Generate Business Intelligence Report
async function generateBusinessIntelligenceReport() {
  const response = await fetch(
    `${API_URL}/reports/generate/business-intelligence`,
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${TOKEN}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        start_date: "2023-01-01",
        end_date: "2023-12-31",
      }),
    }
  );

  const report = await response.json();
  console.log("Report generated:", report.id);
  console.log("Total Revenue:", report.metrics.financial.total_revenue);

  return report;
}

// Download all report files
async function downloadReportFiles(reportId: string) {
  // Get list of files
  const filesResponse = await fetch(`${API_URL}/reports/${reportId}/files`, {
    headers: {
      Authorization: `Bearer ${TOKEN}`,
    },
  });

  const { files } = await filesResponse.json();

  // Download each file
  for (const file of files) {
    const downloadResponse = await fetch(`${API_URL}${file.download_url}`, {
      headers: {
        Authorization: `Bearer ${TOKEN}`,
      },
    });

    const blob = await downloadResponse.blob();

    // Create download link
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = file.name;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
  }
}

// Usage
const report = await generateBusinessIntelligenceReport();
await downloadReportFiles(report.id);
```

## Report Output Details

### Business Intelligence Report

**Main File: `business_sales_analysis_*.png`**

- 2x2 grid of charts
- Monthly revenue and profit trends (line chart)
- Revenue by product category (bar chart)
- Profit margins by category (horizontal bar chart with color coding)
- Product performance matrix (scatter plot sized by revenue, colored by margin)

**Additional File: `operational_insights_*.png`**

- 2x2 grid of operational charts
- Revenue by sales territory (bar chart)
- Top 20 customer value analysis (scatter plot)
- Seasonal sales pattern (monthly bar chart)
- Product category lifecycle (multi-line time series)

### Profit Margin Report

**File: `profit_margin_analysis_*.png`**

- 2x2 grid of cost analysis charts
- Raw material cost vs selling price (scatter with break-even line)
- Profit margin by category (horizontal bar with color coding: red <20%, yellow <40%, green >=40%)
- Break-even analysis for top 15 products (bar chart showing units needed)
- Cost structure breakdown (stacked bar showing cost % vs profit %)

## Notes

- All reports are admin-only and require authentication
- Reports are saved to `/tmp/reports` directory (configurable)
- Image files are high-resolution PNG (300 DPI)
- Date filters are optional; omitting them includes all available data
- Reports are tracked in the database with status and metadata
- Multi-file reports (like Business Intelligence) create related files with matching timestamps

## Error Handling

All endpoints return appropriate HTTP status codes:

- `200 OK` - Successful report generation
- `400 Bad Request` - Invalid parameters or incomplete report
- `401 Unauthorized` - Missing or invalid authentication
- `403 Forbidden` - Non-admin user attempting admin operation
- `404 Not Found` - Report or file not found
- `500 Internal Server Error` - Server-side error during report generation

Error responses include descriptive messages:

```json
{
  "error": "Failed to generate business intelligence report",
  "details": "No data found for the specified filters"
}
```
