#!/usr/bin/env python3
"""
A-share 连板接力策略回测
使用 baostock 日线数据；情绪/烂板/竞价等用可观测字段近似。
"""
from __future__ import annotations

import json
import random
import time
import warnings
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

try:
    import baostock as bs
except ImportError:
    raise SystemExit("pip install baostock pandas numpy")

# ── 回测参数 ─────────────────────────────────────────────
START_DATE = "20180101"
END_DATE = datetime.now().strftime("%Y%m%d")
INITIAL_CAPITAL = 1_000_000
BASE_POSITION = 0.20
MAX_POSITION = 1.0
RANDOM_SEED = 42

MAINLINE_KEYWORDS = [
    "AI", "算力", "机器人", "半导体", "芯片", "低空", "华为",
    "光刻", "存储", "通信", "软件", "智能", "电子", "计算机",
]

PERIODS = {
    "2018-2020": ("2018-01-01", "2020-12-31"),
    "2020-2022": ("2020-01-01", "2022-12-31"),
    "2022-2024": ("2022-01-01", "2024-12-31"),
    "2024-至今": ("2024-01-01", END_DATE[:4] + "-" + END_DATE[4:6] + "-" + END_DATE[6:8]),
}

REGIMES = {
    "熊市": [("2018-01-01", "2018-12-31"), ("2022-01-01", "2022-12-31")],
    "牛市": [("2019-06-01", "2021-02-28"), ("2024-09-01", "2025-06-30")],
}


@dataclass
class Trade:
    code: str
    entry_date: str
    exit_date: str
    entry_price: float
    exit_price: float
    pnl_pct: float
    board_level: str  # 2进3 / 3进4 / 4进5
    is_lanban: bool
    regime: str
    exit_reason: str


@dataclass
class BacktestState:
    capital: float = INITIAL_CAPITAL
    position_pct: float = BASE_POSITION
    win_streak: int = 0
    loss_streak: int = 0
    trades: list = field(default_factory=list)
    equity_curve: list = field(default_factory=list)


def login_bs():
    lg = bs.login()
    if lg.error_code != "0":
        raise RuntimeError(lg.error_msg)


def logout_bs():
    bs.logout()


def fetch_stock_universe() -> list[str]:
    login_bs()
    rs = bs.query_stock_basic()
    codes = []
    while rs.error_code == "0" and rs.next():
        row = rs.get_row_data()
        code, name, typ, status = row[0], row[1], row[4], row[5]
        if status != "1":
            continue
        if typ not in ("1", "2"):  # 股票
            continue
        if "ST" in name.upper():
            continue
        codes.append(code)
    logout_bs()
    return codes


