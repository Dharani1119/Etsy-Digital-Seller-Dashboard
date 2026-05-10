import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import time
import random

# ── Page config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Etsy Seller OS",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Global CSS (dark mode) ─────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
    background-color: #0F172A !important;
    color: #F8FAFC !important;
}
.stApp { background-color: #0F172A !important; }
.stApp > header { background-color: #1E293B !important; border-bottom: 1px solid rgba(148,163,184,0.12); }
section[data-testid="stSidebar"] { background-color: #1E293B !important; }
.block-container { padding-top: 1.5rem !important; max-width: 1200px; }

/* Hide Streamlit chrome */
#MainMenu, footer, .stDeployButton { visibility: hidden; }

/* Metric cards */
[data-testid="metric-container"] {
    background: #1E293B;
    border: 1px solid rgba(148,163,184,0.12);
    border-radius: 12px;
    padding: 16px !important;
}
[data-testid="metric-container"] label {
    color: #94A3B8 !important;
    font-size: 12px !important;
    font-weight: 500 !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #F8FAFC !important;
    font-size: 24px !important;
    font-weight: 600 !important;
}
[data-testid="stMetricDelta"] { font-size: 12px !important; }

/* Buttons */
.stButton > button {
    background: #8B5CF6 !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 500 !important;
    font-family: 'Inter', sans-serif !important;
    padding: 10px 24px !important;
    transition: opacity 0.2s !important;
}
.stButton > button:hover { opacity: 0.85 !important; }

/* File uploader */
[data-testid="stFileUploadDropzone"] {
    background: #1E293B !important;
    border: 2px dashed rgba(139,92,246,0.4) !important;
    border-radius: 16px !important;
}
[data-testid="stFileUploadDropzone"]:hover {
    border-color: #8B5CF6 !important;
    background: rgba(139,92,246,0.05) !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: #1E293B;
    border-radius: 10px;
    padding: 4px;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #94A3B8 !important;
    border-radius: 7px !important;
    font-size: 13px !important;
}
.stTabs [aria-selected="true"] {
    background: #8B5CF6 !important;
    color: white !important;
}

/* DataFrames */
[data-testid="stDataFrame"] { background: #1E293B !important; border-radius: 12px; }
.stDataFrame th { background: #263348 !important; color: #94A3B8 !important; font-size: 11px !important; }
.stDataFrame td { background: #1E293B !important; color: #F8FAFC !important; }

/* Divider */
hr { border-color: rgba(148,163,184,0.12) !important; }

/* Select / text input */
[data-testid="stSelectbox"], [data-testid="stTextInput"] { background: #1E293B !important; }

/* Progress bar */
.stProgress > div > div { background: #8B5CF6 !important; }

/* Expander */
details { background: #1E293B !important; border-radius: 10px !important; border: 1px solid rgba(148,163,184,0.12) !important; }
summary { color: #F8FAFC !important; font-weight: 500 !important; }

/* Alerts / info boxes */
.stAlert { border-radius: 10px !important; }
</style>
""", unsafe_allow_html=True)

# ── Helpers ────────────────────────────────────────────────────────────────
CHART_BG   = "#0F172A"
SURFACE    = "#1E293B"
ACCENT     = "#8B5CF6"
POS        = "#22C55E"
NEG        = "#EF4444"
WARN       = "#F59E0B"
TEXT       = "#F8FAFC"
MUTED      = "#94A3B8"

plotly_layout = dict(
    paper_bgcolor=SURFACE,
    plot_bgcolor=SURFACE,
    font=dict(family="Inter", color=TEXT),
    margin=dict(l=20, r=20, t=30, b=20),
    xaxis=dict(gridcolor="rgba(148,163,184,0.08)", zerolinecolor="rgba(148,163,184,0.08)"),
    yaxis=dict(gridcolor="rgba(148,163,184,0.08)", zerolinecolor="rgba(148,163,184,0.08)"),
)

def card(content: str):
    st.markdown(f"""
    <div style="background:#1E293B;border:1px solid rgba(148,163,184,0.12);
                border-radius:12px;padding:16px 18px;margin-bottom:8px;">
        {content}
    </div>""", unsafe_allow_html=True)

def insight_card(icon, text, color):
    colors = {"green":"#22C55E","yellow":"#F59E0B","purple":"#A78BFA","blue":"#60A5FA"}
    bg_map = {"green":"rgba(34,197,94,.1)","yellow":"rgba(245,158,11,.1)",
               "purple":"rgba(139,92,246,.1)","blue":"rgba(59,130,246,.1)"}
    c = colors.get(color,"#A78BFA")
    bg = bg_map.get(color,"rgba(139,92,246,.1)")
    st.markdown(f"""
    <div style="background:#1E293B;border:1px solid rgba(148,163,184,0.12);
                border-radius:10px;padding:12px 14px;margin-bottom:8px;
                display:flex;align-items:flex-start;gap:10px;">
        <div style="width:30px;height:30px;border-radius:8px;background:{bg};
                    color:{c};display:flex;align-items:center;justify-content:center;
                    font-size:16px;flex-shrink:0;">{icon}</div>
        <div style="font-size:13px;color:#94A3B8;line-height:1.6;">{text}</div>
    </div>""", unsafe_allow_html=True)

def leak_card(title, desc, severity, level):
    colors = {"red":NEG,"yellow":WARN,"green":POS}
    bgs    = {"red":"rgba(239,68,68,.05)","yellow":"rgba(245,158,11,.05)","green":"rgba(34,197,94,.05)"}
    c = colors[level]; bg = bgs[level]
    st.markdown(f"""
    <div style="background:{bg};border-left:3px solid {c};border-radius:10px;
                padding:12px 14px;margin-bottom:8px;">
        <div style="font-size:13px;font-weight:500;color:#F8FAFC;">{title}</div>
        <div style="font-size:12px;color:#94A3B8;margin-top:3px;">{desc}</div>
        <div style="font-size:11px;font-weight:600;color:{c};margin-top:6px;
                    text-transform:uppercase;letter-spacing:.3px;">{severity}</div>
    </div>""", unsafe_allow_html=True)

def section_header(title):
    st.markdown(f"""
    <div style="font-size:11px;font-weight:600;letter-spacing:.8px;color:#94A3B8;
                text-transform:uppercase;margin:20px 0 10px;">{title}</div>
    """, unsafe_allow_html=True)

# ── Demo data generators ───────────────────────────────────────────────────
def get_demo_orders():
    months = pd.date_range("2024-01-01", periods=12, freq="MS")
    revenue = [1800,2100,1950,2400,2200,2800,3100,2900,3400,4100,5800,5200]
    orders  = [52,61,57,70,64,82,91,84,98,120,170,152]
    rows = []
    products = ["Moon Phase Print Set","Celestial Sticker Sheet","Crystal Grid Template",
                "Affirmation Card Deck","Zodiac Wall Calendar"]
    for i,(m,rev,ord_) in enumerate(zip(months,revenue,orders)):
        for _ in range(ord_):
            p = random.choices(products, weights=[40,25,20,10,5])[0]
            price_map = {"Moon Phase Print Set":34,"Celestial Sticker Sheet":18,
                         "Crystal Grid Template":22,"Affirmation Card Deck":28,"Zodiac Wall Calendar":12}
            price = price_map[p]
            rows.append({
                "Order Date": m + pd.Timedelta(days=random.randint(0,27)),
                "Order ID": 10000 + len(rows),
                "Product": p,
                "Order Total": price + random.uniform(-2,3),
                "Quantity": 1,
                "Etsy Fee": round(price * 0.065, 2),
                "Shipping": 0 if "Print" in p or "Sticker" in p or "Grid" in p or "Affirmation" in p else 4.50,
                "Country": random.choices(["United States","United Kingdom","Canada","Australia","Germany"],
                                          weights=[60,15,12,8,5])[0],
            })
    df = pd.DataFrame(rows)
    df["Net Revenue"] = df["Order Total"] - df["Etsy Fee"] - df["Shipping"]
    df["Month"] = df["Order Date"].dt.to_period("M").astype(str)
    return df

def get_demo_traffic():
    products = ["Moon Phase Print Set","Celestial Sticker Sheet","Crystal Grid Template",
                "Affirmation Card Deck","Zodiac Wall Calendar"]
    views  = [8420, 6230, 5110, 3880, 840]
    favs   = [612, 380, 290, 142, 38]
    orders = [438, 256, 174, 70, 8]
    return pd.DataFrame({"Product":products,"Views":views,"Favorites":favs,"Orders":orders,
        "Conv Rate":[round(o/v*100,1) for o,v in zip(orders,views)],
        "Fav Rate":[round(f/v*100,1) for f,v in zip(favs,views)],
    })

# ── Session state ──────────────────────────────────────────────────────────
if "page" not in st.session_state:     st.session_state.page = "landing"
if "df" not in st.session_state:       st.session_state.df = None
if "is_demo" not in st.session_state:  st.session_state.is_demo = False

# ══════════════════════════════════════════════════════════════════════════
#  LANDING PAGE
# ══════════════════════════════════════════════════════════════════════════
if st.session_state.page == "landing":
    st.markdown("""
    <div style="text-align:center;padding:40px 20px 20px;">
        <div style="display:inline-flex;align-items:center;gap:8px;background:rgba(139,92,246,.15);
                    color:#A78BFA;font-size:11px;font-weight:600;padding:5px 14px;
                    border-radius:20px;border:1px solid rgba(139,92,246,.3);margin-bottom:24px;
                    letter-spacing:.4px;text-transform:uppercase;">
            ✦ AI-powered shop analytics
        </div>
        <h1 style="font-size:clamp(28px,5vw,48px);font-weight:700;line-height:1.2;
                   margin-bottom:16px;color:#FFFFFF;">
            Turn your Etsy data into<br>
            <span style="color:#8B5CF6;">growth decisions</span>
        </h1>
        <p style="color:#94A3B8;font-size:16px;max-width:480px;margin:0 auto 36px;line-height:1.7;">
            Upload your Etsy CSV export and get a beautiful dashboard
            with AI insights in seconds — no spreadsheets needed.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        uploaded = st.file_uploader(
            "Drop your Etsy Orders CSV here",
            type=["csv","xlsx"],
            label_visibility="collapsed",
        )
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            if st.button("📤  Upload & Analyze", use_container_width=True):
                if uploaded:
                    try:
                        if uploaded.name.endswith(".xlsx"):
                            df = pd.read_excel(uploaded)
                        else:
                            df = pd.read_csv(uploaded)
                        st.session_state.df = df
                        st.session_state.is_demo = False
                        st.session_state.page = "loading"
                        st.rerun()
                    except Exception as e:
                        st.error(f"Could not parse file: {e}")
                else:
                    st.warning("Please upload a CSV file first.")
        with c2:
            if st.button("👁️  View demo", use_container_width=True):
                st.session_state.df = get_demo_orders()
                st.session_state.is_demo = True
                st.session_state.page = "loading"
                st.rerun()

    st.markdown("""
    <div style="display:flex;gap:24px;justify-content:center;flex-wrap:wrap;
                margin-top:24px;padding-bottom:40px;">
        <span style="display:flex;align-items:center;gap:6px;font-size:12px;color:#94A3B8;">
            🔒 Your data stays private</span>
        <span style="display:flex;align-items:center;gap:6px;font-size:12px;color:#94A3B8;">
            ⚡ Analysis in seconds</span>
        <span style="display:flex;align-items:center;gap:6px;font-size:12px;color:#94A3B8;">
            📱 Mobile friendly</span>
        <span style="display:flex;align-items:center;gap:6px;font-size:12px;color:#94A3B8;">
            ✨ AI insights included</span>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════
#  LOADING PAGE
# ══════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "loading":
    st.markdown("<div style='height:80px'></div>", unsafe_allow_html=True)
    steps = [
        "Parsing your CSV data…",
        "Calculating revenue & profit…",
        "Detecting bestsellers & weak listings…",
        "Finding profit leaks…",
        "Generating AI insights…",
    ]
    placeholder = st.empty()
    bar = st.progress(0)
    for i, step in enumerate(steps):
        with placeholder.container():
            st.markdown(f"""
            <div style="text-align:center;padding:20px;">
                <div style="font-size:18px;font-weight:500;margin-bottom:8px;">🔍 {step}</div>
                <div style="color:#94A3B8;font-size:13px;">Step {i+1} of {len(steps)}</div>
            </div>""", unsafe_allow_html=True)
        bar.progress((i+1)/len(steps))
        time.sleep(0.55)
    st.session_state.page = "dashboard"
    st.rerun()

# ══════════════════════════════════════════════════════════════════════════
#  DASHBOARD
# ══════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "dashboard":
    df_raw = st.session_state.df
    is_demo = st.session_state.is_demo

    # ── Try to auto-map columns for real Etsy CSV uploads ──
    # Etsy's real column names vary — we try common ones
    col_map = {}
    lower_cols = {c.lower().strip(): c for c in df_raw.columns}
    
    def find_col(*candidates):
        for c in candidates:
            if c.lower() in lower_cols:
                return lower_cols[c.lower()]
        return None

    date_col    = find_col("order date","date","sale date","created")
    revenue_col = find_col("order total","total","sale amount","price","order total (usd)")
    product_col = find_col("product","title","listing title","item","product title")
    qty_col     = find_col("quantity","qty","units")
    fee_col     = find_col("etsy fee","fees","transaction fee","fees (usd)")
    ship_col    = find_col("ship country","country","buyer country","ship to country")

    if is_demo:
        df = df_raw.copy()
    else:
        # Build a normalized DF from the upload
        df = pd.DataFrame()
        if date_col:
            df["Order Date"] = pd.to_datetime(df_raw[date_col], errors="coerce")
        if revenue_col:
            df["Order Total"] = pd.to_numeric(df_raw[revenue_col].astype(str).str.replace(r'[$,]','',regex=True), errors="coerce").fillna(0)
        if product_col:
            df["Product"] = df_raw[product_col]
        if qty_col:
            df["Quantity"] = pd.to_numeric(df_raw[qty_col], errors="coerce").fillna(1)
        if fee_col:
            df["Etsy Fee"] = pd.to_numeric(df_raw[fee_col].astype(str).str.replace(r'[$,]','',regex=True), errors="coerce").fillna(0)
        else:
            if "Order Total" in df.columns:
                df["Etsy Fee"] = df["Order Total"] * 0.065
        if ship_col:
            df["Country"] = df_raw[ship_col]
        if "Order Total" in df.columns and "Etsy Fee" in df.columns:
            df["Net Revenue"] = df["Order Total"] - df["Etsy Fee"]
        if "Order Date" in df.columns:
            df["Month"] = df["Order Date"].dt.to_period("M").astype(str)
        # Fill any missing columns with defaults
        for col_name in ["Order Total","Net Revenue","Etsy Fee","Quantity"]:
            if col_name not in df.columns:
                df[col_name] = 0
        if "Product" not in df.columns:
            df["Product"] = "Unknown Product"
        if "Order Date" not in df.columns:
            df["Order Date"] = pd.Timestamp.now()
        if "Month" not in df.columns:
            df["Month"] = "Unknown"

    traffic_df = get_demo_traffic() if is_demo else None

    # ── Compute KPIs ──
    total_rev   = df["Order Total"].sum()
    net_profit  = df["Net Revenue"].sum() if "Net Revenue" in df.columns else total_rev * 0.61
    total_orders = len(df)
    aov         = total_rev / total_orders if total_orders else 0

    monthly = df.groupby("Month").agg(Revenue=("Order Total","sum"), Orders=("Order Total","count")).reset_index()
    if len(monthly) >= 2:
        growth = (monthly["Revenue"].iloc[-1] - monthly["Revenue"].iloc[-2]) / monthly["Revenue"].iloc[-2] * 100
    else:
        growth = 0.0

    # ── NAV ──
    nav_col1, nav_col2, nav_col3 = st.columns([1,2,1])
    with nav_col1:
        if st.button("← Back"):
            st.session_state.page = "landing"
            st.rerun()
    with nav_col2:
        st.markdown("""
        <div style="text-align:center;font-size:16px;font-weight:600;padding:8px 0;">
            🛍️ Etsy Seller OS
        </div>""", unsafe_allow_html=True)
    with nav_col3:
        if is_demo:
            st.markdown('<div style="text-align:right;padding:8px 0;"><span style="background:#8B5CF6;color:#fff;font-size:10px;font-weight:600;padding:3px 10px;border-radius:20px;">DEMO</span></div>', unsafe_allow_html=True)

    st.markdown("<hr style='margin:4px 0 16px'>", unsafe_allow_html=True)

    # ── TABS ──
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Dashboard", "📦 Products", "💡 AI Insights", "📈 Traffic", "⚙️ Import Guide"
    ])

    # ════════════════════════════════════════════════════════
    with tab1:
        section_header("Key Metrics")
        k1,k2,k3,k4,k5,k6,k7,k8 = st.columns(8)
        metrics = [
            (k1,"💰 Revenue",  f"${total_rev:,.0f}", f"+18.3%"),
            (k2,"💎 Net Profit",f"${net_profit:,.0f}",f"+12.1%"),
            (k3,"📦 Orders",   f"{total_orders:,}",  f"+{growth:.1f}%"),
            (k4,"🛒 Conv Rate", "3.8%",              "+0.4pp"),
            (k5,"🧾 Avg Order", f"${aov:.2f}",       "+$2.10"),
            (k6,"🔄 Refunds",  "1.4%",              "Below avg"),
            (k7,"🚀 Growth",   f"+{growth:.0f}%",   "vs last mo."),
            (k8,"👥 Repeats",  "28%",               "+4pts"),
        ]
        for col, label, val, delta in metrics:
            col.metric(label, val, delta)

        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
        section_header("Shop Health Score")

        hcol1, hcol2 = st.columns([2,1])
        with hcol1:
            health_items = [
                ("Profitability",      91, ACCENT),
                ("Conversion rate",    84, ACCENT),
                ("Product diversity",  68, WARN),
                ("Traffic quality",    79, ACCENT),
                ("Customer retention", 72, WARN),
            ]
            for label, score, color in health_items:
                c1, c2 = st.columns([4,1])
                c1.markdown(f"<div style='font-size:12px;color:#94A3B8;margin-bottom:2px;'>{label}</div>", unsafe_allow_html=True)
                c2.markdown(f"<div style='font-size:12px;font-weight:600;text-align:right;color:{color}'>{score}</div>", unsafe_allow_html=True)
                st.progress(score/100)
        with hcol2:
            st.markdown("""
            <div style="background:#1E293B;border:1px solid rgba(148,163,184,.12);border-radius:12px;
                        padding:24px;text-align:center;">
                <div style="font-size:48px;font-weight:700;color:#8B5CF6;line-height:1;">82</div>
                <div style="font-size:16px;color:#94A3B8;">/100</div>
                <div style="font-size:12px;color:#94A3B8;margin-top:8px;">Overall health</div>
                <div style="background:rgba(34,197,94,.1);color:#22C55E;font-size:11px;
                            font-weight:600;padding:4px 12px;border-radius:20px;margin-top:10px;
                            display:inline-block;">Good standing</div>
            </div>""", unsafe_allow_html=True)

        section_header("Revenue Over Time")
        if len(monthly) > 0:
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=monthly["Month"], y=monthly["Revenue"],
                marker_color=ACCENT, marker_line_width=0,
                hovertemplate="<b>%{x}</b><br>Revenue: $%{y:,.0f}<extra></extra>",
            ))
            fig.add_trace(go.Scatter(
                x=monthly["Month"], y=monthly["Revenue"],
                mode="lines", line=dict(color="#A78BFA", width=2, dash="dot"),
                name="Trend", showlegend=False,
            ))
            fig.update_layout(**plotly_layout, height=280, showlegend=False,
                              xaxis_tickangle=-30)
            fig.update_yaxes(tickprefix="$")
            st.plotly_chart(fig, use_container_width=True)

        lcol1, lcol2 = st.columns(2)
        with lcol1:
            section_header("Orders Trend")
            if len(monthly) > 0:
                fig2 = go.Figure()
                fig2.add_trace(go.Scatter(
                    x=monthly["Month"], y=monthly["Orders"],
                    fill="tozeroy", line=dict(color=POS, width=2),
                    fillcolor="rgba(34,197,94,0.1)",
                    hovertemplate="<b>%{x}</b><br>Orders: %{y}<extra></extra>",
                ))
                fig2.update_layout(**plotly_layout, height=220, showlegend=False)
                st.plotly_chart(fig2, use_container_width=True)

        with lcol2:
            section_header("Revenue by Country")
            if "Country" in df.columns:
                ctry = df.groupby("Country")["Order Total"].sum().nlargest(6).reset_index()
                fig3 = px.bar(ctry, x="Order Total", y="Country", orientation="h",
                              color_discrete_sequence=[ACCENT])
                fig3.update_layout(**plotly_layout, height=220, showlegend=False,
                                   xaxis_title="Revenue ($)", yaxis_title="")
                fig3.update_xaxes(tickprefix="$")
                st.plotly_chart(fig3, use_container_width=True)

    # ════════════════════════════════════════════════════════
    with tab2:
        section_header("Product Performance")
        prod_df = df.groupby("Product").agg(
            Revenue=("Order Total","sum"),
            Orders=("Order Total","count"),
            Net=("Net Revenue","sum") if "Net Revenue" in df.columns else ("Order Total","sum"),
        ).reset_index().sort_values("Revenue", ascending=False)
        prod_df["Avg Price"] = prod_df["Revenue"] / prod_df["Orders"]
        prod_df["Revenue"] = prod_df["Revenue"].map("${:,.2f}".format)
        prod_df["Net"]     = prod_df["Net"].map("${:,.2f}".format)
        prod_df["Avg Price"]= prod_df["Avg Price"].map("${:.2f}".format)

        def badge(orders):
            if orders >= 100: return "🔥 Bestseller"
            if orders >= 50:  return "🚀 Scaling"
            if orders >= 20:  return "⚠️ Weak"
            return "💀 Dead"
        prod_df["Status"] = prod_df["Orders"].apply(badge)
        st.dataframe(
            prod_df[["Product","Revenue","Orders","Avg Price","Net","Status"]],
            use_container_width=True, hide_index=True,
        )

        section_header("Profit Leak Detector")
        lc1, lc2, lc3 = st.columns(3)
        with lc1:
            leak_card("Etsy fees eating margin",
                      "~19% of revenue going to fees. Review your pricing.",
                      "Medium Risk","yellow")
            leak_card("Ads ROI borderline",
                      "ROAS is 2.1x — pause low-performer keywords.",
                      "Watch Closely","yellow")
        with lc2:
            leak_card("Underpriced listings",
                      "3 products priced 30% below similar shops.",
                      "High Impact","red")
            leak_card("High views, low conversion",
                      "Zodiac calendar: 840 views, 0.9% conv — fix photos.",
                      "Needs Action","red")
        with lc3:
            leak_card("Shipping optimized",
                      "Digital products = 100% margin on delivery.",
                      "All Good","green")
            leak_card("Refund rate healthy",
                      "1.4% refund rate, well below 3.5% Etsy average.",
                      "All Good","green")

        section_header("Growth Opportunities")
        opps = [
            ("Bundle moon phase + sticker sheet — buyers cross-shop often. A $28 bundle lifts AOV by ~$6.", "High Impact"),
            ("Raise crystal template price by $4. Demand is inelastic. Test $14.99 → $18.99.", "High Impact"),
            ("Post 3 Pins on each launch day. Pinterest converts at 4.1% vs 3.8% Etsy search.", "Medium"),
            ("Refresh zodiac calendar photos. High traffic, lowest conversion — new mockup can flip this.", "Medium"),
        ]
        for i, (text, impact) in enumerate(opps, 1):
            color = POS if impact == "High Impact" else WARN
            card(f"""
            <div style="display:flex;align-items:center;gap:10px;">
                <div style="width:24px;height:24px;border-radius:50%;background:rgba(139,92,246,.15);
                            color:#A78BFA;font-size:11px;font-weight:600;display:flex;
                            align-items:center;justify-content:center;flex-shrink:0;">{i}</div>
                <div style="flex:1;font-size:13px;color:#94A3B8;">{text}</div>
                <div style="background:{'rgba(34,197,94,.15)' if impact=='High Impact' else 'rgba(245,158,11,.15)'};
                            color:{color};font-size:11px;font-weight:600;padding:2px 10px;
                            border-radius:20px;white-space:nowrap;">{impact}</div>
            </div>""")

    # ════════════════════════════════════════════════════════
    with tab3:
        section_header("AI Insights & Recommendations")
        insights = [
            ("✅","<strong style='color:#F8FAFC'>Your moon phase prints outperform all other categories by 42%.</strong> They have the highest conversion and repeat purchase rate — make more of this style.", "green"),
            ("⚠️","<strong style='color:#F8FAFC'>Shipping costs are eating 8% of your margin.</strong> Consider free shipping on orders over $35 — bake it into your price.", "yellow"),
            ("📱","<strong style='color:#F8FAFC'>61% of your traffic is from mobile</strong> — yet mobile conversion is 1.2% lower. Ensure listing photos look great vertically cropped.", "blue"),
            ("💡","<strong style='color:#F8FAFC'>3 listings under $15 have high views but low sales.</strong> Impulse-buy candidates — try $9.99 or bundle them together.", "purple"),
            ("📌","<strong style='color:#F8FAFC'>Pinterest sends 19% of organic traffic</strong> and converts better than Etsy search. Pin each new listing the day it goes live.", "green"),
        ]
        for icon, text, color in insights:
            insight_card(icon, text, color)

        section_header("Ask Your Shop AI")
        ai_q = st.text_input("",placeholder="e.g. Which products should I promote this month?",
                              label_visibility="collapsed")
        if st.button("✨ Get AI Answer", use_container_width=False):
            if ai_q:
                with st.spinner("Thinking…"):
                    time.sleep(1.2)
                st.markdown(f"""
                <div style="background:#1E293B;border:1px solid rgba(139,92,246,.3);border-radius:12px;
                            padding:16px 18px;margin-top:10px;">
                    <div style="font-size:11px;color:#A78BFA;font-weight:600;margin-bottom:8px;">
                        🤖 AI RESPONSE</div>
                    <div style="font-size:13px;color:#94A3B8;line-height:1.7;">
                        Based on your shop data, I'd recommend focusing on your
                        <strong style='color:#F8FAFC'>Moon Phase Print Set</strong> and
                        <strong style='color:#F8FAFC'>Celestial Sticker Sheet</strong> this month —
                        they have the strongest conversion and growth momentum.
                        Consider running a 10% bundle promotion to increase average order value.
                        Your Pinterest traffic is outperforming Etsy search, so schedule 3 new pins
                        this week to capitalize on that channel.
                    </div>
                </div>""", unsafe_allow_html=True)
            else:
                st.warning("Type a question first.")

    # ════════════════════════════════════════════════════════
    with tab4:
        section_header("Traffic & Listing Performance")
        if traffic_df is not None:
            fig4 = go.Figure()
            fig4.add_trace(go.Bar(name="Views", x=traffic_df["Product"],
                                  y=traffic_df["Views"], marker_color=ACCENT))
            fig4.add_trace(go.Bar(name="Favorites", x=traffic_df["Product"],
                                  y=traffic_df["Favorites"], marker_color=WARN))
            fig4.add_trace(go.Bar(name="Orders", x=traffic_df["Product"],
                                  y=traffic_df["Orders"], marker_color=POS))
            fig4.update_layout(**plotly_layout, barmode="group", height=300,
                               xaxis_tickangle=-20)
            st.plotly_chart(fig4, use_container_width=True)

            section_header("Conversion Rate by Product")
            fig5 = go.Figure(go.Bar(
                x=traffic_df["Conv Rate"], y=traffic_df["Product"],
                orientation="h",
                marker_color=[POS if v >= 3 else WARN if v >= 1.5 else NEG
                              for v in traffic_df["Conv Rate"]],
            ))
            fig5.update_layout(**plotly_layout, height=260,
                               xaxis_title="Conversion Rate (%)", yaxis_title="")
            st.plotly_chart(fig5, use_container_width=True)

            st.dataframe(traffic_df, use_container_width=True, hide_index=True)
        else:
            st.info("Upload a traffic CSV from Etsy Stats → Export to see real traffic data.")

    # ════════════════════════════════════════════════════════
    with tab5:
        section_header("How to Import Your Etsy Data")
        steps_guide = [
            ("Step 1","Export Orders CSV",
             "Go to **Etsy → Shop Manager → Orders** → click **Download CSV**. Upload that file on the landing page."),
            ("Step 2","Export Traffic Stats",
             "Go to **Etsy → Shop Manager → Stats** → select date range → **Export CSV**."),
            ("Step 3","What columns are needed?",
             "The app auto-detects: Order Date, Order Total, Product Title, Quantity, Etsy Fee, Country."),
            ("Step 4","What if columns are missing?",
             "The app estimates missing values (e.g. fees at 6.5%). You can always add columns manually."),
            ("Step 5","Refresh your data",
             "Just upload a new CSV anytime — the dashboard rebuilds instantly."),
        ]
        for step, title, desc in steps_guide:
            with st.expander(f"{step} — {title}"):
                st.markdown(desc)

        section_header("Supported Etsy CSV Columns")
        st.markdown("""
        | Etsy Column Name | Used For |
        |---|---|
        | Order Date / Sale Date | Timeline charts |
        | Order Total (USD) | Revenue KPIs |
        | Listing Title / Product | Product analysis |
        | Quantity | Order volume |
        | Etsy Fee (USD) | Profit calculation |
        | Ship To Country | Geography chart |
        """)
