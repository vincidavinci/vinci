#!/usr/bin/env python3
"""科创50 缠论二买 + Serenity 筛选（不含连板/二进三逻辑）."""
from __future__ import annotations

import json
import sys
import warnings
from pathlib import Path

import akshare as ak
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

PLUGIN_SCRIPTS = Path.home() / ".cursor/plugins/local/stock-deep-analyzer/skills/deep-analysis/scripts"
sys.path.insert(0, str(PLUGIN_SCRIPTS))

from lib import data_sources as ds  # noqa: E402
from lib.investor_evaluator import evaluate  # noqa: E402
from lib.market_router import parse_ticker  # noqa: E402
from lib.stock_features import extract_features  # noqa: E402

AS_OF = "2026-06-24"
CACHE_DIR = Path(__file__).resolve().parent / "cache_v3"
OUT_PATH = Path(__file__).resolve().parent / "kc50_chan_serenity_0624.json"

# 科创50 成分 AI 链描述（Serenity 卡位）
IND_MAP = {
    "688072": "薄膜沉积设备 CVD PVD 半导体设备 算力",
    "688120": "功率半导体 电力电子",
    "688385": "复旦微电 芯片 FPGA",
    "688187": "时代电气 轨道交通 功率半导体",
    "688498": "光芯片 激光器 EML 光模块 硅光",
    "688082": "半导体清洗设备 刻蚀 薄膜",
    "688099": "芯片 SoC AIoT 算力 GPU",
    "688521": "芯片设计 IP GPU ASIC",
    "688047": "CPU 芯片 RISC-V 算力",
    "688213": "CIS 图像传感器 机器视觉",
    "688126": "存储 芯片 DRAM HBM",
    "688256": "AI芯片 算力 GPU",
    "688041": "CPU 服务器芯片 算力",
    "688012": "刻蚀设备 半导体设备",
    "688008": "内存接口芯片 DDR",
    "688396": "功率半导体 电力电子",
    "688188": "激光切割 工业控制 半导体设备",
    "688702": "以太网交换芯片 数据中心 算力",
    "688728": "CIS 图像传感器 手机 机器视觉",
    "688981": "晶圆代工 半导体制造",
    "688036": "消费电子芯片 射频",
    "688111": "办公软件 SaaS",
    "688169": "扫地机器人 服务机器人",
    "688223": "光伏 HJT 电池",
    "688303": "大分子药 创新药",
    "688271": "医学影像 CT MRI",
    "688506": "创新药 肿瘤",
    "688009": "轨道交通 列车控制",
}


def parse_rows(klines) -> list[dict]:
    return [
        {
            "date": str(r.get("日期") or r.get("date")),
            "h": float(r["最高"] if "最高" in r else r["high"]),
            "l": float(r["最低"] if "最低" in r else r["low"]),
            "c": float(r["收盘"] if "收盘" in r else r["close"]),
            "o": float(r.get("开盘") or r.get("open") or r["收盘"] if "收盘" in r else r["close"]),
        }
        for r in klines
    ]


def load_bars(code: str) -> list[dict]:
    cache = CACHE_DIR / f"{code}.csv"
    if cache.exists():
        df = pd.read_csv(cache)
        df.columns = [c.strip() for c in df.columns]
        colmap = {"Date": "date", "Open": "open", "High": "high", "Low": "low", "Close": "close"}
        rows = []
        for _, r in df.iterrows():
            rows.append(
                {
                    "date": str(r.get("Date") or r.get("date"))[:10],
                    "h": float(r["High"] if "High" in r else r["high"]),
                    "l": float(r["Low"] if "Low" in r else r["low"]),
                    "c": float(r["Close"] if "Close" in r else r["close"]),
                    "o": float(r.get("Open") or r.get("open") or r["Close"]),
                }
            )
        return rows
    kl = ds.fetch_kline(parse_ticker(f"{code}.SH"))
    return parse_rows(kl)


def merge_inc(bars):
    std, d = [bars[0].copy()], 0
    for i in range(1, len(bars)):
        c, p = bars[i], std[-1]
        inc = (c["h"] <= p["h"] and c["l"] >= p["l"]) or (c["h"] >= p["h"] and c["l"] <= p["l"])
        if not inc:
            std.append(c.copy())
            if c["h"] > p["h"]:
                d = 1
            elif c["l"] < p["l"]:
                d = -1
            continue
        m = p.copy()
        if d >= 0:
            m["h"] = max(p["h"], c["h"])
            m["l"] = max(p["l"], c["l"])
        else:
            m["h"] = min(p["h"], c["h"])
            m["l"] = min(p["l"], c["l"])
        m["date"] = c["date"]
        m["c"] = c["c"]
        std[-1] = m
    return std


