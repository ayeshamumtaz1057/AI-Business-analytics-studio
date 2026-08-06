"""Global configuration and constants."""
from pathlib import Path
import os

APP_NAME = "AI Business Analytics Studio"
APP_ICON = "📊"
VERSION = "1.0.0"

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
REPORT_DIR = DATA_DIR / "reports"
SAMPLE_DIR = DATA_DIR / "samples"
DB_PATH = DATA_DIR / "app.db"

for _d in (DATA_DIR, UPLOAD_DIR, REPORT_DIR, SAMPLE_DIR):
    _d.mkdir(parents=True, exist_ok=True)

# ---- Semantic column roles used across every analytics module -------------
ROLES = [
    "date", "revenue", "profit", "cost", "quantity",
    "order_id", "customer_id", "product", "category", "region",
]

ROLE_LABELS = {
    "date": "Order Date",
    "revenue": "Revenue / Sales",
    "profit": "Profit",
    "cost": "Cost",
    "quantity": "Quantity",
    "order_id": "Order ID",
    "customer_id": "Customer ID",
    "product": "Product",
    "category": "Category",
    "region": "Region / Country",
}

ROLE_PATTERNS = {
    "date": r"(order[_ ]?date|invoice[_ ]?date|^date$|datetime|timestamp|day|period)",
    "revenue": r"(revenue|sales|amount|total|turnover|gross|net[_ ]?sales)",
    "profit": r"(profit|margin|earnings|net[_ ]?income)",
    "cost": r"(cost|cogs|expense|spend)",
    "quantity": r"(qty|quantity|units|volume)",
    "order_id": r"(order[_ ]?id|invoice|transaction|order[_ ]?no|receipt)",
    "customer_id": r"(customer|client|buyer|account|user[_ ]?id)",
    "product": r"(product|item|sku|model)",
    "category": r"(category|segment|dept|department|class)",
    "region": r"(region|country|state|city|market|territory|location)",
}

CURRENCY = os.getenv("APP_CURRENCY", "$")
TARGET_REVENUE = float(os.getenv("APP_TARGET_REVENUE", "8000000"))

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODELS = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"]

CHART_TYPES = [
    "Bar", "Line", "Area", "Pie", "Donut", "Scatter", "Bubble", "Histogram",
    "Box Plot", "Heatmap", "Treemap", "Sunburst", "Waterfall", "Correlation Matrix",
]

AGGREGATIONS = ["sum", "mean", "median", "count", "min", "max", "nunique"]

PALETTE = [
    "#5B7CFA", "#22C55E", "#F59E0B", "#EF4444", "#A855F7",
    "#06B6D4", "#EC4899", "#84CC16", "#F97316", "#14B8A6",
]
