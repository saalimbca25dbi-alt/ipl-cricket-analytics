from pathlib import Path
import sqlite3
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# ================================================================
# IPL BOWLING INTELLIGENCE — Domain B
# Two tabs, exactly 3 KPI cards + 5 charts on each tab.
# Each chart has its OWN filter expander. Displayed figures come from SQL/q().
# ================================================================
st.set_page_config(page_title="IPL Bowling Intelligence", page_icon="🏏", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

:root {
  color-scheme: dark;
  --bg: #07111f;
  --panel: rgba(16, 34, 56, .86);
  --panel-border: rgba(118, 164, 204, .22);
  --text: #eef6ff;
  --muted: #9bb3ca;
  --cyan: #36d6f5;
  --mint: #43e0b5;
  --purple: #a78bfa;
  --orange: #ffb86b;
}
html, body, [class*="css"] { font-family: Inter, sans-serif; }
.stApp {
  background:
    radial-gradient(ellipse at 5% 0%, rgba(27, 111, 163, .32), transparent 34%),
    radial-gradient(ellipse at 95% 8%, rgba(114, 67, 186, .20), transparent 30%),
    linear-gradient(145deg, #07111f 0%, #0a1728 55%, #07101c 100%);
  color: var(--text);
}
[data-testid="stHeader"] { background: rgba(7,17,31,.35); }
.block-container { max-width: 1680px; padding-top: 1.5rem; padding-bottom: 3rem; }
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #0d2036 0%, #081523 100%);
  border-right: 1px solid var(--panel-border);
}
[data-testid="stSidebar"] * { color: var(--text); }
h1,h2,h3,h4,p,label { color: var(--text); }
h2, h3 { letter-spacing: -.45px; }
.eyebrow {
  color: var(--mint); font-size: .72rem; font-weight: 900;
  letter-spacing: 2.5px; text-transform: uppercase;
}
.hero-title {
  font-size: clamp(2.1rem, 4vw, 3.15rem); font-weight: 900;
  letter-spacing: -1.8px; line-height: 1.1; margin: .35rem 0 .55rem;
  background: linear-gradient(90deg, #ffffff 0%, #a8f4ff 48%, #b7a5ff 100%);
  -webkit-background-clip: text; background-clip: text; color: transparent;
}
.subtitle { color: #b2c7dc; font-size: 1.02rem; }
.reader {
  background: linear-gradient(100deg, rgba(67,224,181,.12), rgba(54,214,245,.08), rgba(167,139,250,.09));
  border: 1px solid rgba(91, 220, 215, .27); border-left: 4px solid var(--mint);
  border-radius: 15px; padding: 15px 19px; margin: 18px 0 25px;
  box-shadow: 0 10px 35px rgba(0,0,0,.12);
}
.section-label {
  color: var(--cyan); font-size: .73rem; font-weight: 900;
  letter-spacing: 1.8px; text-transform: uppercase; margin: .45rem 0 .85rem;
}
.metric-box {
  position: relative; overflow: hidden;
  background: linear-gradient(145deg, rgba(24,53,81,.97), rgba(12,29,48,.97));
  border: 1px solid rgba(108,165,207,.27); border-radius: 18px;
  padding: 20px 21px; min-height: 132px;
  box-shadow: 0 12px 32px rgba(0,0,0,.20);
  animation: riseIn .55s ease both;
  transition: transform .22s ease, border-color .22s ease, box-shadow .22s ease;
}
.metric-box:before {
  content: ""; position: absolute; left: 0; top: 0; right: 0; height: 3px;
  background: linear-gradient(90deg, var(--mint), var(--cyan), var(--purple));
}
.metric-box:hover {
  transform: translateY(-4px); border-color: rgba(67,224,181,.6);
  box-shadow: 0 18px 38px rgba(0,0,0,.30);
}
.metric-label { color: #a8c2d8; font-size: .72rem; font-weight: 800; letter-spacing: 1.15px; text-transform: uppercase; }
.metric-value { color: #fff; font-size: clamp(1.65rem, 2.5vw, 2.2rem); font-weight: 900; margin: 9px 0 3px; }
.metric-help { color: #8eabc4; font-size: .78rem; line-height: 1.45; }
[data-testid="stPlotlyChart"] {
  background: linear-gradient(145deg, rgba(16,35,57,.84), rgba(9,23,39,.72));
  border: 1px solid var(--panel-border); border-radius: 17px; padding: 8px;
  box-shadow: 0 12px 30px rgba(0,0,0,.14);
  animation: riseIn .48s ease both;
  transition: border-color .2s ease, transform .2s ease;
}
[data-testid="stPlotlyChart"]:hover { border-color: rgba(54,214,245,.45); transform: translateY(-2px); }
[data-testid="stExpander"] {
  background: rgba(15,34,55,.72); border: 1px solid var(--panel-border);
  border-radius: 13px; margin: 8px 0 13px;
}
[data-testid="stExpander"] summary { font-weight: 700; }
div[data-baseweb="select"] > div {
  background: #102840; border-color: #345671; border-radius: 10px;
}
div[data-baseweb="select"] > div:hover { border-color: var(--cyan); }
div[data-testid="stNumberInput"] input, div[data-testid="stTextInput"] input {
  background: #102840; color: var(--text); border-radius: 9px;
}
div[data-testid="stSlider"] [role="slider"] { border-color: var(--mint); }
.stTabs [data-baseweb="tab-list"] {
  gap: 10px; background: rgba(9,24,41,.65); padding: 7px;
  border: 1px solid var(--panel-border); border-radius: 14px;
}
.stTabs [data-baseweb="tab"] {
  background: rgba(20,43,67,.85); border: 1px solid transparent;
  border-radius: 10px; padding: 12px 23px; font-weight: 800;
  transition: all .2s ease;
}
.stTabs [data-baseweb="tab"]:hover { background: rgba(39,77,108,.9); }
.stTabs [aria-selected="true"] {
  background: linear-gradient(100deg, #087f8c, #1768a5) !important;
  border-color: rgba(87,220,236,.35) !important;
}
.stButton > button {
  border-radius: 10px; border: 1px solid rgba(54,214,245,.35);
  background: linear-gradient(100deg, #087f8c, #1768a5);
  color: white; font-weight: 800; transition: all .2s ease;
}
.stButton > button:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(23,104,165,.3); }
div[data-testid="stAlert"] { border-radius: 12px; }
.small-note { color: var(--muted); font-size: .79rem; line-height: 1.6; }
hr { border-color: var(--panel-border); }
[data-testid="stCaptionContainer"] { color: var(--muted); }
@keyframes riseIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation: none !important; transition: none !important; scroll-behavior: auto !important; }
}
@media (max-width: 768px) {
  .block-container { padding-left: 1rem; padding-right: 1rem; }
  .hero-title { letter-spacing: -1px; }
  .metric-box { padding: 16px; min-height: 115px; }
}
</style>
""", unsafe_allow_html=True)

# Consistent, accessible colors across all Plotly Express charts.
px.defaults.color_discrete_sequence = ["#36D6F5", "#43E0B5", "#A78BFA", "#FFB86B", "#FF6B9A", "#F9E66B", "#70E1A1"]

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

def chart_filters(key, default_season='All seasons', default_styles=None, show_phase=False, show_min_balls=True, show_opponent=False):
    """Unique filter widgets per chart, so each visual can be explored independently."""
    default_styles = default_styles or []
    with st.expander('🎛️ Customize this chart', expanded=False):
        c1, c2, c3 = st.columns([1,1,1])
        with c1:
            s = st.selectbox('Season', ['All seasons'] + [str(y) for y in SEASONS], index=(['All seasons'] + [str(y) for y in SEASONS]).index(default_season) if default_season in (['All seasons'] + [str(y) for y in SEASONS]) else 0, key=f'{key}_season')
        with c2:
            sty = st.multiselect('Bowling style', STYLES, default=default_styles, key=f'{key}_style')
        with c3:
            mb = st.number_input('Minimum legal balls', min_value=0, max_value=20000, value=120 if show_min_balls else 0, step=30, key=f'{key}_minballs') if show_min_balls else 0
        ph = st.selectbox('Innings phase', ['All phases'] + PHASES, key=f'{key}_phase') if show_phase else 'All phases'
        opp = st.selectbox('Opponent team', ['All opponents'] + get_opponents(), key=f'{key}_opponent') if show_opponent else 'All opponents'
    return s, sty, int(mb), ph, opp

@st.cache_data(show_spinner=False, ttl=300)
def get_opponents():
    return q("SELECT DISTINCT batting_team AS team FROM deliveries WHERE batting_team IS NOT NULL AND TRIM(batting_team)<>'' ORDER BY team")['team'].tolist()

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
    fig.update_layout(height=height, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                      font=dict(color='#e8f2fc', family='Inter'), margin=dict(l=18,r=18,t=72,b=22),
                      legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='left', x=0),
                      hoverlabel=dict(bgcolor='#10263b', font_color='#ffffff'),
                      transition=dict(duration=450, easing='cubic-in-out'))
    fig.update_xaxes(gridcolor='rgba(130,165,190,.15)', zerolinecolor='rgba(130,165,190,.18)')
    fig.update_yaxes(gridcolor='rgba(130,165,190,.15)', zerolinecolor='rgba(130,165,190,.18)')
    return fig

def show_fig(fig, key, height=390):
    st.plotly_chart(finish_fig(fig, height), use_container_width=True, key=key, config={'displaylogo':False, 'responsive':True})

def metric_card(col, label, value, help_text):
    with col:
        st.markdown(f'<div class="metric-box"><div class="metric-label">{label}</div><div class="metric-value">{value}</div><div class="metric-help">{help_text}</div></div>', unsafe_allow_html=True)

# Header + global defaults (these drive KPI cards and the selected bowler list; each chart can override its own filters).
st.markdown('<div class="eyebrow">IPL CRICKET ANALYTICS · DOMAIN B</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-title">🏏 Bowling Intelligence</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Read the phase. Trust the sample. Pick the right bowler.</div>', unsafe_allow_html=True)
st.markdown('<div class="reader"><b>For the bowling coach:</b> deciding which bowler to pick and for which overs.</div>', unsafe_allow_html=True)
with st.sidebar:
    st.markdown('<div class="eyebrow">COACH CONTROL CENTRE</div>', unsafe_allow_html=True)
    st.header('Global selection')
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
    metric_card(a, 'Bowlers in dataset', f"{int(total_bowlers['bowlers'] or 0):,}", f"{int(total_bowlers['qualified'] or 0):,} have at least 500 legal balls")
    metric_card(b, 'Wickets credited to bowlers', f"{int(fixed_wickets or 0):,}", 'Fixed total before any filter')
    metric_card(c, 'Spin vs pace · statistical test', 'Add verified result', 'Enter p-value + effect size from your Statistical Report')
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
        d=q(f"""SELECT {STYLE} style,
        SUM(CASE WHEN {LEGAL} AND {RUNS}=0 THEN 1 ELSE 0 END) dots,
        SUM(CASE WHEN {LEGAL} THEN 1 ELSE 0 END) balls,
        100.0*SUM(CASE WHEN {LEGAL} AND {RUNS}=0 THEN 1 ELSE 0 END)/NULLIF(SUM(CASE WHEN {LEGAL} THEN 1 ELSE 0 END),0) dot_pct
        FROM deliveries d LEFT JOIN players p ON p.player_name=d.bowler WHERE 1=1 {wh}
        GROUP BY style HAVING balls>=? AND style<>'Unknown' ORDER BY dots DESC""",pa+[mb])
        if d.empty:
            empty_chart()
        else:
            fig = px.pie(
                d, names='style', values='dots', hole=0.62,
                hover_data={'balls': True, 'dot_pct': ':.1f', 'dots': True},
                labels={'style':'Bowling style','dots':'Dot balls','balls':'Legal balls','dot_pct':'Dot-ball share (%)'},
                title='Dot-ball contribution by bowling style'
            )
            fig.update_traces(
                textposition='inside', textinfo='label+percent',
                insidetextfont=dict(size=13, color='white'),
                marker=dict(line=dict(color='#0a1728', width=3)),
                hole=0.62
            )
            show_fig(fig, 'ov_dot_chart')
        st.caption('Donut slices show each style’s share of all dot balls in the selected sample; hover to see its dot-ball percentage and legal-ball count.')
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
    metric_card(a,'Wickets credited',f"{int(pm.wickets or 0):,}",f"{int(pm.balls or 0):,} legal balls bowled")
    metric_card(b,'Bowling economy','—' if pd.isna(pm.economy) else f'{pm.economy:.2f}',f"Based on {int(pm.balls or 0):,} legal balls")
    metric_card(c,'Dot-ball share','—' if pd.isna(pm.dot_pct) else f'{pm.dot_pct:.1f}%',f"{int(pm.dots or 0):,} dot balls / {int(pm.balls or 0):,} legal balls")

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
        if d.empty:
            empty_chart()
        else:
            fig = px.pie(
                d, names='dismissal', values='wickets', hole=0.60,
                hover_data={'balls': True, 'wickets': True},
                labels={'dismissal':'Dismissal type','wickets':'Credited wickets','balls':'Legal balls'},
                title=f'{selected_bowler}: wicket mix by dismissal type'
            )
            fig.update_traces(
                textposition='inside', textinfo='label+percent',
                insidetextfont=dict(size=12, color='white'),
                marker=dict(line=dict(color='#0a1728', width=3)),
                hole=0.60
            )
            show_fig(fig, 'b_dismissal_chart')
        st.caption('Donut slices represent credited wickets by dismissal type. Hover to inspect wickets and the legal-ball sample.')

st.markdown('---')
st.markdown('<div class="small-note">IPL Bowling Intelligence · Streamlit + SQL + Plotly. Legal balls exclude wides/no-balls. Bowler-conceded runs exclude byes, leg-byes and penalty runs. Economy and dot-ball rates show their supporting ball counts. Treat small samples cautiously.</div>',unsafe_allow_html=True)
