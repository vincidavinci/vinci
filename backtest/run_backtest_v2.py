#!/usr/bin/env python3
"""连板接力策略回测 v2 — 全周期2018-2025，牛熊各50只"""
import json, warnings
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf

warnings.filterwarnings("ignore")

INITIAL = 1_000_000
FULL_START, FULL_END = "2018-01-01", "2025-06-30"
PERIODS = {
    "2018-2020": ("2018-01-01", "2020-12-31"),
    "2020-2022": ("2020-01-01", "2022-12-31"),
    "2022-2024": ("2022-01-01", "2024-12-31"),
    "2024-至今": ("2024-01-01", "2025-06-30"),
}

BEAR50 = [f"{c:06d}.{'SZ' if c<600000 else 'SS'}" for c in [
    1,2,63,100,157,333,338,651,725,768,858,876,2001,2007,2024,2027,2032,2044,2050,2120,
    2142,2179,2230,2236,2241,2252,2271,2304,2311,2352,2410,2415,2456,2460,2475,2493,2508,2555,
    2594,2601,2714,2736,2812,2821,2841,2916,2938,300014,300015,300059]]
BULL50 = [f"{c:06d}.SS" if c>=600000 else f"{c:06d}.SZ" for c in [
    600000,600009,600016,600019,600028,600030,600031,600036,600048,600050,600104,600111,600196,
    600276,600309,600340,600406,600436,600438,600519,600547,600570,600585,600588,600600,600660,
    600690,600703,600745,600809,600887,600893,600900,601012,601066,601088,601138,601166,601211,
    601288,601318,601336,601398,601601,601628,601668,601688,601766,601857,300750]]


@dataclass
class Trade:
    sym: str; entry: str; exit: str; pnl: float; board: str
    lanban: bool; regime: str; reason: str


def load(sym, start, end):
    h = yf.download(sym, start=start, end=end, progress=False, auto_adjust=True)
    if h is None or len(h) < 30:
        return pd.DataFrame()
    if isinstance(h.columns, pd.MultiIndex):
        h.columns = h.columns.get_level_values(0)
    df = h.reset_index()
    df.columns = [str(c).lower() for c in df.columns]
    df["date"] = pd.to_datetime(df["date"]).dt.tz_localize(None)
    df["pct"] = df["close"].pct_change() * 100
    return df


def T(sym):
    return 19.5 if sym.startswith("300") or sym.startswith("688") else 9.5


def zt(r, t):
    return r["pct"] >= t - 0.5


def yizi(r, t):
    return zt(r, t) and (r["high"] - r["low"]) / max(r["low"], 1e-9) * 100 < 1.0


def lb(r, t):
    if not zt(r, t) or yizi(r, t):
        return False
    pc = r["close"] / (1 + r["pct"] / 100)
    lp = pc * (1 + t / 100)
    return (lp - r["low"]) / lp * 100 >= 2.5


def streak(df, i, t):
    n, j = 0, i - 1
    while j >= 0 and zt(df.iloc[j], t):
        n += 1
        j -= 1
    return n


def emo_index(all_dfs):
    rows = []
    for df in all_dfs.values():
        for _, r in df.iterrows():
            rows.append((r["date"], r["pct"]))
    m = pd.DataFrame(rows, columns=["date", "pct"])
    g = m.groupby("date").agg(
        red=("pct", lambda x: (x > 0).mean()),
        n_down=("pct", lambda x: (x <= -9.5).sum()),
        avg=("pct", "mean"),
    ).reset_index()
    g["ice"] = (g["n_down"] >= 3) | (g["red"] <= 0.30) | (g["avg"] < -1.5)
    g["ice2"] = g["ice"].rolling(3).sum() >= 1
    g["node"] = g["ice2"].shift(1) & (g["red"].diff() > 0.03)
    return g.set_index("date")


def run(symbols, start, end, regime, emo):
    trades = []
    cap = INITIAL
    pos_pct = 0.2
    ws = ls = 0
    eq = []
    for sym in symbols:
        df = load(sym, start, end)
        if len(df) < 60:
            continue
        t = T(sym)
        df["ma5"] = df["close"].rolling(5).mean()
        df["vma5"] = df["volume"].rolling(5).mean()
        pos = None
        for i in range(8, len(df) - 1):
            r, p = df.iloc[i], df.iloc[i - 1]
            d = r["date"]
            if pos:
                ex = rs = None
                nx = df.iloc[i + 1]
                if (nx["open"] - r["close"]) / r["close"] * 100 < -3:
                    ex, rs = nx["open"], "低开>3%"
                elif r["close"] < r["ma5"]:
                    ex, rs = r["close"], "破5日线"
                elif zt(p, t) and not zt(r, t):
                    ex, rs = r["close"], "炸板"
                elif r["pct"] <= -T(sym) + 0.5:
                    ex, rs = nx["open"], "跌停次日"
                if ex:
                    pnl = (ex - pos["ep"]) / pos["ep"] * 100
                    cap += cap * pos_pct * pnl / 100
                    trades.append(Trade(sym, pos["ed"], str(d.date()), pnl, pos["bd"], pos["lb"], regime, rs))
                    if pnl > 0:
                        ws += 1; ls = 0
                        if ws >= 3: pos_pct = min(1.0, pos_pct + 0.2)
                    else:
                        ls += 1; ws = 0
                        if ls >= 2: pos_pct = max(0.1, pos_pct / 2)
                    pos = None
            if pos is None:
                if d not in emo.index or not bool(emo.loc[d, "node"]):
                    continue
                st = streak(df, i, t)
                if st not in (2, 3, 4) or yizi(r, t):
                    continue
                if r["volume"] < r["vma5"] * 1.1:
                    continue
                is_lb = lb(r, t)
                oc = (r["open"] - p["close"]) / p["close"] * 100
                if oc < -5 or oc > 9:
                    continue
                if not is_lb and r["volume"] < r["vma5"] * 1.5:
                    continue
                pos = {"ed": str(d.date()), "ep": p["close"] * (1 + t / 100),
                       "bd": {2: "2进3", 3: "3进4", 4: "4进5"}.get(st, "5进6+"), "lb": is_lb}
            eq.append({"date": d, "cap": cap})
    return trades, eq


