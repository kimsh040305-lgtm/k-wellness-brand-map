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

st.set_page_config(page_title="K-웰니스 브랜드 맵", page_icon="📊", layout="wide")

# ── 디자인 토큰 ─────────────────────────────────────────
# 신뢰감: 네이비(주색) + 쿨 그레이(배경·선) + 흰 카드. 강조색은 네이비 하나만 쓰고,
# 브랜드 색은 데이터에만 쓴다. 브랜드 6색은 흰 배경 기준 색약 구분 검사를 통과한 조합.
BRANDS = ["본투윈", "젝시믹스", "안다르", "뮬라웨어", "HDEX", "압도"]
COLOR = {"본투윈": "#257de0", "젝시믹스": "#f47230", "안다르": "#00b894",
         "뮬라웨어": "#f2a600", "HDEX": "#ee7fac", "압도": "#008a17"}
SLUG = {"본투윈": "borntowin", "젝시믹스": "xexymix", "안다르": "andar",
        "뮬라웨어": "mulawear", "HDEX": "hdex", "압도": "abdo"}
NAVY = "#16325c"
PRIMARY = "#1f4e8c"
BG = "#f5f7fa"
SURFACE = "#ffffff"
TEXT = "#1b2433"
MUTED = "#5b6472"
LINE = "#e3e7ee"
GRID = "#eceff4"
AXIS = "#c2c8d2"
NEUTRAL = "#8a94a6"
FONT = "Pretendard, -apple-system, 'Apple SD Gothic Neo', sans-serif"
DIVERGING = [[0, "#eb7b7b"], [0.5, "#f1f2f4"], [1, "#6aabf1"]]
STRENGTH = {"강함": ("#e6efe8", "#1d6b35"), "보통": ("#eef2f8", "#1f4e8c"), "약함": ("#f6efe4", "#8a5a12")}

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
              background: #eef2f8; color: {PRIMARY}; font-weight: 600; }}
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
.insight {{ background: #eef2f8; border-left: 3px solid {PRIMARY}; padding: 10px 14px; margin: .4rem 0 1rem; color: {TEXT};
            line-height: 1.6; border-radius: 0 6px 6px 0; }}
