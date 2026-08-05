"""
data_cleaner.py
Core cleaning functions for the CSV/Excel Data Cleaner & Report Automator.
Each function takes a DataFrame and returns a DataFrame (except remove_duplicates,
which returns a (DataFrame, removed_count) tuple, and generate_report, which
returns a dict of stats instead of printing directly so app.py can reuse it).
"""

import os
import pandas as pd


def load_data(file_path):
    """Load a CSV or Excel file into a DataFrame. Raises ValueError on unsupported types."""
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".csv":
        df = pd.read_csv(file_path)
    elif ext in (".xlsx", ".xls"):
        df = pd.read_excel(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}. Please use .csv, .xlsx, or .xls")

    return df


def clean_column_names(df):
    """Strip leading/trailing spaces from every column header."""
    df = df.copy()
    df.columns = [str(col).strip() for col in df.columns]
    return df


def clean_text_columns(df):
    """Trim whitespace from all text values; title-case Product and Customer Name."""
    df = df.copy()

    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].astype(str).str.strip()
        # Undo the "nan" string created when astype(str) hits a real NaN
        df[col] = df[col].replace("nan", pd.NA)

    if "Product" in df.columns:
        df["Product"] = df["Product"].str.title()

    if "Customer Name" in df.columns:
        df["Customer Name"] = df["Customer Name"].str.title()

    return df


def handle_missing_values(df):
    """Fill gaps with a rule suited to each column."""
    df = df.copy()

    if "Quantity" in df.columns:
        df["Quantity"] = df["Quantity"].fillna(1)

    if "Price" in df.columns and "Product" in df.columns:
        df["Price"] = df.groupby("Product")["Price"].transform(
            lambda x: x.fillna(x.mean())
        )
        # Fallback for products where every row was missing a price
        df["Price"] = df["Price"].fillna(df["Price"].mean())

    if "Customer Name" in df.columns:
        df["Customer Name"] = df["Customer Name"].fillna("Unknown Customer")

    return df


def remove_duplicates(df):
    """Drop fully duplicate rows. Returns (df, removed_count)."""
    before = len(df)
    df = df.drop_duplicates()
    removed = before - len(df)
    return df, removed


def generate_report(df, duplicates_removed):
    """Compute summary stats and return them as a dict (doesn't print)."""
    report = {
        "total_rows": len(df),
        "duplicates_removed": duplicates_removed,
        "quantity_per_product": None,
        "total_revenue": None,
    }

    if "Product" in df.columns and "Quantity" in df.columns:
        report["quantity_per_product"] = (
            df.groupby("Product")["Quantity"].sum().sort_index()
        )

    if "Price" in df.columns and "Quantity" in df.columns:
        df["Total"] = df["Price"] * df["Quantity"]
        report["total_revenue"] = df["Total"].sum()

    return df, report


def print_report(report):
    """Console version of the report, used when running the script directly."""
    print("=" * 40)
    print("        DATA CLEANING REPORT")
    print("=" * 40)
    print(f"Total rows after cleaning : {report['total_rows']}")
    print(f"Duplicate rows removed    : {report['duplicates_removed']}")

    if report["quantity_per_product"] is not None:
        print("\nTotal quantity sold per product:")
        print(report["quantity_per_product"])

    if report["total_revenue"] is not None:
        print(f"\nTotal revenue (approx): {report['total_revenue']:,.0f}")

    print("=" * 40)


def save_clean_data(df, output_path):
    """Write the cleaned DataFrame to a new CSV file."""
    df.to_csv(output_path, index=False)


def main():
    input_file = "data/raw_sales_data.csv"
    output_file = "data/cleaned_sales_data.csv"

    df = load_data(input_file)
    df = clean_column_names(df)
    df = clean_text_columns(df)
    df = handle_missing_values(df)
    df, duplicates_removed = remove_duplicates(df)
    df, report = generate_report(df, duplicates_removed)

    print_report(report)
    save_clean_data(df, output_file)
    print(f"\nCleaned file saved to: {output_file}")


if __name__ == "__main__":
    main()
