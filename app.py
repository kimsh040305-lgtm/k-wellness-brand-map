"""웰니스 브랜드들은 누구를 잡고, 무엇으로 성장했나?

한국 웰니스·애슬레저 브랜드 6개(본투윈, 젝시믹스, 안다르, 뮬라웨어, HDEX, 압도)를
네이버 검색 데이터, 무신사 상품 가격, 공시·기사 매출, 뉴스 이벤트, 국민생활체육조사로 비교하는
Streamlit 대시보드. 데이터 정리는 prep.py, 화면은 이 파일.
"""
import base64
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).parent
DATA = ROOT / "data" / "processed"
LOGOS = ROOT / "assets" / "logos" / "dark"
PRODUCTS = ROOT / "assets" / "products"

st.set_page_config(page_title="대한민국 웰니스 브랜드 6 심층 비교", page_icon="📊", layout="wide")

# ── 디자인 토큰 ─────────────────────────────────────────
# 신뢰감: 네이비(주색) + 쿨 그레이(배경·선) + 흰 카드. 강조색은 네이비 하나만 쓰고,
# 브랜드 색은 데이터에만 쓴다. 브랜드 6색은 흰 배경 기준 색약 구분 검사를 통과한 조합.
BRANDS = ["본투윈", "젝시믹스", "안다르", "뮬라웨어", "HDEX", "압도"]
COLOR = {"본투윈": "#1f6fd6", "젝시믹스": "#e0703a", "안다르": "#2a9d7f",
         "뮬라웨어": "#c99a2e", "HDEX": "#c75b86", "압도": "#4f8f3a"}
SLUG = {"본투윈": "borntowin", "젝시믹스": "xexymix", "안다르": "andar",
        "뮬라웨어": "mulawear", "HDEX": "hdex", "압도": "abdo"}
NAVY = "#000000"
PRIMARY = "#000000"
BG = "#ffffff"
SURFACE = "#ffffff"
TEXT = "#000000"
MUTED = "#757575"
LINE = "#e5e5e5"
GRID = "#f0f0f0"
AXIS = "#bdbdbd"
NEUTRAL = "#9e9e9e"
C_NOW = "#000000"
C_WHY = "#0078ff"
C_NEXT = "#ff6a00"
C_UP = "#0078ff"
C_DOWN = "#f31110"
RAISED = "#f5f5f5"
AMBER = "#b7791f"
EVID = {"데이터": ("#f1f1f1", "#000000"), "보도": ("#f1f1f1", "#555555"), "가설": ("#fff3e8", "#c25100")}
FONT = "Pretendard, -apple-system, 'Apple SD Gothic Neo', sans-serif"
DIVERGING = [[0, "#e5534b"], [0.5, "#f7f7f7"], [1, "#0078ff"]]
STRENGTH = {"강함": ("#000000", "#ffffff"), "보통": ("#e5e5e5", "#000000"), "약함": ("#ffffff", "#757575")}

BRAND_INFO = {
    "본투윈": ("2021", "운동 문화를 일상복으로 푼 프리미엄 스포티 캐주얼"),
    "젝시믹스": ("2015", "국내 애슬레저 매출 1위, 골프·러닝으로 확장"),
    "안다르": ("2015", "2021년 인수 뒤 흑자로 반등한 레깅스 강자"),
    "뮬라웨어": ("2013", "애슬레저 1세대, 2025년 회생 신청"),
    "HDEX": ("—", "김종국 모델·더현대 매장으로 뜬 가성비 짐웨어"),
    "압도": ("—", "보디빌더 대표가 만든 '힘을 파는' 짐웨어"),
}
EVENT_SYMBOL = {"창업/출시": "star", "상품라인": "circle", "콜라보": "diamond",
                "모델·마케팅": "triangle-up", "매장·채널": "square", "해외진출": "hexagon",
                "투자·인수·상장": "cross", "실적": "circle-open", "위기": "x"}