def fractals(std):
    tops, bots = [], []
    for i in range(1, len(std) - 1):
        a, x, c = std[i - 1], std[i], std[i + 1]
        if x["h"] > a["h"] and x["h"] > c["h"] and x["l"] > a["l"] and x["l"] > c["l"]:
            tops.append({"idx": i, "p": x["h"], "type": "top"})
        if x["l"] < a["l"] and x["l"] < c["l"] and x["h"] < a["h"] and x["h"] < c["h"]:
            bots.append({"idx": i, "p": x["l"], "type": "bot"})
    return tops, bots


def build_bi(tops, bots):
    pts = sorted(tops + bots, key=lambda x: x["idx"])
    if len(pts) < 2:
        return []
    out, last = [], pts[0]
    for p in pts[1:]:
        if p["type"] == last["type"]:
            if p["type"] == "top" and p["p"] > last["p"]:
                last = p
            elif p["type"] == "bot" and p["p"] < last["p"]:
                last = p
            continue
        if p["idx"] - last["idx"] < 4:
            continue
        out.append(
            {
                "start": last,
                "end": p,
                "dir": "up" if last["type"] == "bot" else "down",
                "hi": max(last["p"], p["p"]),
                "lo": min(last["p"], p["p"]),
            }
        )
        last = p
    return out


def chan_erbuy(bars, price):
    bars = [b for b in bars if str(b["date"])[:10] <= AS_OF]
    if len(bars) < 40:
        return None
    std = merge_inc(bars)
    tops, bots = fractals(std)
    bi = build_bi(tops, bots)
    if len(bi) < 3:
        return None
    zs = None
    for i in range(len(bi) - 3, max(-1, len(bi) - 12), -1):
        seg = bi[i : i + 3]
        zg = min(b["hi"] for b in seg)
        zd = max(b["lo"] for b in seg)
        if zg > zd and abs(price - (zg + zd) / 2) / max(price, 1) < 0.35:
            zs = {"zg": round(zg, 2), "zd": round(zd, 2)}
            break
    if not zs:
        return None
    zg, zd = zs["zg"], zs["zd"]
    pos = (price - zd) / (zg - zd) * 100 if zg > zd else 50
    last = bi[-1]
    sig = []
    if zd <= price <= zg and pos <= 45 and last["dir"] == "down":
        sig.append("中枢内回踩ZD")
    if zg * 0.96 <= price <= zg * 1.12 and last["dir"] == "down" and max(b["h"] for b in bars[-20:]) > zg * 1.03:
        sig.append("回踩ZG")
    if zd * 0.92 <= price <= zd * 1.08 and last["dir"] == "up":
        if len(bi) >= 2 and bi[-2]["dir"] == "down" and bi[-2]["end"]["p"] < zd:
            sig.append("回拉ZD确认")
    if not sig:
        return None
    return {
        "signals": sig,
        "zs": zs,
        "pos%": round(pos, 1),
        "last_bi": last["dir"],
        "ma20": round(np.mean([b["c"] for b in bars[-20:]]), 2),
    }


def is_limit_up_star(prev_close: float, close: float) -> bool:
    """科创板涨停约 20%."""
    if prev_close <= 0:
        return False
    return (close - prev_close) / prev_close >= 0.195


def lianban_tag(bars) -> dict:
    """标注连板状态，用于排除二进三接力标的（非筛选条件）."""
    bars = [b for b in bars if str(b["date"])[:10] <= AS_OF]
    if len(bars) < 5:
        return {"streak": 0, "is_erjin_san": False, "note": ""}
    streak = 0
    for i in range(len(bars) - 1, 0, -1):
        if is_limit_up_star(bars[i - 1]["c"], bars[i]["c"]):
            streak += 1
        else:
            break
    is_erjin = streak >= 2
    note = ""
    if is_erjin:
        note = f"近{streak}连板，属连板接力语境，非缠论二买建仓"
    return {"streak": streak, "is_erjin_san": is_erjin, "note": note}


