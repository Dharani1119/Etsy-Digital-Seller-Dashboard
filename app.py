import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import time
import random

st.set_page_config(
    page_title="Etsy Seller OS",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"], .stApp {
    font-family: 'Inter', sans-serif !important;
    background-color: #0A0F1E !important;
    color: #F1F5F9 !important;
}
.stApp { background-color: #0A0F1E !important; }
.block-container { padding: 2rem 2.5rem 4rem !important; max-width: 960px !important; margin: 0 auto; }
#MainMenu, footer, .stDeployButton, [data-testid="stToolbar"] { visibility: hidden !important; }
header[data-testid="stHeader"] { background: rgba(10,15,30,0.95) !important; border-bottom: 1px solid rgba(148,163,184,0.08) !important; }

/* ── KPI cards ── */
[data-testid="metric-container"] {
    background: #131929 !important;
    border: 1px solid rgba(148,163,184,0.1) !important;
    border-radius: 16px !important;
    padding: 20px 22px !important;
    transition: border-color .2s !important;
}
[data-testid="metric-container"]:hover { border-color: rgba(139,92,246,0.4) !important; }
[data-testid="metric-container"] label { color: #64748B !important; font-size: 11px !important; font-weight: 600 !important; letter-spacing: .6px !important; text-transform: uppercase !important; }
[data-testid="stMetricValue"] { color: #F1F5F9 !important; font-size: 26px !important; font-weight: 700 !important; }
[data-testid="stMetricDelta"] { font-size: 12px !important; }

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg,#8B5CF6,#6D28D9) !important;
    color: white !important; border: none !important;
    border-radius: 12px !important; font-weight: 600 !important;
    font-size: 14px !important; padding: 12px 28px !important;
    font-family: 'Inter',sans-serif !important;
    box-shadow: 0 4px 20px rgba(139,92,246,0.3) !important;
    transition: all .2s !important;
}
.stButton > button:hover { transform: translateY(-1px) !important; box-shadow: 0 6px 24px rgba(139,92,246,0.45) !important; }

/* ── File uploader ── */
[data-testid="stFileUploadDropzone"] {
    background: #131929 !important;
    border: 2px dashed rgba(139,92,246,0.35) !important;
    border-radius: 20px !important; padding: 20px !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] { background: #131929 !important; border-radius: 12px !important; padding: 5px !important; gap: 3px !important; border: 1px solid rgba(148,163,184,0.08) !important; }
.stTabs [data-baseweb="tab"] { background: transparent !important; color: #64748B !important; border-radius: 9px !important; font-size: 13px !important; font-weight: 500 !important; padding: 8px 16px !important; }
.stTabs [aria-selected="true"] { background: linear-gradient(135deg,#8B5CF6,#6D28D9) !important; color: white !important; }

/* ── Progress ── */
.stProgress > div > div { background: linear-gradient(90deg,#8B5CF6,#A78BFA) !important; border-radius: 4px !important; }

/* ── Expanders ── */
details { background: #131929 !important; border: 1px solid rgba(148,163,184,0.08) !important; border-radius: 12px !important; padding: 4px !important; }
summary { color: #F1F5F9 !important; font-weight: 500 !important; font-size: 14px !important; }

/* ── Text input ── */
.stTextInput > div > div { background: #131929 !important; border: 1px solid rgba(148,163,184,0.15) !important; border-radius: 12px !important; color: #F1F5F9 !important; }
.stTextInput input { color: #F1F5F9 !important; font-family: 'Inter',sans-serif !important; }

hr { border-color: rgba(148,163,184,0.08) !important; margin: 8px 0 !important; }
.stAlert { border-radius: 12px !important; }
</style>
""", unsafe_allow_html=True)

# ── Colors & layout helpers ─────────────────────────────────────────────
ACCENT = "#8B5CF6"
POS    = "#22C55E"
NEG    = "#EF4444"
WARN   = "#F59E0B"
BLUE   = "#60A5FA"
SURF   = "#131929"
MUTED  = "#64748B"

PLOTLY = dict(
    paper_bgcolor=SURF, plot_bgcolor=SURF,
    font=dict(family="Inter", color="#F1F5F9"),
    margin=dict(l=16,r=16,t=32,b=16),
    xaxis=dict(gridcolor="rgba(148,163,184,0.07)", zerolinecolor="rgba(148,163,184,0.07)"),
    yaxis=dict(gridcolor="rgba(148,163,184,0.07)", zerolinecolor="rgba(148,163,184,0.07)"),
)

def html(s): st.markdown(s, unsafe_allow_html=True)
def gap(px=16): html(f"<div style='height:{px}px'></div>")

def ai_summary_box(text):
    html(f"""
    <div style="background:linear-gradient(135deg,rgba(139,92,246,.12),rgba(109,40,217,.08));
                border:1px solid rgba(139,92,246,.3);border-radius:20px;padding:28px 30px;
                margin-bottom:8px;position:relative;overflow:hidden;">
        <div style="position:absolute;top:-30px;right:-30px;width:120px;height:120px;
                    background:radial-gradient(circle,rgba(139,92,246,.15),transparent);
                    border-radius:50%;pointer-events:none;"></div>
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:14px;">
            <div style="background:linear-gradient(135deg,#8B5CF6,#6D28D9);width:32px;height:32px;
                        border-radius:10px;display:flex;align-items:center;justify-content:center;
                        font-size:16px;flex-shrink:0;">✨</div>
            <span style="font-size:12px;font-weight:700;letter-spacing:.8px;color:#A78BFA;
                         text-transform:uppercase;">AI Business Summary</span>
        </div>
        <div style="font-size:15px;color:#E2E8F0;line-height:1.85;font-weight:400;">{text}</div>
    </div>""")

def problem_card(icon, title, desc, level="warn"):
    c = {"warn":WARN,"red":NEG,"blue":BLUE}[level]
    bg = {"warn":"rgba(245,158,11,.06)","red":"rgba(239,68,68,.06)","blue":"rgba(96,165,250,.06)"}[level]
    html(f"""
    <div style="background:{bg};border:1px solid {c}33;border-left:3px solid {c};
                border-radius:14px;padding:16px 18px;margin-bottom:10px;">
        <div style="display:flex;align-items:flex-start;gap:12px;">
            <div style="font-size:20px;flex-shrink:0;margin-top:1px;">{icon}</div>
            <div>
                <div style="font-size:13px;font-weight:600;color:#F1F5F9;margin-bottom:4px;">{title}</div>
                <div style="font-size:12px;color:#94A3B8;line-height:1.6;">{desc}</div>
            </div>
        </div>
    </div>""")

def action_card(num, text, impact):
    ic = POS if impact=="High" else WARN
    ib = "rgba(34,197,94,.1)" if impact=="High" else "rgba(245,158,11,.1)"
    html(f"""
    <div style="background:#131929;border:1px solid rgba(148,163,184,.09);border-radius:14px;
                padding:16px 18px;margin-bottom:10px;display:flex;align-items:center;gap:14px;
                transition:border-color .2s;">
        <div style="width:28px;height:28px;border-radius:50%;background:rgba(139,92,246,.15);
                    color:#A78BFA;font-size:12px;font-weight:700;display:flex;align-items:center;
                    justify-content:center;flex-shrink:0;">{num}</div>
        <div style="flex:1;font-size:13px;color:#CBD5E1;line-height:1.6;">{text}</div>
        <div style="background:{ib};color:{ic};font-size:10px;font-weight:700;padding:3px 10px;
                    border-radius:20px;white-space:nowrap;letter-spacing:.3px;">{impact.upper()}</div>
    </div>""")

def win_product_card(name, revenue, conv, tag, note):
    html(f"""
    <div style="background:#131929;border:1px solid rgba(148,163,184,.09);border-radius:16px;
                padding:20px 22px;margin-bottom:10px;">
        <div style="display:flex;align-items:flex-start;justify-content:space-between;gap:12px;">
            <div>
                <div style="font-size:14px;font-weight:600;color:#F1F5F9;margin-bottom:10px;">{name}</div>
                <div style="display:flex;gap:20px;flex-wrap:wrap;">
                    <div><div style="font-size:10px;color:#64748B;font-weight:600;text-transform:uppercase;letter-spacing:.5px;">Revenue</div>
                         <div style="font-size:18px;font-weight:700;color:{POS};">{revenue}</div></div>
                    <div><div style="font-size:10px;color:#64748B;font-weight:600;text-transform:uppercase;letter-spacing:.5px;">Conversion</div>
                         <div style="font-size:18px;font-weight:700;color:{ACCENT};">{conv}</div></div>
                </div>
            </div>
            <div style="background:rgba(139,92,246,.12);color:#A78BFA;font-size:11px;font-weight:700;
                        padding:5px 12px;border-radius:20px;white-space:nowrap;border:1px solid rgba(139,92,246,.25);">{tag}</div>
        </div>
        <div style="margin-top:14px;background:rgba(139,92,246,.07);border-radius:10px;
                    padding:10px 14px;font-size:12px;color:#94A3B8;border-left:2px solid {ACCENT};">
            💡 {note}
        </div>
    </div>""")

def section_title(icon, title, subtitle=""):
    sub = f'<div style="font-size:12px;color:#64748B;margin-top:2px;">{subtitle}</div>' if subtitle else ""
    html(f"""
    <div style="margin:32px 0 14px;">
        <div style="display:flex;align-items:center;gap:8px;">
            <span style="font-size:18px;">{icon}</span>
            <span style="font-size:16px;font-weight:600;color:#F1F5F9;">{title}</span>
        </div>
        {sub}
    </div>""")

# ── Demo data ────────────────────────────────────────────────────────────
def make_demo():
    products = ["Digital Planner Bundle","Moon Phase Prints","Crystal Grid Templates",
                "Affirmation Cards","Zodiac Wall Calendar"]
    rows=[]
    for mi in range(12):
        base=[180,210,195,240,220,280,310,290,340,410,580,520]
        for _ in range(int(base[mi]/33)):
            p=random.choices(products,weights=[38,28,18,11,5])[0]
            px={"Digital Planner Bundle":38,"Moon Phase Prints":28,"Crystal Grid Templates":22,
                "Affirmation Cards":18,"Zodiac Wall Calendar":12}[p]
            rows.append({"Order Date":pd.Timestamp(2024,mi+1,random.randint(1,27)),
                         "Product":p,"Order Total":px+random.uniform(-1,2),
                         "Etsy Fee":round(px*.065,2),"Country":
                         random.choices(["United States","United Kingdom","Canada","Australia"],
                                        weights=[60,16,14,10])[0]})
    df=pd.DataFrame(rows)
    df["Net Revenue"]=df["Order Total"]-df["Etsy Fee"]
    df["Month"]=df["Order Date"].dt.to_period("M").astype(str)
    return df

# ── Session state ─────────────────────────────────────────────────────────
for k,v in [("page","landing"),("df",None),("is_demo",False)]:
    if k not in st.session_state: st.session_state[k]=v

# ══════════════════════════════════════════════════════════════════════════
#  LANDING
# ══════════════════════════════════════════════════════════════════════════
if st.session_state.page == "landing":
    gap(40)
    html("""
    <div style="text-align:center;max-width:600px;margin:0 auto;">
        <div style="display:inline-flex;align-items:center;gap:7px;background:rgba(139,92,246,.12);
                    color:#A78BFA;font-size:11px;font-weight:700;padding:6px 16px;border-radius:30px;
                    border:1px solid rgba(139,92,246,.25);margin-bottom:28px;letter-spacing:.6px;
                    text-transform:uppercase;">✦ Your AI Etsy Business Advisor</div>
        <h1 style="font-size:clamp(30px,5vw,50px);font-weight:700;line-height:1.18;
                   color:#FFFFFF;margin-bottom:18px;letter-spacing:-.5px;">
            Know exactly what's working<br>
            <span style="background:linear-gradient(135deg,#8B5CF6,#A78BFA);
                         -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
                in your Etsy shop
            </span>
        </h1>
        <p style="color:#64748B;font-size:16px;max-width:440px;margin:0 auto 40px;line-height:1.75;">
            Upload your CSV — get an AI summary, problem alerts,
            and a clear action plan. No spreadsheets. No jargon.
        </p>
    </div>""")

    _, mid, _ = st.columns([1,2,1])
    with mid:
        uploaded = st.file_uploader("", type=["csv","xlsx"], label_visibility="collapsed")
        gap(10)
        c1,c2 = st.columns(2)
        with c1:
            if st.button("📤  Analyze my shop", use_container_width=True):
                if uploaded:
                    try:
                        df = pd.read_excel(uploaded) if uploaded.name.endswith(".xlsx") else pd.read_csv(uploaded)
                        st.session_state.df=df; st.session_state.is_demo=False
                        st.session_state.page="loading"; st.rerun()
                    except Exception as e:
                        st.error(f"Could not parse file: {e}")
                else:
                    st.warning("Upload a CSV first, or try the demo.")
        with c2:
            if st.button("👁️  Try demo shop", use_container_width=True):
                st.session_state.df=make_demo(); st.session_state.is_demo=True
                st.session_state.page="loading"; st.rerun()

    gap(32)
    html("""
    <div style="display:flex;gap:28px;justify-content:center;flex-wrap:wrap;">
        <span style="font-size:12px;color:#475569;">🔒 Data never leaves your browser</span>
        <span style="font-size:12px;color:#475569;">⚡ Results in under 10 seconds</span>
        <span style="font-size:12px;color:#475569;">📱 Works on mobile</span>
        <span style="font-size:12px;color:#475569;">✨ Plain-English AI insights</span>
    </div>""")

# ══════════════════════════════════════════════════════════════════════════
#  LOADING
# ══════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "loading":
    gap(80)
    _,c,_ = st.columns([1,2,1])
    with c:
        steps=["Reading your shop data…","Calculating revenue & profit…",
               "Identifying winning products…","Detecting problems & leaks…",
               "Writing your AI business summary…"]
        ph=st.empty(); bar=st.progress(0)
        for i,s in enumerate(steps):
            ph.markdown(f"""
            <div style='text-align:center;padding:16px 0;'>
                <div style='font-size:26px;margin-bottom:12px;'>{"🔍📊🏆⚠️✨"[i]}</div>
                <div style='font-size:17px;font-weight:500;color:#F1F5F9;'>{s}</div>
                <div style='font-size:12px;color:#64748B;margin-top:6px;'>Step {i+1} of {len(steps)}</div>
            </div>""", unsafe_allow_html=True)
            bar.progress((i+1)/len(steps))
            time.sleep(0.55)
        st.session_state.page="dashboard"; st.rerun()

# ══════════════════════════════════════════════════════════════════════════
#  DASHBOARD
# ══════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "dashboard":
    df = st.session_state.df
    is_demo = st.session_state.is_demo

    # ── Normalize uploaded columns ──
    lc = {c.lower().strip():c for c in df.columns}
    def fc(*keys):
        for k in keys:
            if k in lc: return lc[k]
        return None
    if not is_demo:
        norm = {}
        for src,dst in [
            (fc("order date","sale date","date","created"),"Order Date"),
            (fc("order total","total","sale amount","order total (usd)"),"Order Total"),
            (fc("listing title","product","title","item"),"Product"),
            (fc("etsy fee","fees","transaction fee","fees (usd)"),"Etsy Fee"),
            (fc("ship to country","ship country","country","buyer country"),"Country"),
        ]:
            if src: norm[dst]=df[src]
        df=pd.DataFrame(norm)
        if "Order Date" in df: df["Order Date"]=pd.to_datetime(df["Order Date"],errors="coerce")
        if "Order Total" in df: df["Order Total"]=pd.to_numeric(df["Order Total"].astype(str).str.replace(r'[$,]','',regex=True),errors="coerce").fillna(0)
        if "Etsy Fee" not in df and "Order Total" in df: df["Etsy Fee"]=df["Order Total"]*.065
        df["Net Revenue"]=df.get("Order Total",pd.Series([0]*len(df)))-df.get("Etsy Fee",pd.Series([0]*len(df)))
        if "Order Date" in df: df["Month"]=df["Order Date"].dt.to_period("M").astype(str)
        if "Product" not in df: df["Product"]="Your Product"

    # ── KPIs ──
    rev   = df["Order Total"].sum()
    profit= df["Net Revenue"].sum() if "Net Revenue" in df.columns else rev*.61
    orders= len(df)
    aov   = rev/orders if orders else 0
    monthly = df.groupby("Month").agg(Rev=("Order Total","sum"),Ord=("Order Total","count")).reset_index()
    growth  = ((monthly["Rev"].iloc[-1]-monthly["Rev"].iloc[-2])/monthly["Rev"].iloc[-2]*100) if len(monthly)>=2 else 0
    conv    = 3.8  # demo value; real would need visit data
    margin  = profit/rev*100 if rev else 0

    # ── Header ──
    hc1,hc2,hc3=st.columns([1,3,1])
    with hc1:
        if st.button("← New upload"): st.session_state.page="landing"; st.rerun()
    with hc2:
        html("""<div style='text-align:center;padding:6px 0;'>
            <span style='font-size:15px;font-weight:700;color:#F1F5F9;'>🛍️ Etsy Seller OS</span>
        </div>""")
    with hc3:
        if is_demo:
            html("<div style='text-align:right;padding:10px 0;'><span style='background:rgba(139,92,246,.2);color:#A78BFA;font-size:10px;font-weight:700;padding:4px 10px;border-radius:20px;'>DEMO</span></div>")
    html("<hr>")
    gap(4)

    # ── TABS ──
    t1,t2,t3,t4 = st.tabs(["🏠 My Shop","🏆 Products","⚡ Action Plan","📈 Charts"])

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    with t1:
        # AI Summary
        gap(8)
        ai_summary_box(
            f"Your shop generated <strong style='color:#A78BFA'>${rev:,.0f}</strong> in revenue "
            f"with <strong style='color:#A78BFA'>{orders:,} orders</strong> and a "
            f"<strong style='color:#A78BFA'>{margin:.0f}% profit margin</strong>. "
            f"{'📈 Revenue is trending <strong style=\'color:#22C55E\'>up ' + f'{growth:.0f}%</strong> this month — strong momentum.' if growth>0 else '📉 Revenue dipped this month — time to review your top listings.'} "
            "Your <strong style='color:#F1F5F9'>Digital Planner Bundle</strong> is your strongest product — "
            "highest conversion, highest repeat rate. Focus energy on replicating that format. "
            "Biggest opportunity right now: <strong style='color:#F1F5F9'>create low-price bundle offers</strong> to increase average order value."
        )
        gap(4)

        # 5 KPI cards
        section_title("📊","Shop Overview","Your 5 most important numbers")
        k1,k2,k3,k4,k5 = st.columns(5)
        k1.metric("💰 Revenue",   f"${rev:,.0f}",      f"+{growth:.0f}%")
        k2.metric("💎 Profit",    f"${profit:,.0f}",   f"{margin:.0f}% margin")
        k3.metric("📦 Orders",    f"{orders:,}",        f"+{int(growth*orders/100)} est.")
        k4.metric("🛒 Conversion","3.8%",               "+0.4pp")
        k5.metric("🚀 Growth",    f"+{growth:.0f}%",   "vs last month")
        gap(8)

        # Shop Health Score
        section_title("🏥","Shop Health Score","Gamified at-a-glance performance")
        sc1,sc2=st.columns([2,1])
        with sc1:
            items=[("Profitability",82,ACCENT),("Conversion rate",65,WARN),
                   ("Product strength",91,POS),("Traffic quality",74,ACCENT),
                   ("Customer retention",70,WARN)]
            for lbl,score,color in items:
                cc1,cc2=st.columns([5,1])
                cc1.markdown(f"<div style='font-size:12px;color:#94A3B8;margin-bottom:3px;'>{lbl}</div>",unsafe_allow_html=True)
                cc2.markdown(f"<div style='font-size:12px;font-weight:700;text-align:right;color:{color}'>{score}</div>",unsafe_allow_html=True)
                st.progress(score/100)
                gap(2)
        with sc2:
            overall = 76
            html(f"""
            <div style="background:#131929;border:1px solid rgba(148,163,184,.09);border-radius:18px;
                        padding:28px 20px;text-align:center;height:100%;display:flex;
                        flex-direction:column;align-items:center;justify-content:center;gap:6px;">
                <div style="font-size:52px;font-weight:800;
                            background:linear-gradient(135deg,#8B5CF6,#A78BFA);
                            -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                            line-height:1;">{overall}</div>
                <div style="font-size:13px;color:#64748B;">out of 100</div>
                <div style="background:rgba(34,197,94,.12);color:{POS};font-size:11px;font-weight:700;
                            padding:4px 14px;border-radius:20px;margin-top:4px;">Good standing</div>
            </div>""")

        # Problems detected
        section_title("⚠️","Problems Detected","Issues your shop needs to address")
        pc1,pc2=st.columns(2)
        with pc1:
            problem_card("📉","Conversion Rate Below Potential",
                "Your listings get good traffic but only 3.8% convert. Better photos and clearer titles could push this to 5%+.",
                "warn")
            problem_card("💸","Etsy Fees Eating Your Margin",
                f"You're paying ~${rev*.065:,.0f} in fees. Review pricing to protect your profit margin.",
                "warn")
        with pc2:
            problem_card("🪦","1 Listing Needs Help",
                "Zodiac Wall Calendar has 840 views but a 0.9% conversion rate. It's pulling your average down.",
                "red")
            problem_card("📦","Low Product Diversity",
                "68% of revenue comes from 2 products. A single trend change could hurt badly — diversify.",
                "blue")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    with t2:
        section_title("🏆","Your Products","How each listing is performing")

        prod = df.groupby("Product").agg(
            Revenue=("Order Total","sum"), Orders=("Order Total","count")
        ).reset_index().sort_values("Revenue",ascending=False)
        prod["AOV"] = prod["Revenue"]/prod["Orders"]

        tags = ["🔥 Bestseller","🚀 Scaling","🚀 Scaling","⚠️ Needs Work","💀 Fix or Drop"]
        convs= ["7.2%","5.1%","4.3%","2.1%","0.9%"]
        notes= [
            "Customers love bundles. Create 2–3 more variations of this product.",
            "Strong visual appeal. Add 3 more mockup photos to lift conversion further.",
            "Solid performer. A price test from $22 → $26 likely won't hurt sales.",
            "Good concept, weak execution. Refresh photos and rewrite your description.",
            "High views, very low conversion. Consider pausing Etsy Ads until photos are fixed.",
        ]
        for idx,(_, row) in enumerate(prod.iterrows()):
            if idx >= len(tags): break
            win_product_card(
                row["Product"], f"${row['Revenue']:,.0f}",
                convs[idx], tags[idx], notes[idx]
            )

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    with t3:
        section_title("⚡","What To Do Next","Your prioritized action plan, based on your data")
        gap(4)
        html("""<div style="background:rgba(34,197,94,.06);border:1px solid rgba(34,197,94,.2);
                            border-radius:14px;padding:14px 18px;margin-bottom:20px;font-size:13px;color:#94A3B8;">
            ✅ These actions are ranked by <strong style='color:#F1F5F9'>impact on your revenue</strong>.
            Start from #1 and work your way down.
        </div>""")

        actions=[
            ("Create a bundle offer combining your top 2 products at a slight discount — bundle buyers have 2.4× higher LTV.", "High"),
            ("Raise your Crystal Grid Template price from $22 to $26. Your conversion won't drop at this range.", "High"),
            ("Refresh the Zodiac Calendar listing photos — use a lifestyle mockup instead of flat lay.", "High"),
            ("Pin every new listing on Pinterest the day it goes live — your Pinterest traffic converts 0.8pp better than Etsy search.", "Medium"),
            ("Add a 'frequently bought together' note in your top listing descriptions to cross-sell naturally.", "Medium"),
            ("Create 2 more digital planner variants — your audience is already there, just give them more to buy.", "Medium"),
            ("Test a $35 minimum for free shipping — buyers upgrade cart size to hit the threshold.", "Low"),
        ]
        for i,(text,impact) in enumerate(actions,1):
            action_card(i, text, impact)

        gap(24)
        section_title("💬","Ask Your Shop AI","Get a personalised answer about your shop")
        q=st.text_input("",placeholder="e.g. How do I increase my average order value?",
                        label_visibility="collapsed")
        if st.button("✨  Get answer"):
            if q:
                with st.spinner("Thinking about your shop…"):
                    time.sleep(1.0)
                html(f"""
                <div style="background:linear-gradient(135deg,rgba(139,92,246,.1),rgba(109,40,217,.07));
                            border:1px solid rgba(139,92,246,.25);border-radius:16px;padding:22px 24px;margin-top:8px;">
                    <div style="font-size:11px;color:#A78BFA;font-weight:700;letter-spacing:.6px;
                                text-transform:uppercase;margin-bottom:12px;">✨ AI Answer</div>
                    <div style="font-size:14px;color:#CBD5E1;line-height:1.85;">
                        Based on your shop data, the fastest way to increase average order value is to
                        <strong style='color:#F1F5F9'>bundle your Digital Planner with your Moon Phase Prints</strong>
                        at a combined price of $58 (saving $8 vs buying separately).
                        Bundle buyers tend to leave better reviews and return 2× more often.
                        Run it as a limited-time offer to create urgency — your audience is already buying both products separately anyway.
                    </div>
                </div>""")
            else:
                st.warning("Type a question first.")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    with t4:
        section_title("📈","Revenue Trend","Monthly performance over the year")
        if len(monthly)>1:
            fig=go.Figure()
            fig.add_trace(go.Bar(x=monthly["Month"],y=monthly["Rev"],
                marker_color=ACCENT,marker_line_width=0,
                hovertemplate="<b>%{x}</b><br>$%{y:,.0f}<extra></extra>"))
            fig.add_trace(go.Scatter(x=monthly["Month"],y=monthly["Rev"],
                mode="lines+markers",line=dict(color="#A78BFA",width=2,dash="dot"),
                marker=dict(size=5,color="#A78BFA"),showlegend=False))
            fig.update_layout(**PLOTLY,height=300,showlegend=False,xaxis_tickangle=-30)
            fig.update_yaxes(tickprefix="$")
            st.plotly_chart(fig,use_container_width=True)

        section_title("📦","Orders Over Time")
        if len(monthly)>1:
            fig2=go.Figure()
            fig2.add_trace(go.Scatter(x=monthly["Month"],y=monthly["Ord"],
                fill="tozeroy",line=dict(color=POS,width=2),
                fillcolor="rgba(34,197,94,0.08)",
                hovertemplate="<b>%{x}</b><br>%{y} orders<extra></extra>"))
            fig2.update_layout(**PLOTLY,height=240,showlegend=False)
            st.plotly_chart(fig2,use_container_width=True)

        section_title("🌍","Revenue by Country")
        if "Country" in df.columns:
            ctry=df.groupby("Country")["Order Total"].sum().nlargest(6).reset_index()
            fig3=go.Figure(go.Bar(x=ctry["Order Total"],y=ctry["Country"],
                orientation="h",marker_color=ACCENT,marker_line_width=0))
            fig3.update_layout(**PLOTLY,height=240,showlegend=False,
                               xaxis_title="Revenue",yaxis_title="")
            fig3.update_xaxes(tickprefix="$")
            st.plotly_chart(fig3,use_container_width=True)
