#!/usr/bin/env python3
"""连板接力策略快速回测 — yfinance 拉数 + 策略逻辑"""
import json, random, warnings
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf

warnings.filterwarnings("ignore")
random.seed(42)
np.random.seed(42)

INITIAL = 1_000_000
BASE_POS = 0.20

REGIMES = {
    "熊市": ("2018-01-01", "2018-12-31"),
    "牛市": ("2019-06-01", "2021-02-28"),
}

# 固定随机样本（可复现）
BEAR_POOL = [
    "000001.SZ","000002.SZ","000063.SZ","000100.SZ","000157.SZ","000333.SZ","000538.SZ","000651.SZ",
    "000725.SZ","000768.SZ","000858.SZ","000876.SZ","002001.SZ","002007.SZ","002024.SZ","002027.SZ",
    "002032.SZ","002044.SZ","002050.SZ","002120.SZ","002142.SZ","002179.SZ","002230.SZ","002236.SZ",
    "002241.SZ","002252.SZ","002271.SZ","002304.SZ","002311.SZ","002352.SZ","002410.SZ","002415.SZ",
    "002456.SZ","002460.SZ","002475.SZ","002493.SZ","002508.SZ","002555.SZ","002594.SZ","002601.SZ",
    "002714.SZ","002736.SZ","002812.SZ","002821.SZ","002841.SZ","002916.SZ","002938.SZ","300014.SZ",
    "300015.SZ","300059.SZ",
]
BULL_POOL = [
    "600000.SS","600009.SS","600016.SS","600019.SS","600028.SS","600030.SS","600031.SS","600036.SS",
    "600048.SS","600050.SS","600104.SS","600111.SS","600196.SS","600276.SS","600309.SS","600340.SS",
    "600406.SS","600436.SS","600438.SS","600519.SS","600547.SS","600570.SS","600585.SS","600588.SS",
    "600600.SS","600660.SS","600690.SS","600703.SS","600745.SS","600809.SS","600837.SS","600887.SS",
    "600893.SS","600900.SS","601012.SS","601066.SS","601088.SS","601138.SS","601166.SS","601211.SS",
    "601288.SS","601318.SS","601336.SS","601398.SS","601601.SS","601628.SS","601668.SS","601688.SS",
    "601766.SS","601857.SS",
]


@dataclass
class Trade:
    symbol: str
    entry: str
    exit: str
    pnl_pct: float
    board: str
    lanban: bool
    regime: str
    reason: str


def yf_to_df(sym: str, start: str, end: str) -> pd.DataFrame:
    h = yf.download(sym, start=start, end=end, progress=False, auto_adjust=True)
    if h is None or len(h) == 0:
        return pd.DataFrame()
    if isinstance(h.columns, pd.MultiIndex):
        h.columns = h.columns.get_level_values(0)
    df = h.reset_index()
    df.columns = [str(c).lower() for c in df.columns]
    df["date"] = pd.to_datetime(df["date"]).dt.tz_localize(None)
    df["pctchg"] = df["close"].pct_change() * 100
    df["turn"] = df["volume"] / df["volume"].rolling(20).mean() * 10  # 换手代理
    df["amount"] = df["close"] * df["volume"]
    return df.dropna(subset=["close"])


def thresh(sym: str) -> float:
    if sym.startswith("300") or sym.startswith("688"):
        return 19.5
    return 9.5


def limit_up(r, t) -> bool:
    return r["pctchg"] >= t - 0.4


def one_word(r, t) -> bool:
    if not limit_up(r, t):
        return False
    amp = (r["high"] - r["low"]) / max(r["low"], 1e-9) * 100
    return amp < 0.8


def lanban(r, t) -> bool:
    if not limit_up(r, t) or one_word(r, t):
        return False
    prev_c = r["close"] / (1 + r["pctchg"] / 100)
    lp = prev_c * (1 + t / 100)
    return (lp - r["low"]) / lp * 100 >= 3


def streak(df, i, t) -> int:
    n, j = 0, i - 1
    while j >= 0 and limit_up(df.iloc[j], t):
        n += 1
        j -= 1
    return n


def board_label(n):
    return {2: "2进3", 3: "3进4", 4: "4进5", 5: "5进6+"}.get(n)


def emotion_proxy(dfs: dict) -> pd.DataFrame:
    rows = []
    for df in dfs.values():
        for _, r in df.iterrows():
            rows.append({"date": r["date"], "pct": r["pctchg"]})
    m = pd.DataFrame(rows)
    g = m.groupby("date").agg(red=("pct", lambda x: (x > 0).mean()), avg=("pct", "mean"),
                              ld=("pct", lambda x: (x <= -9.5).sum())).reset_index()
    g["ice"] = ((g["ld"] >= 5) | (g["red"] <= 0.25)).astype(int) >= 1
    g["prev_ice"] = g["ice"].shift(1)
    g["node"] = g["prev_ice"] & (g["red"].diff() > 0.05)
    return g