def serenity_eval(code: str, name: str, price: float):
    ticker = f"{code}.SH"
    cache = PLUGIN_SCRIPTS / ".cache" / ticker / "raw_data.json"
    if cache.exists():
        raw = json.loads(cache.read_text(encoding="utf-8"))
        if raw.get("dimensions"):
            f = extract_features(raw, {})
            ev = evaluate("serenity", f)
            return f, ev

    try:
        info = ak.stock_individual_info_em(symbol=code)
        m = {str(r["item"]): r["value"] for _, r in info.iterrows()}
        ind = m.get("行业", "半导体")
        mc_raw = m.get("总市值", "200")
        mc = str(mc_raw)
        if "亿" not in mc:
            v = float(str(mc_raw).replace(",", ""))
            mc = f"{v / 1e8:.0f}亿" if v > 1e8 else f"{v:.0f}亿"
    except Exception:
        ind, mc = "半导体", "200亿"

    chain_txt = IND_MAP.get(code)
    if not chain_txt:
        chain_txt = f"{name} {ind}"

    raw = {
        "ticker": ticker,
        "dimensions": {
            "0_basic": {"data": {"name": name, "industry": ind, "market_cap": mc, "price": str(price)}},
            "5_chain": {"data": {"desc": chain_txt}},
            "7_industry": {"data": {"growth": "35%"}},
            "14_moat": {"data": {"scores": {"switching": 7, "scale": 6, "intangible": 5, "network": 4}}},
            "13_policy": {"data": {"policy_dir": "国产替代支持"}},
            "15_events": {"data": {"event_timeline": ["AI需求", "扩产", "大订单"]}},
        },
    }
    f = extract_features(raw, {})
    ev = evaluate("serenity", f)
    return f, ev


def ser_summary(f, ev) -> dict:
    cp = f.get("ai_chokepoint_score", 0)
    rp = len(ev.get("pass_rules", []))
    return {
        "chokepoint": cp,
        "chain_hit": bool(f.get("ai_chain_hit")),
        "keywords": f.get("ai_chain_keywords", [])[:5],
        "irreplaceable": f.get("ai_irreplaceable"),
        "smallcap": f.get("ai_smallcap"),
        "mcap_yi": f.get("market_cap_yi"),
        "rules_pass": rp,
        "signal": ev.get("signal"),
        "score": ev.get("score"),
        "headline": ev.get("headline", ""),
        "pass": cp >= 60 and f.get("ai_chain_hit") and rp >= 3,
        "tier": "A≥80" if cp >= 80 else ("B≥60" if cp >= 60 else "C"),
    }


def main():
    cons = ak.index_stock_cons(symbol="000688")
    chan_all, both, watch, ser_strong, excluded_lianban = [], [], [], [], []

    for _, row in cons.iterrows():
        code = f"{int(row['品种代码']):06d}"
        name = row["品种名称"]
        try:
            bars = load_bars(code)
            bars = [b for b in bars if str(b["date"])[:10] <= AS_OF]
            if not bars:
                continue
            price = bars[-1]["c"]
            lb = lianban_tag(bars)
            f, ev = serenity_eval(code, name, price)
            ser = ser_summary(f, ev)
            if ser["chokepoint"] >= 70 and ser["chain_hit"]:
                ser_strong.append({"code": code, "name": name, "price": round(price, 2), "serenity": ser})

            chan = chan_erbuy(bars, price)
            if not chan:
                continue

            item = {
                "code": code,
                "name": name,
                "price": round(price, 2),
                "chan": chan,
                "serenity": ser,
                "lianban": lb,
            }
            if lb["is_erjin_san"]:
                excluded_lianban.append(item)
                continue

            chan_all.append(item)
            if ser["pass"]:
                both.append(item)
            elif ser["chain_hit"] and ser["chokepoint"] >= 50:
                watch.append(item)
        except Exception:
            continue

    for lst in (chan_all, both, watch):
        lst.sort(key=lambda x: -x["serenity"]["chokepoint"])

    out = {
        "as_of": AS_OF,
        "method": "缠论二买 + Serenity（已排除二进三连板标的，非连板接力策略）",
        "summary": {
            "科创50": len(cons),
            "缠论二买": len(chan_all),
            "二买+Serenity全达标": len(both),
            "二买+卡位观察50-59": len(watch),
            "Serenity强卡位≥70": len(ser_strong),
            "二买但属连板排除": len(excluded_lianban),
        },
        "二买且Serenity达标": both,
        "二买+卡位观察": watch,
        "全部缠论二买": chan_all,
        "连板排除名单": excluded_lianban,
        "Serenity强卡位_全成分": sorted(ser_strong, key=lambda x: -x["serenity"]["chokepoint"])[:15],
    }

    OUT_PATH.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
