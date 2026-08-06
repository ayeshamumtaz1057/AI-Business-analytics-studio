"""Generate a realistic demo sales dataset (used by the 'Load demo dataset' button)."""
from __future__ import annotations
import sys
from pathlib import Path

import numpy as np
import pandas as pd

CATALOG = {
    "Electronics": [("iPhone 15 Pro Max", 1150, .28), ("Samsung Galaxy S24", 890, .26),
                    ("MacBook Air M2", 1180, .22), ("Sony WH-1000XM5", 320, .35),
                    ("AirPods Pro 2", 230, .40), ("iPad Air 5", 590, .24),
                    ("Dell XPS 13", 1050, .18)],
    "Fashion": [("Nike Air Max 270", 145, .45), ("Adidas Ultraboost", 165, .42),
                ("Levi's 501 Jeans", 78, .52), ("Zara Wool Coat", 190, .48)],
    "Home & Kitchen": [("Dyson V15 Vacuum", 620, .30), ("Instant Pot Duo", 110, .38),
                       ("Nespresso Vertuo", 180, .33), ("IKEA Malm Desk", 130, .40)],
    "Beauty": [("Dior Sauvage 100ml", 145, .55), ("Olaplex No.3", 30, .60),
               ("La Mer Cream 60ml", 340, .50)],
    "Sports": [("Apple Watch Series 9", 420, .27), ("Peloton Dumbbells", 95, .35),
               ("Wilson Tennis Racket", 210, .38)],
    "Others": [("Kindle Paperwhite", 140, .30), ("Lego Millennium Falcon", 165, .32)],
}

REGIONS = {
    "United States": .30, "United Kingdom": .12, "Germany": .10, "France": .08,
    "Canada": .07, "Australia": .06, "Japan": .06, "India": .07, "Brazil": .05,
    "United Arab Emirates": .05, "Pakistan": .04,
}
CHANNELS = ["Online", "Retail Store", "Marketplace", "Wholesale"]
SEGMENTS = ["Consumer", "Corporate", "Small Business"]


def build(out_path: Path, rows: int = 9000, seed: int = 7) -> Path:
    rng = np.random.default_rng(seed)
    products = [(p, c, price, margin) for c, items in CATALOG.items() for p, price, margin in items]

    dates = pd.date_range("2024-01-01", "2024-12-31", freq="D")
    # trend + yearly seasonality + weekend lift
    t = np.arange(len(dates))
    weight = (1 + t / len(dates) * 0.55
              + 0.22 * np.sin(2 * np.pi * (t - 20) / 365)
              + 0.10 * (pd.Series(dates).dt.dayofweek >= 5).to_numpy())
    weight[(dates.month == 11) & (dates.day >= 24)] *= 2.1   # Black Friday
    weight[(dates.month == 12) & (dates.day <= 24)] *= 1.7   # Christmas
    weight[(dates.month == 7) & (dates.day <= 10)] *= 0.72   # summer dip
    weight = np.clip(weight, 0.05, None)
    weight = weight / weight.sum()

    picks = rng.choice(len(dates), size=rows, p=weight)
    order_dates = dates[np.sort(picks)]

    n_customers = 1400
    cust_ids = [f"CUST-{i:05d}" for i in range(1, n_customers + 1)]
    # power-law-ish customer activity
    cust_w = rng.pareto(1.6, n_customers) + 1
    cust_w /= cust_w.sum()

    idx = rng.choice(len(products), size=rows, p=_product_weights(products, rng))
    recs = []
    for i, (di, pi) in enumerate(zip(range(rows), idx)):
        name, cat, base_price, margin = products[pi]
        qty = int(rng.choice([1, 1, 1, 2, 2, 3, 4, 5], p=[.34, .18, .13, .13, .09, .07, .04, .02]))
        disc = float(rng.choice([0, 0, 0, .05, .10, .15, .25], p=[.42, .18, .12, .10, .09, .06, .03]))
        unit = base_price * (1 + rng.normal(0, .04))
        revenue = round(unit * qty * (1 - disc), 2)
        cost = round(unit * qty * (1 - margin), 2)
        recs.append({
            "order_id": f"ORD-{100000 + i}",
            "order_date": order_dates[di].strftime("%Y-%m-%d"),
            "customer_id": rng.choice(cust_ids, p=cust_w),
            "customer_segment": rng.choice(SEGMENTS, p=[.62, .23, .15]),
            "product": name,
            "category": cat,
            "region": rng.choice(list(REGIONS), p=list(REGIONS.values())),
            "channel": rng.choice(CHANNELS, p=[.55, .22, .16, .07]),
            "quantity": qty,
            "unit_price": round(unit, 2),
            "discount": disc,
            "cost": cost,
            "revenue": revenue,
            "profit": round(revenue - cost, 2),
        })

    df = pd.DataFrame(recs)

    # inject realistic messiness + a few anomalies for the demo
    m = len(df)
    df.loc[rng.choice(m, 55, replace=False), "region"] = np.nan
    df.loc[rng.choice(m, 30, replace=False), "customer_segment"] = np.nan
    df.loc[rng.choice(m, 22, replace=False), "cost"] = np.nan
    spike = rng.choice(m, 12, replace=False)
    df.loc[spike, ["revenue", "profit"]] = df.loc[spike, ["revenue", "profit"]] * 14
    df = pd.concat([df, df.sample(40, random_state=1)], ignore_index=True)
    df["product"] = df["product"].where(rng.random(len(df)) > .03, df["product"] + "  ")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
    return out_path


def _product_weights(products, rng):
    w = rng.pareto(1.1, len(products)) + 0.6
    return w / w.sum()


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1] / "data/samples/sales_2024.csv"
    print("Wrote", build(target))