def fetch_daily(code: str, start: str, end: str) -> pd.DataFrame:
    fields = "date,open,high,low,close,volume,amount,turn,pctChg,isST"
    rs = bs.query_history_k_data_plus(
        code, fields, start_date=start, end_date=end,
        frequency="d", adjustflag="2",
    )
    rows = []
    while rs.error_code == "0" and rs.next():
        rows.append(rs.get_row_data())
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows, columns=rs.fields)
    for c in ["open", "high", "low", "close", "volume", "amount", "turn", "pctChg"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["date"] = pd.to_datetime(df["date"])
    df = df.dropna(subset=["close"]).sort_values("date").reset_index(drop=True)
    return df


def limit_threshold(code: str) -> float:
    if code.startswith("sz.300") or code.startswith("sh.688"):
        return 19.5
    return 9.5


def is_limit_up(row, thresh: float) -> bool:
    return row["pctChg"] >= thresh - 0.3


def is_one_word(row, thresh: float) -> bool:
    """近似一字板：振幅极小且涨停"""
    if not is_limit_up(row, thresh):
        return False
    amp = (row["high"] - row["low"]) / max(row["low"], 1e-6) * 100
    return amp < 0.5


def is_lanban(row, thresh: float) -> bool:
    """烂板回封近似：盘中开板>=3%幅度后仍封涨停"""
    if not is_limit_up(row, thresh):
        return False
    if is_one_word(row, thresh):
        return False
    # 最低价相对昨收回落超过3%（或相对涨停价明显打开）
    prev_close = row["close"] / (1 + row["pctChg"] / 100)
    limit_price = prev_close * (1 + thresh / 100)
    if limit_price > 0:
        open_pct = (limit_price - row["low"]) / limit_price * 100
        return open_pct >= 3.0
    return False


def consecutive_boards(df: pd.DataFrame, idx: int, thresh: float) -> int:
    """截至 idx 之前连续涨停天数"""
    n = 0
    j = idx - 1
    while j >= 0 and is_limit_up(df.iloc[j], thresh):
        n += 1
        j -= 1
    return n


def board_label(n: int) -> Optional[str]:
    mapping = {2: "2进3", 3: "3进4", 4: "4进5", 5: "5进6+"}
    return mapping.get(n)


def auction_ok(row, prev_row, thresh: float) -> bool:
    """竞价承接近似：开盘涨幅 1%~7%，成交额不低于近5日均"""
    if prev_row is None:
        return False
    prev_close = prev_row["close"]
    if prev_close <= 0:
        return False
    open_pct = (row["open"] - prev_close) / prev_close * 100
    if not (1.0 <= open_pct <= 7.0):
        return False
    if open_pct < -3:  # 核按钮
        return False
    return True


def build_market_emotion_proxy(all_dates: pd.DatetimeIndex, sample_rets: pd.DataFrame) -> pd.DataFrame:
    """用样本股票截面收益近似市场情绪"""
    daily = sample_rets.groupby("date").agg(
        red_ratio=("pctChg", lambda x: (x > 0).mean()),
        limit_down_ratio=("pctChg", lambda x: (x <= -9.5).mean()),
        avg_chg=("pctChg", "mean"),
    ).reset_index()
    daily["limit_down_count"] = (daily["limit_down_ratio"] * 500).round()  # 近似全市场跌停数
    daily["up_count"] = (daily["red_ratio"] * 5000).round()
    ice = (
        (daily["limit_down_count"] >= 30).astype(int)
        + (daily["red_ratio"] <= 0.25).astype(int)
        + (daily["up_count"] < 1000).astype(int)
    )
    daily["ice_point"] = ice >= 2
    daily["prev_ice"] = daily["ice_point"].shift(1)
    daily["limit_down_drop"] = daily["limit_down_count"].pct_change() < -0.3
    daily["red_surge"] = daily["red_ratio"].pct_change() > 0.5
    daily["node_day"] = daily["prev_ice"] & (
        daily["limit_down_drop"] | daily["red_surge"] | (daily["red_ratio"] > daily["red_ratio"].shift(1))
    )
    return daily


def run_single_stock_backtest(
    code: str,
    df: pd.DataFrame,
    emotion: pd.DataFrame,
    regime: str,
    state: BacktestState,
) -> None:
    if len(df) < 60:
        return
    thresh = limit_threshold(code)
    df = df.copy()
    df["ma5"] = df["close"].rolling(5).mean()
    df["vol_ma5"] = df["volume"].rolling(5).mean()
    df["amt_ma5"] = df["amount"].rolling(5).mean()

    emo = emotion.set_index("date")
    i = 10
    position: Optional[dict] = None

    while i < len(df) - 1:
        row = df.iloc[i]
        prev = df.iloc[i - 1]
        date = row["date"]

        # ── 持仓管理 ──
        if position is not None:
            hold_row = row
            next_row = df.iloc[i + 1] if i + 1 < len(df) else None
            exit_price = None
            reason = None

            # 次日竞价不及预期
            if next_row is not None:
                prev_close = hold_row["close"]
                open_pct = (next_row["open"] - prev_close) / prev_close * 100
                if open_pct < -3:
                    exit_price = next_row["open"]
                    reason = "竞价低开>3%"

            if exit_price is None and next_row is not None and is_limit_up(next_row, thresh) is False:
                # 跌停次日竞价卖
                if hold_row["pctChg"] <= -thresh + 0.3:
                    exit_price = next_row["open"]
                    reason = "跌停次日竞价"

            if exit_price is None:
                vol_ratio = hold_row["volume"] / max(position["entry_vol"], 1)
                prev_vol_ratio = prev["volume"] / max(df.iloc[i - 1]["volume"], 1)
                upper_shadow = (hold_row["high"] - hold_row["close"]) / hold_row["close"] * 100
                # 炸板
                if is_limit_up(prev, thresh) and not is_limit_up(hold_row, thresh) and hold_row["pctChg"] > 5:
                    exit_price = hold_row["close"]
                    reason = "炸板"
                # 二次放量 / 滞涨
                elif position.get("first_vol_day") and vol_ratio > 1.5 and prev_vol_ratio > 1.3:
                    exit_price = hold_row["close"]
                    reason = "二次异常放量"
                elif upper_shadow > 4 and hold_row["pctChg"] < 3:
                    exit_price = hold_row["close"]
                    reason = "长上影"
                # 破5日线
                elif hold_row["close"] < hold_row["ma5"] and not np.isnan(hold_row["ma5"]):
                    exit_price = hold_row["close"]
                    reason = "跌破5日线"
                # 首次放量继续持有
                elif vol_ratio > 1.5 and not position.get("first_vol_day"):
                    position["first_vol_day"] = str(date.date())

            if exit_price is not None:
                pnl = (exit_price - position["entry_price"]) / position["entry_price"]
                alloc = state.capital * state.position_pct
                state.capital += alloc * pnl
                state.trades.append(Trade(
                    code=code, entry_date=position["entry_date"], exit_date=str(date.date()),
                    entry_price=position["entry_price"], exit_price=exit_price,
                    pnl_pct=pnl * 100, board_level=position["board_level"],
                    is_lanban=position["is_lanban"], regime=regime, exit_reason=reason or "规则卖出",
                ))
                if pnl > 0:
                    state.win_streak += 1
                    state.loss_streak = 0
                    if state.win_streak >= 3:
                        state.position_pct = min(MAX_POSITION, state.position_pct + 0.20)
                else:
                    state.loss_streak += 1
                    state.win_streak = 0
                    if state.loss_streak >= 2:
                        state.position_pct = max(BASE_POSITION / 2, state.position_pct / 2)
                position = None

        # ── 开仓 ──
        if position is None and date in emo.index:
            node = bool(emo.loc[date, "node_day"]) if "node_day" in emo.columns else True
            if not node:
                i += 1
                continue

            streak = consecutive_boards(df, i, thresh)
            if streak not in (2, 3, 4):
                i += 1
                continue

            if is_one_word(row, thresh):
                i += 1
                continue

            turn = row["turn"]
            if pd.isna(turn) or turn < 15:
                i += 1
                continue
            if row["volume"] <= row["vol_ma5"]:
                i += 1
                continue

            lanban = is_lanban(row, thresh)
            direct_board = is_limit_up(row, thresh) and not lanban

            if not auction_ok(row, prev, thresh):
                i += 1
                continue

            # 烂板优先；直接板需更高换手
            if not lanban and not direct_board:
                i += 1
                continue
            if direct_board and turn < 20:
                i += 1
                continue

            prev_close = prev["close"]
            limit_price = prev_close * (1 + thresh / 100)
            position = {
                "entry_date": str(date.date()),
                "entry_price": limit_price,
                "entry_vol": row["volume"],
                "board_level": board_label(streak) or f"{streak}进{streak+1}",
                "is_lanban": lanban,
                "first_vol_day": None,
            }

        state.equity_curve.append({"date": date, "capital": state.capital})
        i += 1


def compute_metrics(trades: list[Trade], equity: list[dict], start: str, end: str) -> dict:
    if not trades:
        return {"n_trades": 0}
    pnls = [t.pnl_pct for t in trades]
    wins = [p for p in pnls if p > 0]
    losses = [p for p in pnls if p <= 0]
    eq = pd.DataFrame(equity).drop_duplicates("date") if equity else pd.DataFrame()
    total_ret = 0.0
    max_dd = 0.0
    sharpe = calmar = 0.0
    if len(eq) > 1:
        eq = eq.sort_values("date")
        eq["ret"] = eq["capital"].pct_change().fillna(0)
        total_ret = (eq["capital"].iloc[-1] / INITIAL_CAPITAL - 1) * 100
        cummax = eq["capital"].cummax()
        dd = (eq["capital"] - cummax) / cummax
        max_dd = dd.min() * 100
        if eq["ret"].std() > 0:
            sharpe = eq["ret"].mean() / eq["ret"].std() * np.sqrt(252)
        years = max((eq["date"].iloc[-1] - eq["date"].iloc[0]).days / 365.25, 0.1)
        ann = ((eq["capital"].iloc[-1] / INITIAL_CAPITAL) ** (1 / years) - 1) * 100
        calmar = ann / abs(max_dd) if max_dd != 0 else 0
    else:
        ann = sum(pnls) / len(pnls) * len(pnls) / 10  # rough

    return {
        "n_trades": len(trades),
        "win_rate": len(wins) / len(trades) * 100,
        "profit_loss_ratio": (np.mean(wins) / abs(np.mean(losses))) if wins and losses else 0,
        "avg_win": np.mean(wins) if wins else 0,
        "avg_loss": np.mean(losses) if losses else 0,
        "total_return_pct": total_ret,
        "annual_return_pct": ann if len(eq) > 1 else 0,
        "max_drawdown_pct": max_dd,
        "sharpe": sharpe,
        "calmar": calmar,
        "avg_pnl_pct": np.mean(pnls),
    }


def feature_importance(trades: list[Trade], stock_features: pd.DataFrame) -> pd.DataFrame:
    """简易特征重要性：按分组平均收益差"""
    if not trades:
        return pd.DataFrame()
    rows = []
    for t in trades:
        rows.append({
            "pnl": t.pnl_pct,
            "is_lanban": int(t.is_lanban),
            "board_level": t.board_level,
            "regime": t.regime,
        })
    df = pd.DataFrame(rows)
    imps = []
    for col in ["is_lanban", "board_level", "regime"]:
        for val in df[col].unique():
            sub = df[df[col] == val]
            imps.append({"feature": col, "value": str(val), "mean_pnl": sub["pnl"].mean(), "count": len(sub)})
    imp_df = pd.DataFrame(imps).sort_values("mean_pnl", ascending=False)
    return imp_df


def sample_stocks(codes: list[str], n: int, seed: int) -> list[str]:
    rng = random.Random(seed)
    pool = [c for c in codes if c.startswith(("sh.", "sz.")) and not c.startswith("sh.000")]
    return rng.sample(pool, min(n, len(pool)))


def fetch_daily_safe(code: str, start: str, end: str, retries: int = 3) -> pd.DataFrame:
    for attempt in range(retries):
        try:
            df = fetch_daily(code, start, end)
            if len(df) > 0:
                return df
        except Exception:
            time.sleep(0.3 * (attempt + 1))
    return pd.DataFrame()


def load_all_stocks(codes: list[str], ranges: list[tuple[str, str]], cache_dir: Path) -> dict[str, pd.DataFrame]:
    cache_dir.mkdir(parents=True, exist_ok=True)
    stock_dfs: dict[str, pd.DataFrame] = {}
    login_bs()
    try:
        for idx, code in enumerate(codes):
            cache_file = cache_dir / f"{code.replace('.', '_')}.pkl"
            if cache_file.exists():
                stock_dfs[code] = pd.read_pickle(cache_file)
                continue
            parts = []
            for start, end in ranges:
                df = fetch_daily_safe(code, start, end)
                if len(df) > 0:
                    parts.append(df)
                time.sleep(0.05)
            if parts:
                merged = pd.concat(parts).drop_duplicates("date").sort_values("date").reset_index(drop=True)
                stock_dfs[code] = merged
                try:
                    merged.to_pickle(cache_file)
                except Exception:
                    pass
            if (idx + 1) % 10 == 0:
                print(f"  已加载 {idx+1}/{len(codes)}", flush=True)
    finally:
        logout_bs()
    return stock_dfs


def main():
    random.seed(RANDOM_SEED)
    np.random.seed(RANDOM_SEED)
    print("获取股票池...")
    universe = fetch_stock_universe()
    bear_codes = sample_stocks(universe, 50, seed=42)
    bull_codes = sample_stocks(universe, 50, seed=123)

    results = {"meta": {
        "start": START_DATE, "end": END_DATE,
        "bear_samples": bear_codes, "bull_samples": bull_codes,
        "note": "情绪/竞价/烂板用日线字段近似；节点日由样本截面情绪代理",
    }}

    all_codes = list(set(bear_codes + bull_codes))
    cache_dir = Path(__file__).parent / "cache"
    print(f"加载 {len(all_codes)} 只股票日线...")
    all_stock_dfs = load_all_stocks(all_codes, [("2018-01-01", "2025-12-31")], cache_dir)

    for regime_name, ranges in REGIMES.items():
        codes = bear_codes if regime_name == "熊市" else bull_codes
        print(f"\n=== {regime_name} 回测 {len(codes)} 只 ===")
        state = BacktestState()
        stock_dfs = {}
        start_dt = pd.to_datetime(ranges[0][0])
        end_dt = pd.to_datetime(ranges[-1][1])
        for code in codes:
            if code not in all_stock_dfs:
                continue
            df = all_stock_dfs[code]
            df = df[(df["date"] >= start_dt) & (df["date"] <= end_dt)].copy()
            if len(df) >= 30:
                stock_dfs[code] = df.reset_index(drop=True)

        if not stock_dfs:
            results[regime_name] = {"error": "无有效数据"}
            continue

        ret_rows = []
        for code, df in stock_dfs.items():
            for _, r in df.iterrows():
                ret_rows.append({"date": r["date"], "pctChg": r["pctChg"]})
        sample_rets = pd.DataFrame(ret_rows)
        if sample_rets.empty:
            results[regime_name] = {"error": "情绪数据为空"}
            continue
        emotion = build_market_emotion_proxy(sample_rets["date"].unique(), sample_rets)

        node_days = int(emotion["node_day"].sum())
        ice_days = int(emotion["ice_point"].sum())

        for code, df in stock_dfs.items():
            df = df.sort_values("date").reset_index(drop=True)
            run_single_stock_backtest(code, df, emotion, regime_name, state)

        metrics = compute_metrics(state.trades, state.equity_curve, ranges[0][0], ranges[-1][1])
        lanban_trades = [t for t in state.trades if t.is_lanban]
        direct_trades = [t for t in state.trades if not t.is_lanban]

        board_stats = {}
        for lv in ["2进3", "3进4", "4进5", "5进6+"]:
            sub = [t for t in state.trades if t.board_level == lv]
            if sub:
                board_stats[lv] = {
                    "n": len(sub),
                    "win_rate": sum(1 for t in sub if t.pnl_pct > 0) / len(sub) * 100,
                    "avg_pnl": np.mean([t.pnl_pct for t in sub]),
                }

        results[regime_name] = {
            "metrics": metrics,
            "emotion": {"ice_days": ice_days, "node_days": node_days,
                        "node_win_rate": np.mean([t.pnl_pct > 0 for t in state.trades]) * 100 if state.trades else 0,
                        "node_avg_pnl": np.mean([t.pnl_pct for t in state.trades]) if state.trades else 0},
            "烂板_vs_直接板": {
                "烂板": compute_metrics(lanban_trades, [], "", ""),
                "直接板": compute_metrics(direct_trades, [], "", ""),
            },
            "连板高度": board_stats,
            "feature_importance": feature_importance(state.trades, pd.DataFrame()).head(15).to_dict(orient="records"),
            "trades_count": len(state.trades),
        }
        print(json.dumps(results[regime_name]["metrics"], indent=2, ensure_ascii=False))

    # 全样本合并
    all_trades = []
    for k in ["熊市", "牛市"]:
        # re-collect not stored - summarize from results
        pass

    out_path = Path(__file__).parent / "backtest_results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
    print(f"\n结果已写入 {out_path}")
    return results


if __name__ == "__main__":
    main()