st.markdown(
    f"""
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css">
<style>
html, body, [class*="css"], .stMarkdown, button, input, textarea {{ font-family: {FONT} !important; }}
.stApp, .stApp p, .stApp div, .stApp span, .stApp li, .stApp dd, .stApp td, .stApp th, .stApp label {{ word-break: keep-all; overflow-wrap: break-word; }}
.stApp p, .stApp li, .stApp dd, .t, .body, .desc, .ev, .q, .sum, .why, .lead, .insight, .head, [data-testid="stCaptionContainer"] {{ text-wrap: pretty; }}
.stApp h1, .stApp h3, .stApp h4, .stApp h5, .find .head {{ text-wrap: balance; }}
.use .q b, .chip, .st-chip, .ev-chip, .tag {{ white-space: nowrap; }}
.block-container {{ padding-top: 3.2rem; max-width: 1280px; }}
h3 {{ letter-spacing: -.01em; color: {NAVY}; }}
.topbar {{ border-bottom: 1px solid {LINE}; padding-bottom: 18px; margin-bottom: 4px; }}
.eyebrow {{ color: {PRIMARY}; font-weight: 700; letter-spacing: .14em; font-size: .74rem; }}
.hero h1 {{ font-size: 2.3rem; font-weight: 800; line-height: 1.22; margin: .35rem 0 .5rem; letter-spacing: -.02em; color: {NAVY}; }}
.hero p {{ color: {MUTED}; margin: 0; }}
.meta-row {{ display: flex; flex-wrap: wrap; gap: 8px; margin-top: 14px; }}
.chip {{ font-size: .76rem; padding: 4px 10px; border-radius: 6px; background: {SURFACE}; border: 1px solid {LINE}; color: {MUTED}; }}
.chip b {{ color: {TEXT}; font-weight: 600; }}
.cards {{ display: grid; grid-template-columns: repeat(6, minmax(0, 1fr)); gap: 12px; margin: 1.2rem 0 .4rem; }}
@media (max-width: 1000px) {{ .cards {{ grid-template-columns: repeat(3, minmax(0, 1fr)); }} .finds, .uses {{ grid-template-columns: 1fr 1fr !important; }} }}
@media (max-width: 600px) {{ .cards, .finds, .uses {{ grid-template-columns: 1fr !important; }} .hero h1 {{ font-size: 1.6rem; }} }}
.card {{ background: {SURFACE}; border: 1px solid {LINE}; border-radius: 10px; padding: 14px; position: relative; }}
.card::before {{ content: ""; position: absolute; left: 14px; right: 14px; top: 0; height: 3px; background: var(--c); border-radius: 0 0 3px 3px; }}
.card .logo {{ height: 44px; display: flex; align-items: center; margin: 4px 0 10px; }}
.card .logo img {{ max-height: 36px; max-width: 78%; object-fit: contain; }}
.badge {{ width: 36px; height: 36px; border-radius: 8px; background: var(--c); color: #fff; font-weight: 800;
          display: flex; align-items: center; justify-content: center; }}
.card .name {{ font-weight: 700; font-size: 1rem; color: {TEXT}; }}
.card .meta {{ color: {MUTED}; font-size: .76rem; margin-top: 2px; }}
.card .tag {{ display: inline-block; margin-top: 8px; font-size: .72rem; padding: 2px 8px; border-radius: 4px;
              background: #eaf0fb; color: {PRIMARY}; font-weight: 600; }}
.card .desc {{ color: {MUTED}; font-size: .8rem; margin-top: 8px; line-height: 1.45; }}
.section-label {{ color: {MUTED}; font-size: .78rem; font-weight: 700; letter-spacing: .08em; margin: 1.2rem 0 .5rem; }}
.uses {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; }}
.use {{ background: {SURFACE}; border: 1px solid {LINE}; border-radius: 10px; padding: 14px 16px; }}
.use .who {{ font-weight: 700; color: {NAVY}; font-size: .92rem; }}
.use .q {{ color: {MUTED}; font-size: .83rem; margin-top: 4px; line-height: 1.5; }}
.finds {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; margin: .2rem 0 1rem; }}
.find {{ background: {SURFACE}; border: 1px solid {LINE}; border-radius: 10px; padding: 16px 18px; }}
.find .no {{ color: {MUTED}; font-weight: 700; font-size: .72rem; letter-spacing: .1em; }}
.find .big {{ font-size: 1.65rem; font-weight: 800; margin: 6px 0 2px; color: {NAVY}; letter-spacing: -.01em; }}
.find .head {{ font-weight: 700; margin-bottom: 6px; line-height: 1.35; color: {TEXT}; }}
.find .body {{ color: {MUTED}; font-size: .84rem; line-height: 1.55; }}
.kpi {{ background: {SURFACE}; border: 1px solid {LINE}; border-radius: 10px; padding: 16px 18px; height: 100%; }}
.kpi .label {{ color: {MUTED}; font-size: .8rem; }}
.kpi .value {{ font-size: 1.7rem; font-weight: 800; margin-top: 4px; color: {NAVY}; }}
.kpi .sub {{ color: {MUTED}; font-size: .8rem; margin-top: 2px; }}
.insight {{ background: #eaf0fb; border-left: 3px solid {PRIMARY}; padding: 10px 14px; margin: .4rem 0 1rem; color: {TEXT};
            line-height: 1.6; border-radius: 0 6px 6px 0; }}
.verdict {{ background: {SURFACE}; border: 1px solid {LINE}; border-top: 3px solid {PRIMARY}; border-radius: 10px; padding: 18px 20px; }}
.verdict h4 {{ margin: 0 0 4px; color: {NAVY}; }}
.verdict .lead {{ color: {MUTED}; font-size: .82rem; margin-bottom: 10px; }}
.vi {{ padding: 9px 0; border-top: 1px solid {GRID}; font-size: .88rem; line-height: 1.5; color: {TEXT}; }}
.vi .ev {{ color: {MUTED}; font-size: .78rem; }}
.st-chip {{ display: inline-block; font-size: .68rem; font-weight: 700; padding: 1px 7px; border-radius: 4px; margin-left: 6px; vertical-align: 1px; }}
.profile-logo img {{ max-height: 60px; max-width: 220px; }}
.tl {{ border-left: 2px solid {LINE}; margin-left: 6px; padding-left: 16px; }}
.tl .it {{ margin-bottom: 12px; position: relative; color: {TEXT}; }}
.tl .it::before {{ content: ""; position: absolute; left: -22px; top: 6px; width: 10px; height: 10px; border-radius: 50%; background: var(--c); box-shadow: 0 0 0 2px {BG}; }}
.tl .d {{ color: {MUTED}; font-size: .78rem; }}
.tl .t {{ font-size: .7rem; padding: 1px 7px; border-radius: 4px; background: #eaf0fb; color: {PRIMARY}; margin-left: 6px; }}
.stTabs [data-baseweb="tab-list"] {{ gap: 6px; border-bottom: 1px solid {LINE}; }}
.stTabs [data-baseweb="tab"] {{ font-weight: 600; }}
.arch {{ background: {SURFACE}; border: 1px solid {LINE}; border-radius: 10px; padding: 16px 18px; height: 100%; }}
.arch h5 {{ margin: 0; color: {NAVY}; font-size: 1.02rem; }}
.arch .sum {{ color: {MUTED}; font-size: .82rem; margin: 4px 0 6px; line-height: 1.5; }}
.story {{ border-top: 1px solid {GRID}; padding-top: 14px; margin-top: 14px; }}
.story .lg img {{ max-height: 26px; max-width: 120px; }}
.story .hero {{ font-weight: 800; color: {TEXT}; font-size: 1rem; margin-top: 8px; line-height: 1.35; }}
.story .proof {{ font-size: .74rem; color: {PRIMARY}; background: #eaf0fb; display: inline-block; padding: 1px 7px; border-radius: 4px; margin-top: 4px; }}
.story dl {{ margin: 8px 0 0; font-size: .82rem; line-height: 1.5; }}
.story dt {{ color: {MUTED}; font-size: .72rem; font-weight: 700; letter-spacing: .04em; margin-top: 6px; }}
.story dd {{ margin: 0; color: {TEXT}; }}
.story .src {{ font-size: .72rem; }}
.story .src a {{ color: {MUTED}; }}
.ev-chip {{ display: inline-block; font-size: .68rem; font-weight: 700; padding: 1px 7px; border-radius: 4px; letter-spacing: .02em; margin-right: 6px; }}
.thesis {{ background: #173566; color: #fff; border: 1px solid {LINE}; border-radius: 10px; padding: 18px 22px; margin: .4rem 0 1rem; }}
.thesis .k {{ font-size: .72rem; letter-spacing: .12em; font-weight: 700; color: #b9c9e3; }}
.thesis .t {{ font-size: 1.12rem; line-height: 1.6; margin-top: 4px; }}
.thesis b {{ color: #fff; border-bottom: 2px solid #6aabf1; }}
.phase {{ display: flex; align-items: baseline; gap: 8px; margin: 0 0 8px; }}
.phase .pk {{ font-weight: 800; color: {NAVY}; font-size: 1.05rem; }}
.phase .pq {{ color: {MUTED}; font-size: .84rem; }}
.find + .find {{ margin-top: 10px; }}
.trend {{ background: {SURFACE}; border: 1px solid {LINE}; border-radius: 10px; padding: 16px; height: 100%; }}
.trend h5 {{ margin: 8px 0 2px; color: {NAVY}; font-size: 1rem; }}
.trend .what {{ color: {MUTED}; font-size: .78rem; }}
.trend .why {{ color: {TEXT}; font-size: .84rem; line-height: 1.55; margin-top: 8px; }}
.trend dl, .story dl {{ margin: 8px 0 0; font-size: .82rem; line-height: 1.5; }}
.trend dt {{ color: {MUTED}; font-size: .72rem; font-weight: 700; margin-top: 6px; }}
.trend dd {{ margin: 0; color: {TEXT}; }}
.pimg {{ background: #f1f3f6; border-radius: 8px; margin-top: 10px; aspect-ratio: 4 / 3; display: flex; align-items: center; justify-content: center; overflow: hidden; }}
.pimg img {{ height: 100%; width: 100%; object-fit: contain; }}
.pimg-lg {{ background: #f1f3f6; border-radius: 10px; aspect-ratio: 1 / 1; display: flex; align-items: center; justify-content: center; overflow: hidden; border: 1px solid {LINE}; }}
.pimg-lg img {{ width: 100%; height: 100%; object-fit: contain; }}
/* ── pro layer ── */
[data-testid="stHeader"] {{ background: transparent !important; }}
.stApp {{ background:
   radial-gradient(1200px 500px at 85% -10%, rgba(37,99,235,.07), transparent 60%),
   radial-gradient(900px 420px at -5% 5%, rgba(8,145,178,.06), transparent 60%),
   {BG} !important; }}
.hero.topbar {{ border-bottom: 1px solid rgba(15,23,42,.08); }}
.eyebrow {{ color: {C_NEXT} !important; display: flex; align-items: center; gap: 8px; }}
.pulse {{ width: 7px; height: 7px; border-radius: 50%; background: {C_UP}; box-shadow: 0 0 0 4px rgba(52,211,153,.18); display: inline-block; }}
.hero h1 .grad {{ background: linear-gradient(90deg, {C_NOW}, {C_WHY} 55%, {C_NEXT}); -webkit-background-clip: text; background-clip: text; color: transparent; }}
.chip {{ background: #ffffff !important; border-color: rgba(15,23,42,.09) !important; }}
.card {{ background: linear-gradient(180deg, color-mix(in srgb, var(--c) 6%, {SURFACE}), {SURFACE} 55%) !important; border-color: rgba(15,23,42,.08) !important;
         box-shadow: 0 1px 0 rgba(255,255,255,.6) inset, 0 8px 24px rgba(15,23,42,.06); }}
.card .tag {{ background: color-mix(in srgb, var(--c) 22%, transparent) !important; color: color-mix(in srgb, var(--c) 75%, black) !important; }}
.thesis {{ background: linear-gradient(120deg, #0f172a 0%, #13294b 55%, #1e3a8a 100%) !important; border: 1px solid rgba(15,23,42,.09) !important; position: relative; overflow: hidden; }}
.thesis::after {{ content: ""; position: absolute; left: 0; top: 0; bottom: 0; width: 4px; background: linear-gradient({C_NOW}, {C_WHY}, {C_NEXT}); }}
.thesis .k {{ color: {C_NEXT} !important; }}
.thesis b {{ border-bottom-color: {C_NEXT} !important; }}
.phasebox .phase {{ padding-bottom: 8px; border-bottom: 2px solid var(--pc); margin-bottom: 12px; }}
.phasebox .dot {{ width: 9px; height: 9px; border-radius: 50%; background: var(--pc); display: inline-block; align-self: center; }}
.phasebox .pk {{ color: var(--pc) !important; }}
.phasebox .find {{ border-left: 3px solid var(--pc); background: linear-gradient(90deg, color-mix(in srgb, var(--pc) 8%, {SURFACE}), {SURFACE} 60%) !important; }}
.phasebox .find .big {{ color: var(--pc) !important; font-size: 1.9rem !important; }}
.find, .verdict, .use, .kpi, .trend, .arch {{ border-color: rgba(15,23,42,.08) !important; box-shadow: 0 8px 24px rgba(15,23,42,.05); }}
.verdict {{ background: linear-gradient(180deg, {RAISED}, {SURFACE}) !important; border-top: 3px solid {C_NEXT} !important; }}
.verdict h4 {{ color: {NAVY} !important; }}
.vi b {{ color: {NAVY}; }}
.use .who {{ color: {C_NOW} !important; }}
.stTabs [aria-selected="true"] {{ color: {C_NEXT} !important; }}
.stTabs [data-baseweb="tab-highlight"] {{ background: {C_NEXT} !important; }}
.foot {{ color: {MUTED}; font-size: .76rem; border-top: 1px solid {LINE}; margin-top: 2rem; padding-top: 12px; }}
/* ── musinsa layer ── */
.stApp {{ background: #ffffff !important; overflow-x: hidden; }}
[data-testid="stHeader"] {{ background: #000 !important; }}
[data-testid="stHeader"] * {{ color: #fff !important; }}
.block-container {{ padding-top: calc(3.75rem - 16px) !important; }}
.mbar {{ background: #000; color: #fff; margin: 0 calc(50% - 50vw); padding: 14px calc(50vw - 50% + 0px); display: flex; align-items: center; gap: 22px;
        font-weight: 800; font-size: 1.05rem; letter-spacing: .01em; }}
.mbar span {{ color: #fff; }}
.mbar .ham {{ font-weight: 400; font-size: 1.2rem; }}
.mbar .sep {{ width: 1px; height: 18px; background: #666; margin: 0 -6px; }}
.mbar .right {{ margin-left: auto; font-size: .82rem; font-weight: 500; color: #9e9e9e !important; }}
@media (max-width: 500px) {{ .mbar .right {{ display: none; }} }}
.hero.topbar {{ border-bottom: 0 !important; padding-top: 22px; }}
.hero h1 {{ font-weight: 800 !important; color: #000 !important; }}
.chip {{ background: transparent !important; border: 0 !important; padding: 0 !important; color: #9e9e9e !important; font-size: .86rem !important; border-radius: 0 !important; margin-right: 10px; }}
.chip b {{ color: #555 !important; font-weight: 600 !important; }}
.cards {{ gap: 0 !important; border-top: 1px solid #e5e5e5; }}
.card {{ background: #fff !important; border: 0 !important; border-right: 1px solid #f0f0f0 !important; border-radius: 0 !important; box-shadow: none !important; padding: 0 0 16px !important; }}
.card:last-child {{ border-right: 0 !important; }}
.card::before {{ display: none; }}
.card .logo {{ background: #f4f4f4; height: 96px !important; margin: 0 0 12px !important; justify-content: center; }}
.card .name, .card .meta, .card .tag, .card .desc {{ margin-left: 14px; margin-right: 14px; }}
.card .name {{ font-size: .95rem !important; font-weight: 800 !important; }}
.card .tag {{ background: transparent !important; padding: 0 !important; color: var(--c) !important; font-weight: 700; }}
.card .tag::before {{ content: "●"; margin-right: 4px; font-size: .6rem; vertical-align: 2px; }}
.card .desc {{ color: #000 !important; }}
.stTabs [data-baseweb="tab-list"] {{ gap: 22px !important; border-bottom: 1px solid #e5e5e5 !important; }}
.stTabs [data-baseweb="tab"] {{ color: #757575 !important; font-weight: 500 !important; font-size: 1.02rem; }}
.stTabs [aria-selected="true"] {{ color: #000 !important; font-weight: 800 !important; }}
.stTabs [data-baseweb="tab-highlight"] {{ background: #000 !important; height: 2px !important; }}
.thesis {{ background: #000 !important; border: 0 !important; border-radius: 0 !important; }}
.thesis::after {{ display: none; }}
.thesis .k {{ color: #9e9e9e !important; }}
.thesis b {{ border-bottom: 0 !important; color: #fff; background: linear-gradient(transparent 62%, rgba(0,120,255,.55) 62%); }}
.phasebox .phase {{ background: #f1f1f1; padding: 12px 14px !important; border-bottom: 0 !important; margin-bottom: 0 !important; }}
.phasebox .pk {{ color: #000 !important; }}
.phasebox .dot {{ background: var(--pc) !important; }}
.phasebox .find {{ background: #fff !important; border: 0 !important; border-bottom: 1px solid #e5e5e5 !important; border-radius: 0 !important; box-shadow: none !important; margin-top: 0 !important; }}
.phasebox .find .big {{ color: #000 !important; }}
.phasebox .find .big::after {{ content: ""; display: block; width: 18px; height: 2px; background: var(--pc); margin-top: 6px; }}
.find, .verdict, .use, .kpi, .trend, .arch {{ border-radius: 0 !important; box-shadow: none !important; border-color: #e5e5e5 !important; }}
.verdict {{ background: #fff !important; border: 0 !important; border-top: 2px solid #000 !important; padding: 14px 0 !important; }}
.vi {{ border-top-color: #f0f0f0 !important; }}
.st-chip {{ border-radius: 2px !important; border: 1px solid #000; }}
.ev-chip {{ border-radius: 2px !important; }}
.section-label {{ color: #000 !important; font-size: .95rem !important; letter-spacing: 0 !important; background: #f1f1f1; padding: 10px 14px; }}
.uses {{ gap: 0 !important; }}
.use {{ border: 0 !important; border-right: 1px solid #f0f0f0 !important; }}
.use .who {{ color: #000 !important; font-weight: 800 !important; }}
.insight, .story .proof, .tl .t {{ background: #f1f1f1 !important; color: #000 !important; border-radius: 0 !important; }}
.insight {{ border-left-color: #000 !important; }}
.pimg, .pimg-lg {{ border-radius: 0 !important; }}
.pulse {{ display: none; }}
@media (max-width: 600px) {{ .cards {{ grid-template-columns: 1fr 1fr !important; }} .card .logo {{ height: 72px !important; }} .card {{ border-bottom: 1px solid #f0f0f0 !important; }} }}
.arch {{ padding: 0 !important; }}
.arch h5 {{ background: #000; color: #fff !important; padding: 11px 16px; font-size: .98rem !important; }}
.arch .sum {{ padding: 10px 16px 0; }}
.arch .story {{ margin-left: 16px; margin-right: 16px; }}
.arch > *:last-child {{ margin-bottom: 16px; }}
.kpi {{ border-width: 0 0 0 0 !important; background: #f5f5f5 !important; }}
.pimg-lg {{ border: 0 !important; }}
</style>
""",
    unsafe_allow_html=True,
)


