import pathlib
import warnings, sys
warnings.filterwarnings("ignore")
from streamlit.testing.v1 import AppTest
import pandas as pd

VIEWS = ["home","dashboard","upload","profiling","cleaning","transform","visualizations",
         "insights","chat","forecasting","anomalies","customers","products","sql",
         "reports","exports","history","settings","admin","docs"]

df = pd.read_csv(str(pathlib.Path(__file__).resolve().parent.parent / "data/samples/sales_2024.csv"))
sys.path.insert(0, ".")
from core.mapping import auto_map

fails = 0
for v in VIEWS:
    at = AppTest.from_file(str(pathlib.Path(__file__).resolve().parent.parent / f"views/{v}.py"), default_timeout=120)
    at.session_state["user"] = "demo"
    at.session_state["datasets"] = {"Sales_2024.csv": df}
    at.session_state["active"] = "Sales_2024.csv"
    at.session_state["mapping"] = {"Sales_2024.csv": auto_map(df)}
    at.session_state["clean_log"] = {"Sales_2024.csv": []}
    at.session_state["messages"] = []
    at.session_state["ai_cache"] = {}
    at.run()
    if at.exception:
        fails += 1
        print(f"❌ {v}: {at.exception[0].message[:400]}")
    else:
        warn = [w.value[:80] for w in at.warning] if hasattr(at,'warning') else []
        print(f"✅ {v}  (widgets: {len(at.selectbox)+len(at.button)+len(at.tabs)})")
print("FAILURES:", fails)