.verdict {{ background: {SURFACE}; border: 1px solid {LINE}; border-top: 3px solid {NAVY}; border-radius: 10px; padding: 18px 20px; }}
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
.tl .t {{ font-size: .7rem; padding: 1px 7px; border-radius: 4px; background: #eef2f8; color: {PRIMARY}; margin-left: 6px; }}
.stTabs [data-baseweb="tab-list"] {{ gap: 6px; border-bottom: 1px solid {LINE}; }}
.stTabs [data-baseweb="tab"] {{ font-weight: 600; }}
.foot {{ color: {MUTED}; font-size: .76rem; border-top: 1px solid {LINE}; margin-top: 2rem; padding-top: 12px; }}
</style>
""",
    unsafe_allow_html=True,
)


@st.cache_data
def load():
    names = ["monthly_index", "segment_share", "positioning", "kdh_weekly", "events", "revenue",
             "sports", "sports_participation", "products", "seasonality", "event_effects",
             "baseline", "sos", "validation"]
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


def kpi(col, label, value, sub=""):
    col.markdown(f'<div class="kpi"><div class="label">{label}</div><div class="value">{value}</div>'
                 f'<div class="sub">{sub}</div></div>', unsafe_allow_html=True)


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
<div class="hero topbar">
  <div class="eyebrow">K-WELLNESS BRAND MAP · 2016–2026</div>
  <h1>웰니스 브랜드들은 누구를 잡고, 무엇으로 성장했나?</h1>
  <p>한국 애슬레저·짐웨어 브랜드 6개의 고객층, 가격, 성장 계기를 공개 데이터로 비교한 경쟁 분석 대시보드예요.</p>
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

TABS = ["한눈에 보기", "① 누구를 잡았나", "② 무엇으로 컸나", "③ 시장의 흐름", "④ 브랜드 프로필", "데이터·방법"]
T = dict(zip(TABS, st.tabs(TABS)))

# ── 한눈에 보기 ────────────────────────────────────────
with T["한눈에 보기"]:
    st.markdown('<div class="section-label">이 대시보드로 답하는 실무 질문</div>', unsafe_allow_html=True)
    st.markdown(
        """<div class="uses">
<div class="use"><div class="who">브랜드 기획·MD</div><div class="q">경쟁사는 어떤 고객을 잡고 있고, 얼마에, 얼마나 할인해서 파나? 우리가 들어갈 빈자리는 어디인가?</div></div>
<div class="use"><div class="who">마케팅</div><div class="q">경쟁사 대비 검색 점유율(Share of Search)은 어떻게 움직이나? 모델·콜라보·매장 중 무엇이 관심을 바꿨나? 언제 출시해야 하나?</div></div>
<div class="use"><div class="who">창업·투자 검토</div><div class="q">어느 운동·고객층이 커지고 있나? 앞선 브랜드는 어디서 성장하고 어디서 무너졌나?</div></div>
</div>""",
        unsafe_allow_html=True,
    )

    st.markdown('<div class="section-label">핵심 발견</div>', unsafe_allow_html=True)
    finds = [
        ("FINDING 01", f"{male_gym:.0f}%", "짐웨어 브랜드는 남성 검색에서 자리를 잡았다",
         f"여성 검색은 안다르·젝시믹스가 {female_top:.0f}%를 쥔 2강 구도예요. 남성 검색에서는 본투윈·HDEX·압도가 {male_gym:.0f}%, 20대에서는 {young_gym:.0f}%를 가져왔어요."),
        ("FINDING 02", f"{psum.loc['본투윈', 'disc']:.0f}% vs {psum.loc['HDEX', 'disc']:.0f}%", "할인율이 포지션을 가른다",
         f"같은 남성 20대를 노려도 본투윈은 할인 중앙값 {psum.loc['본투윈', 'disc']:.0f}%(판매가 {psum.loc['본투윈', 'sale'] / 10000:.1f}만 원), "
         f"HDEX는 {psum.loc['HDEX', 'disc']:.0f}%({psum.loc['HDEX', 'sale'] / 10000:.1f}만 원)예요. 무신사 상품 {len(pr)}개 기준이에요."),
        ("FINDING 03", "5–8월", "관심은 여름에 몰린다",
         "2022–2026년 매해 평균과 비교하면 6개 브랜드 모두 5–8월에 높고 12–2월에 낮아요. 신상품·캠페인은 4–5월에 맞추는 게 유리해요."),
        ("FINDING 04", f"{n_out} / {n_eff}건", "단발 이벤트는 검색 흐름을 잘 바꾸지 못했다",
         f"이벤트 {n_eff}건 중 평소 변동 범위를 벗어난 건 {n_out}건, 위로 벗어난 건 {n_out_up}건뿐이에요. 김동현 모델 발탁, HDEX 더현대 매장도 평소 범위 안이었어요."),
    ]
    st.markdown('<div class="finds">' + "".join(
        f'<div class="find"><div class="no">{n}</div><div class="big">{big}</div><div class="head">{h}</div><div class="body">{body}</div></div>'
        for n, big, h, body in finds) + "</div>", unsafe_allow_html=True)

    left, right = st.columns([1.1, 1], gap="large")
    with left:
        st.markdown("**최근 1년 검색 관심 변화 (전년 대비)**")
        yy = pd.Series({b: yoy(b) for b in BRANDS}).sort_values()
        fig = go.Figure(go.Bar(
            x=yy.values, y=yy.index, orientation="h",
            marker=dict(color=[COLOR[b] for b in yy.index], line=dict(color=SURFACE, width=2)),
            text=[f"{v:+.0f}%" for v in yy.values], textposition="outside", textfont=dict(color=TEXT),
            hovertemplate="%{y} %{x:+.1f}%<extra></extra>",
        ))
        style(fig, height=330, hover="closest")
        fig.add_vline(x=0, line=dict(color=AXIS, width=1))
        fig.update_xaxes(showgrid=True, gridcolor=GRID, ticksuffix="%", range=[min(yy.min() * 1.35, -10), max(yy.max() * 1.35, 10)])
        chart(fig)
        st.caption("2025.11–2026.10 평균 검색 지수 ÷ 2024.11–2025.10 평균 − 1. 압도는 검색량이 매우 작아 변화율이 크게 흔들려요.")
    with right:
        items = [
            ("강함", "남성 20대 · 헬스/러닝을 겨냥한다",
             f"남성 검색 {male_gym:.0f}%, 20대 {young_gym:.0f}%를 짐웨어 브랜드가 가져왔고, 헬스 {gym.rate_2024}→{gym.rate_2025}%, 달리기 {run.rate_2024}→{run.rate_2025}%로 참여가 가장 빨리 늘어요."),
            ("강함", "출시와 캠페인은 4–5월에",
             "6개 브랜드 모두 5–8월 정점, 12–2월 바닥. 5년치 월별 패턴이 같아요."),
            ("보통", "가격보다 할인 정책으로 포지션을 지킨다",
             f"프리미엄(본투윈)은 할인 {psum.loc['본투윈', 'disc']:.0f}%, 가성비(HDEX·젝시믹스)는 30%대. 하루치 무신사 상품 {len(pr)}개 기준이에요."),
            ("보통", "모델 한 명보다 꾸준한 접점",
             f"이벤트 {n_eff}건 중 검색을 평소 범위 위로 끌어올린 건 {n_out_up}건. 단발 이벤트에 예산을 몰기보다 시즌마다 반복하는 편이 안전해요."),
            ("약함", "성장보다 수익 구조",
             "뮬라웨어는 판관비가 매출의 약 60%까지 올라간 뒤 2025년 회생을 신청했어요. 사례 1건이라 일반화는 조심해야 해요."),
        ]
        html = "".join(f'<div class="vi"><b>{i + 1}. {t}</b>{strength(lv)}<div class="ev">{ev}</div></div>'
                       for i, (lv, t, ev) in enumerate(items))
        st.markdown(f'<div class="verdict"><h4>실무 시사점</h4>'
                    f'<div class="lead">새 웰니스 브랜드를 만든다면. 근거 강도 = 데이터 양과 기간, 다른 해석의 여지를 함께 본 판단이에요.</div>{html}</div>',
                    unsafe_allow_html=True)

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
        fig.add_shape(type="rect", x0=0, x1=5, y0=0, y1=2, fillcolor=rgba(COLOR["본투윈"], 0.06), line_width=0, layer="below")
        fig.add_shape(type="rect", x0=-2, x1=0, y0=-1, y1=0, fillcolor=rgba(COLOR["안다르"], 0.07), line_width=0, layer="below")
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
                                         line=dict(color=COLOR[b], width=0.5), fillcolor=rgba(COLOR[b], 0.85),
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

# ── ③ 시장의 흐름 ──────────────────────────────────
with T["③ 시장의 흐름"]:
    if sp is not None:
        spd = sp.sort_values("rate_2025")
        st.markdown("### 남성 짐웨어 시장은 왜 커졌나")
        st.markdown(f'<div class="insight">2024→2025년 <b>보디빌딩(헬스)</b> {gym.rate_2024}%→{gym.rate_2025}%, <b>달리기</b> {run.rate_2024}%→{run.rate_2025}%. '
                    "본투윈·HDEX·압도가 노리는 헬스·러닝이 가장 빠르게 크는 운동이에요.</div>", unsafe_allow_html=True)
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
            style(fig, height=440, xtitle="참여율(%)", hover="closest")
            fig.update_xaxes(showgrid=True, gridcolor=GRID, range=[0, 46])
            chart(fig)
        with right:
            pp = d.get("sports_participation")
            if pp is not None:
                st.markdown("**주 1회 이상 생활체육 참여율 (%)**")
                fig = go.Figure(go.Scatter(x=pp.year, y=pp.rate, mode="lines+markers+text", line=dict(color=PRIMARY, width=2),
                                           marker=dict(size=9, line=dict(color=SURFACE, width=2)), text=[f"{v:.1f}" for v in pp.rate],
                                           textposition="top center", textfont=dict(color=TEXT, size=11),
                                           hovertemplate="%{x}년 %{y:.1f}%<extra></extra>"))
                fig.add_annotation(x=2020, y=60.1, text="코로나19", showarrow=True, arrowcolor=AXIS, ax=0, ay=30, font=dict(color=MUTED, size=11))
                style(fig, height=440, hover="closest")
                fig.update_xaxes(dtick=1)
                fig.update_yaxes(range=[55, 70])
                chart(fig)
        st.caption("출처: 문화체육관광부 국민생활체육조사(2024·2025). 걷기·달리기는 2023년과 분류가 달라 이전 해와 직접 비교하지 않았어요. 복싱·격투기는 따로 집계되지 않아요.")

    st.markdown("### 애슬레저 관심의 10년")
    tot = mon[mon.brand.isin(["젝시믹스", "안다르", "뮬라웨어"])].groupby("month")["index"].sum().rolling(3, min_periods=1).mean()
    gym_b = mon[mon.brand.isin(["본투윈", "HDEX", "압도"])].groupby("month")["index"].sum().rolling(3, min_periods=1).mean()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=tot.index, y=tot.values, name="여성 중심 애슬레저 3사", mode="lines", line=dict(color=COLOR["안다르"], width=2),
                             hovertemplate="여성 중심 애슬레저 3사 %{y:.1f}<extra></extra>"))
    fig.add_trace(go.Scatter(x=gym_b.index, y=gym_b.values, name="남성 중심 짐웨어 3사", mode="lines", line=dict(color=COLOR["본투윈"], width=2),
                             hovertemplate="남성 중심 짐웨어 3사 %{y:.1f}<extra></extra>"))
    style(fig, height=360, ytitle="검색 지수 합 (3개월 이동평균)")
    chart(fig)
    st.caption("여성 중심 애슬레저는 2019년 레깅스 열풍 이후 정체, 남성 중심 짐웨어는 2022년부터 등장해 꾸준히 자리를 넓히고 있어요. 같은 척도의 검색 지수 합이에요.")

# ── ④ 브랜드 프로필 ──────────────────────────────────
with T["④ 브랜드 프로필"]:
    b = st.radio("브랜드 선택", BRANDS, horizontal=True, label_visibility="collapsed")
    c = COLOR[b]
    head_l, head_r = st.columns([1, 3])
    head_l.markdown(f'<div class="profile-logo">{logo_html(b)}</div>', unsafe_allow_html=True)
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

    st.write("")
    left, right = st.columns([1.6, 1], gap="large")
    with left:
        s = mon[mon.brand == b].copy()
        s["index"] = s["index"] / s["index"].max() * 100
        s["sm"] = s["index"].rolling(3, min_periods=1).mean()
        first = s[s["index"] > 0].month.min()
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

**검증과 한계**
- **검색 지수는 상대값이에요.** 실제 검색 횟수가 아니라 조회 안에서 최고값을 100으로 놓은 값이에요. 5개씩 나눠 조회했고, 압도는 HDEX를 공통 기준으로 같은 척도에 옮겼어요.
- **검색이 매출을 대변하는지 확인했어요.** 매출이 공개된 3개 브랜드의 연평균 검색 지수와 연매출의 상관은 {r_all:.2f}예요. 다만 큰 브랜드는 검색이 줄어도 매출이 유지돼요.
- **이벤트 효과는 평소 변동과 비교했어요.** 계절성을 걷어낸 뒤 전후 3개월 변화를 구하고, 같은 계산을 모든 달에 해서 얻은 10–90 백분위(평소 범위)를 벗어났는지 봤어요. 인과가 아니라 동반된 변화예요.
- 검색어: 본투윈(본투윈, borntowin) · 젝시믹스(젝시믹스, xexymix) · 안다르(안다르, andar) · 뮬라웨어(뮬라웨어, 뮬라 레깅스) · HDEX(HDEX, 에이치덱스) · 압도(압도 짐웨어·반팔·후드·브랜드). '안다르', '압도'처럼 일반 단어와 겹치는 이름은 다른 뜻의 검색이 섞였을 수 있어요.
- 고객층은 네이버 검색 이용자 기준이라 무신사·인스타그램 안의 관심은 잡히지 않아요. 가격은 하루치 표본이에요.
- 로고는 각 브랜드의 상표이며, 학습·포트폴리오 목적의 식별 용도로만 사용했어요.
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

st.markdown('<div class="foot">K-웰니스 브랜드 맵 · 산업데이터 시각화 개인 프로젝트 · 공개 데이터 기반, 2026.11 작성</div>',
            unsafe_allow_html=True)
