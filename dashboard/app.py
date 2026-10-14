from pathlib import Path
import sqlite3
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# ================================================================
# IPL BOWLING INTELLIGENCE — ADVANCED UI · Domain B
# Two tabs, exactly 3 KPI cards + 5 charts on each tab.
# Each chart has its OWN filter expander. Displayed figures come from SQL/q().
# Cricket animation layer: bowling-delivery scene, ticker, floating balls,
# bat-swing title, spinning-ball KPI icons.
# ================================================================
st.set_page_config(page_title="IPL Bowling Intelligence | Pro Analytics", page_icon="🏏", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

:root {
  color-scheme: dark;
  --bg: #07111f;
  --panel: rgba(15, 34, 56, .88);
  --panel-border: rgba(124, 178, 220, .24);
  --text: #eff7ff;
  --muted: #9bb4cc;
  --cyan: #38d9f5;
  --mint: #47e4b8;
  --purple: #b39aff;
  --orange: #ffbd72;
  --pink: #ff78b7;
  --lime: #d6f36a;
}

html, body, [class*="css"] { font-family: Inter, sans-serif; }
.stApp {
  background:
    radial-gradient(ellipse at 4% 0%, rgba(24, 135, 190, .27), transparent 32%),
    radial-gradient(ellipse at 96% 6%, rgba(133, 76, 222, .19), transparent 29%),
    radial-gradient(ellipse at 52% 100%, rgba(15, 112, 119, .13), transparent 35%),
    linear-gradient(145deg, #06101d 0%, #0a192b 48%, #07111f 100%);
  background-size: 150% 150%;
  animation: backgroundDrift 24s ease-in-out infinite alternate;
  color: var(--text);
}
[data-testid="stHeader"] { background: rgba(7,17,31,.42); }
.block-container { max-width: 1720px; padding-top: 1.4rem; padding-bottom: 3.2rem; position: relative; z-index: 1; }
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #102943 0%, #0a1a2c 54%, #071321 100%);
  border-right: 1px solid var(--panel-border);
  box-shadow: 12px 0 40px rgba(0,0,0,.14);
}
[data-testid="stSidebar"] * { color: var(--text); }
h1,h2,h3,h4,p,label { color: var(--text); }
h2, h3 { letter-spacing: -.45px; }

.eyebrow {
  display: inline-block; color: var(--mint); font-size: .70rem; font-weight: 900;
  letter-spacing: 2.4px; text-transform: uppercase; padding: 6px 10px;
  border: 1px solid rgba(71,228,184,.2); border-radius: 999px;
  background: rgba(71,228,184,.06); margin-bottom: 7px;
}
.hero-row { display: flex; align-items: center; gap: 14px; margin: .35rem 0 .6rem; }
.hero-title {
  font-size: clamp(2.1rem, 4vw, 3.25rem); font-weight: 900;
  letter-spacing: -1.8px; line-height: 1.08; margin: 0;
  background: linear-gradient(100deg, #ffffff 0%, #9ff4ff 38%, #b7a5ff 70%, #ff9fcf 100%);
  background-size: 220% auto; -webkit-background-clip: text; background-clip: text; color: transparent;
  animation: titleShimmer 9s linear infinite;
}
.bat {
  display: inline-block; font-size: clamp(2.1rem, 4vw, 3.1rem); line-height: 1;
  transform-origin: 78% 92%; animation: batSwing 3.6s ease-in-out infinite;
  filter: drop-shadow(0 4px 10px rgba(0,0,0,.35));
}
.subtitle { color: #b6cbe0; font-size: 1rem; margin-bottom: .4rem; }
.reader {
  background: linear-gradient(105deg, rgba(71,228,184,.12), rgba(56,217,245,.09), rgba(179,154,255,.10));
  border: 1px solid rgba(91,220,215,.30); border-left: 4px solid var(--mint);
  border-radius: 15px; padding: 15px 19px; margin: 18px 0 24px;
  box-shadow: 0 12px 34px rgba(0,0,0,.16); animation: riseIn .55s ease both;
}
.section-label {
  color: var(--cyan); font-size: .72rem; font-weight: 900; letter-spacing: 1.8px;
  text-transform: uppercase; margin: .45rem 0 .9rem; padding: 8px 11px;
  border-left: 3px solid var(--cyan); border-radius: 0 9px 9px 0;
  background: linear-gradient(90deg, rgba(56,217,245,.09), transparent 75%);
}
.section-label::before {
  content: ""; display: inline-block; width: 10px; height: 10px; border-radius: 50%;
  background: radial-gradient(circle at 30% 30%, #ff8a80, #c62828); margin-right: 9px; vertical-align: -1px;
  box-shadow: 0 0 8px rgba(255,80,80,.55); animation: ballPulse 2.4s ease-in-out infinite;
}

/* ---------- CRICKET LAYER: floating balls ---------- */
.ball-field { position: fixed; inset: 0; pointer-events: none; z-index: 0; overflow: hidden; }
.ball-field span {
  position: absolute; bottom: -50px; border-radius: 50%; opacity: 0;
  background: radial-gradient(circle at 30% 28%, #ff8a80 0%, #d32f2f 45%, #7f0f17 100%);
  box-shadow: inset -2px -2px 4px rgba(0,0,0,.35);
  animation: ballFloat linear infinite;
}
.ball-field span::before {
  content: ""; position: absolute; left: 50%; top: 10%; bottom: 10%; width: 0;
  border-left: 1.5px dashed rgba(255,255,255,.7); transform: translateX(-50%);
}
.ball-field span:nth-child(1) { left: 6%;  width: 16px; height: 16px; animation-duration: 26s; animation-delay: 0s; }
.ball-field span:nth-child(2) { left: 22%; width: 22px; height: 22px; animation-duration: 34s; animation-delay: 6s; }
.ball-field span:nth-child(3) { left: 41%; width: 14px; height: 14px; animation-duration: 29s; animation-delay: 12s; }
.ball-field span:nth-child(4) { left: 63%; width: 20px; height: 20px; animation-duration: 37s; animation-delay: 3s; }
.ball-field span:nth-child(5) { left: 80%; width: 15px; height: 15px; animation-duration: 31s; animation-delay: 15s; }
.ball-field span:nth-child(6) { left: 93%; width: 19px; height: 19px; animation-duration: 40s; animation-delay: 9s; }

/* ---------- CRICKET LAYER: bowling delivery scene ---------- */
.pitch-scene {
  position: relative; height: 138px; margin: 14px 0 8px; border-radius: 18px; overflow: hidden;
  border: 1px solid rgba(71,228,184,.28);
  background:
    repeating-linear-gradient(90deg, rgba(34,139,84,.34) 0 60px, rgba(26,115,70,.34) 60px 120px),
    linear-gradient(180deg, #0b2a22, #0a3a2a);
  box-shadow: 0 12px 34px rgba(0,0,0,.22);
}
.pitch-strip {
  position: absolute; left: 7%; right: 7%; bottom: 18px; height: 36px; border-radius: 6px;
  background: linear-gradient(180deg, #d9b980, #b8925a); opacity: .88;
  box-shadow: inset 0 0 18px rgba(0,0,0,.28);
}
.crease { position: absolute; bottom: 18px; height: 36px; width: 2px; background: rgba(255,255,255,.85); }
.crease.c1 { left: 12%; } .crease.c2 { right: 12%; }
.runner { position: absolute; left: 4%; bottom: 24px; font-size: 28px; animation: runUp 6s ease-in-out infinite; }
.batter { position: absolute; right: 15.5%; bottom: 22px; font-size: 28px; transform-origin: 80% 90%; animation: batterSwing 6s ease-in-out infinite; }
.stumps {
  position: absolute; bottom: 22px; right: 11%; width: 30px; height: 48px;
  display: flex; justify-content: space-between; align-items: flex-end;
  transform-origin: bottom center; animation: stumpWobble 6s linear infinite;
}
.stump { width: 4px; height: 46px; background: #f4e6c4; border-radius: 2px; box-shadow: 0 0 6px rgba(255,230,160,.35); }
.bail { position: absolute; top: 0; height: 3px; width: 12px; background: #ffd166; border-radius: 2px; }
.bail.b1 { left: 2px;  animation: bailL 6s ease-out infinite; }
.bail.b2 { right: 2px; animation: bailR 6s ease-out infinite; }
.ball {
  position: absolute; width: 20px; height: 20px; border-radius: 50%; left: 9%; bottom: 92px; opacity: 0;
  background: radial-gradient(circle at 30% 28%, #ff8a80 0%, #d32f2f 45%, #7f0f17 100%);
  box-shadow: 0 0 12px rgba(255,70,70,.55), inset -2px -2px 4px rgba(0,0,0,.35);
  animation: bowl 6s linear infinite;
}
.ball::before {
  content: ""; position: absolute; left: 50%; top: 8%; bottom: 8%; width: 0; margin-left: -1px;
  border-left: 2px dashed rgba(255,255,255,.85); border-radius: 50%; animation: seamSpin .45s linear infinite;
}
.ball::after {
  content: ""; position: absolute; right: 16px; top: 8px; width: 46px; height: 4px; border-radius: 4px;
  background: linear-gradient(270deg, rgba(255,90,90,.55), transparent);
}
.wicket-pop {
  position: absolute; right: 19%; top: 14px; font-weight: 900; letter-spacing: 3px; font-size: 1.05rem;
  color: #ffd166; text-shadow: 0 0 14px rgba(255,209,102,.6); opacity: 0; animation: wicketPop 6s ease-out infinite;
}
.scene-tag {
  position: absolute; left: 14px; top: 10px; font-size: .64rem; font-weight: 900; letter-spacing: 2px;
  color: rgba(239,247,255,.78); text-transform: uppercase;
}

/* ---------- CRICKET LAYER: scoreboard ticker ---------- */
.ticker {
  overflow: hidden; white-space: nowrap; border: 1px solid var(--panel-border); border-radius: 12px;
  background: rgba(8,23,39,.78); padding: 9px 0; margin: 6px 0 4px;
}
.ticker-track { display: inline-block; animation: tickerMove 42s linear infinite; }
.ticker:hover .ticker-track { animation-play-state: paused; }
.ticker-track span {
  display: inline-block; margin: 0 26px; color: #b6cbe0; font-size: .74rem; font-weight: 800;
  letter-spacing: 1.4px; text-transform: uppercase;
}
.ticker-track span b { color: var(--mint); }

.metric-box {
  position: relative; overflow: hidden; isolation: isolate;
  background: linear-gradient(145deg, rgba(25,56,85,.97), rgba(10,27,46,.97));
  border: 1px solid rgba(108,165,207,.30); border-radius: 18px;
  padding: 20px 21px; min-height: 137px; box-shadow: 0 12px 32px rgba(0,0,0,.20);
  animation: riseIn .6s ease both; transition: transform .24s ease, border-color .24s ease, box-shadow .24s ease;
}
.metric-box:before {
  content: ""; position: absolute; left: 0; top: 0; right: 0; height: 3px;
  background: linear-gradient(90deg, var(--mint), var(--cyan), var(--purple), var(--pink));
  background-size: 220% 100%; animation: gradientFlow 7s linear infinite;
}
.metric-box:after {
  content: ""; position: absolute; width: 130px; height: 130px; right: -55px; bottom: -75px;
  border-radius: 50%; background: rgba(56,217,245,.09); filter: blur(2px); z-index: -1;
}
.metric-box:hover { transform: translateY(-5px); border-color: rgba(71,228,184,.68); box-shadow: 0 18px 40px rgba(0,0,0,.31), 0 0 22px rgba(56,217,245,.08); }
.metric-icon {
  position: absolute; right: 16px; top: 16px; font-size: 1.45rem; animation: ballBob 3.6s ease-in-out infinite;
  filter: drop-shadow(0 4px 8px rgba(0,0,0,.35));
}
.metric-box:hover .metric-icon { animation: ballSpin .8s linear infinite; }
.metric-label { color: #a8c6de; font-size: .70rem; font-weight: 800; letter-spacing: 1.1px; text-transform: uppercase; }
.metric-value { color: #fff; font-size: clamp(1.65rem, 2.5vw, 2.25rem); font-weight: 900; margin: 9px 0 4px; font-variant-numeric: tabular-nums; }
.metric-help { color: #9ab5cd; font-size: .77rem; line-height: 1.5; }

[data-testid="stPlotlyChart"] {
  background: linear-gradient(145deg, rgba(16,36,59,.88), rgba(8,22,38,.83));
  border: 1px solid var(--panel-border); border-radius: 17px; padding: 8px;
  box-shadow: 0 12px 30px rgba(0,0,0,.16); animation: riseIn .48s ease both;
  transition: border-color .22s ease, transform .22s ease, box-shadow .22s ease;
}
[data-testid="stPlotlyChart"]:hover { border-color: rgba(56,217,245,.52); transform: translateY(-2px); box-shadow: 0 16px 35px rgba(0,0,0,.22); }
[data-testid="stExpander"] {
  background: linear-gradient(115deg, rgba(18,41,65,.90), rgba(12,29,48,.88));
  border: 1px solid var(--panel-border); border-radius: 13px; margin: 8px 0 13px;
  transition: border-color .2s ease, box-shadow .2s ease;
}
[data-testid="stExpander"]:hover { border-color: rgba(56,217,245,.42); box-shadow: 0 8px 20px rgba(0,0,0,.10); }
[data-testid="stExpander"] summary { font-weight: 800; }
[data-testid="stExpander"] details { border-radius: 13px; }
div[data-baseweb="select"] > div {
  background: #102840; border-color: #345671; border-radius: 10px; min-height: 42px;
  transition: border-color .2s ease, box-shadow .2s ease;
}
div[data-baseweb="select"] > div:hover { border-color: var(--cyan); box-shadow: 0 0 0 2px rgba(56,217,245,.08); }
div[data-testid="stNumberInput"] input, div[data-testid="stTextInput"] input {
  background: #102840; color: var(--text); border-radius: 9px; border-color: #345671;
}
div[data-testid="stSlider"] [role="slider"] { border-color: var(--mint); }
.stTabs [data-baseweb="tab-list"] {
  gap: 9px; background: rgba(8,23,39,.78); padding: 7px;
  border: 1px solid var(--panel-border); border-radius: 15px; margin-bottom: 12px;
}
.stTabs [data-baseweb="tab"] {
  background: rgba(20,43,67,.84); border: 1px solid transparent; border-radius: 10px;
  padding: 12px 23px; font-weight: 800; transition: all .22s ease;
}
.stTabs [data-baseweb="tab"]:hover { background: rgba(39,77,108,.94); transform: translateY(-1px); }
.stTabs [aria-selected="true"] {
  background: linear-gradient(100deg, #087f8c, #1768a5, #6651b8) !important;
  border-color: rgba(87,220,236,.40) !important; box-shadow: 0 6px 20px rgba(23,104,165,.20);
}
.stButton > button {
  border-radius: 10px; border: 1px solid rgba(56,217,245,.38);
  background: linear-gradient(100deg, #087f8c, #1768a5, #6651b8); background-size: 180% auto;
  color: white; font-weight: 800; transition: all .22s ease;
}
.stButton > button:hover { transform: translateY(-2px); background-position: right center; box-shadow: 0 8px 20px rgba(23,104,165,.32); }
div[data-testid="stAlert"] { border-radius: 12px; border: 1px solid var(--panel-border); }
.small-note { color: var(--muted); font-size: .78rem; line-height: 1.7; padding: 12px 14px; border-radius: 12px; background: rgba(13,31,51,.58); }
hr { border-color: var(--panel-border); }
[data-testid="stCaptionContainer"] { color: var(--muted); }
[data-testid="stMarkdownContainer"] h3 { margin-top: .45rem; }

@keyframes riseIn { from { opacity: 0; transform: translateY(12px); } to { opacity: 1; transform: translateY(0); } }
@keyframes titleShimmer { 0% { background-position: 0% center; } 100% { background-position: 220% center; } }
@keyframes gradientFlow { 0% { background-position: 0% 50%; } 100% { background-position: 220% 50%; } }
@keyframes backgroundDrift { 0% { background-position: 0% 0%; } 100% { background-position: 100% 80%; } }

/* cricket keyframes */
@keyframes ballFloat {
  0%   { transform: translateY(0) rotate(0deg); opacity: 0; }
  10%  { opacity: .22; }
  90%  { opacity: .22; }
  100% { transform: translateY(-115vh) rotate(720deg); opacity: 0; }
}
@keyframes batSwing {
  0%, 58%, 100% { transform: rotate(-14deg); }
  74%           { transform: rotate(42deg); }
  86%           { transform: rotate(-6deg); }
}
@keyframes bowl {
  0%   { left: 9%;  bottom: 94px; opacity: 0; animation-timing-function: ease-in; }
  5%   { left: 12%; bottom: 92px; opacity: 1; animation-timing-function: ease-in; }
  52%  { left: 60%; bottom: 22px; opacity: 1; animation-timing-function: ease-out; }
  78%  { left: 85%; bottom: 50px; opacity: 1; }
  80%  { left: 86%; bottom: 52px; opacity: 0; }
  100% { left: 86%; bottom: 52px; opacity: 0; }
}
@keyframes seamSpin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
@keyframes runUp {
  0%   { transform: translateX(-6px) translateY(0); }
  8%   { transform: translateX(10px) translateY(-6px); }
  16%  { transform: translateX(26px) translateY(0); }
  24%  { transform: translateX(44px) translateY(-8px); }
  34%  { transform: translateX(62px) translateY(0); }
  100% { transform: translateX(62px) translateY(0); }
}
@keyframes batterSwing {
  0%, 70%, 100% { transform: rotate(0deg); }
  78%           { transform: rotate(-52deg); }
  90%           { transform: rotate(8deg); }
}
@keyframes stumpWobble {
  0%, 78%, 100% { transform: rotate(0deg); }
  82% { transform: rotate(5deg); } 86% { transform: rotate(-4deg); } 90% { transform: rotate(2deg); } 94% { transform: rotate(0deg); }
}
@keyframes bailL {
  0%, 78% { transform: translate(0,0) rotate(0deg); opacity: 1; }
  88%     { transform: translate(-22px,-34px) rotate(-160deg); opacity: 1; }
  96%     { transform: translate(-34px,14px) rotate(-300deg); opacity: 0; }
  100%    { transform: translate(0,0) rotate(0deg); opacity: 0; }
}
@keyframes bailR {
  0%, 78% { transform: translate(0,0) rotate(0deg); opacity: 1; }
  88%     { transform: translate(24px,-40px) rotate(180deg); opacity: 1; }
  96%     { transform: translate(38px,12px) rotate(320deg); opacity: 0; }
  100%    { transform: translate(0,0) rotate(0deg); opacity: 0; }
}
@keyframes wicketPop {
  0%, 79%   { opacity: 0; transform: scale(.6); }
  84%       { opacity: 1; transform: scale(1.25); }
  92%       { opacity: 1; transform: scale(1); }
  98%, 100% { opacity: 0; transform: scale(1); }
}
@keyframes tickerMove { from { transform: translateX(0); } to { transform: translateX(-50%); } }
@keyframes ballBob { 0%, 100% { transform: translateY(0) rotate(0deg); } 50% { transform: translateY(-5px) rotate(18deg); } }
@keyframes ballSpin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
@keyframes ballPulse { 0%, 100% { transform: scale(1); } 50% { transform: scale(1.35); } }

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation: none !important; transition: none !important; scroll-behavior: auto !important; }
}
@media (max-width: 768px) {
  .block-container { padding-left: 1rem; padding-right: 1rem; }
  .hero-title { letter-spacing: -1px; }
  .metric-box { padding: 16px; min-height: 118px; }
  .stTabs [data-baseweb="tab"] { padding: 10px 12px; }
  .pitch-scene { height: 118px; }
  .wicket-pop { font-size: .8rem; }
}
</style>
""", unsafe_allow_html=True)

# Consistent, accessible colors across all Plotly Express charts.
px.defaults.color_discrete_sequence = ["#38D9F5", "#47E4B8", "#B39AFF", "#FFBD72", "#FF78B7", "#D6F36A", "#70E1A1", "#FF6B6B"]
px.defaults.template = "plotly_dark"

ROOT = Path(__file__).resolve().parents[1]
CANDIDATES = [ROOT/'data'/'raw'/'ipl.db', ROOT/'notebooks'/'ipl.db', ROOT/'data'/'ipl.db', ROOT/'ipl.db', Path.cwd()/'data'/'raw'/'ipl.db', Path.cwd()/'ipl.db']
DB_PATH = next((p for p in CANDIDATES if p.exists()), None)
if DB_PATH is None:
    st.error("IPL database not found. Place ipl.db in data/raw/ or notebooks/ in your project.")
    st.code("ipl-cricket-data-analysis/\n├── dashboard/app.py\n├── data/raw/ipl.db")
    st.stop()

@st.cache_data(show_spinner=False, ttl=300)
def q(sql, params=()):
    """Run SQL and return its result. Dashboard metrics/charts are calculated in SQL."""
    with sqlite3.connect(str(DB_PATH)) as con:
        return pd.read_sql_query(sql, con, params=list(params))

# SQL metric definitions for this dataset
RUNS = "(COALESCE(d.total_runs,0)-COALESCE(d.bye_runs,0)-COALESCE(d.leg_bye_runs,0)-COALESCE(d.penalty_runs,0))"
LEGAL = "(COALESCE(d.is_wide_ball,0)=0 AND COALESCE(d.is_no_ball,0)=0)"
CREDITED = "LOWER(REPLACE(COALESCE(d.wicket_kind,''),'-',' ')) NOT IN ('run out','retired hurt','obstructing the field','retired out')"
PHASE = "CASE WHEN d.over_number BETWEEN 0 AND 5 THEN 'Powerplay (1–6)' WHEN d.over_number BETWEEN 6 AND 14 THEN 'Middle (7–15)' ELSE 'Death (16+)' END"
STYLE = "CASE WHEN LOWER(COALESCE(p.bowl_style,'')) LIKE '%spin%' OR LOWER(COALESCE(p.bowl_style,'')) LIKE '%legbreak%' OR LOWER(COALESCE(p.bowl_style,'')) LIKE '%offbreak%' OR LOWER(COALESCE(p.bowl_style,'')) LIKE '%orthodox%' OR LOWER(COALESCE(p.bowl_style,'')) LIKE '%googly%' OR LOWER(COALESCE(p.bowl_style,'')) LIKE '%wrist spin%' OR LOWER(COALESCE(p.bowl_style,'')) LIKE '%slow left arm%' THEN 'Spin' WHEN TRIM(COALESCE(p.bowl_style,''))='' THEN 'Unknown' ELSE 'Pace' END"
PHASE_ORDER = "CASE phase WHEN 'Powerplay (1–6)' THEN 1 WHEN 'Middle (7–15)' THEN 2 ELSE 3 END"

# Validate expected tables/columns before rendering.
try:
    q("SELECT season_id, match_id, bowler, total_runs FROM deliveries LIMIT 1")
    q("SELECT player_name, bowl_style FROM players LIMIT 1")
except Exception as e:
    st.error(f"Database schema check failed: {e}")
    st.stop()

season_rows = q("SELECT DISTINCT season_id AS season FROM deliveries WHERE season_id IS NOT NULL ORDER BY season")
SEASONS = [int(x) for x in season_rows['season'].dropna().tolist()]
style_rows = q(f"SELECT DISTINCT {STYLE} AS style FROM deliveries d LEFT JOIN players p ON p.player_name=d.bowler ORDER BY style")
STYLES = [x for x in style_rows['style'].dropna().tolist() if x in ['Pace','Spin']]
PHASES = ['Powerplay (1–6)', 'Middle (7–15)', 'Death (16+)']

# SQL WHERE helper for optional season/style filters. Returns SQL + params.
def filters_sql(season, styles, alias='d'):
    where = ''
    params = []
    if season != 'All seasons':
        where += f' AND {alias}.season_id = ?'
        params.append(int(season))
    if styles:
        where += ' AND ' + STYLE + ' IN (' + ','.join(['?']*len(styles)) + ')'
        params.extend(styles)
    return where, params

@st.cache_data(show_spinner=False, ttl=300)
def get_opponents():
    return q("SELECT DISTINCT batting_team AS team FROM deliveries WHERE batting_team IS NOT NULL AND TRIM(batting_team)<>'' ORDER BY team")['team'].tolist()

def chart_filters(key, default_season='All seasons', default_styles=None, show_phase=False, show_min_balls=True, show_opponent=False):
    """Unique filter widgets per chart, so each visual can be explored independently."""
    default_styles = default_styles or []
    season_options = ['All seasons'] + [str(y) for y in SEASONS]
    with st.expander('🎛️ Customize this chart', expanded=False):
        c1, c2, c3 = st.columns([1,1,1])
        with c1:
            s = st.selectbox('Season', season_options, index=season_options.index(default_season) if default_season in season_options else 0, key=f'{key}_season')
        with c2:
            sty = st.multiselect('Bowling style', STYLES, default=default_styles, key=f'{key}_style')
        with c3:
            mb = st.number_input('Minimum legal balls', min_value=0, max_value=20000, value=120 if show_min_balls else 0, step=30, key=f'{key}_minballs') if show_min_balls else 0
        ph = st.selectbox('Innings phase', ['All phases'] + PHASES, key=f'{key}_phase') if show_phase else 'All phases'
        opp = st.selectbox('Opponent team', ['All opponents'] + get_opponents(), key=f'{key}_opponent') if show_opponent else 'All opponents'
    return s, sty, int(mb), ph, opp

# Compose filter fragments; all displayed figures still come from q(SQL).
def make_where(season, styles, phase='All phases', opponent='All opponents'):
    where, params = filters_sql(season, styles)
    if phase != 'All phases':
        where += f' AND {PHASE} = ?'
        params.append(phase)
    if opponent != 'All opponents':
        where += ' AND d.batting_team = ?'
        params.append(opponent)
    return where, params

def empty_chart(message='No data matches these chart filters. Try widening the filters.'):
    st.info(message)

def finish_fig(fig, height=390):
    """Apply the shared premium chart theme and smooth Plotly transitions."""
    fig.update_layout(
        height=height,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#eaf4ff', family='Inter, sans-serif', size=12),
        title=dict(font=dict(size=17, color='#f4f8ff'), x=0.02, xanchor='left'),
        margin=dict(l=18, r=18, t=76, b=28),
        legend=dict(
            orientation='h', yanchor='bottom', y=1.02,
            xanchor='left', x=0, bgcolor='rgba(0,0,0,0)',
            font=dict(size=11)
        ),
        hoverlabel=dict(
            bgcolor='#10263b', font_color='#ffffff',
            bordercolor='#38D9F5', font_size=12
        ),
        transition=dict(duration=500, easing='cubic-in-out'),
        hovermode='closest'
    )
    fig.update_xaxes(
        gridcolor='rgba(130,165,190,.14)',
        zerolinecolor='rgba(130,165,190,.18)',
        linecolor='rgba(130,165,190,.24)',
        tickfont=dict(color='#b7cbe0')
    )
    fig.update_yaxes(
        gridcolor='rgba(130,165,190,.14)',
        zerolinecolor='rgba(130,165,190,.18)',
        linecolor='rgba(130,165,190,.24)',
        tickfont=dict(color='#b7cbe0')
    )
    return fig

def show_fig(fig, key, height=390):
    fig = finish_fig(fig, height)
    cfg = {'displaylogo': False, 'responsive': True}
    # Newer Streamlit replaced use_container_width with width='stretch'; fall back for older versions.
    try:
        st.plotly_chart(fig, width='stretch', key=key, config=cfg)
    except Exception:
        st.plotly_chart(fig, use_container_width=True, key=key, config=cfg)

def metric_card(col, label, value, help_text, icon='🏏'):
    with col:
        st.markdown(f'<div class="metric-box"><div class="metric-icon">{icon}</div><div class="metric-label">{label}</div><div class="metric-value">{value}</div><div class="metric-help">{help_text}</div></div>', unsafe_allow_html=True)

# ---------------------------- CRICKET ANIMATION BLOCKS ----------------------------
def ball_field():
    # Six red cricket balls drifting upward behind the dashboard.
    st.markdown('<div class="ball-field"><span></span><span></span><span></span><span></span><span></span><span></span></div>', unsafe_allow_html=True)

def bowling_scene():
    # Loop: bowler runs up -> ball pitches -> batter swings and misses -> stumps hit, bails fly, WICKET! pops.
    st.markdown(
        '<div class="pitch-scene">'
        '<div class="scene-tag">Live delivery · 6.0</div>'
        '<div class="pitch-strip"></div><div class="crease c1"></div><div class="crease c2"></div>'
        '<div class="runner">🏃</div>'
        '<div class="ball"></div>'
        '<div class="batter">🏏</div>'
        '<div class="stumps"><div class="bail b1"></div><div class="bail b2"></div>'
        '<div class="stump"></div><div class="stump"></div><div class="stump"></div></div>'
        '<div class="wicket-pop">WICKET!</div>'
        '</div>', unsafe_allow_html=True)

def ticker():
    items = [
        '<b>OVER 1–6</b> · Powerplay: fielding restrictions on',
        '<b>DOT BALL</b> · pressure builds wickets',
        '<b>OVER 7–15</b> · Middle overs: spin squeeze',
        '<b>SIX!</b> · bowler goes for 6 runs',
        '<b>OVER 16–20</b> · Death overs: yorkers decide it',
        '<b>WICKET</b> · caught, bowled, lbw, stumped',
        '<b>ECONOMY</b> · runs per 6 legal balls',
    ]
    html = ''.join(f'<span>{i}</span>' for i in items)
    st.markdown(f'<div class="ticker"><div class="ticker-track">{html}{html}</div></div>', unsafe_allow_html=True)

# Header + global defaults (these drive KPI cards and the selected bowler list; each chart can override its own filters).
ball_field()
st.markdown('<div class="eyebrow">IPL CRICKET ANALYTICS · DOMAIN B</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-row"><span class="bat">🏏</span><div class="hero-title">Bowling Intelligence</div></div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Read the phase. Trust the sample. Pick the right bowler.</div>', unsafe_allow_html=True)
bowling_scene()
ticker()
st.markdown('<div class="reader"><b>For the bowling coach:</b> deciding which bowler to pick and for which overs.</div>', unsafe_allow_html=True)
with st.sidebar:
    st.markdown('<div class="eyebrow">COACH CONTROL CENTRE</div>', unsafe_allow_html=True)
    st.header('Global selection')
    st.caption('Set the baseline first. Each chart can then be customized independently.')
    global_season = st.selectbox('Default season', ['All seasons'] + [str(y) for y in SEASONS], key='global_season')
    global_styles = st.multiselect('Default bowling style', STYLES, default=[], key='global_styles')
    global_min_balls = st.slider('Bowler eligibility · minimum legal balls', 0, 3000, 500, 30, key='global_minballs')
    global_min_wickets = st.slider('Bowler eligibility · minimum wickets', 0, 100, 0, 1, key='global_minwickets')
    st.caption('Each chart also has a separate filter panel. Global filters set the initial context and eligible bowler list.')

# Exactly two tabs, as required by the assignment.
overview_tab, bowler_tab = st.tabs(['📊  Overview', '🎯  Bowler profile'])

# ---------------------------- OVERVIEW ----------------------------
with overview_tab:
    st.markdown('<div class="section-label">01 / League overview · compare bowling groups</div>', unsafe_allow_html=True)
    # Exactly 3 KPI cards. The total wickets card remains fixed before filters.
    total_bowlers = q(f"WITH x AS (SELECT d.bowler, SUM(CASE WHEN {LEGAL} THEN 1 ELSE 0 END) balls FROM deliveries d GROUP BY d.bowler) SELECT COUNT(*) bowlers, SUM(CASE WHEN balls>=500 THEN 1 ELSE 0 END) qualified FROM x").iloc[0]
    fixed_wickets = q(f"SELECT SUM(CASE WHEN d.is_wicket=1 AND {CREDITED} THEN 1 ELSE 0 END) wickets FROM deliveries d").iloc[0,0]
    a,b,c = st.columns(3)
    metric_card(a, 'Bowlers in dataset', f"{int(total_bowlers['bowlers'] or 0):,}", f"{int(total_bowlers['qualified'] or 0):,} have at least 500 legal balls", '🏃')
    metric_card(b, 'Wickets credited to bowlers', f"{int(fixed_wickets or 0):,}", 'Fixed total before any filter', '🎯')
    metric_card(c, 'Spin vs pace · statistical test', 'Add verified result', 'Enter p-value + effect size from your Statistical Report', '📊')
    st.caption('The statistical card is intentionally not fabricated. Replace it with your verified test result before submitting.')

    # Chart 1: HERO, independent filters
    st.markdown('### ⭐ Hero chart · Economy by innings phase')
    s, sty, mb, ph, opp = chart_filters('ov_hero', global_season, global_styles, show_min_balls=True)
    wh, pa = make_where(s, sty, ph, opp)
    hero = q(f"""SELECT {PHASE} phase, {STYLE} style,
      SUM({RUNS})*6.0/NULLIF(SUM(CASE WHEN {LEGAL} THEN 1 ELSE 0 END),0) economy,
      SUM(CASE WHEN {LEGAL} THEN 1 ELSE 0 END) balls
      FROM deliveries d LEFT JOIN players p ON p.player_name=d.bowler WHERE 1=1 {wh}
      GROUP BY phase,style HAVING balls>=? AND style IN ('Spin','Pace') ORDER BY {PHASE_ORDER},style""", pa+[mb])
    league = q(f"""SELECT {PHASE} phase, SUM({RUNS})*6.0/NULLIF(SUM(CASE WHEN {LEGAL} THEN 1 ELSE 0 END),0) league_economy
      FROM deliveries d WHERE 1=1 {' AND d.season_id=?' if s!='All seasons' else ''}
      GROUP BY phase""", [int(s)] if s!='All seasons' else [])
    if hero.empty: empty_chart()
    else:
        fig = go.Figure()
        for style in ['Pace','Spin']:
            z = hero[hero['style'] == style]
            if not z.empty:
                fig.add_trace(go.Bar(name=style, marker_color=('#36D6F5' if style == 'Pace' else '#A78BFA'), x=z['phase'], y=z['economy'], customdata=z[['balls']], text=z['balls'].map(lambda v:f'{int(v):,} balls'), textposition='outside', hovertemplate='%{x}<br>Economy %{y:.2f}<br>Legal balls %{customdata[0]:,.0f}<extra>'+style+'</extra>'))
        for _,r in league.iterrows():
            fig.add_trace(go.Scatter(x=[r.phase], y=[r.league_economy], mode='markers', marker=dict(symbol='line-ew',size=23,color='#ffd166',line=dict(width=3,color='#ffd166')), name='League reference', showlegend=False, hovertemplate='League economy %{y:.2f}<extra></extra>'))
        fig.update_layout(title='Spin vs pace: compare run control with the league benchmark', barmode='group', xaxis_title='Innings phase', yaxis_title='Economy (runs per 6 legal balls)')
        show_fig(fig,'ov_hero_chart',510)

    l,r=st.columns(2)
    with l:
        st.markdown('### 🧭 Bowling styles ranked by economy')
        s,sty,mb,ph,opp=chart_filters('ov_style_rank',global_season,global_styles,show_min_balls=True)
        wh,pa=make_where(s,sty,ph,opp)
        d=q(f"""SELECT {STYLE} style, COUNT(DISTINCT d.bowler) bowlers, SUM({RUNS})*6.0/NULLIF(SUM(CASE WHEN {LEGAL} THEN 1 ELSE 0 END),0) economy, SUM(CASE WHEN {LEGAL} THEN 1 ELSE 0 END) balls
        FROM deliveries d LEFT JOIN players p ON p.player_name=d.bowler WHERE 1=1 {wh} GROUP BY style HAVING balls>=? AND style<>'Unknown' ORDER BY economy""",pa+[mb])
        if d.empty: empty_chart()
        else:
            fig=px.bar(d,x='economy',y='style',orientation='h',text='bowlers',hover_data=['balls'],labels={'economy':'Economy / 6 legal balls','style':'Bowling style','bowlers':'Bowlers'},title=f'Ranked styles · minimum {mb:,} legal balls per style')
            fig.update_traces(texttemplate='%{text} bowlers',textposition='outside'); show_fig(fig,'ov_style_rank_chart')
        st.caption(f'Ranking rule: each style needs at least {mb:,} legal balls.')
    with r:
        st.markdown('### 🎯 Wickets by innings phase')
        s,sty,mb,ph,opp=chart_filters('ov_phase_wkts',global_season,global_styles,show_min_balls=True,show_phase=False)
        wh,pa=make_where(s,sty,ph,opp)
        d=q(f"""SELECT {PHASE} phase, SUM(CASE WHEN d.is_wicket=1 AND {CREDITED} THEN 1 ELSE 0 END) wickets, SUM(CASE WHEN {LEGAL} THEN 1 ELSE 0 END) balls
        FROM deliveries d LEFT JOIN players p ON p.player_name=d.bowler WHERE 1=1 {wh} GROUP BY phase HAVING balls>=? ORDER BY {PHASE_ORDER}""",pa+[mb])
        if d.empty: empty_chart()
        else: show_fig(px.bar(d,x='phase',y='wickets',text='wickets',hover_data=['balls'],labels={'phase':'Innings phase','wickets':'Credited wickets','balls':'Legal balls'},title='Wicket-taking is separate from run containment'),'ov_phase_wkts_chart')
    l,r=st.columns(2)
    with l:
        st.markdown('### 🟢 Dot-ball pressure by phase')
        s,sty,mb,ph,opp=chart_filters('ov_dot',global_season,global_styles,show_min_balls=True,show_phase=True)
        wh,pa=make_where(s,sty,ph,opp)
        d=q(f"""SELECT {PHASE} phase,{STYLE} style,100.0*SUM(CASE WHEN {LEGAL} AND {RUNS}=0 THEN 1 ELSE 0 END)/NULLIF(SUM(CASE WHEN {LEGAL} THEN 1 ELSE 0 END),0) dot_pct,SUM(CASE WHEN {LEGAL} THEN 1 ELSE 0 END) balls
        FROM deliveries d LEFT JOIN players p ON p.player_name=d.bowler WHERE 1=1 {wh} GROUP BY phase,style HAVING balls>=? AND style<>'Unknown' ORDER BY {PHASE_ORDER}""",pa+[mb])
        if d.empty: empty_chart()
        else: show_fig(px.bar(d,x='phase',y='dot_pct',color='style',barmode='group',hover_data=['balls'],labels={'phase':'Phase','dot_pct':'Dot balls (%)','style':'Style','balls':'Legal balls'},title='Higher dot-ball share means more pressure'),'ov_dot_chart')
    with r:
        st.markdown('### 📈 League economy across seasons')
        s,sty,mb,ph,opp=chart_filters('ov_season_econ',global_season,global_styles,show_min_balls=True)
        wh,pa=make_where(s,sty,ph,opp)
        # Season trend must span all seasons, so this chart uses its own optional season as a single-season focus only when chosen.
        d=q(f"""SELECT d.season_id season,SUM({RUNS})*6.0/NULLIF(SUM(CASE WHEN {LEGAL} THEN 1 ELSE 0 END),0) economy,SUM(CASE WHEN {LEGAL} THEN 1 ELSE 0 END) balls
        FROM deliveries d LEFT JOIN players p ON p.player_name=d.bowler WHERE 1=1 {wh} GROUP BY d.season_id HAVING balls>=? ORDER BY season""",pa+[mb])
        if d.empty: empty_chart()
        else: show_fig(px.line(d,x='season',y='economy',markers=True,hover_data=['balls'],labels={'season':'Season','economy':'Economy / 6 legal balls','balls':'Legal balls'},title='Season trend · ball count shown on hover'),'ov_season_econ_chart')

# ---------------------------- BOWLER PROFILE ----------------------------
with bowler_tab:
    st.markdown('<div class="section-label">02 / Player profile · inspect one bowler</div>', unsafe_allow_html=True)
    # Candidate list respects global eligibility controls and filters.
    list_where,list_params=filters_sql(global_season,global_styles)
    bowler_df=q(f"""SELECT d.bowler,MAX(COALESCE(p.bowl_style,'Unknown')) bowl_style,SUM(CASE WHEN {LEGAL} THEN 1 ELSE 0 END) balls,SUM(CASE WHEN d.is_wicket=1 AND {CREDITED} THEN 1 ELSE 0 END) wickets
    FROM deliveries d LEFT JOIN players p ON p.player_name=d.bowler WHERE d.bowler IS NOT NULL {list_where} GROUP BY d.bowler HAVING balls>=? AND wickets>=? ORDER BY d.bowler""",list_params+[global_min_balls,global_min_wickets])
    if bowler_df.empty:
        st.warning('No bowlers match the global filters. Reduce minimum balls/wickets or change season/style.')
        st.stop()
    selected_bowler=st.selectbox('🔎 Search / select bowler',bowler_df.bowler.tolist(),key='profile_bowler')
    style_label=bowler_df.loc[bowler_df.bowler==selected_bowler,'bowl_style'].iloc[0]
    st.caption(f'Bowler profile: **{selected_bowler}** · Style: **{style_label}** · every chart below has independent filters.')

    # Exactly 3 player metric cards, filtered to the selected bowler and global season.
    pseason = '' if global_season=='All seasons' else ' AND d.season_id=?'
    pparams=[selected_bowler]+([] if global_season=='All seasons' else [int(global_season)])
    pm=q(f"""SELECT SUM(CASE WHEN d.is_wicket=1 AND {CREDITED} THEN 1 ELSE 0 END) wickets,SUM(CASE WHEN {LEGAL} THEN 1 ELSE 0 END) balls,
    SUM({RUNS})*6.0/NULLIF(SUM(CASE WHEN {LEGAL} THEN 1 ELSE 0 END),0) economy,
    SUM(CASE WHEN {LEGAL} AND {RUNS}=0 THEN 1 ELSE 0 END) dots,
    100.0*SUM(CASE WHEN {LEGAL} AND {RUNS}=0 THEN 1 ELSE 0 END)/NULLIF(SUM(CASE WHEN {LEGAL} THEN 1 ELSE 0 END),0) dot_pct
    FROM deliveries d WHERE d.bowler=? {pseason}""",pparams).iloc[0]
    a,b,c=st.columns(3)
    metric_card(a,'Wickets credited',f"{int(pm.wickets or 0):,}",f"{int(pm.balls or 0):,} legal balls bowled",'🏆')
    metric_card(b,'Bowling economy','—' if pd.isna(pm.economy) else f'{pm.economy:.2f}',f"Based on {int(pm.balls or 0):,} legal balls",'⚡')
    metric_card(c,'Dot-ball share','—' if pd.isna(pm.dot_pct) else f'{pm.dot_pct:.1f}%',f"{int(pm.dots or 0):,} dot balls / {int(pm.balls or 0):,} legal balls",'🔴')

    # Each bowler chart gets separate filters; bowler identity stays fixed.
    st.markdown('### ⭐ Hero chart · Economy by season vs league')
    s,sty,mb,ph,opp=chart_filters('b_hero',global_season,[style_label] if style_label in STYLES else [],show_min_balls=True)
    wh,pa=make_where(s,sty,ph,opp)
    bow=q(f"""SELECT d.season_id season,SUM({RUNS})*6.0/NULLIF(SUM(CASE WHEN {LEGAL} THEN 1 ELSE 0 END),0) economy,SUM(CASE WHEN {LEGAL} THEN 1 ELSE 0 END) balls
    FROM deliveries d LEFT JOIN players p ON p.player_name=d.bowler WHERE d.bowler=? {wh} GROUP BY d.season_id HAVING balls>=? ORDER BY season""",[selected_bowler]+pa+[mb])
    league=q(f"""SELECT d.season_id season,SUM({RUNS})*6.0/NULLIF(SUM(CASE WHEN {LEGAL} THEN 1 ELSE 0 END),0) league_economy FROM deliveries d WHERE 1=1 {' AND d.season_id=?' if s!='All seasons' else ''} GROUP BY d.season_id ORDER BY season""",[int(s)] if s!='All seasons' else [])
    if bow.empty: empty_chart()
    else:
        fig=go.Figure()
        fig.add_trace(go.Scatter(x=bow.season,y=bow.economy,mode='lines+markers',name=selected_bowler,line=dict(width=4, color='#36D6F5'), marker=dict(size=9, color='#43E0B5'),customdata=bow[['balls']],hovertemplate='Season %{x}<br>Economy %{y:.2f}<br>Legal balls %{customdata[0]:,.0f}<extra></extra>'))
        if not league.empty: fig.add_trace(go.Scatter(x=league.season,y=league.league_economy,mode='lines',name='League economy',line=dict(color='#ffd166',width=3,dash='dash')))
        fig.update_layout(title=f'{selected_bowler}: season economy against the league reference',xaxis_title='Season',yaxis_title='Economy / 6 legal balls')
        show_fig(fig,'b_hero_chart',500)

    l,r=st.columns(2)
    with l:
        st.markdown('### 🎯 Wickets and economy by phase')
        s,sty,mb,ph,opp=chart_filters('b_phase',global_season,[style_label] if style_label in STYLES else [],show_min_balls=True,show_phase=True)
        wh,pa=make_where(s,sty,ph,opp)
        d=q(f"""SELECT {PHASE} phase,SUM(CASE WHEN d.is_wicket=1 AND {CREDITED} THEN 1 ELSE 0 END) wickets,SUM({RUNS})*6.0/NULLIF(SUM(CASE WHEN {LEGAL} THEN 1 ELSE 0 END),0) economy,SUM(CASE WHEN {LEGAL} THEN 1 ELSE 0 END) balls
        FROM deliveries d LEFT JOIN players p ON p.player_name=d.bowler WHERE d.bowler=? {wh} GROUP BY phase HAVING balls>=? ORDER BY {PHASE_ORDER}""",[selected_bowler]+pa+[mb])
        if d.empty: empty_chart()
        else:
            fig=go.Figure(); fig.add_trace(go.Bar(x=d.phase,y=d.wickets,name='Credited wickets',customdata=d[['balls','economy']],hovertemplate='%{x}<br>Wickets %{y}<br>Legal balls %{customdata[0]}<br>Economy %{customdata[1]:.2f}<extra></extra>'))
            fig.update_layout(title='Where does the bowler take wickets?',xaxis_title='Phase',yaxis_title='Credited wickets'); show_fig(fig,'b_phase_chart')
    with r:
        st.markdown('### 🆚 Economy against opponents')
        s,sty,mb,ph,opp=chart_filters('b_opponent',global_season,[style_label] if style_label in STYLES else [],show_min_balls=True,show_opponent=True)
        wh,pa=make_where(s,sty,ph,opp)
        d=q(f"""SELECT d.batting_team opponent,SUM({RUNS})*6.0/NULLIF(SUM(CASE WHEN {LEGAL} THEN 1 ELSE 0 END),0) economy,SUM(CASE WHEN d.is_wicket=1 AND {CREDITED} THEN 1 ELSE 0 END) wickets,SUM(CASE WHEN {LEGAL} THEN 1 ELSE 0 END) balls
        FROM deliveries d LEFT JOIN players p ON p.player_name=d.bowler WHERE d.bowler=? {wh} GROUP BY d.batting_team HAVING balls>=? ORDER BY economy""",[selected_bowler]+pa+[mb])
        if d.empty: empty_chart()
        else: show_fig(px.bar(d,x='economy',y='opponent',orientation='h',text='balls',hover_data=['wickets'],labels={'opponent':'Opponent','economy':'Economy / 6 legal balls','balls':'Legal balls','wickets':'Wickets'},title='Opponent ranking · sorted by economy'),'b_opponent_chart')
        st.caption(f'Ranking rule: opponent samples require at least {mb:,} legal balls.')
    l,r=st.columns(2)
    with l:
        st.markdown('### 🏟️ Economy by over number')
        s,sty,mb,ph,opp=chart_filters('b_over',global_season,[style_label] if style_label in STYLES else [],show_min_balls=True,show_phase=True,show_opponent=True)
        wh,pa=make_where(s,sty,ph,opp)
        d=q(f"""SELECT d.over_number+1 over_number,SUM({RUNS})*6.0/NULLIF(SUM(CASE WHEN {LEGAL} THEN 1 ELSE 0 END),0) economy,SUM(CASE WHEN d.is_wicket=1 AND {CREDITED} THEN 1 ELSE 0 END) wickets,SUM(CASE WHEN {LEGAL} THEN 1 ELSE 0 END) balls
        FROM deliveries d LEFT JOIN players p ON p.player_name=d.bowler WHERE d.bowler=? {wh} GROUP BY d.over_number HAVING balls>=? ORDER BY over_number""",[selected_bowler]+pa+[mb])
        if d.empty: empty_chart()
        else: show_fig(px.line(d,x='over_number',y='economy',markers=True,hover_data=['wickets','balls'],labels={'over_number':'Over number','economy':'Economy / 6 legal balls','wickets':'Wickets','balls':'Legal balls'},title='Economy by over · sample shown on hover'),'b_over_chart')
    with r:
        st.markdown('### 🧤 Dismissal types')
        s,sty,mb,ph,opp=chart_filters('b_dismissal',global_season,[style_label] if style_label in STYLES else [],show_min_balls=True,show_phase=True,show_opponent=True)
        wh,pa=make_where(s,sty,ph,opp)
        d=q(f"""SELECT COALESCE(d.wicket_kind,'Not recorded') dismissal,SUM(CASE WHEN d.is_wicket=1 AND {CREDITED} THEN 1 ELSE 0 END) wickets,SUM(CASE WHEN {LEGAL} THEN 1 ELSE 0 END) balls
        FROM deliveries d LEFT JOIN players p ON p.player_name=d.bowler WHERE d.bowler=? {wh} GROUP BY dismissal HAVING wickets>0 AND balls>=? ORDER BY wickets DESC""",[selected_bowler]+pa+[mb])
        if d.empty: empty_chart()
        else: show_fig(px.bar(d,x='dismissal',y='wickets',text='wickets',hover_data=['balls'],labels={'dismissal':'Dismissal type','wickets':'Credited wickets','balls':'Legal balls'},title='Which dismissal types produce wickets?'),'b_dismissal_chart')

st.markdown('---')
st.markdown('<div class="small-note">IPL Bowling Intelligence · Streamlit + SQL + Plotly. Animated CSS interface with interactive Plotly charts. Legal balls exclude wides/no-balls. Bowler-conceded runs exclude byes, leg-byes and penalty runs. Economy and dot-ball rates show their supporting ball counts. Treat small samples cautiously.</div>',unsafe_allow_html=True)