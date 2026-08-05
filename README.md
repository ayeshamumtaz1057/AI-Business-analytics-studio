# 📊 AI CSV Analytics Pro

**AI CSV Analytics Pro** is a high-performance Streamlit analytics application engineered to ingest, clean, visualize, and extract predictive machine learning insights from any CSV or Excel file. Built with modular Python architecture and styled with an enterprise dark dashboard theme.

---

## 🚀 Key Features

- **Multi-Format File Ingestion**: Intelligent parsing for `.csv`, `.xlsx`, and `.xls` files with automatic encoding fallback.
- **Automated Data Sanitization**:
  - Drops duplicate records and empty feature columns.
  - Imputes numerical NaNs with **Median** and categorical NaNs with **Mode**.
  - Automatically parses datetime columns.
- **Dynamic Interactive Data Visualizations**: Render 10+ interactive Plotly charts including Correlation Heatmaps, Treemaps, Box Plots, and Sunbursts.
- **Automated AI Business Insights**:
  - Calculates a **Data Health Quality Score** (0–100 scale).
  - Identifies highest/lowest category aggregations.
  - Generates strategic recommendations.
- **Predictive Machine Learning Engine**: Train Scikit-Learn **Linear Regression** models automatically with evaluation metrics ($R^2$, $RMSE$, $MAE$).
- **Multi-Format Export Hub**: Download cleaned CSVs, multi-sheet Excel workbooks, or polished PDF executive summaries.

---

## 🛠️ Tech Stack

- **Framework**: [Streamlit](https://streamlit.io/)
- **Data Engineering**: [Pandas](https://pandas.pydata.org/), [NumPy](https://numpy.org/), [OpenPyXL](https://openpyxl.readthedocs.io/)
- **Visualization**: [Plotly Express](https://plotly.com/python/)
- **Machine Learning**: [Scikit-Learn](https://scikit-learn.org/)
- **PDF Generation**: [FPDF2](https://pyfpdf.github.io/fpdf2/)

---

## 📦 Installation & Setup

1. **Clone the Repository**
   ```bash
   git clone [https://github.com/your-username/AI_CSV_Analytics_Pro.git](https://github.com/your-username/AI_CSV_Analytics_Pro.git)
   cd AI_CSV_Analytics_Pro