@st.cache_data
def load():
    names = ["monthly_index", "segment_share", "positioning", "kdh_weekly", "events", "revenue",
             "sports", "sports_participation", "products", "seasonality", "event_effects",
             "baseline", "sos", "validation", "brand_story", "outlook"]
    return {n: pd.read_csv(DATA / f"{n}.csv") for n in names if (DATA / f"{n}.csv").exists()}


d = load()


def style(fig, height=420, ytitle=None, xtitle=None, hover="x unified"):
    fig.update_layout(
        height=height, font=dict(family=FONT, color=TEXT, size=13),
        margin=dict(l=8, r=8, t=24, b=8), hovermode=hover,
        hoverlabel=dict(bgcolor=SURFACE, bordercolor=LINE, font=dict(family=FONT, color=TEXT)),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, font=dict(color=MUTED)),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    )
    fig.update_xaxes(showgrid=False, linecolor=AXIS, tickfont=dict(color=MUTED), title=xtitle,
                     title_font=dict(color=MUTED))
    fig.update_yaxes(gridcolor=GRID, zeroline=False, tickfont=dict(color=MUTED), title=ytitle,
                     title_font=dict(color=MUTED))
    return fig


def chart(fig):
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})


def rgba(hex_color, a):
    return "rgba({},{},{},{})".format(*(int(hex_color[i:i + 2], 16) for i in (1, 3, 5)), a)


@st.cache_data
def logo_b64(slug):
    f = LOGOS / f"{slug}.png"
    return base64.b64encode(f.read_bytes()).decode() if f.exists() else None


def logo_html(brand):
    b64 = logo_b64(SLUG[brand])
    if b64:
        return f'<img src="data:image/png;base64,{b64}" alt="{brand} 로고">'
    return f'<div class="badge">{brand[0]}</div>'


@st.cache_data
def product_b64(slug):
    f = PRODUCTS / f"{slug}.jpg"
    return base64.b64encode(f.read_bytes()).decode() if f.exists() else None


def product_html(brand, cls="pimg"):
    b64 = product_b64(SLUG[brand])
    return f'<div class="{cls}"><img src="data:image/jpeg;base64,{b64}" alt="{brand} 대표 라인 이미지"></div>' if b64 else ""


def kpi(col, label, value, sub=""):
    col.markdown(f'<div class="kpi"><div class="label">{label}</div><div class="value">{value}</div>'
                 f'<div class="sub">{sub}</div></div>', unsafe_allow_html=True)


def evid(kind):
    bg, fg = EVID[kind]
    return f'<span class="ev-chip" style="background:{bg};color:{fg}">{kind}</span>'


def strength(level):
    bg, fg = STRENGTH[level]
    return f'<span class="st-chip" style="background:{bg};color:{fg}">근거 {level}</span>'


# ── 공통 계산 ───────────────────────────────────────────
share = d["segment_share"]
seg = share.pivot(index="brand", columns="segment", values="share")
pos = d["positioning"].set_index("brand")
mon = d["monthly_index"]
pr = d.get("products")
psum = (pr.groupby("brand").agg(sale=("sale_price", "median"), disc=("discount_pct", "median"), n=("product", "size"))
        if pr is not None else pd.DataFrame())
rev = d["revenue"]
eff = d.get("event_effects")
val = d.get("validation")
sea = d.get("seasonality")
sp = d.get("sports")


def yoy(b):
    s = mon[mon.brand == b].set_index("month")["index"]
    last, prev = s.loc["2025-11":"2026-10"].mean(), s.loc["2024-11":"2025-10"].mean()
    return (last / prev - 1) * 100 if prev else float("nan")


def tilt_label(b):
    p = pos.loc[b]
    sex = "남성" if p.male_tilt > 0.5 else ("여성" if p.male_tilt < -0.5 else "남녀")
    age = "20대" if p.young_tilt > 0.3 else ("30대" if p.young_tilt < -0.3 else "20·30대")
    return f"{sex} · {age}"


female_top = seg.loc["안다르", "여성"] + seg.loc["젝시믹스", "여성"]
male_gym = seg.loc["본투윈", "남성"] + seg.loc["HDEX", "남성"] + seg.loc["압도", "남성"]
young_gym = seg.loc["본투윈", "19-29"] + seg.loc["HDEX", "19-29"] + seg.loc["압도", "19-29"]
n_eff = len(eff) if eff is not None else 0
n_out = int(eff.outside.sum()) if eff is not None else 0
n_out_up = int((eff.outside & (eff.change_pct > 0)).sum()) if eff is not None else 0
r_all = val["revenue_억원"].corr(val["search"]) if val is not None else float("nan")
gym = sp.set_index("sport").loc["보디빌딩(헬스)"] if sp is not None else None
run = sp.set_index("sport").loc["달리기"] if sp is not None else None