def stats(trades, eq, emo):
    if not trades:
        return {"交易次数": 0, "说明": "该区间无触发信号"}
    pnls = [t.pnl for t in trades]
    w = [x for x in pnls if x > 0]
    l = [x for x in pnls if x <= 0]
    eqdf = pd.DataFrame(eq).drop_duplicates("date").sort_values("date") if eq else pd.DataFrame([{"cap": INITIAL}])
    tr = (eqdf["cap"].iloc[-1] / INITIAL - 1) * 100
    dd = ((eqdf["cap"] - eqdf["cap"].cummax()) / eqdf["cap"].cummax()).min() * 100 if len(eqdf) > 1 else 0
    yrs = max((eqdf["date"].iloc[-1] - eqdf["date"].iloc[0]).days / 365.25, 0.2) if len(eqdf) > 1 else 1
    ann = ((eqdf["cap"].iloc[-1] / INITIAL) ** (1 / yrs) - 1) * 100
    sh = eqdf["cap"].pct_change().mean() / (eqdf["cap"].pct_change().std() + 1e-9) * np.sqrt(252) if len(eqdf) > 2 else 0

    def sub(f):
        s = [t for t in trades if f(t)]
        if not s: return {}
        ps = [t.pnl for t in s]
        return {"次数": len(s), "胜率%": round(sum(1 for p in ps if p > 0) / len(ps) * 100, 1),
                "均收益%": round(float(np.mean(ps)), 2)}

    return {
        "收益": {"总收益率%": round(tr, 2), "年化%": round(ann, 2), "最大回撤%": round(dd, 2),
                "Sharpe": round(float(sh), 2), "Calmar": round(ann / abs(dd), 2) if dd else 0},
        "胜率": {"交易次数": len(trades), "胜率%": round(len(w) / len(trades) * 100, 1),
                "盈亏比": round(np.mean(w) / abs(np.mean(l)), 2) if w and l else 0,
                "均盈%": round(float(np.mean(w)), 2) if w else 0,
                "均亏%": round(float(np.mean(l)), 2) if l else 0},
        "情绪": {"冰点样本日": int(emo["ice"].sum()), "节点日": int(emo["node"].sum())},
        "烂板vs直接板": {"烂板": sub(lambda t: t.lanban), "直接板": sub(lambda t: not t.lanban)},
        "连板高度": {b: sub(lambda t, bb=b: t.board == bb) for b in ["2进3", "3进4", "4进5", "5进6+"]},
        "特征排序": feature_imp(trades),
    }


def feature_imp(trades):
    imp = []
    for name, fn in [("烂板回封", lambda t: t.lanban), ("2进3", lambda t: t.board == "2进3"),
                     ("3进4", lambda t: t.board == "3进4"), ("4进5", lambda t: t.board == "4进5")]:
        s = [t.pnl for t in trades if fn(t)]
        if s:
            imp.append({"变量": name, "均收益%": round(float(np.mean(s)), 2), "次数": len(s)})
    return sorted(imp, key=lambda x: -x["均收益%"])


def main():
    print("预加载全市场样本情绪指数...", flush=True)
    all_syms = list(set(BEAR50 + BULL50))
    all_dfs = {s: load(s, FULL_START, FULL_END) for s in all_syms}
    all_dfs = {k: v for k, v in all_dfs.items() if len(v) > 0}
    emo_full = emo_index(all_dfs)
    print(f"有效股票 {len(all_dfs)} 只", flush=True)

    result = {
        "数据说明": [
            "数据源: yfinance 前复权日线",
            "涨停/烂板/换手/竞价由 OHLCV 近似，非 tick 级",
            "情绪冰点/节点由100只样本截面涨跌代理全市场",
            "熊市样本: 2018全年50只 | 牛市样本: 2019.6-2021.2的50只",
            "全周期分阶段统计使用合并100只",
        ],
    }

    for label, syms in [("熊市50只_2018", BEAR50), ("牛市50只_2019-2021", BULL50)]:
        s, e = ("2018-01-01", "2018-12-31") if "熊" in label else ("2019-06-01", "2021-02-28")
        emo = emo_index({k: v[(v["date"] >= s) & (v["date"] <= e)] for k, v in all_dfs.items() if len(v) > 0})
        tr, eq = run(syms, s, e, label, emo)
        result[label] = stats(tr, eq, emo)
        print(f"\n=== {label} 交易{len(tr)}笔 ===", flush=True)

    for pname, (s, e) in PERIODS.items():
        emo = emo_index({k: v[(v["date"] >= s) & (v["date"] <= e)] for k, v in all_dfs.items()})
        tr, eq = run(all_syms, s, e, pname, emo)
        result[f"分阶段_{pname}"] = stats(tr, eq, emo)
        print(f"=== {pname} 交易{len(tr)}笔 ===", flush=True)

    # 合并
    tr_all, eq_all = run(all_syms, FULL_START, FULL_END, "全样本", emo_full)
    result["全样本_2018至今"] = stats(tr_all, eq_all, emo_full)

    p = Path(__file__).parent / "backtest_results.json"
    p.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n✓ 完成 → {p}", flush=True)
    return result


if __name__ == "__main__":
    main()
