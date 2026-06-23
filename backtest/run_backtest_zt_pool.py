#!/usr/bin/env python3
"""
连板接力回测 v3 — 动态涨停池（2022-2025）
从活跃 A 股中扫描真实连板事件，等效于「当日涨停池中的连板标的」
"""
import json, random, time, warnings
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf
import akshare as ak

warnings.filterwarnings("ignore")
random.seed(42)

START, END = "2022-01-01", "2025-06-30"
INITIAL = 1_000_000
CACHE = Path(__file__).parent / "cache_v3"


@dataclass
class Trade:
    code: str
    name: str
    entry: str
    exit: str
    pnl: float
    board: str
    lanban: bool
    zhaban: int  # 炸板次数代理
    reason: str


def get_universe(n_active: int = 200) -> list[tuple[str, str]]:
    """沪深300 + 高波动中小盘，再筛出2022-2025有过涨停的活跃股"""
    hs = ak.index_stock_cons(symbol="000300")
    codes = [(f"{int(c):06d}", n) for c, n in zip(hs["品种代码"], hs["品种名称"])]
    # 补充常见连板活跃板块
    extra = [
        ("300476", "胜宏科技"), ("002384", "东山精密"), ("002463", "沪电股份"), ("688072", "拓荆科技"),
        ("688498", "源杰科技"), ("688146", "中船特气"), ("600183", "生益科技"), ("002436", "兴森科技"),
        ("300308", "中际旭创"), ("300502", "新易盛"), ("601138", "工业富联"), ("002230", "科大讯飞"),
        ("300024", "机器人"), ("002261", "拓维信息"), ("603019", "中科曙光"), ("000977", "浪潮信息"),
        ("300418", "昆仑万维"), ("688256", "寒武纪"), ("688041", "海光信息"), ("301217", "铜冠铜箔"),
        ("002428", "云南锗业"), ("688676", "金盘科技"), ("002837", "英维克"), ("688082", "盛美上海"),
    ]
    for c, n in extra:
        codes.append((c, n))
    # 去重
    seen = set()
    uniq = []
    for c, n in codes:
        if c not in seen:
            seen.add(c)
            uniq.append((c, n))
    return uniq[:350]  # 扫描池


def to_yf(code: str) -> str:
    c = int(code)
    if c >= 600000:
        return f"{code}.SS"
    return f"{code}.SZ"


def load(code: str) -> pd.DataFrame:
    CACHE.mkdir(parents=True, exist_ok=True)
    fp = CACHE / f"{code}.csv"
    if fp.exists():
        df = pd.read_csv(fp, parse_dates=["date"])
        return df
    sym = to_yf(code)
    h = yf.download(sym, start=START, end=END, progress=False, auto_adjust=True)
    if h is None or len(h) < 30:
        return pd.DataFrame()
    if isinstance(h.columns, pd.MultiIndex):
        h.columns = h.columns.get_level_values(0)
    df = h.reset_index()
    df.columns = [str(c).lower() for c in df.columns]
    df["date"] = pd.to_datetime(df["date"]).dt.tz_localize(None)
    df["pct"] = df["close"].pct_change() * 100
    df.to_csv(fp, index=False)
    time.sleep(0.02)
    return df


def thresh(code: str) -> float:
    if code.startswith("688") or code.startswith("300"):
        return 19.5
    return 9.5


def zt(r, t) -> bool:
    return r["pct"] >= t - 0.5


def yizi(r, t) -> bool:
    return zt(r, t) and (r["high"] - r["low"]) / max(r["low"], 1e-9) * 100 < 1.0


def lanban_metrics(r, t) -> tuple[bool, int]:
    if not zt(r, t) or yizi(r, t):
        return False, 0
    pc = r["close"] / (1 + r["pct"] / 100)
    lp = pc * (1 + t / 100)
    open_pct = (lp - r["low"]) / lp * 100 if lp > 0 else 0
    is_lb = open_pct >= 2.5
    zhaban = 1 if is_lb else 0
    if is_lb and open_pct >= 5:
        zhaban = 2
    return is_lb, zhaban


def streak(df, i, t) -> int:
    n, j = 0, i - 1
    while j >= 0 and zt(df.iloc[j], t):
        n += 1
        j -= 1
    return n