# ── 머리말 ─────────────────────────────────────────────
st.markdown(
    f"""
<div class="mbar"><b>K-WELLNESS BRAND MAP</b><span class="right">2016–2026 · 6 BRANDS</span></div>
<div class="hero topbar">
  <h1>대한민국 웰니스 브랜드 6 심층 비교</h1>
  <p><b style="color:#000">누구를 잡고, 무엇으로 성장했으며, 다음은 어디로 가나?</b> 애슬레저·짐웨어 브랜드 6개를 공개 데이터로 비교하고, 한국의 운동 변화와 엮어 다음 기회를 짚었어요.</p>
  <div class="meta-row">
    <span class="chip">검색 <b>네이버 데이터랩</b> · 2016.01–2026.10</span>
    <span class="chip">가격 <b>무신사</b> · {len(pr) if pr is not None else 0}개 상품 · 2026.11.25</span>
    <span class="chip">매출 <b>공시·증권사 리포트</b> · 2018–2025</span>
    <span class="chip">이벤트 <b>언론 보도</b> · {len(d['events'])}건</span>
    <span class="chip">시장 <b>국민생활체육조사</b> · 2019–2025</span>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

cards = "".join(
    f"""<div class="card" style="--c:{COLOR[b]}">
  <div class="logo">{logo_html(b)}</div>
  <div class="name">{b}</div>
  <div class="meta">설립 {BRAND_INFO[b][0]}</div>
  <div class="tag">주 고객 {tilt_label(b)}</div>
  <div class="desc">{BRAND_INFO[b][1]}</div>
</div>"""
    for b in BRANDS
)
st.markdown(f'<div class="cards">{cards}</div>', unsafe_allow_html=True)

TABS = ["한눈에 보기", "브랜드 스토리", "① 누구를 잡았나", "② 무엇으로 컸나", "③ 다음은 어디로", "브랜드 프로필", "데이터·방법"]
T = dict(zip(TABS, st.tabs(TABS)))

# ── 한눈에 보기 ────────────────────────────────────────
with T["한눈에 보기"]:
    st.markdown(
        f'<div class="thesis"><div class="k">한 줄 결론</div>'
        f'<div class="t">시장의 몸집은 여전히 <b>여성·레깅스 중심 애슬레저</b>가 크지만, 성장의 무게중심은 '
        f'<b>헬스·러닝을 하는 남성 20대</b>로 옮겨 가고 있어요. 그런데 이 수요를 먼저 잡은 짐웨어 3사의 검색 점유율은 2024년을 정점으로 주춤해요. '
        f'운동 문화를 가진 다음 브랜드가 들어올 자리가 열려 있다는 뜻이에요.</div></div>',
        unsafe_allow_html=True)

    sos_now = d["sos"].set_index("month") if d.get("sos") is not None else None
    gsum = sos_now[["본투윈", "HDEX", "압도"]].sum(axis=1) if sos_now is not None else pd.Series(dtype=float)
    gym_sos_22 = gsum.loc["2022-01":"2022-12"].mean()
    gym_sos_24 = gsum.loc["2024-01":"2024-12"].mean()
    gym_sos_26 = gsum.loc["2025-11":"2026-10"].mean()
    cols3 = [
        ("지금", "누가 시장을 쥐고 있나", [
            ("데이터", f"{female_top:.0f}%", "여성 시장은 2강이 굳혔다", f"여성 검색의 {female_top:.0f}%가 안다르·젝시믹스예요."),
            ("데이터", f"{male_gym:.0f}%", "남성 시장은 아직 열려 있다", f"남성 검색에서 짐웨어 3사가 {male_gym:.0f}%, 20대에선 {young_gym:.0f}%를 가져왔어요."),
        ]),
        ("왜", "무엇이 성장을 만들었나", [
            ("데이터", f"{psum.loc['본투윈', 'disc']:.0f}% vs {psum.loc['HDEX', 'disc']:.0f}%", "할인율이 포지션을 가른다",
             f"같은 남성 20대를 노려도 본투윈은 정가, HDEX는 할인으로 팔아요(무신사 {len(pr)}개 상품)."),
            ("데이터", f"{n_out_up} / {n_eff}건", "한 방 이벤트는 잘 안 통했다",
             f"이벤트 {n_eff}건 중 검색을 평소 범위 위로 올린 건 부정 이슈 {n_out_up}건뿐. 대신 모든 브랜드가 5–8월에 정점이에요."),
        ]),
        ("다음", "어디로 가나", [
            ("데이터", f"+{gym.rate_2025 - gym.rate_2024:.1f}%p", "헬스·달리기가 가장 빨리 큰다",
             f"규칙적으로 운동하는 사람 중 헬스 {gym.rate_2024}→{gym.rate_2025}%, 달리기 {run.rate_2024}→{run.rate_2025}%. 10개 종목 중 가장 큰 증가예요."),
            ("데이터", f"{gym_sos_24:.0f}% → {gym_sos_26:.0f}%", "그런데 기존 짐웨어는 주춤",
             f"짐웨어 3사의 검색 점유율은 2022년 {gym_sos_22:.0f}%에서 2024년 {gym_sos_24:.0f}%까지 컸다가 최근 {gym_sos_26:.0f}%로 내려왔어요. 늘어난 운동 인구를 잡을 자리가 비어 있어요."),
        ]),
    ]
    cc = st.columns(3, gap="medium")
    for col, (k, q, cards_) in zip(cc, cols3):
        html = "".join(
            f'<div class="find"><div class="no">{evid(ev)}</div><div class="big">{big}</div><div class="head">{h}</div><div class="body">{body}</div></div>'
            for ev, big, h, body in cards_)
        pc = {"지금": C_NOW, "왜": C_WHY, "다음": C_NEXT}[k]
        col.markdown(f'<div class="phasebox" style="--pc:{pc}"><div class="phase"><span class="dot"></span><div class="pk">{k}</div><div class="pq">{q}</div></div>{html}</div>', unsafe_allow_html=True)

    st.write("")
    left, right = st.columns([1.1, 1], gap="large")
    with left:
        st.markdown("**최근 1년 검색 관심 변화 (전년 대비)**")
        yy = pd.Series({b: yoy(b) for b in BRANDS}).sort_values()
        fig = go.Figure(go.Bar(
            x=yy.values, y=yy.index, orientation="h",
            marker=dict(color=["#111111" if v > 0.5 else ("#c8c8c8" if v < -0.5 else "#e5e5e5") for v in yy.values], line=dict(color=SURFACE, width=2)),
            text=[f"{v:+.0f}%" for v in yy.values], textposition="outside", textfont=dict(color=[C_UP if v > 0.5 else (C_DOWN if v < -0.5 else MUTED) for v in yy.values], size=13),
            hovertemplate="%{y} %{x:+.1f}%<extra></extra>",
        ))
        style(fig, height=330, hover="closest")
        fig.add_vline(x=0, line=dict(color=AXIS, width=1))
        fig.update_xaxes(showgrid=True, gridcolor=GRID, ticksuffix="%", range=[min(yy.min() * 1.35, -10), max(yy.max() * 1.35, 10)])
        chart(fig)
        st.caption("2025.11–2026.10 평균 검색 지수 ÷ 2024.11–2025.10 평균 − 1. 압도는 검색량이 매우 작아 변화율이 크게 흔들려요. "
                   "6개 중 5개가 줄거나 제자리라, 브랜드 화제성만으로 크던 시기는 지났다고 볼 수 있어요.")
    with right:
        items = [
            ("강함", "남성 20대 · 헬스/러닝을 겨냥한다",
             f"남성 검색 {male_gym:.0f}%, 20대 {young_gym:.0f}%를 짐웨어 브랜드가 가져왔고, 헬스·달리기 참여가 가장 빨리 늘어요."),
            ("강함", "출시와 캠페인은 4–5월에",
             "6개 브랜드 모두 5–8월 정점, 12–2월 바닥. 5년치 월별 패턴이 같아요."),
            ("보통", "가격보다 할인 정책으로 포지션을 지킨다",
             f"프리미엄(본투윈)은 할인 {psum.loc['본투윈', 'disc']:.0f}%, 가성비(HDEX·젝시믹스)는 30%대. 하루치 무신사 상품 {len(pr)}개 기준이에요."),
            ("보통", "단발 이벤트보다 반복되는 운동 달력",
             f"단발 이벤트 {n_eff}건 중 검색을 끌어올린 건 {n_out_up}건. 크루·대회처럼 매 시즌 돌아오는 접점을 브랜드 달력으로 삼는 편이 안전해요."),
            ("약함", "성장보다 수익 구조",
             "뮬라웨어는 판관비가 매출의 약 60%까지 올라간 뒤 2025년 회생을 신청했어요. 사례 1건이라 일반화는 조심해야 해요."),
        ]
        html = "".join(f'<div class="vi"><b>{i + 1}. {t}</b>{strength(lv)}<div class="ev">{ev}</div></div>'
                       for i, (lv, t, ev) in enumerate(items))
        st.markdown(f'<div class="verdict"><h4>실무 시사점</h4>'
                    f'<div class="lead">새 웰니스 브랜드를 만든다면. 근거 강도 = 데이터 양과 기간, 다른 해석의 여지를 함께 본 판단이에요.</div>{html}</div>',
                    unsafe_allow_html=True)

    st.markdown('<div class="section-label">누가, 어디를 보면 되나</div>', unsafe_allow_html=True)
    st.markdown(
        """<div class="uses">
<div class="use"><div class="who">브랜드 기획·MD</div><div class="q">경쟁사의 고객층과 가격·할인 → <b>① 누구를 잡았나</b>, 브랜드별 대표상품과 성장 공식 → <b>브랜드 스토리</b></div></div>
<div class="use"><div class="who">마케팅</div><div class="q">검색 점유율, 이벤트 전후 변화, 출시 시즌 → <b>② 무엇으로 컸나</b></div></div>
<div class="use"><div class="who">창업·투자 검토</div><div class="q">운동 참여 변화와 다음 흐름, 브랜드별 준비도 → <b>③ 다음은 어디로</b></div></div>
</div>""",
        unsafe_allow_html=True,
    )

# ── 브랜드 스토리 ──────────────────────────────────────
story = d.get("brand_story")
ARCH = [
    ("원단 기술·확장형", "레깅스 하나로 시작해 자체 원단으로 차별화하고, 카테고리와 해외로 넓혀 간 1세대 애슬레저.", ["젝시믹스", "안다르", "뮬라웨어"]),
    ("볼륨·가성비형", "운동하는 사람이 매일 입는 기본템을 묶음·할인으로 많이 파는 방식.", ["HDEX"]),
    ("문화·커뮤니티형", "옷보다 '운동하는 사람의 태도'를 판다. 커뮤니티와 격투기·짐 콜라보 드롭으로 팬을 만든다.", ["본투윈", "압도"]),
]


def story_html(b):
    r = story.set_index("brand").loc[b]
    return (f'<div class="story"><div class="lg">{logo_html(b)}</div>{product_html(b)}'
            f'<div class="hero">{r.hero_product}</div>{evid("데이터" if "무신사" in r.hero_evidence else "보도")}<span class="proof">{r.hero_evidence}</span>'
            f'<dl><dt>정체성 · 가치</dt><dd>{r.identity}</dd><dt>성장 방식</dt><dd>{r.growth}</dd>'
            f'<dt>데이터로 본 결과</dt><dd>{r.data_link}</dd>'
            f'<dt>기회 · 위험</dt><dd>＋ {r.opportunity}<br>－ {r.risk}</dd></dl>'
            f'<div class="src"><a href="{r.source}" target="_blank">출처</a></div></div>')


with T["브랜드 스토리"]:
    st.markdown("### 대표상품으로 읽는 세 가지 성장 공식")
    st.markdown('<div class="insight">대표상품을 보면 브랜드가 무엇을 파는지 보여요. 젝시믹스·안다르·뮬라웨어는 <b>원단 기술</b>을, '
                "HDEX는 <b>매일 입는 기본템의 가격</b>을, 본투윈·압도는 <b>운동하는 사람의 태도와 문화</b>를 팔아요. "
                "같은 레깅스 출신이라도 안다르·젝시믹스는 확장에 성공했고, 직접 운영 비용이 컸던 뮬라웨어는 회생 신청까지 갔어요.</div>",
                unsafe_allow_html=True)
    if story is not None:
        cols = st.columns(3, gap="medium")
        for col, (name, desc, members) in zip(cols, ARCH):
            col.markdown(f'<div class="arch"><h5>{name}</h5><div class="sum">{desc}</div>'
                         + "".join(story_html(b) for b in members) + "</div>", unsafe_allow_html=True)
        st.caption("대표상품: 회사·언론이 발표한 누적 판매 기록이 있으면 그것을, 없으면 2026.11.25 무신사 리뷰 수 최다 상품을 기준으로 골랐어요. "
                   "판매 수치는 회사 발표라 기준 시점이 서로 달라요. 정체성은 공식 슬로건·인터뷰 기사를 요약했어요. "
                   "상품 사진은 각 브랜드 공식 판매 페이지의 대표 라인 이미지이며, 학습·포트폴리오 목적의 식별 용도로만 사용했어요.")

# ── ① 누구를 잡았나 ──────────────────────────────────
with T["① 누구를 잡았나"]:
    st.markdown("### 같은 시장, 다른 고객")
    st.markdown(f'<div class="insight">여성 검색은 안다르·젝시믹스가 <b>{female_top:.0f}%</b>를 쥔 2강 구도예요. '
                f'남성 검색은 더 나뉘어 있고, 짐웨어 브랜드(본투윈·HDEX·압도)가 <b>{male_gym:.0f}%</b>까지 올라왔어요. '
                "신생 브랜드가 들어갈 틈은 남성·20대 쪽에 있어요.</div>", unsafe_allow_html=True)
    left, right = st.columns([1.1, 1], gap="large")
    with left:
        st.markdown("**포지셔닝 지도**")
        fig = go.Figure()
        fig.add_shape(type="rect", x0=0, x1=5, y0=0, y1=2, fillcolor="#f5f5f5", line_width=0, layer="below")
        fig.add_shape(type="rect", x0=-2, x1=0, y0=-1, y1=0, fillcolor="#f5f5f5", line_width=0, layer="below")
        for b, r in pos.iterrows():
            unstable = b == "압도"
            fig.add_trace(go.Scatter(
                x=[r.male_tilt], y=[r.young_tilt], mode="markers+text", name=b,
                marker=dict(size=18, color=COLOR[b], opacity=0.5 if unstable else 1, line=dict(width=2, color=SURFACE)),
                text=[f"<b>{b}</b>" + (" *" if unstable else "")], textposition="top center", textfont=dict(color=TEXT),
                hovertemplate=f"<b>{b}</b><br>남성 지향도 %{{x:.2f}}<br>20대 지향도 %{{y:.2f}}<extra></extra>",
            ))
        fig.add_hline(y=0, line=dict(color=AXIS, width=1))
        fig.add_vline(x=0, line=dict(color=AXIS, width=1))
        fig.add_annotation(x=4.6, y=1.9, text="남성 · 20대", showarrow=False, font=dict(color=MUTED, size=11), xanchor="right")
        fig.add_annotation(x=-1.9, y=-0.95, text="여성 · 30대", showarrow=False, font=dict(color=MUTED, size=11), xanchor="left")
        style(fig, height=460, xtitle="← 여성 중심 · 남성 중심 →", ytitle="← 30대 중심 · 20대 중심 →", hover="closest")
        fig.update_layout(showlegend=False)
        fig.update_xaxes(range=[-2, 4.7], showgrid=True, gridcolor=GRID)
        fig.update_yaxes(range=[-1, 2])
        chart(fig)
        st.caption("지향도 = log₂(남성 점유율 ÷ 여성 점유율), log₂(19–29세 ÷ 30–39세). 1이면 한쪽이 2배. * 압도는 검색량이 작아 위치가 불안정해요.")
    with right:
        st.markdown("**고객층별 검색 점유율 (최근 12개월)**")
        seg_order = ["여성", "남성", "19-29", "30-39"]
        seg_label = {"여성": "여성", "남성": "남성", "19-29": "19–29세", "30-39": "30–39세"}
        fig = go.Figure()
        for b in BRANDS:
            fig.add_trace(go.Bar(
                y=[seg_label[x] for x in seg_order], x=seg.loc[b, seg_order].values, name=b, orientation="h",
                marker=dict(color=COLOR[b], line=dict(color=SURFACE, width=2)),
                hovertemplate=f"<b>{b}</b> %{{x:.1f}}%<extra></extra>",
            ))
        style(fig, height=460, xtitle="점유율(%)", hover="closest")
        fig.update_layout(barmode="stack", legend_traceorder="normal", bargap=0.35)
        fig.update_xaxes(range=[0, 100], showgrid=True, gridcolor=GRID)
        fig.update_yaxes(autorange="reversed", showgrid=False)
        chart(fig)
        st.caption("6개 브랜드 검색 합 = 100%. '안다르'는 일반 단어와 겹쳐 남성 점유율이 실제보다 높게 잡혔을 수 있어요.")

    if pr is not None:
        st.markdown("### 가격으로 본 포지셔닝")
        st.markdown(
            f'<div class="insight">판매가만 보면 브랜드끼리 많이 겹쳐요. 차이는 <b>할인</b>에서 나요. 본투윈은 할인 중앙값 '
            f'<b>{psum.loc["본투윈", "disc"]:.0f}%</b>로 정가를 지키고, 젝시믹스·HDEX는 <b>{psum.loc["젝시믹스", "disc"]:.0f}–{psum.loc["HDEX", "disc"]:.0f}%</b> 할인으로 '
            "가격 경쟁을 해요. 같은 남성 20대를 노려도 본투윈은 프리미엄, HDEX는 가성비 자리예요.</div>",
            unsafe_allow_html=True,
        )
        order = [x for x in BRANDS if x in pr.brand.unique()]
        left, right = st.columns([1.5, 1], gap="large")
        with left:
            st.markdown("**무신사 대표 상품 판매가 (점 하나 = 상품 하나)**")
            fig = go.Figure()
            for b in order:
                s = pr[pr.brand == b]
                fig.add_trace(go.Box(
                    x=s.sale_price, y=[b] * len(s), name=b, orientation="h",
                    marker=dict(color=COLOR[b], size=8, line=dict(color=SURFACE, width=1)),
                    line=dict(color=COLOR[b], width=1.5), fillcolor="rgba(0,0,0,0)",
                    boxpoints="all", jitter=0.5, pointpos=0,
                    customdata=s[["product", "discount_pct", "gender"]],
                    hovertemplate="<b>%{customdata[0]}</b><br>%{x:,.0f}원 · 할인 %{customdata[1]}% · %{customdata[2]}<extra></extra>",
                ))
            style(fig, height=340, xtitle="판매가(원)", hover="closest")
            fig.update_layout(showlegend=False)
            fig.update_xaxes(showgrid=True, gridcolor=GRID, tickformat=",")
            fig.update_yaxes(autorange="reversed", showgrid=False)
            chart(fig)
        with right:
            st.markdown("**할인율 중앙값 (%)**")
            fig = go.Figure(go.Bar(
                x=[psum.loc[b, "disc"] for b in order], y=order, orientation="h",
                marker=dict(color=[COLOR[b] for b in order], line=dict(color=SURFACE, width=2)),
                text=[f"{psum.loc[b, 'disc']:.0f}%" for b in order], textposition="outside",
                textfont=dict(color=TEXT), hovertemplate="%{y} %{x:.0f}%<extra></extra>",
            ))
            style(fig, height=340, hover="closest")
            fig.update_layout(bargap=0.45)
            fig.update_xaxes(range=[0, 45], showgrid=True, gridcolor=GRID)
            fig.update_yaxes(autorange="reversed", showgrid=False)
            chart(fig)
        st.caption("2026.11.25 무신사 브랜드 상품 목록(추천순) 상위 17–20개. 뮬라웨어는 무신사 미입점, 압도는 검색 결과가 없어 제외했어요. "
                   "하루치 표본이라 시즌·쿠폰에 따라 달라질 수 있어요.")

# ── ② 무엇으로 컸나 ──────────────────────────────────
with T["② 무엇으로 컸나"]:
    st.markdown("### 검색 점유율(Share of Search)의 변화")
    st.markdown('<div class="insight">검색 점유율은 경쟁사 대비 관심의 몫으로, 마케팅 실무에서 시장 점유율의 선행 지표로 쓰여요. '
                "2021년까지 안다르·젝시믹스·뮬라웨어 3강이던 시장에 2022년부터 짐웨어 브랜드가 끼어들었고, 뮬라웨어의 몫은 계속 줄었어요.</div>",
                unsafe_allow_html=True)
    left, right = st.columns([1.6, 1], gap="large")
    with left:
        sos = d.get("sos")
        if sos is not None:
            sos = sos.set_index("month")
            sos = sos.rolling(3, min_periods=1).mean()
            fig = go.Figure()
            for b in BRANDS:
                fig.add_trace(go.Scatter(x=sos.index, y=sos[b], name=b, mode="lines", stackgroup="one",
                                         line=dict(color=COLOR[b], width=0.5), fillcolor=rgba(COLOR[b], 0.62),
                                         hovertemplate=f"{b} %{{y:.1f}}%<extra></extra>"))
            style(fig, height=380, ytitle="검색 점유율(%)")
            fig.update_layout(legend_traceorder="normal")
            fig.update_yaxes(range=[0, 100], ticksuffix="%")
            chart(fig)
            st.caption("6개 브랜드 월별 검색 합 = 100%, 3개월 이동평균. 2018.01–2026.10.")
    with right:
        if val is not None:
            st.markdown(f"**검색 지수는 매출을 대변하나?** · 상관 {r_all:.2f}")
            fig = go.Figure()
            for b in [x for x in BRANDS if x in val.brand.unique()]:
                v = val[val.brand == b].sort_values("year")
                fig.add_trace(go.Scatter(x=v.search, y=v["revenue_억원"], name=b, mode="markers+lines",
                                         line=dict(color=rgba(COLOR[b], 0.35), width=1),
                                         marker=dict(size=10, color=COLOR[b], line=dict(color=SURFACE, width=2)),
                                         customdata=v.year, hovertemplate=f"{b} %{{customdata}}년<br>검색 %{{x:.1f}} · 매출 %{{y:,.0f}}억<extra></extra>"))
            style(fig, height=340, xtitle="연평균 검색 지수", ytitle="연매출(억 원)", hover="closest")
            chart(fig)
            st.caption(f"매출이 공개된 3개 브랜드, {len(val)}개 연도. 검색이 높은 해에 매출도 높았어요(상관 {r_all:.2f}). "
                       "다만 젝시믹스처럼 커진 브랜드는 검색이 줄어도 매출이 유지돼, 검색은 '관심'이지 '매출' 그 자체는 아니에요.")

    st.markdown("### 검색 관심의 흐름과 그 순간의 사건들")
    c1, c2, c3 = st.columns([1.1, 1.3, 0.8])
    picked = c1.multiselect("브랜드", BRANDS, default=["본투윈", "젝시믹스", "안다르", "HDEX"])
    ev_types = c2.multiselect("이벤트 유형", list(EVENT_SYMBOL), default=list(EVENT_SYMBOL))
    scale = c3.radio("척도", ["브랜드별 최고=100", "브랜드끼리 비교"],
                     help="작은 브랜드의 흐름을 보려면 '브랜드별 최고=100'을 고르세요.")
    smooth = c3.toggle("3개월 이동평균", value=True)

    m = mon.copy()
    if smooth:
        m["index"] = m.groupby("brand")["index"].transform(lambda s: s.rolling(3, min_periods=1).mean())
    if scale == "브랜드별 최고=100":
        m["index"] = m.groupby("brand")["index"].transform(lambda s: s / s.max() * 100)
    ev = d["events"].dropna(subset=["month"])
    ev = ev[ev.brand.isin(picked) & ev.event_type.isin(ev_types)]
    fig = go.Figure()
    for b in [x for x in BRANDS if x in picked]:
        s = m[m.brand == b]
        fig.add_trace(go.Scatter(x=s.month, y=s["index"], mode="lines", name=b, line=dict(color=COLOR[b], width=2),
                                 hovertemplate=f"{b} %{{y:.1f}}<extra></extra>"))
        e = ev[ev.brand == b].merge(s, on=["month", "brand"], how="left")
        if len(e):
            fig.add_trace(go.Scatter(
                x=e.month, y=e["index"], mode="markers", showlegend=False,
                marker=dict(size=12, color=COLOR[b], symbol=[EVENT_SYMBOL[t] for t in e.event_type],
                            line=dict(color=SURFACE, width=2)),
                customdata=e[["event_type", "description", "date"]],
                hovertemplate=f"<b>{b}</b> · %{{customdata[2]}}<br>%{{customdata[0]}}: %{{customdata[1]}}<extra></extra>",
            ))
    style(fig, height=440, hover="closest",
          ytitle="검색 지수 (브랜드별 최고 = 100)" if scale.startswith("브랜드별") else "검색 지수 (전체 최고 = 100)")
    chart(fig)
    st.caption("점 모양 = 이벤트 유형 (★ 창업 · ● 상품라인 · ◆ 콜라보 · ▲ 모델·마케팅 · ■ 매장 · ⬢ 해외 · ✚ 투자·인수 · ✕ 위기). 점에 마우스를 올리면 내용이 보여요.")

    st.markdown("### 어떤 사건이 검색 흐름을 바꿨나")
    st.markdown(f'<div class="insight">브랜드마다 검색은 원래 출렁여요. 그래서 각 이벤트의 변화를 그 브랜드의 <b>평소 변동 범위</b>(회색 띠)와 겹쳐 봤어요. '
                f"{n_eff}건 중 띠를 벗어난 건 <b>{n_out}건</b>이고, 위로 벗어난 건 안다르의 2021년 오너 리스크 보도 {n_out_up}건뿐이에요. "
                "부정 이슈도 검색은 올린다는 점에서, 검색 증가가 곧 좋은 신호는 아니에요.</div>", unsafe_allow_html=True)
    left, right = st.columns([1.5, 1], gap="large")
    with left:
        if eff is not None:
            e2 = eff.sort_values("change_pct")
            labels = [f"{r.brand} · {r.description[:24]}{'…' if len(r.description) > 24 else ''}" for r in e2.itertuples()]
            fig = go.Figure()
            fig.add_trace(go.Bar(x=e2.p90 - e2.p10, base=e2.p10, y=labels, orientation="h", name="평소 변동 범위(10–90%)",
                                 marker=dict(color="#e4e8ef"), width=0.8, hoverinfo="skip"))
            fig.add_trace(go.Bar(
                x=e2.change_pct, y=labels, orientation="h", name="이벤트 전후 변화", width=0.45,
                marker=dict(color=[COLOR[b] for b in e2.brand], opacity=[1 if o else 0.45 for o in e2.outside],
                            line=dict(color=[NAVY if o else "rgba(0,0,0,0)" for o in e2.outside], width=1.5)),
                customdata=e2[["event_type", "month", "p10", "p90"]],
                hovertemplate="%{y}<br>%{customdata[0]} · %{customdata[1]}<br>변화 %{x:+.1f}% (평소 %{customdata[2]:.0f}~%{customdata[3]:.0f}%)<extra></extra>",
            ))
            fig.add_vline(x=0, line=dict(color=AXIS, width=1))
            style(fig, height=max(380, 24 * len(e2)), hover="closest", xtitle="이벤트 전 3개월 대비 변화(%)")
            fig.update_layout(barmode="overlay", legend=dict(y=1.0))
            fig.update_xaxes(showgrid=True, gridcolor=GRID, ticksuffix="%")
            fig.update_yaxes(tickfont=dict(size=11, color=MUTED))
            chart(fig)
            st.caption("계절 효과를 걷어낸 월별 검색 지수로 이벤트 직전 3개월과 이벤트 달부터 3개월을 비교했어요. 진한 막대가 평소 범위를 벗어난 이벤트예요. "
                       "평소 범위 = 2020년 이후 그 브랜드의 모든 달에 같은 계산을 했을 때의 10–90 백분위.")
    with right:
        if eff is not None:
            st.markdown("**이벤트 유형별 요약**")
            g = (eff.groupby("event_type")
                 .agg(건수=("change_pct", "size"), 중앙값=("change_pct", "median"), 범위이탈=("outside", "sum"))
                 .sort_values("건수", ascending=False).reset_index().rename(columns={"event_type": "유형"}))
            g["중앙값"] = g["중앙값"].map(lambda v: f"{v:+.0f}%")
            g["범위이탈"] = g["범위이탈"].astype(int).astype(str) + "건"
            st.dataframe(g, hide_index=True, width="stretch")
            st.caption("유형마다 1–6건이라 '어떤 유형이 효과적이다'라고 결론 내리기엔 표본이 작아요. 실무에서는 같은 방법을 자사 매출 데이터에 적용해 검증하는 출발점으로 쓸 수 있어요.")

    left, right = st.columns([1, 1], gap="large")
    with left:
        st.markdown("### 언제 관심이 높나")
        if sea is not None:
            z = sea.set_index("moy")[BRANDS].T
            fig = go.Figure(go.Heatmap(
                z=z.values - 100, x=[f"{i}월" for i in z.columns], y=z.index,
                colorscale=DIVERGING, zmid=0, zmin=-60, zmax=60, xgap=2, ygap=2,
                text=z.values.round(0), texttemplate="%{text:.0f}", textfont=dict(size=10, color=TEXT),
                colorbar=dict(title=dict(text="평균 대비", font=dict(color=MUTED)), tickfont=dict(color=MUTED), thickness=10),
                hovertemplate="%{y} %{x}: 연평균의 %{text:.0f}%<extra></extra>",
            ))
            style(fig, height=340, hover="closest")
            fig.update_yaxes(autorange="reversed", showgrid=False)
            chart(fig)
            st.caption("2022–2026년, 각 해 평균 = 100. 파랑은 평균보다 높고 빨강은 낮아요. 출시 적기는 정점 직전인 4–5월이에요.")
    with right:
        st.markdown("### 공개 매출")
        fig = go.Figure()
        for b in [x for x in BRANDS if x in rev.brand.unique()]:
            r = rev[rev.brand == b].sort_values("year")
            fig.add_trace(go.Scatter(x=r.year, y=r["revenue_억원"], mode="lines+markers+text", name=b,
                                     line=dict(color=COLOR[b], width=2), marker=dict(size=9, line=dict(color=SURFACE, width=2)),
                                     text=[f"{v:,.0f}" if i == len(r) - 1 else "" for i, v in enumerate(r["revenue_억원"])],
                                     textposition="top center", textfont=dict(color=TEXT, size=11),
                                     hovertemplate=f"{b} %{{x}}년 %{{y:,.0f}}억 원<extra></extra>"))
        fig.add_annotation(x=2025, y=388, text="뮬라웨어 2025.1 회생 신청", showarrow=True, arrowcolor=AXIS, ax=0, ay=-40,
                           font=dict(color=MUTED, size=11))
        style(fig, height=340, ytitle="매출(억 원)", hover="closest")
        fig.update_xaxes(dtick=1)
        chart(fig)
        st.caption("본투윈·HDEX·압도는 비상장이라 공개 매출이 없어요. 안다르 2020·2021년은 '700억 원대', '1000억 원대' 기사 표현의 근사값이에요.")

    st.markdown("### 사례: 김동현 모델 발탁, 효과가 있었나")
    k = d["kdh_weekly"]
    kk = k.pivot(index="period", columns="brand", values="ratio")
    before = kk.loc["2025-08-01":"2025-10-26", "본투윈"].mean()
    after = kk.loc["2025-10-27":"2026-01-25", "본투윈"].mean()
    corr = kk["본투윈"].corr(kk["김동현"])
    left, right = st.columns([2.2, 1], gap="large")
    with left:
        fig = go.Figure()
        for b, color in [("김동현", NEUTRAL), ("본투윈", COLOR["본투윈"])]:
            s = k[k.brand == b]
            fig.add_trace(go.Scatter(x=s.period, y=s.ratio, mode="lines", name=b, line=dict(color=color, width=2),
                                     hovertemplate=f"{b} %{{y:.1f}}<extra></extra>"))
        fig.add_vrect(x0="2025-10-27", x1="2026-01-25", fillcolor=rgba(PRIMARY, 0.06), line_width=0)
        for i, (date, label) in enumerate([("2025-10-27", "김동현 모델·무신사 협업"), ("2025-12-01", "스타필드 하남 오픈"),
                                           ("2026-04-06", "나띠 모델 발탁"), ("2026-08-17", "골드짐 콜라보")]):
            fig.add_vline(x=date, line=dict(color=AXIS, width=1, dash="dot"))
            fig.add_annotation(x=date, y=1.1 if i % 2 == 0 else 1.02, yref="paper", text=label, showarrow=False,
                               xanchor="left", yanchor="top", font=dict(size=11, color=MUTED))
        style(fig, height=380, ytitle="주간 검색 지수")
        fig.update_layout(margin=dict(t=60), legend=dict(y=1.22))
        chart(fig)
    with right:
        kpi(st, "발탁 전 12주 → 후 13주", f"{(after / before - 1) * 100:+.0f}%", f"{before:.1f} → {after:.1f} (본투윈 주간 검색)")
        st.write("")
        kpi(st, "김동현 검색과의 상관", f"{corr:.2f}", "1에 가까울수록 같이 움직임")
        st.write("")
        st.caption("발탁 직후 한 주는 반짝 올랐지만 석 달 평균은 오히려 낮았고, 이 정도 하락은 본투윈의 평소 변동 범위 안이에요. "
                   "같은 시기 매장 오픈·겨울 비수기가 겹쳐 '효과 없음'으로 단정할 수는 없어요.")

# ── ③ 다음은 어디로 ──────────────────────────────────
with T["③ 다음은 어디로"]:
    st.markdown("### 한국의 운동은 어떻게 바뀌고 있나")
    if sp is not None:
        spd = sp.sort_values("rate_2025")
        st.markdown(f'<div class="insight">{evid("데이터")} 2024→2025년 <b>보디빌딩(헬스)</b> {gym.rate_2024}%→{gym.rate_2025}%, <b>달리기</b> {run.rate_2024}%→{run.rate_2025}%. '
                    "규칙적으로 운동하는 사람이 고르는 운동 중 가장 빠르게 컸어요. 남성 짐웨어 브랜드가 노리는 바로 그 운동이에요.</div>", unsafe_allow_html=True)
        left, right = st.columns([1.3, 1], gap="large")
        with left:
            st.markdown("**규칙적으로 운동하는 사람이 하는 운동 (1~3순위 합, %)**")
            fig = go.Figure()
            for _, r in spd.iterrows():
                up = r.rate_2025 > r.rate_2024
                fig.add_trace(go.Scatter(x=[r.rate_2024, r.rate_2025], y=[r.sport, r.sport], mode="lines",
                                         line=dict(color=PRIMARY if up else AXIS, width=3), showlegend=False, hoverinfo="skip"))
            fig.add_trace(go.Scatter(x=spd.rate_2024, y=spd.sport, mode="markers", name="2024",
                                     marker=dict(size=11, color="#b7bfcc", line=dict(color=SURFACE, width=2)),
                                     hovertemplate="%{y} 2024년 %{x:.1f}%<extra></extra>"))
            fig.add_trace(go.Scatter(x=spd.rate_2025, y=spd.sport, mode="markers+text", name="2025",
                                     marker=dict(size=12, color=PRIMARY, line=dict(color=SURFACE, width=2)),
                                     text=[f"{v:.1f}" for v in spd.rate_2025], textposition="middle right",
                                     textfont=dict(color=TEXT, size=11), hovertemplate="%{y} 2025년 %{x:.1f}%<extra></extra>"))
            style(fig, height=420, xtitle="참여율(%)", hover="closest")
            fig.update_xaxes(showgrid=True, gridcolor=GRID, range=[0, 46])
            chart(fig)
        with right:
            st.markdown("**애슬레저 관심의 10년 (검색 지수 합, 3개월 평균)**")
            tot = mon[mon.brand.isin(["젝시믹스", "안다르", "뮬라웨어"])].groupby("month")["index"].sum().rolling(3, min_periods=1).mean()
            gym_b = mon[mon.brand.isin(["본투윈", "HDEX", "압도"])].groupby("month")["index"].sum().rolling(3, min_periods=1).mean()
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=tot.index, y=tot.values, name="여성 중심 애슬레저 3사", mode="lines", line=dict(color=COLOR["안다르"], width=2),
                                     hovertemplate="여성 중심 애슬레저 3사 %{y:.1f}<extra></extra>"))
            fig.add_trace(go.Scatter(x=gym_b.index, y=gym_b.values, name="남성 중심 짐웨어 3사", mode="lines", line=dict(color=COLOR["본투윈"], width=2),
                                     hovertemplate="남성 중심 짐웨어 3사 %{y:.1f}<extra></extra>"))
            style(fig, height=420)
            chart(fig)
        st.caption("출처: 문화체육관광부 국민생활체육조사(2024·2025), 네이버 데이터랩. 걷기·달리기는 2023년과 분류가 달라 이전 해와 직접 비교하지 않았어요. "
                   "복싱·격투기는 따로 집계되지 않아요. 여성 중심 애슬레저는 2019년 레깅스 열풍 이후 정체, 남성 중심 짐웨어는 2022년부터 자리를 넓히고 있어요.")

    st.markdown("### 다음 네 가지 흐름")
    st.markdown(f'<div class="insight">{evid("가설")} 아래는 위 데이터와 시장 흐름을 엮은 해석이에요. 검증된 사실이 아니라, '
                "브랜드가 다음 투자처를 고를 때 점검할 질문으로 읽어 주세요.</div>", unsafe_allow_html=True)
    trends = [
        ("운동이 정체성이 된다", "헬스·달리기 참여가 가장 빨리 늘어남",
         "오운완 인증, 러닝 크루, 격투기 예능처럼 운동이 '내가 누구인지'를 보여 주는 수단이 됐어요. 옷은 기능품에서 소속의 표시로 바뀌어요.",
         "본투윈 · 압도", "가성비 기본템 중심 브랜드"),
        ("하이브리드 트레이닝", "달리기와 근력을 섞은 대회형 운동(하이록스 등)",
         "헬스장 고객과 러너가 한 경기에서 만나요. 함께 훈련하고 매년 대회에 나가는 구조라, 단발 이벤트가 아닌 반복 접점이 생겨요.",
         "본투윈 · 압도(커뮤니티), 젝시믹스 · 안다르(여성·혼성 기능복)", "HDEX(경기용 기능 라인 필요)"),
        ("트레일·아웃도어 러닝", "산과 들을 달리는 장거리 러닝",
         "핵심은 신발·조끼·방수 재킷 같은 장비라 아웃도어·신발 브랜드가 강해요. 의류 브랜드는 장비 브랜드와의 콜라보로 문화만 가져오는 게 현실적이에요.",
         "콜라보에 강한 본투윈, 러닝 라인을 가진 젝시믹스", "레깅스 중심 브랜드"),
        ("3040 웰니스 케어", "저속노화·근감소 예방 같은 '오래 건강하게'",
         "20대 헬스 고객이 나이 들며 러닝·회복·건강관리로 옮겨 가요. 의류가 보충제·운동 기록 같은 웰니스 서비스와 묶일 여지가 커요.",
         "젝시믹스 · 안다르(3040 여성 기반)", "20대 남성에만 집중한 브랜드"),
    ]
    tc = st.columns(4, gap="small")
    for col, (name, what, why, win, press) in zip(tc, trends):
        col.markdown(f'<div class="trend">{evid("가설")}<h5>{name}</h5><div class="what">{what}</div><div class="why">{why}</div>'
                     f'<dl><dt>유리한 쪽</dt><dd>{win}</dd><dt>압박받는 쪽</dt><dd>{press}</dd></dl></div>', unsafe_allow_html=True)

    ol = d.get("outlook")
    if ol is not None:
        st.markdown("### 브랜드별 준비도")
        left, right = st.columns([1.5, 1], gap="large")
        with left:
            tr_order = ["정체성·커뮤니티", "하이브리드 트레이닝", "트레일·아웃도어 러닝", "3040 웰니스 케어"]
            zp = ol.pivot(index="brand", columns="trend", values="score").loc[BRANDS, tr_order]
            rp = ol.pivot(index="brand", columns="trend", values="reason").loc[BRANDS, tr_order]
            lab = {0: "낮음", 1: "보통", 2: "높음"}
            fig = go.Figure(go.Heatmap(
                z=zp.values, x=tr_order, y=BRANDS, zmin=0, zmax=2, xgap=3, ygap=3, showscale=False,
                colorscale=[[0, "#f5f5f5"], [0.5, "#cfcfcf"], [1, "#111111"]],
                text=[[lab[v] for v in row] for row in zp.values], texttemplate="%{text}",
                textfont=dict(size=12), customdata=rp.values,
                hovertemplate="<b>%{y}</b> · %{x}<br>%{text}: %{customdata}<extra></extra>",
            ))
            style(fig, height=360, hover="closest")
            fig.update_yaxes(autorange="reversed", showgrid=False)
            fig.update_xaxes(side="top")
            chart(fig)
            st.caption("판단 기준: 현재 고객층, 보유 상품 라인, 커뮤니티·콜라보 경험(브랜드 스토리 탭의 출처 기준). 칸에 마우스를 올리면 이유가 보여요.")
        with right:
            st.markdown("**놓치면 안 되는 위험**")
            st.markdown(
                f"""<div class="verdict" style="border-top-color:{AMBER}">
<div class="vi"><b>유행의 수명</b><div class="ev">크로스핏 붐이 꺾였듯 특정 대회형 운동은 짧게 끝날 수 있어요. 한 종목보다 '달리기 + 근력'이라는 넓은 문화에 거는 편이 안전해요.</div></div>
<div class="vi"><b>오프라인 고정비</b><div class="ev">운동 공간형 매장은 커뮤니티 거점이 되지만, 직접 운영 비용이 뮬라웨어를 무너뜨린 원인이기도 했어요.</div></div>
<div class="vi"><b>따라 하기 쉬운 강점</b><div class="ev">가성비와 유명인 모델은 쉽게 복제돼요. 김동현 발탁도 검색을 평소 범위 밖으로 움직이지 못했어요.</div></div>
</div>""", unsafe_allow_html=True)

# ── 브랜드 프로필 ──────────────────────────────────
with T["브랜드 프로필"]:
    b = st.radio("브랜드 선택", BRANDS, horizontal=True, label_visibility="collapsed")
    c = COLOR[b]
    head_l, head_r, head_img = st.columns([1, 2.4, 0.6])
    head_l.markdown(f'<div class="profile-logo">{logo_html(b)}</div>', unsafe_allow_html=True)
    head_img.markdown(product_html(b, "pimg-lg"), unsafe_allow_html=True)
    head_r.markdown(f"### {b}\n<span style='color:{MUTED}'>설립 {BRAND_INFO[b][0]} · {BRAND_INFO[b][1]}</span>",
                    unsafe_allow_html=True)
    k1, k2, k3, k4 = st.columns(4)
    kpi(k1, "주 고객", tilt_label(b), f"남성 점유율 {seg.loc[b, '남성']:.0f}% · 여성 {seg.loc[b, '여성']:.0f}%")
    kpi(k2, "검색 관심 (전년 대비)", f"{yoy(b):+.0f}%", "최근 12개월 평균")
    if b in psum.index:
        kpi(k3, "무신사 판매가 중앙값", f"{psum.loc[b, 'sale'] / 10000:.1f}만 원", f"할인 중앙값 {psum.loc[b, 'disc']:.0f}% · {psum.loc[b, 'n']}개 상품")
    else:
        kpi(k3, "무신사 판매가 중앙값", "—", "무신사 상품 없음")
    rb = rev[rev.brand == b].sort_values("year")
    if len(rb):
        kpi(k4, f"매출 ({int(rb.year.iloc[-1])})", f"{rb['revenue_억원'].iloc[-1]:,.0f}억", "공시·기사 기준")
    else:
        kpi(k4, "매출", "비공개", "비상장")

    if story is not None:
        r = story.set_index("brand").loc[b]
        st.markdown(f'<div class="insight"><b>{r.archetype}</b> · 대표상품 <b>{r.hero_product}</b> ({r.hero_evidence})<br>'
                    f'{r.identity}. 성장 방식: {r.growth}.<br><b>기회</b> {r.opportunity} · <b>위험</b> {r.risk}</div>', unsafe_allow_html=True)
    st.write("")
    left, right = st.columns([1.6, 1], gap="large")
    with left:
        s = mon[mon.brand == b].copy()
        s["index"] = s["index"] / s["index"].max() * 100
        s["sm"] = s["index"].rolling(3, min_periods=1).mean()
        first = s[s["index"] > 1].month.min()
        s = s[s.month >= first]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=s.month, y=s["index"], mode="lines", line=dict(color=c, width=1), opacity=0.35,
                                 name="월별", hovertemplate="%{x} %{y:.1f}<extra></extra>"))
        fig.add_trace(go.Scatter(x=s.month, y=s.sm, mode="lines", line=dict(color=c, width=2.5), name="3개월 평균",
                                 fill="tozeroy", fillcolor=rgba(c, 0.10),
                                 hovertemplate="%{x} 3개월 평균 %{y:.1f}<extra></extra>"))
        evb = d["events"][(d["events"].brand == b)].dropna(subset=["month"]).merge(s[["month", "sm"]], on="month", how="left")
        evb = evb.dropna(subset=["sm"])
        if len(evb):
            fig.add_trace(go.Scatter(x=evb.month, y=evb.sm, mode="markers", showlegend=False,
                                     marker=dict(size=12, color=c, symbol=[EVENT_SYMBOL[t] for t in evb.event_type],
                                                 line=dict(color=SURFACE, width=2)),
                                     customdata=evb[["event_type", "description"]],
                                     hovertemplate="%{customdata[0]}: %{customdata[1]}<extra></extra>"))
        style(fig, height=380, ytitle="검색 지수 (브랜드 최고=100)", hover="closest")
        chart(fig)
    with right:
        items = d["events"][d["events"].brand == b].sort_values("date", ascending=False)
        st.markdown(f"**타임라인** · {len(items)}건")
        html = "".join(
            f'<div class="it" style="--c:{c}"><span class="d">{r.date if pd.notna(r.date) else "날짜 미상"}</span>'
            f'<span class="t">{r.event_type}</span><br>{r.description} <a href="{r.source}" target="_blank" style="color:{MUTED};font-size:.75rem">출처</a></div>'
            for r in items.itertuples())
        st.markdown(f'<div class="tl">{html}</div>', unsafe_allow_html=True)

# ── 데이터·방법 ──────────────────────────────────────
with T["데이터·방법"]:
    st.markdown("### 데이터와 방법")
    st.markdown(
        f"""
| 데이터 | 출처 | 기간·규모 | 쓰임 |
|---|---|---|---|
| 검색어 트렌드 | 네이버 데이터랩 | 2016.01–2026.10 월별, 성별·연령 4구간 | 고객층, 검색 점유율, 계절성, 이벤트 효과 |
| 주간 검색 | 네이버 데이터랩 | 2025.01–2026.10 | 김동현 모델 사례 |
| 상품 가격 | 무신사 브랜드 상품 목록 | 2026.11.25, {len(pr)}개 상품 | 가격·할인 포지셔닝 |
| 매출 | 공시 인용 기사, 증권사 리포트 | 2018–2025, 3개 브랜드 | 성장 규모, 검색 지수 검증 |
| 이벤트 | 언론 기사, 기업정보 | {len(d['events'])}건 (월까지 확인된 {n_eff}건으로 효과 계산) | 무엇으로 컸나 |
| 운동 참여 | 문체부 국민생활체육조사 | 2019–2025 | 시장 배경 |

**근거 표기**
- 화면의 꼬리표는 근거의 종류예요. **데이터**는 우리가 모은 수치로 계산한 것, **보도**는 회사 발표·기사 인용, **가설**은 데이터와 시장 흐름을 엮은 해석이에요.
- '브랜드별 준비도'는 보유 상품 라인·고객층·콜라보 경험을 바탕으로 한 판단(낮음·보통·높음)이에요.

**검증과 한계**
- **검색 지수는 상대값이에요.** 실제 검색 횟수가 아니라 조회 안에서 최고값을 100으로 놓은 값이에요. 5개씩 나눠 조회했고, 압도는 HDEX를 공통 기준으로 같은 척도에 옮겼어요.
- **검색이 매출을 대변하는지 확인했어요.** 매출이 공개된 3개 브랜드의 연평균 검색 지수와 연매출의 상관은 {r_all:.2f}예요. 다만 큰 브랜드는 검색이 줄어도 매출이 유지돼요.
- **이벤트 효과는 평소 변동과 비교했어요.** 계절성을 걷어낸 뒤 전후 3개월 변화를 구하고, 같은 계산을 모든 달에 해서 얻은 10–90 백분위(평소 범위)를 벗어났는지 봤어요. 인과가 아니라 동반된 변화예요.
- 검색어: 본투윈(본투윈, borntowin) · 젝시믹스(젝시믹스, xexymix) · 안다르(안다르, andar) · 뮬라웨어(뮬라웨어, 뮬라 레깅스) · HDEX(HDEX, 에이치덱스) · 압도(압도 짐웨어·반팔·후드·브랜드). '안다르', '압도'처럼 일반 단어와 겹치는 이름은 다른 뜻의 검색이 섞였을 수 있어요.
- 고객층은 네이버 검색 이용자 기준이라 무신사·인스타그램 안의 관심은 잡히지 않아요. 가격은 하루치 표본이에요.
- 로고와 상품 사진은 각 브랜드의 상표·저작물이며, 학습·포트폴리오 목적의 식별 용도로만 사용했어요.
"""
    )
    with st.expander("매출 원자료"):
        st.dataframe(rev, width="stretch", hide_index=True,
                     column_config={"source": st.column_config.LinkColumn("출처")})
    with st.expander("이벤트 원자료"):
        st.dataframe(d["events"][["brand", "date", "event_type", "description", "source"]], width="stretch",
                     hide_index=True, column_config={"source": st.column_config.LinkColumn("출처")})
    if eff is not None:
        with st.expander("이벤트 효과 계산 결과"):
            st.dataframe(eff, width="stretch", hide_index=True)
    if pr is not None:
        with st.expander("무신사 상품 원자료"):
            st.dataframe(pr, width="stretch", hide_index=True)

st.markdown('<div class="foot">대한민국 웰니스 브랜드 6 심층 비교 · 산업데이터 시각화 개인 프로젝트 · 공개 데이터 기반, 2026.11 작성</div>',
            unsafe_allow_html=True)
