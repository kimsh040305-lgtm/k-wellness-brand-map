"""원본 데이터를 앱이 읽는 정리된 CSV로 바꾼다.

실행: python prep.py
입력: data/search_trend_long.csv, data/events.csv, data/revenue_raw.csv
출력: data/processed/*.csv
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).parent
DATA = ROOT / "data"
OUT = DATA / "processed"
OUT.mkdir(parents=True, exist_ok=True)

A_BRANDS = ["본투윈", "젝시믹스", "안다르", "뮬라웨어", "HDEX"]
END = "2026-10"
RECENT_START = "2025-11"  # 최근 12개월: 2025-11 ~ 2026-10

trend = pd.read_csv(DATA / "search_trend_long.csv")
trend["month"] = trend["period"].str[:7]
trend = trend[trend["month"] <= END]


def series(query, segment):
    d = trend[(trend["query"] == query) & (trend["segment"] == segment)]
    return d.pivot_table(index="month", columns="brand", values="ratio")


# 1) 월별 검색 지수: 조회 A 전체 기준 척도로 6개 브랜드를 맞춘다.
a_all = series("A", "전체")
b_all = series("B", "전체")
# 압도는 조회 B에만 있으므로 HDEX를 다리로 써서 A 척도로 옮긴다.
window = a_all.index[a_all.index >= "2023-01"]
bridge = a_all.loc[window, "HDEX"].sum() / b_all.loc[window, "HDEX"].sum()
monthly = a_all.copy()
monthly["압도"] = b_all["압도"] * bridge
# 보기 좋게 전체 최고값을 100으로 다시 맞춘다.
monthly = monthly / monthly.max().max() * 100
monthly = monthly.reset_index().melt(id_vars="month", var_name="brand", value_name="index")
monthly.to_csv(OUT / "monthly_index.csv", index=False)

# 2) 최근 12개월 세그먼트별 점유율 (조회 A 5개 브랜드 + 압도 HDEX 다리)
rows = []
for seg in ["여성", "남성", "19-29", "30-39"]:
    a = series("A", seg)
    b = series("B", seg)
    a_r = a[a.index >= RECENT_START].mean()
    b_r = b[b.index >= RECENT_START].mean()
    vals = a_r[A_BRANDS].copy()
    vals["압도"] = b_r["압도"] / b_r["HDEX"] * a_r["HDEX"]
    share = vals / vals.sum() * 100
    for brand, v in share.items():
        rows.append({"segment": seg, "brand": brand, "share": round(v, 2)})
shares = pd.DataFrame(rows)
shares.to_csv(OUT / "segment_share.csv", index=False)

# 3) 포지셔닝 지도: 남성 지향도(남성 점유율/여성 점유율), 20대 지향도(19-29 점유율/30-39 점유율)
p = shares.pivot(index="brand", columns="segment", values="share")
pos = pd.DataFrame({
    "brand": p.index,
    "male_tilt": np.log2(p["남성"] / p["여성"]),
    "young_tilt": np.log2(p["19-29"] / p["30-39"]),
})
pos.to_csv(OUT / "positioning.csv", index=False)

# 4) 본투윈 vs 김동현 주간
c = trend[(trend["query"] == "C")].copy()
c = c[c["period"] <= "2026-10-31"]
c[["period", "brand", "ratio"]].to_csv(OUT / "kdh_weekly.csv", index=False)

# 5) 이벤트: 날짜를 월 단위로 맞추고, 날짜 없는 항목은 표에만 남긴다.
ev = pd.read_csv(DATA / "events.csv")
def to_month(s):
    s = str(s) if pd.notna(s) else ""
    if len(s) == 7 and s[4] == "-" and s[5:7].isdigit() and 1 <= int(s[5:7]) <= 12:
        return s[:7]
    if len(s) >= 4 and s[:4].isdigit():
        return s[:4] + "-01"
    return None
ev["month"] = ev["date"].map(to_month)
ev.to_csv(OUT / "events.csv", index=False)

# 6) 매출
rev = pd.read_csv(DATA / "revenue_raw.csv")
rev.to_csv(OUT / "revenue.csv", index=False)

print("bridge factor (압도):", round(bridge, 4))
print(shares.pivot(index="brand", columns="segment", values="share").round(1))
print(pos.round(2))

# 7) 무신사 상품 (2026-11-25, 브랜드 상품 목록 '무신사 추천순' 상위 상품을 직접 기록)
pr = pd.read_csv(DATA / "musinsa_products_raw.csv")
pr["list_price"] = (pr["sale_price"] / (1 - pr["discount_pct"] / 100)).round(-2)
pr.rename(columns={"product": "product"}).to_csv(OUT / "products.csv", index=False)
summary = pr.groupby("brand").agg(
    n=("product", "size"),
    median_list=("list_price", "median"),
    median_sale=("sale_price", "median"),
    median_discount=("discount_pct", "median"),
    male_share=("gender", lambda g: (g == "남성").mean() * 100),
)
summary.to_csv(OUT / "products_summary.csv")
print(summary.round(0))

# 8) 계절성: 2022년 이후, 각 해 평균=100으로 놓고 월별 평균
mi = pd.read_csv(OUT / "monthly_index.csv")
mi["month"] = pd.PeriodIndex(mi["month"], freq="M")
pv = mi.pivot(index="month", columns="brand", values="index")
recent = pv[pv.index >= pd.Period("2022-01", "M")]
rel = recent / recent.groupby(recent.index.year).transform("mean") * 100
season = rel.groupby(rel.index.month).mean()
season.index.name = "moy"
season.round(1).to_csv(OUT / "seasonality.csv")

# 9) 이벤트 효과: 계절성을 걷어낸 검색 지수로, 이벤트 직전 3개월 대비 이벤트 달 포함 3개월 변화율
factor = season / 100
deseason = pv.copy()
for b in deseason.columns:
    deseason[b] = pv[b] / pv.index.month.map(factor[b]).values
rows = []
for _, e in pd.read_csv(OUT / "events.csv").dropna(subset=["month"]).iterrows():
    if e.brand not in deseason:
        continue
    t = pd.Period(e.month, "M")
    s = deseason[e.brand]
    pre, post = s.loc[t - 3:t - 1].mean(), s.loc[t:t + 2].mean()
    if pd.notna(pre) and pre > 0 and pd.notna(post) and len(str(e.date)) == 7:
        rows.append({"brand": e.brand, "month": e.month, "event_type": e.event_type,
                     "description": e.description, "change_pct": round((post / pre - 1) * 100, 1)})
eff = pd.DataFrame(rows)
eff.to_csv(OUT / "event_effects.csv", index=False)
print(eff.groupby("event_type").change_pct.agg(["count", "median"]).round(0))
print(eff.sort_values("change_pct", ascending=False).head(8).to_string())

# 10) 평소 변동 범위: 이벤트가 없어도 3개월 전후 비교값이 얼마나 흔들리는지(브랜드별 10~90 백분위)
base_rows = []
for b in deseason.columns:
    s = deseason[b]
    s = s[s.index >= pd.Period("2020-01", "M")]
    for t in s.index[3:-2]:
        pre, post = s.loc[t - 3:t - 1].mean(), s.loc[t:t + 2].mean()
        if pre > 0.05:
            base_rows.append({"brand": b, "change_pct": (post / pre - 1) * 100})
base = pd.DataFrame(base_rows).groupby("brand").change_pct.quantile([0.1, 0.9]).unstack()
base.columns = ["p10", "p90"]
base.round(1).to_csv(OUT / "baseline.csv")
eff = eff.merge(base, left_on="brand", right_index=True, how="left")
eff["outside"] = (eff.change_pct > eff.p90) | (eff.change_pct < eff.p10)
eff.to_csv(OUT / "event_effects.csv", index=False)
print(base.round(1))
print(eff.groupby("event_type").agg(n=("change_pct", "size"), med=("change_pct", "median"), out=("outside", "sum")))

# 11) Share of Search: 같은 척도(Search A + 압도 환산) 안에서 월별 점유율
sos = pv.div(pv.sum(axis=1), axis=0) * 100
sos.index = sos.index.astype(str)
sos = sos[sos.index >= "2018-01"]
sos.round(2).to_csv(OUT / "sos.csv")

# 12) 검색 지수가 매출을 대변하는가: 연평균 검색 지수 vs 연매출
rv = pd.read_csv(OUT / "revenue.csv")
yr = mi.assign(year=mi.month.dt.year).groupby(["brand", "year"])["index"].mean().rename("search").reset_index()
val = rv.merge(yr, on=["brand", "year"])[["brand", "year", "revenue_억원", "search"]]
val.round(2).to_csv(OUT / "validation.csv", index=False)
for b, g in val.groupby("brand"):
    print(b, len(g), round(g["revenue_억원"].corr(g.search), 2))
print("all", round(val["revenue_억원"].corr(val.search), 2))