def backtest_regime(name: str, symbols: list, start: str, end: str) -> dict:
    print(f"加载 {name} {len(symbols)} 只...", flush=True)
    dfs = {}
    for s in symbols:
        df = yf_to_df(s, start, end)
        if len(df) >= 40:
            dfs[s] = df
    print(f"  有效 {len(dfs)} 只", flush=True)
    if not dfs:
        return {"error": "no data"}

    emo = emotion_proxy(dfs).set_index("date")
    trades: list[Trade] = []
    capital = INITIAL
    pos_pct = BASE_POS
    win_s = loss_s = 0
    equity = []

    for sym, df in dfs.items():
        t = thresh(sym)
        df = df.copy()
        df["ma5"] = df["close"].rolling(5).mean()
        df["vma5"] = df["volume"].rolling(5).mean()
        pos = None
        for i in range(10, len(df) - 1):
            row, prev = df.iloc[i], df.iloc[i - 1]
            d = row["date"]
            if pos:
                reason = exit_p = None
                nxt = df.iloc[i + 1]
                op = (nxt["open"] - row["close"]) / row["close"] * 100
                if op < -3:
                    exit_p, reason = nxt["open"], "竞价低开>3%"
                elif row["close"] < row["ma5"]:
                    exit_p, reason = row["close"], "破5日线"
                elif limit_up(prev, t) and not limit_up(row, t) and row["pctchg"] > 4:
                    exit_p, reason = row["close"], "炸板"
                if exit_p:
                    pnl = (exit_p - pos["ep"]) / pos["ep"] * 100
                    capital += capital * pos_pct * pnl / 100
                    trades.append(Trade(sym, pos["ed"], str(d.date()), pnl, pos["bd"], pos["lb"], name, reason))
                    if pnl > 0:
                        win_s += 1; loss_s = 0
                        if win_s >= 3: pos_pct = min(1.0, pos_pct + 0.2)
                    else:
                        loss_s += 1; win_s = 0
                        if loss_s >= 2: pos_pct = max(0.1, pos_pct / 2)
                    pos = None
            if pos is None and d in emo.index and bool(emo.loc[d, "node"]):
                st = streak(df, i, t)
                if st not in (2, 3, 4) or one_word(row, t):
                    continue
                if row["turn"] < 15 or row["volume"] <= row["vma5"]:
                    continue
                lb = lanban(row, t)
                oc = (row["open"] - prev["close"]) / prev["close"] * 100
                if not (1 <= oc <= 7) or oc < -3:
                    continue
                if not lb and row["turn"] < 20:
                    continue
                ep = prev["close"] * (1 + t / 100)
                pos = {"ed": str(d.date()), "ep": ep, "bd": board_label(st) or str(st), "lb": lb}
            equity.append({"date": d, "cap": capital})

    return summarize(trades, equity, emo, name)


def summarize(trades, equity, emo, regime) -> dict:
    if not trades:
        return {"regime": regime, "n_trades": 0, "note": "样本期内无满足全部条件的交易"}
    pnls = [t.pnl_pct for t in trades]
    wins = [p for p in pnls if p > 0]
    losses = [p for p in pnls if p <= 0]
    eq = pd.DataFrame(equity).drop_duplicates("date").sort_values("date")
    total_ret = (eq["cap"].iloc[-1] / INITIAL - 1) * 100
    dd = ((eq["cap"] - eq["cap"].cummax()) / eq["cap"].cummax()).min() * 100
    yrs = max((eq["date"].iloc[-1] - eq["date"].iloc[0]).days / 365.25, 0.1)
    ann = ((eq["cap"].iloc[-1] / INITIAL) ** (1 / yrs) - 1) * 100
    sh = eq["cap"].pct_change().mean() / (eq["cap"].pct_change().std() + 1e-9) * np.sqrt(252)

    lanban = [t for t in trades if t.lanban]
    direct = [t for t in trades if not t.lanban]

    def sub_stats(ts):
        if not ts: return {}
        ps = [t.pnl_pct for t in ts]
        return {"n": len(ts), "win_rate": sum(1 for p in ps if p > 0) / len(ps) * 100,
                "avg_pnl": float(np.mean(ps))}

    boards = {}
    for lv in ["2进3", "3进4", "4进5", "5进6+"]:
        boards[lv] = sub_stats([t for t in trades if t.board == lv])

    return {
        "regime": regime,
        "收益": {"总收益率%": round(total_ret, 2), "年化%": round(ann, 2),
                "最大回撤%": round(dd, 2), "Sharpe": round(sh, 2),
                "Calmar": round(ann / abs(dd), 2) if dd else 0},
        "胜率": {"交易次数": len(trades), "胜率%": round(len(wins) / len(trades) * 100, 1),
                "盈亏比": round(np.mean(wins) / abs(np.mean(losses)), 2) if wins and losses else 0,
                "均盈%": round(np.mean(wins), 2) if wins else 0, "均亏%": round(np.mean(losses), 2) if losses else 0},
        "情绪节点": {"冰点日": int(emo["ice"].sum()), "节点日": int(emo["node"].sum()),
                  "节点交易胜率%": round(len(wins) / len(trades) * 100, 1),
                  "节点均收益%": round(float(np.mean(pnls)), 2)},
        "烂板vs直接板": {"烂板回封": sub_stats(lanban), "直接封板": sub_stats(direct)},
        "连板高度": boards,
        "特征重要性": feature_rank(trades),
    }


def feature_rank(trades: list[Trade]) -> list:
    rows = [{"pnl": t.pnl_pct, "烂板": t.lanban, "board": t.board} for t in trades]
    df = pd.DataFrame(rows)
    out = []
    for col in ["烂板", "board"]:
        for v in df[col].unique():
            s = df[df[col] == v]
            out.append({"变量": col, "取值": str(v), "均收益%": round(s["pnl"].mean(), 2), "次数": len(s)})
    return sorted(out, key=lambda x: -x["均收益%"])[:8]


def main():
    out = {"说明": "yfinance日线近似回测；换手/烂板/竞价/情绪为代理变量；牛熊各50只固定样本"}
    for regime, (s, e) in REGIMES.items():
        syms = BEAR_POOL if regime == "熊市" else BULL_POOL
        out[regime] = backtest_regime(regime, syms, s, e)
        print(json.dumps(out[regime], ensure_ascii=False, indent=2), flush=True)
    p = Path(__file__).parent / "backtest_results.json"
    p.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n✓ 已保存 {p}", flush=True)


if __name__ == "__main__":
    main()
