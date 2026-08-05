<div align="center">

# 🧹 DataCleaner Pro
### Excel/CSV Data Cleaner & Report Automator

A production-grade Python tool that automatically cleans messy CSV/Excel data and turns it into a clear, auditable report — available as a **command-line script** and as a **premium Streamlit dashboard**, so anyone on the team can clean a file without touching code.

[![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![pandas](https://img.shields.io/badge/pandas-Data%20Engine-150458?logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Web%20App-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](#-license)
[![Status](https://img.shields.io/badge/Status-Actively%20Maintained-brightgreen)](#)

**Built by [Ayesha Mumtaz](#-author)**

[Problem](#-problem-it-solves) · [Features](#-features) · [How It Works](#-how-it-works) · [Getting Started](#-getting-started) · [Deploy the Web App](#-deploying-the-web-app) · [Cleaning Logic](#-cleaning-logic) · [FAQ](#-faq)

</div>

---

## 📑 Table of Contents

- [Problem It Solves](#-problem-it-solves)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [How It Works](#-how-it-works)
- [Cleaning Logic](#-cleaning-logic)
- [Function Reference](#-function-reference)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
- [Deploying the Web App](#-deploying-the-web-app)
- [Example Output](#-example-output)
- [How to Customize for Your Data](#-how-to-customize-for-your-data)
- [Performance](#-performance)
- [Troubleshooting](#-troubleshooting)
- [FAQ](#-faq)
- [Key Concepts Demonstrated](#-key-concepts-demonstrated)
- [What I Learned Building This](#-what-i-learned-building-this)
- [Roadmap](#-roadmap)
- [Real-World Use Cases](#-real-world-use-cases)
- [Contributing](#-contributing)
- [Author](#-author)
- [License](#-license)

---

## 🎯 Problem It Solves

Raw data exports — from forms, POS systems, CRMs, and surveys — are almost never clean. The same issues show up every time:

- Extra spaces in column names and text values
- Inconsistent capitalization (`mouse` vs `MOUSE` vs `Mouse`)
- Missing values in quantity, price, or customer-name fields
- Duplicate rows
- Inconsistent data types

Cleaning this by hand in Excel takes twenty minutes, is easy to get wrong, and leaves no record of what changed. **DataCleaner Pro** automates the cleanup, applies a defensible rule to every gap it fills, and produces a report that shows exactly what happened — in under a second, with identical results every time.

---

## ✨ Features

### Cleaning

| Feature | What it does |
|---|---|
| Multi-format loading | Reads `.csv`, `.xlsx`, and `.xls`; raises a clear error on anything else |
| Column name cleanup | Strips stray leading/trailing spaces from every header |
| Whitespace trimming | Strips surrounding spaces from every text value in the file |
| Capitalization fix | `Product` and `Customer Name` converted to title case, so `mouse` / `MOUSE` / `Mouse` collapse into one value |
| Type-safe text handling | Text columns are coerced to a proper string dtype before cleaning, so the tool doesn't crash on columns that arrive empty or numeric |
| Smart missing values | Each column filled by a rule suited to it — see [Cleaning Logic](#-cleaning-logic) |
| Duplicate removal | Fully duplicate rows dropped, with the count reported |
| Null normalization | Text `"nan"` produced during conversion is turned back into a real missing value |

### Reporting

| Feature | What it does |
|---|---|
| Row summary | Total rows remaining after cleaning |
| Duplicate count | How many duplicate rows were removed |
| Quantity per product | Total units sold, grouped by product — table (CLI) or chart (web app) |
| Revenue total | Price × Quantity summed across the dataset |
| Derived column | A `Total` column is calculated and carried into the cleaned output |
| Data quality analytics | Missing-value counts, null percentage, dtype breakdown, and duplicate ratio, visualized in the web app |

### Interfaces

| Feature | What it does |
|---|---|
| Command-line script | `python data_cleaner.py` cleans the bundled sample data and writes a new CSV |
| Streamlit dashboard | `streamlit run app.py` — a dark-themed, executive-style dashboard with drag-and-drop upload, live metrics, before/after preview, quality charts, and one-click export to CSV, Excel, or a text report |
| Free hosting | Deployable in minutes on Streamlit Community Cloud for a shareable public URL |

### System

| Feature | What it does |
|---|---|
| Non-destructive | The input file is never modified — output goes to a new file |
| Column-safe | Every rule checks the column exists first, so it degrades gracefully on a different schema instead of crashing |
| Reusable functions | Small, single-purpose functions in `data_cleaner.py` you can import individually |
| Zero config | No API keys, no accounts, no internet connection required to run it |
| Sample data included | Ships with `raw_sales_data.csv`, so both interfaces run the moment you clone it |

---

## 📊 Tech Stack

| Purpose | Library |
|---|---|
| Data manipulation | pandas |
| Excel I/O | openpyxl |
| Web dashboard | Streamlit |
| Charts | Plotly |

<details>
<summary><strong>Why these choices</strong> (click to expand)</summary>

| Decision | Reasoning |
|---|---|
| pandas over the manual `csv` module | Vectorized operations clean thousands of rows in milliseconds. A per-product price fill is one `groupby().transform()` call instead of twenty lines of loops. |
| Group-based price fill over a global average | A missing laptop price filled with the overall average would land near a mouse's price. Filling from that product's own rows keeps the estimate plausible. |
| Quantity filled with `1` over an average | An order exists, so the quantity is at least one. Assuming the minimum is conservative — an average would invent sales that never happened. |
| `"Unknown Customer"` over dropping the row | The sale is real even when the name is missing. Deleting the row would silently reduce revenue; labeling it keeps the total honest and the gap visible. |
| Non-destructive output | Cleaning rules are judgment calls. Writing to a new file means a wrong rule costs a re-run, not the original data. |
| A function per step | Each rule can be read, tested, reordered, or reused on its own — something one long `clean()` function couldn't offer. |
| Existence checks before every rule | `if "Product" in df.columns` means pointing this at a different schema degrades gracefully instead of crashing. |
| pandas' nullable `"string"` dtype for text columns | `.str` accessors fail on columns pandas infers as `float64` (e.g., a completely empty `Customer Name` column). Coercing to `"string"` first makes the tool resilient to messy real-world files. |
| Streamlit for the UI | Turns the script into a shareable, presentable web app — file uploader, live metrics, charts, and downloads — without a separate front-end framework. |

</details>

---

## 🏗️ How It Works

Both interfaces run the exact same pipeline from `data_cleaner.py`:

```
 [ your CSV or Excel file ]
              │
              ▼
      load_data()              CSV or Excel → DataFrame   (CLI only — the web app reads the upload directly)
              │
              ▼
      clean_column_names()     strip spaces from headers
              │
              ▼
      clean_text_columns()     trim values, title-case names
              │
              ▼
      handle_missing_values()  per-column fill rules
              │
              ▼
      remove_duplicates()      drop exact duplicates, count them
              │
              ▼
      generate_report()        compute the summary stats
              │
              ▼
   CLI: print_report() + save_clean_data()   │   Web app: dashboard metrics, charts, and download buttons
              │
              ▼
      [ cleaned file, in hand either way ]
```

Every function takes a DataFrame and returns a DataFrame, so steps can be reordered, skipped, or reused independently. `main()` wires them together for the CLI; `app.py` imports the same functions and wires them into the dashboard — **no cleaning logic is duplicated or reimplemented for the UI.**

---

## 🧮 Cleaning Logic

### Missing values — one rule per column

The core idea: a single fill strategy for the whole file is always wrong somewhere. Each column gets the rule that fits it.

| Column | Rule | Reasoning |
|---|---|---|
| `Quantity` | Fill with `1` | An order exists, so at least one unit was sold. Conservative — never invents sales |
| `Price` | Group mean per product (overall mean as fallback) | A laptop's missing price is estimated from other laptops, not from the whole catalogue |
| `Customer Name` | `"Unknown Customer"` | The sale is real; deleting the row would understate revenue |

The price rule is the interesting one:

```python
# ❌ A missing laptop price becomes roughly a mouse price
df["Price"] = df["Price"].fillna(df["Price"].mean())

# ✅ Each product's gap is filled from its own rows
df["Price"] = df.groupby("Product")["Price"].transform(
    lambda x: x.fillna(x.mean())
)
```

Filling from the overall average would flatten every product toward the middle — exactly the difference the data exists to show.

### Capitalization

`Product` and `Customer Name` are title-cased, so `mouse`, `MOUSE`, and `Mouse` stop being three separate entries. This matters more than it looks — without it, `groupby("Product")` reports the same product three times and every total is wrong.

These columns are also coerced to pandas' nullable `"string"` dtype before any `.str` operation runs, so a column that arrives completely empty (which pandas reads as `float64`, not text) cleans normally instead of raising an `AttributeError`.

### Whitespace

Both headers and values are stripped. `" Product "` and `"Product"` are different columns to pandas, and `" Mouse"` and `"Mouse"` are different products — invisible bugs that produce wrong totals rather than errors.

---

## 🔍 Function Reference

| Function | Signature | Returns |
|---|---|---|
| `load_data` | `(file_path)` | DataFrame — raises `ValueError` on unsupported extensions |
| `clean_column_names` | `(df)` | DataFrame with stripped headers |
| `clean_text_columns` | `(df)` | DataFrame with trimmed, title-cased text |
| `handle_missing_values` | `(df)` | DataFrame with gaps filled per the rules above |
| `remove_duplicates` | `(df)` | Tuple — `(df, removed_count)` |
| `generate_report` | `(df, duplicates_removed)` | Tuple — `(df, report_dict)` holding row count, duplicate count, per-product quantities, and total revenue |
| `print_report` | `(report_dict)` | `None` — prints the report to the console (CLI only) |
| `save_clean_data` | `(df, output_path)` | `None` — writes the cleaned CSV |

> ⚠️ `remove_duplicates` and `generate_report` both return **tuples** — unpack them:
> ```python
> df, removed = remove_duplicates(df)
> df, report = generate_report(df, removed)
> ```

Using a single function on its own:

```python
import pandas as pd
from data_cleaner import clean_text_columns, handle_missing_values

df = pd.read_csv("your_file.csv")
df = clean_text_columns(df)
df = handle_missing_values(df)
```

---

## 📂 Project Structure

```
data-cleaner-pro/
├── app.py                     # Streamlit dashboard — upload, preview, charts, downloads
├── data_cleaner.py            # Core script — all cleaning functions, shared by both interfaces
├── requirements.txt
├── data/
│   ├── raw_sales_data.csv     # Sample messy input data
│   └── cleaned_sales_data.csv # Generated after running the CLI script
├── README.md
└── .github/
    └── ISSUE_TEMPLATE/        # Feature request template
```

---

## 🚀 Getting Started

### Prerequisites

| Requirement | Version | Required? |
|---|---|---|
| Python | 3.x | ✅ Yes |
| pip | latest | ✅ Yes |
| Internet | — | ❌ No — runs fully offline |

### 1. Clone the repository

```bash
git clone https://github.com/ayeshamumtaz1057/csv-excel-data-cleaner.git
cd csv-excel-data-cleaner
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

Recommended: use a virtual environment first.

```bash
python -m venv venv

venv\Scripts\activate           # Windows
source venv/bin/activate        # macOS / Linux

pip install -r requirements.txt
```

Your prompt should now begin with `(venv)`.

### 3a. Run the command-line script

```bash
python data_cleaner.py
```

- **Console output:** a summary report of the cleaning operations
- **Generated file:** `data/cleaned_sales_data.csv`

### 3b. Run the web dashboard locally

```bash
streamlit run app.py
```

Opens the app at `http://localhost:8501`. Upload any `.csv`, `.xlsx`, or `.xls` file, review the raw and cleaned data side by side, explore the metrics and quality charts, and download the result as CSV, Excel, or a text report — no terminal output to read.

---

## 🌐 Deploying the Web App

The dashboard deploys for free on **Streamlit Community Cloud** with no extra configuration.

1. Make sure `requirements.txt` includes `streamlit`, `pandas`, `openpyxl`, and `plotly`.
2. Push `app.py`, `data_cleaner.py`, and `requirements.txt` to the `main` branch of this repo.
3. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
4. Click **New app**, select this repository and the `main` branch, and set the main file path to `app.py`.
5. Click **Deploy**. Streamlit installs `requirements.txt` and builds the app — this takes a minute or two.
6. Once live, the app is reachable at a public URL (e.g., `yourapp.streamlit.app`) that anyone can use without installing anything.
7. Every future push to `main` automatically triggers a redeploy.

If the build fails, check **Manage app → Logs** — it almost always points to a missing dependency or a column-handling edge case (see [Troubleshooting](#-troubleshooting)).

---

## 📋 Example Output

```
========================================
        DATA CLEANING REPORT
========================================
Total rows after cleaning : 10
Duplicate rows removed    : 0

Total quantity sold per product:
Product
Keyboard    4.0
Laptop      7.0
Monitor     1.0
Mouse       9.0
Webcam      2.0

Total revenue (approx): 552,200
========================================
```

The web dashboard shows the same numbers as metric cards, plus before/after tables and quality charts, with CSV/Excel/report download buttons underneath.

---

## 🔧 How to Customize for Your Data

1. **Replace sample data:** swap `data/raw_sales_data.csv` for your own file, or upload directly in the web app.
2. **Update column names:** edit the column references in `data_cleaner.py` if your headers differ.
3. **Adjust cleaning logic:** modify the relevant function to match your data structure.
4. **Change output:** customize `print_report()` (CLI) or the metrics/chart section of `app.py` (web app).

<details>
<summary><strong>Worked example — adapting to an HR dataset</strong></summary>

Rules are keyed to column names, so swapping schemas means editing those references:

```python
# clean_text_columns()
if "Department" in df.columns:
    df["Department"] = df["Department"].astype("string").str.strip().str.title()

# handle_missing_values()
if "Salary" in df.columns and "Department" in df.columns:
    df["Salary"] = df.groupby("Department")["Salary"].transform(
        lambda x: x.fillna(x.median())
    )
```

Every rule is wrapped in an existence check, so columns that don't apply are skipped rather than causing a crash.

</details>

<details>
<summary><strong>Using an Excel file instead of CSV (CLI)</strong></summary>

`load_data()` already handles `.xlsx` and `.xls` — just change the path:

```python
input_file = "data/raw_sales_data.xlsx"
```

Make sure `openpyxl` is installed. The web app accepts Excel uploads out of the box via the file selector.

</details>

<details>
<summary><strong>Protecting a column from being filled</strong></summary>

Identifier columns should never be imputed — a fabricated `Order ID` silently corrupts every join that uses it. Simply don't add a rule for it in `handle_missing_values()`; anything without a rule is left untouched.

</details>

---

## ⚡ Performance

| Rows | Typical time |
|---|---|
| 100 | instant |
| 10,000 | ~0.3 s |
| 100,000 | ~2 s |
| 1,000,000 | ~20 s |

pandas operations are vectorized, so cost grows roughly linearly. Excel files are noticeably slower to read than CSV — that's `openpyxl` parsing XML, not the cleaning itself. For large datasets, convert to CSV first. On Streamlit Community Cloud's free tier, very large uploads may hit the app's memory limit before they hit a time limit.

---

## 🛠 Troubleshooting

<details>
<summary><strong>Setup</strong></summary>

| Error | Fix |
|---|---|
| `ModuleNotFoundError: No module named 'pandas'` | Dependencies not installed, or the virtual environment isn't active. Run `pip install -r requirements.txt` |
| `ModuleNotFoundError: No module named 'streamlit'` | Add `streamlit` to `requirements.txt` and reinstall |
| `Missing optional dependency 'openpyxl'` | `pip install openpyxl` — pandas needs it to read `.xlsx` |
| `'python' is not recognized` | Reinstall Python and tick "Add Python to PATH", or use `py` on Windows |

</details>

<details>
<summary><strong>Reading files</strong></summary>

| Error | Fix |
|---|---|
| `FileNotFoundError: data/raw_sales_data.csv` | Run the CLI script from the project root — the path is relative |
| `ValueError: Unsupported file type` | Only `.csv`, `.xlsx`, and `.xls` are accepted |
| `UnicodeDecodeError` | The CSV isn't UTF-8. Try `pd.read_csv(path, encoding="latin-1")` |
| `PermissionError` | The file is open in Excel. Close it and re-run |
| `ParserError: Error tokenizing data` | Inconsistent column counts. Add `on_bad_lines="skip"` to identify the offending rows |
| All data lands in one column | Wrong delimiter — pass `sep=";"` or `sep="\t"` to `read_csv` |

</details>

<details>
<summary><strong>Cleaning behavior</strong></summary>

| Issue | Fix |
|---|---|
| `AttributeError: Can only use .str accessor with string values, not float64` | A text column arrived completely empty or numeric, so pandas inferred it as `float64`. Fixed by coercing to `.astype("string")` before any `.str` call — confirm you're on the latest `data_cleaner.py` |
| Nothing gets title-cased | Rules look for `Product` and `Customer Name` exactly. Check your headers match |
| Price still has blanks | That product has no price anywhere, so the group average is itself empty. Confirm the overall-mean fallback is present |
| Same product appears twice in the report | A capitalization or whitespace variant survived — print `df["Product"].unique()` to spot it |
| Revenue looks wrong | Price or Quantity is stored as text — check with `df.dtypes` |
| Fewer rows than expected | Duplicate detection matches on all columns — pass a subset to `drop_duplicates()` instead |
| `SettingWithCopyWarning` | You're modifying a slice — use `.copy()` or assign with `.loc` |

</details>

<details>
<summary><strong>Writing output & Streamlit Cloud</strong></summary>

| Error | Fix |
|---|---|
| `PermissionError` on save | The output CSV is open in Excel — close it |
| `FileNotFoundError` on save | The `data/` folder doesn't exist — create it or use `os.makedirs(..., exist_ok=True)` |
| Leading zeros vanish in Excel | Excel treats `00123` as a number — keep the column as text |
| Accented / Urdu text is garbled | Save with `encoding="utf-8-sig"` |
| Streamlit build fails immediately | Check **Manage app → Logs** — almost always a missing package in `requirements.txt` |
| App loads but crashes on upload | Usually the `.str` accessor issue above, or a column your rules assume exists — guard clauses should skip it |
| App is slow to wake up | Free-tier apps sleep after inactivity — a few seconds' delay on the next visit is normal |

</details>

---

## ❓ FAQ

**Does it modify my original file?**
No. The input is read-only; the cleaned data is written to a separate file or offered as a fresh download in the web app.

**Why is a missing Price filled per product instead of one overall average?**
A global average is wrong for almost every row. Grouping by product keeps each estimate inside a plausible range.

**Why is a missing Quantity filled with `1` rather than an average?**
The row exists, so at least one unit was sold — that's a fact, not an estimate.

**Why not just delete rows with missing customer names?**
The sale still happened. Labeling it `"Unknown Customer"` keeps the revenue total honest and the data-quality gap visible.

**Will it work on data that isn't sales data?**
The generic steps — whitespace, headers, duplicates — work on anything. The specific rules look for `Product`, `Price`, `Quantity`, and `Customer Name`, and are skipped when absent.

**Does it support Excel files?**
Yes — both interfaces read `.xlsx` and `.xls` as well as `.csv`. Output is always written as CSV (or Excel, from the web app).

**How large a file can it handle?**
Comfortably a few hundred thousand rows on a normal laptop. Very large files may need to run through the CLI locally rather than Streamlit Cloud's free tier.

**Is my data sent anywhere?**
No. Everything runs locally (CLI) or within your own Streamlit deployment — there are no third-party API calls.

**Why does the output have a `Total` column that wasn't in the input?**
`generate_report()` calculates Price × Quantity to compute revenue, and that column is carried into the cleaned data. Drop it before saving if you'd rather match the input schema exactly.

---

## 📚 Key Concepts Demonstrated

- Real-world data cleaning with pandas
- Group-based logic for handling missing data
- Structuring a script into clear, reusable functions shared across two interfaces
- Building a dashboard on top of an existing script without duplicating logic
- Deploying a Python data tool for free on Streamlit Community Cloud
- Writing a project others can actually clone, run, and deploy

<details>
<summary><strong>What I learned building this</strong></summary>

**One fill strategy for the whole file is always wrong somewhere.** The obvious approach — fill every gap with the column average — produces laptop prices near mouse prices and invents quantities that were never ordered. Working out a separate rule for Quantity, Price, and Customer Name was the point this stopped being a tutorial exercise and started being a tool.

**`groupby().transform()` was the unlock.** Filling each product's price from its own rows sounds like it needs a loop over products. It's one line — and understanding why `transform` returns something the same shape as the original was the most valuable pandas concept the project taught.

**Capitalization bugs don't crash — they lie.** `mouse`, `Mouse`, and `MOUSE` grouped into three separate products, and the report showed three sets of totals that all looked plausible. Nothing errored. Normalizing text early prevents a whole category of bugs that produce confident wrong answers.

**Dtype assumptions don't crash until real data breaks them.** The script worked on the bundled sample, then threw an `AttributeError` the first time someone uploaded a file with a completely empty `Customer Name` column. Coercing to a proper string dtype before any `.str` call closed that gap.

**Guard clauses make a script reusable.** Wrapping every rule in `if "Product" in df.columns` turned a sales-only script into something adaptable to any schema.

**A cleaner without a report is a black box.** Printing rows removed, gaps filled, and resulting totals — or showing the same numbers as dashboard metrics — turned the output into something reviewable.

**A script and a dashboard can share one brain.** `app.py` imports the exact same functions from `data_cleaner.py` rather than duplicating logic. Any bug fix or new rule only needs to happen in one place.

</details>

---

## 🚀 Roadmap

- [ ] Batch cleaning for multiple files (CLI and web app)
- [ ] Export the report as PDF or an Excel summary sheet
- [ ] Additional chart types (revenue over time, price distribution)
- [ ] Command-line arguments for custom file paths
- [ ] Logging for detailed cleaning operations
- [ ] In-app data validation checks with clearer warnings
- [ ] Support for JSON and XML input
- [ ] Configurable fill rules from the web app UI
- [ ] Unit test suite for each cleaning function
- [ ] Auto-detect numeric columns stored as text and convert them

---

## 💼 Real-World Use Cases

- **E-commerce:** clean product inventory and sales data
- **HR Analytics:** process employee records and surveys
- **Finance:** prepare financial reports from raw exports
- **Marketing:** clean customer databases and contact lists
- **Research:** prepare datasets for analysis

---

## 🤝 Contributing

Contributions are welcome.

```bash
git checkout -b feature/your-feature
git commit -m "Add your feature"
git push origin feature/your-feature
```

Please keep each cleaning rule in its own function, guard it with a column-existence check, add a line to the report for anything it changes, and keep `data_cleaner.py` and `app.py` in sync.

Have an idea? Open an issue using the feature request template.

---

## 👩‍💻 Author

**Ayesha Mumtaz**
BS Information Technology Student
📍Pakistan

[GitHub](https://github.com/ayeshamumtaz1057) · [Repository](https://github.com/ayeshamumtaz1057/csv-excel-data-cleaner)

---

## 📄 License

This project is open-sourced for educational purposes under the [MIT License](LICENSE).

---

<div align="center">

**⭐ If this project was useful, consider starring the repo.**

🍴 Fork it · 💬 Open an issue · 🤝 Submit a pull request

</div>
