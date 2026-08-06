import pathlib
import pandas as pd, warnings
warnings.filterwarnings("ignore")
from core.mapping import auto_map, coerce_types
from core import profiling, cleaning, transform, kpis, charts, forecasting, customers, products, anomalies, insights, nlq, reports

df = pd.read_csv(str(pathlib.Path(__file__).resolve().parent.parent / "data/samples/sales_2024.csv"))
m = auto_map(df)
print("MAPPING:", {k:v for k,v in m.items() if v})
d = kpis.prepare(df, m)
k = kpis.compute(d, m)
print("KPIS:", {n: (kpis.format_kpi(n, v['value']), None if v['delta'] is None else round(v['delta'],1)) for n,v in k.items()})
print("QUALITY:", profiling.quality_score(df), profiling.overview(df))
print("PROFILE cols:", profiling.column_profile(df).shape)
corr, strong = profiling.correlations(df); print("STRONG:", len(strong))
d2,msg = cleaning.remove_duplicates(df); print(msg)
d3,msg = cleaning.handle_missing(d2, "median", ["cost"]); print(msg)
d4,msg = cleaning.trim_whitespace(d3); print(msg)
print("GROUPBY:", transform.group_by(d, ["category"], {"revenue":"sum"}).shape)
print("PIVOT:", transform.pivot(d, "category","region","revenue").shape)
print("BIN:", transform.binning(d,"revenue",5).shape, "ENC:", transform.encode(d,["category"],"onehot").shape)
ts = kpis.timeseries(d, m, "D"); print("TS:", ts.shape)
fc, met = forecasting.forecast(ts, 90); print("FORECAST:", fc.shape, {kk: round(vv,2) for kk,vv in met.items() if isinstance(vv,float)})
for mo in forecasting.MODELS:
    f2,_ = forecasting.forecast(ts, 30, mo); assert len(f2)==30
print("all forecast models ok")
an = anomalies.detect_timeseries(ts, "Rolling Z-Score", 3.0); print("ANOM:", len(an), anomalies.summarize(an))
print("ANOM-TX:", anomalies.detect_transactions(d, ["revenue","quantity"], 0.02).shape)
r = customers.rfm(d, m); print("RFM:", r.shape, customers.summary(r))
print("COHORT:", customers.cohort_retention(d, m).shape)
p = products.performance(d, m); print("PROD:", p.shape, list(p.columns))
print("INVENTORY:", products.inventory_suggestions(p).shape)
print("CATPERF:", products.category_performance(d,m).shape)
rep = insights.rule_based_report(d, m); print("REPORT chars:", len(rep)); print(rep[:400])
ans, tbl = nlq.fallback_answer("top 10 products", d, m); print("NLQ:", ans[:90], None if tbl is None else tbl.shape)
for q in nlq.SUGGESTIONS:
    a,t = nlq.fallback_answer(q, d, m); assert a
print("nlq suggestions ok")
figs = [charts.revenue_trend(kpis.timeseries(d,m,"ME"))]
b = kpis.breakdown(d,m,"category","revenue",8)
figs.append(charts.donut(b["label"], b["value"], "Total", kpis.money(b["value"].sum())))
for kind in ["Bar","Line","Area","Pie","Donut","Scatter","Bubble","Histogram","Box Plot","Heatmap","Treemap","Sunburst","Waterfall","Correlation Matrix"]:
    kwargs = dict(x="category", y="revenue", agg="sum")
    if kind in ("Scatter","Bubble"): kwargs = dict(x="quantity", y="revenue", size="revenue")
    if kind == "Box Plot": kwargs = dict(x="category", y="revenue", color="category")
    if kind == "Heatmap": kwargs = dict(x="category", y="revenue", color="region", agg="sum")
    if kind in ("Treemap","Sunburst"): kwargs = dict(x="product", y="revenue", color="category", agg="sum")
    if kind == "Histogram": kwargs = dict(x="revenue")
    if kind == "Correlation Matrix": kwargs = {}
    charts.build(d, kind, **kwargs)
print("all 14 chart types ok")
pdf = reports.build_pdf(d, m, "Test Report", rep, {"Products": p.head(20)}, figs)
open("/tmp/t.pdf","wb").write(pdf); print("PDF bytes:", len(pdf))
xl = reports.build_excel({"Products": p.head(50), "Data": d.head(200)}, k)
open("/tmp/t.xlsx","wb").write(xl); print("XLSX bytes:", len(xl))
pp = reports.build_pptx("Test", k, rep, figs); print("PPTX:", None if pp is None else len(pp))
print("SMOKE OK")