def build_emotion(dfs: dict) -> pd.DataFrame:
    rows = []
    for df in dfs.values():
        for _, r in df.iterrows():
            rows.append((r["date"], r["pct"]))
    m = pd.DataFrame(rows, columns=["date", "pct"])
    g = m.groupby("date").agg(
        red=("pct", lambda x: (x > 0).mean()),
        down_limit=("pct", lambda x: (x <= -9.5).sum()),
        up_count=("pct", lambda x: (x > 0).sum()),
    ).reset_index()
    g["ice"] = (
        (g["down_limit"] >= 3)
        | (g["red"] <= 0.28)
        | (g["up_count"] < len(dfs) * 0.15)
    )
    g["node"] = g["ice"].shift(1) & (
        (g["down_limit"].diff() < 0) | (g["red"].diff() > 0.04)
    )
    return g.set_index("date")


def run_backtest(universe: list[tuple[str, str]]) -> dict:
    print(f"加载 {len(universe)} 只股票...", flush=True)
    dfs, names = {}, {}
    active = []
    for code, name in universe:
        df = load(code)
        if len(df) < 80:
            continue
        t = thresh(code)
        n_zt = sum(zt(df.iloc[i], t) for i in range(1, len(df)))
        if n_zt >= 2:  # 涨停活跃池：至少2次涨停
            dfs[code] = df
            names[code] = name
            active.append((code, name, n_zt))
    print(f"涨停活跃池 {len(dfs)} 只（2022-2025 至少2次涨停）", flush=True)
    top = sorted(active, key=lambda x: -x[2])[:15]
    print("最活跃:", ", ".join(f"{n}({c})" for c, n, _ in top[:8]), flush=True)

    emo = build_emotion(dfs)
    trades: list[Trade] = []
    cap = INITIAL
    pos_pct = 0.2
    ws = ls = 0
    eq = []

    for code, df in dfs.items():
        t = thresh(code)
        name = names[code]
        df = df.copy()
        df["ma5"] = df["close"].rolling(5).mean()
        df["vma5"] = df["volume"].rolling(5).mean()
        pos = None
        for i in range(10, len(df) - 2):
            r, p = df.iloc[i], df.iloc[i - 1]
            d = r["date"]
            if pos:
                ex = rs = None
                nx, n2 = df.iloc[i + 1], df.iloc[i + 2]
                op = (nx["open"] - r["close"]) / r["close"] * 100
                if op < -3:
                    ex, rs = nx["open"], "竞价低开>3%"
                elif r["close"] < r["ma5"]:
                    ex, rs = r["close"], "破5日线"
                elif zt(p, t) and not zt(r, t) and r["pct"] > 3:
                    ex, rs = r["close"], "炸板"
                elif r["volume"] > p["volume"] * 1.5 and pos.get("vol_hold"):
                    if r["volume"] > df.iloc[i - 1]["volume"] * 1.3:
                        ex, rs = r["close"], "二次放量"
                elif r["pct"] <= -t + 0.5:
                    ex, rs = n2["open"], "跌停次日竞价"
                else:
                    if r["volume"] > p["volume"] * 1.5:
                        pos["vol_hold"] = True
                if ex:
                    pnl = (ex - pos["ep"]) / pos["ep"] * 100
                    cap += cap * pos_pct * pnl / 100
                    trades.append(Trade(code, name, pos["ed"], str(d.date()), pnl,
                                        pos["bd"], pos["lb"], pos["zb"], rs))
                    if pnl > 0:
                        ws += 1; ls = 0
                        if ws >= 3: pos_pct = min(1.0, pos_pct + 0.2)
                    else:
                        ls += 1; ws = 0
                        if ls >= 2: pos_pct = max(0.1, pos_pct / 2)
                    pos = None
            if pos is None and d in emo.index and bool(emo.loc[d, "node"]):
                st = streak(df, i, t)
                if st not in (2, 3, 4) or yizi(r, t):
                    continue
                if r["volume"] < r["vma5"] * 1.1:
                    continue
                is_lb, zb = lanban_metrics(r, t)
                oc = (r["open"] - p["close"]) / p["close"] * 100
                if oc < -5 or oc > 9:
                    continue
                turn_proxy = r["volume"] / r["vma5"] * 10
                if turn_proxy < 12:
                    continue
                if not is_lb and turn_proxy < 18:
                    continue
                ep = p["close"] * (1 + t / 100)
                pos = {
                    "ed": str(d.date()), "ep": ep,
                    "bd": {2: "2进3", 3: "3进4", 4: "4进5"}.get(st, "5进6+"),
                    "lb": is_lb, "zb": zb, "vol_hold": False,
                }
            eq.append({"date": d, "cap": cap})

    return pack(trades, eq, emo, len(dfs))


