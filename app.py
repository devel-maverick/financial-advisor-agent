from dotenv import load_dotenv
load_dotenv(override=True)

import streamlit as st
import requests
import sys
import os

# API Config — use .env by default, only check st.secrets if file exists
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
try:
    _secrets = st.secrets._parse()
    API_BASE_URL = _secrets.get("API_BASE_URL", API_BASE_URL)
    for key in ["GROQ_API_KEY", "OPENAI_API_KEY", "LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY", "LANGFUSE_HOST"]:
        if key in _secrets:
            os.environ[key] = _secrets[key]
except Exception:
    pass

from services.logger import logger

import streamlit.components.v1 as components

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="DalalAI — Financial Advisor Agent",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)




# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* Reset & base */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    color: #0f172a;
}

/* White background everywhere */
.stApp {
    background: #ffffff;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #f8fafc;
    border-right: 1px solid #e2e8f0;
}
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span {
    color: #0f172a !important;
}

/* Selectbox */
.stSelectbox > div > div {
    background: #ffffff;
    border: 1.5px solid #e2e8f0;
    border-radius: 10px;
    color: #0f172a;
}


section[data-testid="stSidebar"] > div:first-child { padding-top: 16px; }


/* Metric card */
.metric-card {
    background: #ffffff;
    border: 1.5px solid #e2e8f0;
    border-radius: 16px;
    padding: 20px 24px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    transition: box-shadow 0.2s;
}
.metric-card:hover { box-shadow: 0 4px 16px rgba(0,0,0,0.08); }
.metric-label {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #64748b;
    margin-bottom: 6px;
}
.metric-value {
    font-size: 26px;
    font-weight: 700;
    color: #0f172a;
    line-height: 1.2;
}
.metric-sub {
    font-size: 13px;
    font-weight: 500;
    margin-top: 4px;
}
.positive { color: #16a34a; }
.negative { color: #dc2626; }
.neutral  { color: #0f172a; }

/* Section headers */
.section-title {
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #94a3b8;
    margin: 28px 0 12px;
}

/* Risk badge */
.risk-badge {
    display: inline-block;
    padding: 5px 14px;
    border-radius: 99px;
    font-size: 12px;
    font-weight: 600;
    margin: 4px 4px 4px 0;
}
.risk-critical { background: #fee2e2; color: #b91c1c; border: 1px solid #fca5a5; }
.risk-high     { background: #ffedd5; color: #c2410c; border: 1px solid #fdba74; }
.risk-ok       { background: #dcfce7; color: #15803d; border: 1px solid #86efac; }

/* Sector bar */
.sector-row { margin-bottom: 10px; }
.sector-name {
    font-size: 13px;
    font-weight: 500;
    color: #334155;
    margin-bottom: 4px;
    display: flex;
    justify-content: space-between;
}
.bar-track {
    background: #f1f5f9;
    border-radius: 99px;
    height: 8px;
    width: 100%;
}
.bar-fill {
    height: 8px;
    border-radius: 99px;
    background: linear-gradient(90deg, #3b82f6, #6366f1);
    transition: width 0.5s ease;
}
.bar-fill-risk {
    height: 8px;
    border-radius: 99px;
    background: linear-gradient(90deg, #ef4444, #f97316);
    transition: width 0.5s ease;
}

/* Stock mover row */
.mover-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 0;
    border-bottom: 1px solid #f1f5f9;
}
.mover-symbol {
    font-weight: 600;
    font-size: 14px;
    color: #0f172a;
}
.mover-pct {
    font-weight: 700;
    font-size: 14px;
    padding: 3px 10px;
    border-radius: 8px;
}
.pct-pos { background: #dcfce7; color: #15803d; }
.pct-neg { background: #fee2e2; color: #b91c1c; }

/* AI Analysis card */
.analysis-card {
    background: #f8fafc;
    border: 1.5px solid #e2e8f0;
    border-radius: 20px;
    padding: 28px 32px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.04);
}
.analysis-section {
    margin-bottom: 20px;
}
.analysis-section-title {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #6366f1;
    margin-bottom: 6px;
}
.analysis-section-body {
    font-size: 15px;
    line-height: 1.7;
    color: #1e293b;
}

/* Divider */
.divider {
    border: none;
    border-top: 1px solid #f1f5f9;
    margin: 8px 0 16px;
}

/* Spinner override */
.stSpinner > div { border-top-color: #6366f1 !important; }

/* Button */
.stButton > button {
    background: linear-gradient(135deg, #6366f1, #3b82f6);
    color: white;
    border: none;
    border-radius: 12px;
    padding: 12px 28px;
    font-size: 15px;
    font-weight: 600;
    letter-spacing: 0.02em;
    width: 100%;
    transition: opacity 0.2s, transform 0.1s;
    box-shadow: 0 4px 14px rgba(99,102,241,0.3);
}
.stButton > button:hover {
    opacity: 0.9;
    transform: translateY(-1px);
}
.stButton > button:active { transform: translateY(0); }

/* Asset pill */
.asset-pill {
    display: inline-block;
    background: #eff6ff;
    color: #1d4ed8;
    border: 1px solid #bfdbfe;
    padding: 4px 12px;
    border-radius: 99px;
    font-size: 12px;
    font-weight: 600;
    margin-right: 6px;
}

/* News ticker */
@keyframes ticker-scroll {
    0%   { transform: translateX(0); }
    100% { transform: translateX(-50%); }
}
.ticker-wrapper {
    width: 100%;
    overflow: hidden;
    background: #f8fafc;
    border: 1.5px solid #e2e8f0;
    border-radius: 14px;
    padding: 10px 0;
    position: relative;
}
.ticker-wrapper::before,
.ticker-wrapper::after {
    content: '';
    position: absolute;
    top: 0; bottom: 0; width: 60px;
    z-index: 2;
    pointer-events: none;
}
.ticker-wrapper::before {
    left: 0;
    background: linear-gradient(to right, #f8fafc, transparent);
}
.ticker-wrapper::after {
    right: 0;
    background: linear-gradient(to left, #f8fafc, transparent);
}
.ticker-track {
    display: inline-flex;
    animation: ticker-scroll 60s linear infinite;
    will-change: transform;
}
.ticker-track:hover { animation-play-state: paused; }
/* Expander */
.stExpander {
    background: #ffffff !important;
    border: 1.5px solid #e2e8f0 !important;
    border-radius: 12px !important;
    margin-top: 10px;
}
.stExpander summary p {
    color: #0f172a !important;
    font-weight: 600 !important;
}
.stExpander [data-testid="stExpanderDetails"] p,
.stExpander [data-testid="stExpanderDetails"] span,
.stExpander [data-testid="stExpanderDetails"] div,
.stExpander [data-testid="stExpanderDetails"] label {
    color: #0f172a !important;
}
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────
def fmt_inr(v: float) -> str:
    sign = "+" if v > 0 else ""
    if abs(v) >= 1_00_00_000:
        return f"{sign}₹{v/1_00_00_000:.2f}Cr"
    if abs(v) >= 1_00_000:
        return f"{sign}₹{v/1_00_000:.2f}L"
    return f"{sign}₹{v:,.0f}"

def parse_analysis(text: str) -> dict:
    """Parse JSON analysis result."""
    import json
    import re
    try:
        clean_text = re.sub(r"```json\s*|\s*```", "", text.strip())
        data = json.loads(clean_text)
        
        # Mapping JSON keys to UI Display Keys if needed
        mapping = {
            "summary": "Summary",
            "primary_driver": "Primary Driver",
            "causal_chain": "Causal Chain",
            "conflicting_signals": "Conflicting Signals",
            "key_risk": "Key Risk",
            "action": "Action"
        }
        
        result = {}
        for k, v in data.items():
            ui_key = mapping.get(k, k.replace("_", " ").title())
            if isinstance(v, list):
                result[ui_key] = "\n".join(v)
            else:
                result[ui_key] = str(v)
        return result
    except:
        # Fallback for old text or failed JSON
        return {"Analysis": text}

def text_to_bullets(text: str, section: str) -> str:
    """Convert a text block into styled HTML."""
    import re

    # Strip stray ## markers
    text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE).strip()

    # ── Causal Chain: numbered step flow ──────────────────────────────────────
    if section == "Causal Chain":
        raw   = re.split(r'\s*(?:\u2192|->)\s*|\n+', text)
        steps = [re.sub(r'^[-*•\d+\.]+\s*', '', s).strip() for s in raw if s.strip()]

        # Separate intro phrase (ends with colon) as italic header
        intro_html = ""
        if steps and steps[0].endswith(':'):
            intro_html = f'<p style="font-size:13px;color:#64748b;font-weight:500;font-style:italic;margin:0 0 14px 0;">{steps[0]}</p>'
            steps = steps[1:]

        STEP_BADGES = {
            "[NEWS]":      ("📰 News",      "#1d4ed8", "#dbeafe"),
            "[SECTOR]":    ("🏭 Sector",    "#7c3aed", "#ede9fe"),
            "[STOCK]":     ("📈 Stock",     "#065f46", "#d1fae5"),
            "[PORTFOLIO]": ("💼 Portfolio", "#92400e", "#fef3c7"),
        }

        if steps:
            steps_html = ""
            for idx, step in enumerate(steps):
                connector = ""
                # Improved connector line
                if idx < len(steps) - 1:
                    connector = f'<div style="margin-left: 17px; border-left: 2px dashed #6366f1; height: 20px; margin-top: -2px; margin-bottom: -2px;"></div>'
                
                badge_html = ""
                for tag, (label, color, bg) in STEP_BADGES.items():
                    if tag in step:
                        step = step.replace(tag, "").strip()
                        badge_html = f'<span style="font-size:10px;font-weight:800;background:{bg};color:{color};border-radius:4px;padding:1px 6px;margin-right:8px;vertical-align:middle;">{label}</span>'
                        break
                
                steps_html += f'''
                <div style="display:flex;align-items:center;gap:12px;margin-bottom:0px;">
                    <div style="width:36px;height:36px;border-radius:8px;background:#000000;color:#ffffff;
                        font-size:16px;font-weight:900;display:flex;align-items:center;
                        justify-content:center;flex-shrink:0;border:2px solid #000000;box-shadow: 2px 2px 0px #6366f1;">{idx+1}</div>
                    <div style="background:#ffffff;border:2px solid #000000;border-radius:8px;
                        padding:12px 16px;font-size:14px;font-weight:600;color:#000000;
                        line-height:1.4;flex:1;box-shadow: 3px 3px 0px rgba(0,0,0,0.05);">
                        {badge_html} {step}
                    </div>
                </div>{connector}'''
            return f'<div style="padding:10px 0;">{intro_html}{steps_html}</div>'
            return f'<div style="padding:4px 0;">{intro_html}{steps_html}</div>'

    # ── Bullet list for all other sections ────────────────────────────────────
    lines   = [re.sub(r'^[-*•]\s*|^\d+\.\s+', '', l).strip() for l in text.split('\n')]
    bullets = [l for l in lines if l]

    if len(bullets) <= 1:
        sentences = re.split(r'(?<=[.!?])\s+', text.strip())
        bullets   = [s.strip() for s in sentences if s.strip()]

    if not bullets:
        return f'<p style="font-size:14px;line-height:1.7;color:#1e293b;margin:0;">{text}</p>'

    items_html = "".join(
        f'<div style="display:flex;align-items:flex-start;gap:10px;margin-bottom:10px;">'
        f'<span style="color:#6366f1;font-size:18px;line-height:1.3;flex-shrink:0;">›</span>'
        f'<span style="font-size:14px;line-height:1.6;color:#1e293b;">{b}</span></div>'
        for b in bullets
    )
    return f'<div style="padding:2px 0;">{items_html}</div>'


SECTION_ICONS = {
    "Summary": "📋",
    "Primary Driver": "🎯",
    "Causal Chain": "🔗",
    "Key Risk": "⚠️",
    "Action": "💡",
    "Analysis": "🤖",
}

PORTFOLIO_META = {
    "PORTFOLIO_001": {"label": "Diversified Portfolio", "owner": "Rahul Sharma",    "icon": "⚖️"},
    "PORTFOLIO_002": {"label": "Sector-Concentrated",   "owner": "Priya Patel",     "icon": "🏦"},
    "PORTFOLIO_003": {"label": "Conservative",          "owner": "Arun Krishnamurthy","icon":"🛡️"},
}


# ── Portfolio selector (top bar — no sidebar) ────────────────────────────────
PORTFOLIO_OPTIONS = {
    f"{v['icon']} {v['label']} — {v['owner']}": k
    for k, v in PORTFOLIO_META.items()
}

top_l, top_m, top_r = st.columns([3, 2, 1])
with top_l:
    st.markdown("""
    <div style="display:flex;align-items:center;gap:10px;padding:8px 0 16px;">
        <span style="font-size:24px;font-weight:800;color:#0f172a;letter-spacing:-0.5px;">🏦 DalalAI</span>
        <span style="font-size:12px;color:#94a3b8;font-weight:500;">Financial Advisor Agent</span>
    </div>
    """, unsafe_allow_html=True)
with top_m:
    selected_label = st.selectbox(
        "Portfolio",
        list(PORTFOLIO_OPTIONS.keys()),
        label_visibility="collapsed"
    )
with top_r:
    run_btn = st.button("🤖 Run Analysis", use_container_width=True)

selected_id = PORTFOLIO_OPTIONS[selected_label]
meta = PORTFOLIO_META[selected_id]

st.markdown("<hr style='border:none;border-top:1.5px solid #e2e8f0;margin:0 0 20px;'>", unsafe_allow_html=True)


# ── Load data ─────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_analytics(portfolio_id: str):
    try:
        response = requests.get(f"{API_BASE_URL}/portfolio/{portfolio_id}")
        response.raise_for_status()
        data = response.json()
        return (
            data["analytics"], 
            data["market"], 
            data["sectors"], 
            data["news"], 
            data["historical"]
        )
    except Exception as e:
        st.error(f"Failed to fetch data from API: {str(e)}")
        return None, None, None, None, None


analytics, market, sectors, news, historical = load_analytics(selected_id)

if analytics is None:
    st.error("Could not connect to the DalalAI API. Please ensure the server is running.")
    st.stop()

pnl        = analytics["total_daily_pnl"]
pnl_pct    = analytics["daily_pnl_percent"]
port_value = analytics["total_current_value"]
is_pos     = pnl >= 0
pnl_class  = "positive" if is_pos else "negative"
pnl_sign   = "+" if is_pos else ""
sentiment  = market["market_sentiment"]
sent_color = {"BULLISH": "#16a34a", "BEARISH": "#dc2626", "NEUTRAL": "#64748b"}.get(sentiment, "#64748b")
sent_bg    = {"BULLISH": "#dcfce7", "BEARISH": "#fee2e2", "NEUTRAL": "#f1f5f9"}.get(sentiment, "#f1f5f9")
sent_icon  = {"BULLISH": "📈", "BEARISH": "📉", "NEUTRAL": "➡️"}.get(sentiment, "➡️")
avg_chg    = market.get("average_change_percent", 0)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="margin-bottom:24px;">
    <div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap;">
        <div>
            <div style="font-size:28px;font-weight:800;color:#0f172a;letter-spacing:-0.5px;">
                {meta['icon']} {meta['label']}
            </div>
            <div style="font-size:14px;color:#64748b;margin-top:2px;">
                {meta['owner']} &nbsp;·&nbsp; <span style="color:{sent_color};font-weight:600;">Market: {sentiment}</span>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ── KPI Row ───────────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Portfolio Value</div>
        <div class="metric-value">₹{port_value/1_00_000:.2f}L</div>
        <div class="metric-sub neutral">Total Current Value</div>
    </div>""", unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Daily P&amp;L</div>
        <div class="metric-value {pnl_class}">{fmt_inr(pnl)}</div>
        <div class="metric-sub {pnl_class}">{pnl_sign}{pnl_pct:.2f}% today</div>
    </div>""", unsafe_allow_html=True)

with c3:
    ab = analytics["asset_breakdown"]
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Asset Mix</div>
        <div class="metric-value" style="font-size:20px;padding-top:4px;">
            <span class="asset-pill">Stocks {ab['stocks']}%</span>
            <span class="asset-pill" style="background:#f0fdf4;color:#15803d;border-color:#86efac;">MF {ab['mutual_funds']}%</span>
        </div>
        <div class="metric-sub neutral">{analytics['risk_profile']} risk profile</div>
    </div>""", unsafe_allow_html=True)

with c4:
    risks = analytics["risks"]
    risk_level = "✅ No Concentration Risk" if not risks else risks[0].split(":")[0]
    risk_card_class = "positive" if not risks else ("negative" if "CRITICAL" in (risks[0] if risks else "") else "neutral")
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Risk Alert</div>
        <div class="metric-value" style="font-size:18px;padding-top:6px;" class="{risk_card_class}">
            {'⚠️ ' + risks[0].split(':')[0] if risks else '✅ All Clear'}
        </div>
        <div class="metric-sub {risk_card_class}">{len(risks)} risk(s) detected</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

# ── Historical Trends Section ────────────────────────────────────────────────
st.markdown('<div class="section-title">7-Day Market Trends</div>', unsafe_allow_html=True)
tr1, tr2, tr3, tr4 = st.columns(4)

trends = historical.get("market_trend", {})
fii_obs = historical.get("fii_dii_observations", "N/A")

with tr1:
    val = trends.get("NIFTY50", 0)
    cls = "positive" if val >= 0 else "negative"
    st.markdown(f"""<div class="metric-card"><div class="metric-label">Nifty50 (7D)</div><div class="metric-value {cls}">{val:+.2f}%</div><div class="metric-sub neutral">Cumulative Trend</div></div>""", unsafe_allow_html=True)
with tr2:
    val = trends.get("SENSEX", 0)
    cls = "positive" if val >= 0 else "negative"
    st.markdown(f"""<div class="metric-card"><div class="metric-label">Sensex (7D)</div><div class="metric-value {cls}">{val:+.2f}%</div><div class="metric-sub neutral">Cumulative Trend</div></div>""", unsafe_allow_html=True)
with tr3:
    st.markdown(f"""<div class="metric-card"><div class="metric-label">Sentiment</div><div class="metric-value" style="font-size:20px; color:#6366f1;">{historical.get('market_sentiment', 'NEUTRAL')}</div><div class="metric-sub neutral">Market Breadth</div></div>""", unsafe_allow_html=True)
with tr4:
    st.markdown(f"""<div class="metric-card"><div class="metric-label">FII/DII Flow</div><div class="metric-value" style="font-size:14px; line-height:1.3; padding-top:4px;">{fii_obs[:60]}...</div><div class="metric-sub neutral">Observation</div></div>""", unsafe_allow_html=True)

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)


# ── Middle: Sector + Movers ───────────────────────────────────────────────────
left, right = st.columns([3, 2], gap="large")

with left:
    st.markdown('<div class="section-title">Sector Exposure</div>', unsafe_allow_html=True)
    sector_alloc = analytics["sector_allocation_percent"]
    for sector, pct in sorted(sector_alloc.items(), key=lambda x: -x[1]):
        is_risky = pct > 40
        bar_class = "bar-fill-risk" if is_risky else "bar-fill"
        risk_label = ' <span style="font-size:11px;color:#dc2626;font-weight:700;">⚠ HIGH</span>' if is_risky else ""
        st.markdown(f"""
        <div class="sector-row">
            <div class="sector-name">
                <span>{sector}{risk_label}</span>
                <span style="font-weight:700;">{pct}%</span>
            </div>
            <div class="bar-track">
                <div class="{bar_class}" style="width:{min(pct,100)}%;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Risk alerts
    if risks:
        st.markdown('<div class="section-title" style="margin-top:20px;">Risk Alerts</div>', unsafe_allow_html=True)
        for r in risks:
            level = "risk-critical" if "CRITICAL" in r else "risk-high"
            st.markdown(f'<span class="risk-badge {level}">{r}</span>', unsafe_allow_html=True)

with right:
    st.markdown('<div class="section-title">Top Gainers</div>', unsafe_allow_html=True)
    for s in analytics["top_gainers"]:
        chg = s["change_pct"]
        st.markdown(f"""
        <div class="mover-row">
            <span class="mover-symbol">{s['symbol']}</span>
            <span class="mover-pct pct-pos">+{chg:.2f}%</span>
        </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-title" style="margin-top:20px;">Top Losers</div>', unsafe_allow_html=True)
    for s in analytics["top_losers"]:
        chg = s["change_pct"]
        st.markdown(f"""
        <div class="mover-row">
            <span class="mover-symbol">{s['symbol']}</span>
            <span class="mover-pct pct-neg">{chg:.2f}%</span>
        </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-title" style="margin-top:20px;">Market Indices</div>', unsafe_allow_html=True)
    for idx, chg in market.get("important_indices", {}).items():
        cls = "pct-pos" if chg >= 0 else "pct-neg"
        sign = "+" if chg >= 0 else ""
        st.markdown(f"""
        <div class="mover-row">
            <span class="mover-symbol" style="font-size:13px;">{idx}</span>
            <span class="mover-pct {cls}" style="font-size:13px;">{sign}{chg:.2f}%</span>
        </div>""", unsafe_allow_html=True)


# ── Relevant News Ticker ──────────────────────────────────────────────────────
st.markdown("---")
st.markdown('<div class="section-title">Relevant Market News</div>', unsafe_allow_html=True)

IMPACT_STYLE = {
    "HIGH":   ("🔴", "#fee2e2", "#b91c1c", "#fca5a5"),
    "MEDIUM": ("🟡", "#fef9c3", "#92400e", "#fde68a"),
    "LOW":    ("🟢", "#dcfce7", "#166534", "#86efac"),
}
SCOPE_STYLE = {
    "MARKET_WIDE":     ("🌐", "#eff6ff", "#1d4ed8"),
    "SECTOR_SPECIFIC": ("🏭", "#f0fdf4", "#15803d"),
    "STOCK_SPECIFIC":  ("📌", "#faf5ff", "#7c3aed"),
}
SENT_COLOR = lambda s: "#16a34a" if s > 0.1 else ("#dc2626" if s < -0.1 else "#64748b")
SENT_LABEL = lambda s: "▲ Positive" if s > 0.1 else ("▼ Negative" if s < -0.1 else "● Neutral")

def build_ticker_item(n):
    impact  = n.get("impact_level", "LOW")
    scope   = n.get("scope", "MARKET_WIDE")
    headline= n.get("headline", "")
    score   = n.get("sentiment_score", 0)
    entities= n.get("entities", {})
    sectors_hit = ", ".join(entities.get("sectors", [])[:1]) or "Market"

    imp_icon, imp_bg, imp_text, imp_border = IMPACT_STYLE.get(impact, IMPACT_STYLE["LOW"])
    scope_icon, _, scope_text = SCOPE_STYLE.get(scope, SCOPE_STYLE["MARKET_WIDE"])
    sent_color = SENT_COLOR(score)
    sent_label = SENT_LABEL(score)

    return f"""
    <div style="
        display:inline-flex;align-items:center;gap:10px;
        background:#ffffff;border:1.5px solid #e2e8f0;
        border-radius:12px;padding:10px 18px;
        margin-right:16px;white-space:nowrap;
        box-shadow:0 1px 4px rgba(0,0,0,0.05);
        flex-shrink:0;
    ">
        <span style="background:{imp_bg};color:{imp_text};border:1px solid {imp_border};
            font-size:11px;font-weight:700;padding:2px 8px;border-radius:99px;">
            {imp_icon} {impact}
        </span>
        <span style="font-size:13px;font-weight:600;color:#0f172a;white-space:nowrap;">
            {headline}
        </span>
        <span style="font-size:11px;color:#94a3b8;">| {scope_icon} {sectors_hit}</span>
        <span style="font-size:12px;font-weight:700;color:{sent_color};">{sent_label} ({score:+.2f})</span>
    </div>"""

# Build items HTML (duplicate for seamless loop) — use ALL news, not just filtered
all_news = news  # portfolio-relevant top 7 from analyze_relevant_news()
items_html = "".join(build_ticker_item(n) for n in all_news)
items_html_doubled = items_html + items_html  # duplicate for seamless infinite loop

ticker_speed = len(all_news) * 12  # ~12s per item for comfortable reading

st.markdown(
    f'<div class="ticker-wrapper"><div class="ticker-track">{items_html_doubled}</div></div>',
    unsafe_allow_html=True
)


# ── AI Analysis Section ───────────────────────────────────────────────────────
st.markdown("---")

ai_title_col, ai_btn_col = st.columns([5, 1])
with ai_title_col:
    title_placeholder = st.empty()
    score_html = ""
    if st.session_state.get("eval_result"):
        score = st.session_state.eval_result.get("mixed_score", 0)
        score_html = f'<span style="margin-left:12px;font-size:12px;font-weight:700;background:#dcfce7;color:#166534;padding:4px 10px;border-radius:99px;border:1px solid #bbf7d0;">Confidence: {score}%</span>'
    title_placeholder.markdown(f'<div class="section-title" style="display:flex;align-items:center;">AI Reasoning Engine {score_html}</div>', unsafe_allow_html=True)
with ai_btn_col:
    inline_run_btn = st.button("🤖 Run Analysis", key="inline_run", use_container_width=True)

if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None
if "eval_result" not in st.session_state:
    st.session_state.eval_result = None
if "last_portfolio" not in st.session_state:
    st.session_state.last_portfolio = None

# Auto-clear if portfolio switched
if st.session_state.last_portfolio != selected_id:
    st.session_state.analysis_result = None
    st.session_state.eval_result = None
    st.session_state.last_portfolio = selected_id

if run_btn or inline_run_btn:
    logger.info(f"Streamlit UI: Analysis started for portfolio {selected_id}")
    with st.spinner("Agent is reasoning through your portfolio..."):
        try:
            response = requests.post(
                f"{API_BASE_URL}/analyze",
                json={"portfolio_id": selected_id}
            )
            response.raise_for_status()
            api_result = response.json()
            
            # The API returns 'analysis' as a dict or string, and 'evaluation' as a dict
            st.session_state.analysis_result = api_result["analysis"]
            st.session_state.eval_result = api_result["evaluation"]
            
            logger.info(f"Streamlit UI: Analysis complete.")
            
            # Update title placeholder with new score immediately
            score = st.session_state.eval_result.get("mixed_score", 0)
            score_html = f'<span style="margin-left:12px;font-size:12px;font-weight:700;background:#dcfce7;color:#166534;padding:4px 10px;border-radius:99px;border:1px solid #bbf7d0;">Confidence: {score}%</span>'
            title_placeholder.markdown(f'<div class="section-title" style="display:flex;align-items:center;">AI Reasoning Engine {score_html}</div>', unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Analysis failed: {str(e)}")

if st.session_state.analysis_result:
    # If analysis_result is already a dict (from API), we don't need to parse it
    if isinstance(st.session_state.analysis_result, dict):
        sections = {}
        mapping = {
            "summary": "Summary",
            "primary_driver": "Primary Driver",
            "causal_chain": "Causal Chain",
            "conflicting_signals": "Conflicting Signals",
            "key_risk": "Key Risk",
            "action": "Action"
        }
        for k, v in st.session_state.analysis_result.items():
            ui_key = mapping.get(k, k.replace("_", " ").title())
            if isinstance(v, list):
                sections[ui_key] = "\n".join(v)
            else:
                sections[ui_key] = str(v)
    else:
        sections = parse_analysis(st.session_state.analysis_result)

    CARD_STYLES = {
        "Summary":              ("📋", "#6366f1", "#eff6ff"),
        "Primary Driver":       ("🎯", "#0ea5e9", "#f0f9ff"),
        "Causal Chain":         ("🔗", "#8b5cf6", "#faf5ff"),
        "Conflicting Signals":  ("⚡", "#f59e0b", "#fffbeb"),
        "Key Risk":             ("⚠️",  "#ef4444", "#fef2f2"),
        "Action":               ("💡", "#16a34a", "#f0fdf4"),
        "Analysis":             ("🤖", "#6366f1", "#eff6ff"),
    }

    for title, body in sections.items():
        if "Self-Evaluation" in title or "Self Score" in title or "Justification" in title:
            continue
            
        icon, accent, _ = CARD_STYLES.get(title, ("•", "#6366f1", "#ffffff"))
        formatted_body = text_to_bullets(body, title)
        st.markdown(f"""
        <div style="
            background: #ffffff;
            border: 3px solid #000000;
            border-left: 8px solid #000000;
            border-radius: 12px;
            padding: 24px 28px;
            margin-bottom: 20px;
            box-shadow: 6px 6px 0px rgba(0, 0, 0, 1);
            word-wrap: break-word;
            overflow-wrap: break-word;
            min-height: fit-content;
        ">
            <div style="
                font-size: 16px; font-weight: 900; letter-spacing: 0.1em;
                text-transform: uppercase; color: #000000; margin-bottom: 16px;
                display: flex; align-items: center; gap: 10px;
            ">
                <span style="font-size: 22px;">{icon}</span> {title}
            </div>
            <div style="font-size:15px;line-height:1.7;color:#000000;font-weight:600;">
                {formatted_body}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── AI Self-Reflection Card (Compliance & Confidence) ─────────────────────
    ev = st.session_state.eval_result
    if ev:
        st.markdown("---")
        with st.expander("🔍 Reasoning Evaluation & Compliance", expanded=False):
            c1, c2 = st.columns([1, 2])
            with c1:
                st.metric("Overall Confidence", f"{ev.get('mixed_score', 0)}%")
            with c2:
                st.markdown(f"**AI Justification:** *\"{ev.get('justification', 'N/A')}\"*")
            
            st.markdown("---")
            st.markdown("**Compliance Checks:**")
            check_cols = st.columns(2)
            for i, (name, passed, reason) in enumerate(ev.get("checks", [])):
                icon = "✅" if passed else "❌"
                with check_cols[i % 2]:
                    st.markdown(f"{icon} **{name.title()}**: {reason}")

else:
    st.markdown("""
    <div style="
        background: #f8fafc;
        border: 1.5px dashed #cbd5e1;
        border-radius: 20px;
        padding: 48px 32px;
        text-align: center;
        color: #94a3b8;
    ">
        <div style="font-size:40px;margin-bottom:12px;">🤖</div>
        <div style="font-size:16px;font-weight:600;color:#64748b;">No analysis yet</div>
        <div style="font-size:13px;margin-top:6px;">Click <strong>"Run AI Analysis"</strong> in the sidebar to generate causal reasoning for this portfolio.</div>
    </div>
    """, unsafe_allow_html=True)


# ── Floating Chat Widget (AskDisha style) ────────────────────────────────────
chat_widget_html = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html, body {{
    margin: 0; padding: 0;
    background: transparent !important;
    overflow: hidden;
    width: 100%; height: 100%;
    pointer-events: none;
    font-family: 'Inter', sans-serif;
}}
#dalal-fab, #dalal-fab-label, #dalal-chat {{ pointer-events: auto; }}

#dalal-fab {{
    position: absolute; bottom: 12px; left: 12px;
    width: 64px; height: 64px; border-radius: 50%;
    background: linear-gradient(135deg, #6366f1, #3b82f6);
    color: #fff; border: none; cursor: pointer;
    box-shadow: 0 6px 24px rgba(99,102,241,0.45);
    display: flex; align-items: center; justify-content: center;
    font-size: 28px; transition: transform 0.2s, box-shadow 0.2s; z-index: 10;
}}
#dalal-fab:hover {{ transform: scale(1.1); box-shadow: 0 8px 30px rgba(99,102,241,0.55); }}

#dalal-fab-label {{
    position: absolute; bottom: 24px; left: 84px;
    background: #0f172a; color: #fff; padding: 8px 16px;
    border-radius: 20px; font-size: 13px; font-weight: 600;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    pointer-events: none; white-space: nowrap; z-index: 10;
}}

#dalal-chat {{
    position: absolute; bottom: 12px; left: 12px;
    width: 390px; height: 520px; background: #ffffff;
    border-radius: 20px; border: 2px solid #e2e8f0;
    box-shadow: 0 12px 48px rgba(0,0,0,0.18);
    display: none; flex-direction: column; overflow: hidden; z-index: 10;
}}
#dalal-chat.open {{ display: flex; }}

#dalal-chat-header {{
    background: linear-gradient(135deg, #6366f1, #3b82f6);
    color: #fff; padding: 16px 20px;
    display: flex; align-items: center; justify-content: space-between; flex-shrink: 0;
}}
#dalal-chat-header .hdr-left {{ display: flex; align-items: center; gap: 10px; }}
#dalal-chat-header .hdr-left .avatar {{
    width: 36px; height: 36px; background: rgba(255,255,255,0.2);
    border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 20px;
}}
#dalal-chat-header .hdr-title {{ font-size: 16px; font-weight: 700; }}
#dalal-chat-header .hdr-sub {{ font-size: 11px; opacity: 0.85; }}
#dalal-chat-close {{
    background: rgba(255,255,255,0.2); border: none; color: #fff;
    width: 32px; height: 32px; border-radius: 50%; cursor: pointer;
    font-size: 18px; display: flex; align-items: center; justify-content: center;
}}
#dalal-chat-close:hover {{ background: rgba(255,255,255,0.35); }}

#dalal-chat-body {{
    flex: 1; overflow-y: auto; padding: 16px;
    display: flex; flex-direction: column; gap: 12px; background: #f8fafc;
}}

.msg-row {{ display: flex; gap: 8px; max-width: 88%; }}
.msg-row.user {{ align-self: flex-end; flex-direction: row-reverse; }}
.msg-row.bot {{ align-self: flex-start; }}
.msg-bubble {{
    padding: 10px 16px; border-radius: 16px;
    font-size: 14px; line-height: 1.55; word-wrap: break-word;
}}
.msg-row.user .msg-bubble {{
    background: linear-gradient(135deg, #6366f1, #3b82f6);
    color: #fff; border-bottom-right-radius: 4px;
}}
.msg-row.bot .msg-bubble {{
    background: #ffffff; color: #0f172a;
    border: 1px solid #e2e8f0; border-bottom-left-radius: 4px;
}}
.msg-time {{ font-size: 10px; color: #94a3b8; margin-top: 4px; text-align: right; }}
.msg-row.bot .msg-time {{ text-align: left; }}

.typing-dots {{ display: inline-flex; gap: 4px; padding: 12px 16px; }}
.typing-dots span {{
    width: 8px; height: 8px; border-radius: 50%; background: #94a3b8;
    animation: bounce 1.4s infinite ease-in-out;
}}
.typing-dots span:nth-child(2) {{ animation-delay: 0.2s; }}
.typing-dots span:nth-child(3) {{ animation-delay: 0.4s; }}
@keyframes bounce {{ 0%,80%,100% {{ transform: scale(0); }} 40% {{ transform: scale(1); }} }}

#dalal-chat-footer {{
    padding: 12px 16px; border-top: 1px solid #e2e8f0;
    display: flex; gap: 8px; background: #fff; flex-shrink: 0;
}}
#dalal-chat-input {{
    flex: 1; border: 1.5px solid #e2e8f0; border-radius: 24px;
    padding: 10px 18px; font-size: 14px; font-family: 'Inter', sans-serif;
    outline: none; color: #0f172a;
}}
#dalal-chat-input:focus {{ border-color: #6366f1; }}
#dalal-chat-send {{
    width: 40px; height: 40px; border-radius: 50%;
    background: linear-gradient(135deg, #6366f1, #3b82f6);
    border: none; color: #fff; cursor: pointer;
    display: flex; align-items: center; justify-content: center;
    font-size: 18px; flex-shrink: 0;
}}
#dalal-chat-send:hover {{ transform: scale(1.08); }}
</style>

<div id="dalal-fab-label">Ask DalalAI</div>
<button id="dalal-fab" onclick="toggleChat()">\U0001f4ac</button>

<div id="dalal-chat">
    <div id="dalal-chat-header">
        <div class="hdr-left">
            <div class="avatar">\U0001f916</div>
            <div>
                <div class="hdr-title">DalalAI</div>
                <div class="hdr-sub">Financial Advisor Agent</div>
            </div>
        </div>
        <button id="dalal-chat-close" onclick="toggleChat()">&times;</button>
    </div>
    <div id="dalal-chat-body">
        <div class="msg-row bot">
            <div>
                <div class="msg-bubble">Hi! I'm DalalAI \U0001f44b Ask me anything about your portfolio, stocks, mutual funds, or markets.</div>
            </div>
        </div>
    </div>
    <div id="dalal-chat-footer">
        <input id="dalal-chat-input" type="text" placeholder="Type your question..." onkeydown="if(event.key==='Enter')sendMsg()" />
        <button id="dalal-chat-send" onclick="sendMsg()">&#10148;</button>
    </div>
</div>

<script>
const frame = window.frameElement;
function resizeFrame(wide) {{
    if (!frame) return;
    if (wide) {{
        frame.style.cssText = 'position:fixed!important;bottom:0!important;left:0!important;z-index:99999!important;width:420px!important;height:560px!important;border:none!important;background:transparent!important;';
    }} else {{
        frame.style.cssText = 'position:fixed!important;bottom:0!important;left:0!important;z-index:99999!important;width:200px!important;height:100px!important;border:none!important;background:transparent!important;';
    }}
}}
resizeFrame(false);

const API_URL = "{API_BASE_URL}";
const PORTFOLIO_ID = "{selected_id}";
let chatHistory = [];
let chatOpen = false;

function toggleChat() {{
    chatOpen = !chatOpen;
    resizeFrame(chatOpen);
    document.getElementById('dalal-chat').classList.toggle('open', chatOpen);
    document.getElementById('dalal-fab').style.display = chatOpen ? 'none' : 'flex';
    document.getElementById('dalal-fab-label').style.display = chatOpen ? 'none' : 'block';
    if (chatOpen) document.getElementById('dalal-chat-input').focus();
}}

function getTime() {{
    return new Date().toLocaleTimeString([], {{hour: '2-digit', minute:'2-digit'}});
}}

function mdToHtml(t) {{
    t = t.replace(/\\n/g, '<br>');
    t = t.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    t = t.replace(/\*(.+?)\*/g, '<em>$1</em>');
    t = t.replace(/(?:^|<br>)\s*[\*\-]\s+/g, '<br>• ');
    t = t.replace(/`([^`]+)`/g, '<code style="background:#e2e8f0;padding:2px 6px;border-radius:4px;font-size:13px;">$1</code>');
    return t;
}}

function appendMsg(role, text) {{
    const body = document.getElementById('dalal-chat-body');
    const row = document.createElement('div');
    row.className = 'msg-row ' + role;
    const rendered = role === 'bot' ? mdToHtml(text) : text.replace(/\\n/g,'<br>');
    row.innerHTML = '<div><div class="msg-bubble">' + rendered + '</div><div class="msg-time">' + getTime() + '</div></div>';
    body.appendChild(row);
    body.scrollTop = body.scrollHeight;
}}

function showTyping() {{
    const body = document.getElementById('dalal-chat-body');
    const row = document.createElement('div');
    row.className = 'msg-row bot';
    row.id = 'typing-indicator';
    row.innerHTML = '<div><div class="msg-bubble"><div class="typing-dots"><span></span><span></span><span></span></div></div></div>';
    body.appendChild(row);
    body.scrollTop = body.scrollHeight;
}}

function removeTyping() {{
    const el = document.getElementById('typing-indicator');
    if (el) el.remove();
}}

async function sendMsg() {{
    const input = document.getElementById('dalal-chat-input');
    const text = input.value.trim();
    if (!text) return;
    input.value = '';
    appendMsg('user', text);
    chatHistory.push({{role: 'user', content: text}});
    showTyping();
    try {{
        const res = await fetch(API_URL + '/chat', {{
            method: 'POST',
            headers: {{'Content-Type': 'application/json'}},
            body: JSON.stringify({{
                message: text,
                portfolio_id: PORTFOLIO_ID,
                chat_history: chatHistory.slice(-10)
            }})
        }});
        const data = await res.json();
        removeTyping();
        const reply = data.reply || 'Sorry, something went wrong.';
        appendMsg('bot', reply);
        chatHistory.push({{role: 'assistant', content: reply}});
    }} catch (e) {{
        removeTyping();
        appendMsg('bot', 'Could not connect to DalalAI server. Make sure server.py is running.');
    }}
}}
</script>
"""

components.html(chat_widget_html, height=600, scrolling=False)
