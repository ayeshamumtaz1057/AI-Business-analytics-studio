"""Custom CSS + shared UI primitives (KPI cards, section headers, insight cards)."""
import streamlit as st
from .config import PALETTE

CSS = """
<style>
:root {
  --bg:#0b1020; --panel:#111a2e; --panel-2:#0f1729; --border:#1e2a44;
  --text:#e8edf9; --muted:#93a2c4; --accent:#5B7CFA;
}
.stApp { background: var(--bg); }
section[data-testid="stSidebar"] { background:#0d1425; border-right:1px solid var(--border); }
section[data-testid="stSidebar"] * { color:#dbe4f7; }
h1,h2,h3,h4 { color:var(--text) !important; letter-spacing:-.02em; }
.block-container { padding-top:2.2rem; padding-bottom:3rem; max-width:1500px; }

.kpi { background:linear-gradient(160deg,var(--panel) 0%,var(--panel-2) 100%);
  border:1px solid var(--border); border-radius:14px; padding:16px 18px; height:100%; }
.kpi .lbl { color:var(--muted); font-size:.80rem; font-weight:600; letter-spacing:.02em; }
.kpi .val { color:var(--text); font-size:1.65rem; font-weight:700; margin:6px 0 4px; }
.kpi .dlt { font-size:.78rem; font-weight:600; }
.kpi .up { color:#22c55e; } .kpi .down { color:#ef4444; } .kpi .flat { color:var(--muted); }
.kpi .ico { float:right; font-size:1.1rem; opacity:.9; }

.panel { background:var(--panel); border:1px solid var(--border); border-radius:14px; padding:18px; }
.insight { border:1px solid var(--border); border-left:4px solid var(--accent);
  background:var(--panel-2); border-radius:10px; padding:12px 14px; margin-bottom:10px; }
.insight .t { font-weight:700; font-size:.92rem; margin-bottom:3px; }
.insight .b { color:var(--muted); font-size:.85rem; line-height:1.45; }
.i-good { border-left-color:#22c55e; } .i-good .t { color:#22c55e; }
.i-warn { border-left-color:#f59e0b; } .i-warn .t { color:#f59e0b; }
.i-bad  { border-left-color:#ef4444; } .i-bad  .t { color:#ef4444; }
.i-info { border-left-color:#5B7CFA; } .i-info .t { color:#8ea3ff; }

.pill { display:inline-block; padding:2px 10px; border-radius:999px; font-size:.72rem;
  background:#1b2540; color:#9fb2dd; border:1px solid var(--border); margin-right:6px; }
.sub { color:var(--muted); font-size:.9rem; margin-top:-8px; }
div[data-testid="stMetricValue"] { font-size:1.5rem; }
[data-testid="stDataFrame"] { border:1px solid var(--border); border-radius:12px; }
.stTabs [data-baseweb="tab-list"] { gap:4px; }
.stTabs [data-baseweb="tab"] { background:#0f1729; border:1px solid var(--border);
  border-radius:10px 10px 0 0; padding:6px 14px; }
</style>
"""


def inject():
    st.markdown(CSS, unsafe_allow_html=True)


def page_header(title: str, subtitle: str = "", icon: str = ""):
    st.markdown(f"# {icon} {title}".replace("#  ", "# ").strip())
    if subtitle:
        st.markdown(f"<div class='sub'>{subtitle}</div>", unsafe_allow_html=True)
    st.write("")


def kpi_card(label, value, delta=None, icon="", help_text=""):
    cls, arrow = "flat", "→"
    if delta is not None:
        cls, arrow = ("up", "↑") if delta >= 0 else ("down", "↓")
    dlt = (f"<div class='dlt {cls}'>{arrow} {abs(delta):.1f}% vs prev. period</div>"
           if delta is not None else f"<div class='dlt flat'>{help_text}</div>")
    st.markdown(
        f"<div class='kpi'><span class='ico'>{icon}</span>"
        f"<div class='lbl'>{label}</div><div class='val'>{value}</div>{dlt}</div>",
        unsafe_allow_html=True,
    )


def insight_card(title, body, kind="info"):
    st.markdown(
        f"<div class='insight i-{kind}'><div class='t'>{title}</div>"
        f"<div class='b'>{body}</div></div>",
        unsafe_allow_html=True,
    )


def plotly_layout(fig, height=380, legend=True):
    """Apply the dark studio theme to any plotly figure."""
    fig.update_layout(
        height=height,
        margin=dict(l=10, r=10, t=30, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#c9d5ee", size=12),
        colorway=PALETTE,
        showlegend=legend,
        legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="#1e2a44", borderwidth=0),
        hoverlabel=dict(bgcolor="#111a2e", bordercolor="#1e2a44"),
    )
    fig.update_xaxes(gridcolor="#1a2440", zerolinecolor="#1a2440")
    fig.update_yaxes(gridcolor="#1a2440", zerolinecolor="#1a2440")
    return fig