def pack(trades, eq, emo, n_stocks) -> dict:
    if not trades:
        return {"交易次数": 0, "涨停池股票数": n_stocks}
    pnls = [t.pnl for t in trades]
    w = [x for x in pnls if x > 0]
    l = [x for x in pnls if x <= 0]
    eqdf = pd.DataFrame(eq).drop_duplicates("date").sort_values("date")
    tr = (eqdf["cap"].iloc[-1] / INITIAL - 1) * 100
    dd = ((eqdf["cap"] - eqdf["cap"].cummax()) / eqdf["cap"].cummax()).min() * 100
    yrs = max((eqdf["date"].iloc[-1] - eqdf["date"].iloc[0]).days / 365.25, 0.3)
    ann = ((eqdf["cap"].iloc[-1] / INITIAL) ** (1 / yrs) - 1) * 100
    sh = eqdf["cap"].pct_change().mean() / (eqdf["cap"].pct_change().std() + 1e-9) * np.sqrt(252)

    def sub(f):
        s = [t for t in trades if f(t)]
        if not s: return {}
        ps = [t.pnl for t in s]
        return {"次数": len(s), "胜率%": round(sum(1 for p in ps if p > 0) / len(ps) * 100, 1),
                "均收益%": round(float(np.mean(ps)), 2),
                "累计贡献%": round(float(np.sum(ps)), 2)}

    # ML-style feature importance via mean pnl diff
    feats = []
    for label, fn in [
        ("烂板回封", lambda t: t.lanban),
        ("直接封板", lambda t: not t.lanban),
        ("炸板≥2次", lambda t: t.zhaban >= 2),
        ("2进3", lambda t: t.board == "2进3"),
        ("3进4", lambda t: t.board == "3进4"),
        ("4进5", lambda t: t.board == "4进5"),
    ]:
        s = [t.pnl for t in trades if fn(t)]
        if s:
            feats.append({"变量": label, "次数": len(s), "均收益%": round(float(np.mean(s)), 2),
                          "胜率%": round(sum(1 for p in s if p > 0) / len(s) * 100, 1)})
    feats.sort(key=lambda x: -x["均收益%"])

    return {
        "涨停池股票数": n_stocks,
        "收益": {"总收益率%": round(tr, 2), "年化%": round(ann, 2),
                "最大回撤%": round(dd, 2), "Sharpe": round(float(sh), 2),
                "Calmar": round(ann / abs(dd), 2) if dd else 0},
        "胜率": {"交易次数": len(trades), "胜率%": round(len(w) / len(trades) * 100, 1),
                "盈亏比": round(np.mean(w) / abs(np.mean(l)), 2) if w and l else 0,
                "均盈%": round(float(np.mean(w)), 2) if w else 0,
                "均亏%": round(float(np.mean(l)), 2) if l else 0},
        "情绪节点": {"冰点日": int(emo["ice"].sum()), "节点日": int(emo["node"].sum()),
                  "节点交易笔数": len(trades)},
        "烂板vs直接板": {"烂板回封": sub(lambda t: t.lanban), "直接封板": sub(lambda t: not t.lanban)},
        "连板高度": {b: sub(lambda t, bb=b: t.board == bb) for b in ["2进3", "3进4", "4进5", "5进6+"]},
        "特征重要性": feats,
        "样本交易": [{"代码": t.code, "名称": t.name, "板": t.board, "烂板": bool(t.lanban),
                    "收益%": round(t.pnl, 2), "卖因": t.reason} for t in trades[:12]],
    }


def main():
    uni = get_universe()
    result = {
        "版本": "v3 动态涨停池 2022-2025",
        "说明": "从沪深300+热门题材股扫描；纳入至少2次涨停的活跃股；东财API不可用故用日线近似烂板/换手",
    }
    result["全周期"] = run_backtest(uni)
    print(json.dumps(result["全周期"], ensure_ascii=False, indent=2), flush=True)
    out = Path(__file__).parent / "backtest_zt_pool_2022_2025.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n✓ {out}", flush=True)


if __name__ == "__main__":
    main()
