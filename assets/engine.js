/**
 * Gold Gamma Stress scoring engine.
 * Browser + Node. Does not invent missing GEX/IV/skew inputs.
 */
(function (root, factory) {
  if (typeof module === "object" && module.exports) {
    module.exports = factory();
  } else {
    root.GoldEngine = factory();
  }
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";

  function num(value) {
    if (value === null || value === undefined || value === "") return null;
    if (typeof value === "number") return Number.isFinite(value) ? value : null;
    const n = Number(String(value).replace(/,/g, "").trim());
    return Number.isFinite(n) ? n : null;
  }

  function clamp(n, lo, hi) {
    return Math.min(hi, Math.max(lo, n));
  }

  function round(n, d) {
    if (n === null || n === undefined || !Number.isFinite(n)) return null;
    const p = 10 ** d;
    return Math.round(n * p) / p;
  }

  function computeRatios(state) {
    const gold = num(state.gold);
    const silver = num(state.silver);
    const wti = num(state.wti);
    const copper = num(state.copper);
    const heatingOil = num(state.heatingOil);
    const y30 = num(state.y30);
    const y2 = num(state.y2);
    return {
      goldSilver: gold != null && silver ? round(gold / silver, 2) : null,
      goldWti: gold != null && wti ? round(gold / wti, 2) : null,
      goldCopper: gold != null && copper ? round(gold / copper, 1) : null,
      dieselCrack: heatingOil != null && wti != null ? round(heatingOil * 42 - wti, 2) : null,
      curve30_2Bp: y30 != null && y2 != null ? round((y30 - y2) * 100, 2) : null,
      y30ChangeBp: num(state.y30ChangeBp),
      y2ChangeBp: num(state.y2ChangeBp),
    };
  }

  function gammaStress(state) {
    const gex = num(state.netGexBn);
    const zero = num(state.zeroGamma);
    const wall = num(state.callWall);
    if (gex == null || zero == null || wall == null) return null;

    const gold = num(state.gold);
    const dayPct = num(state.goldDayPct);
    const iv = num(state.iv1m);
    const skew = state.skew || "";
    let score = 0;

    if (gex < 0) score += 34;
    else if (gex < 0.5) score += 18;
    else score += 6;

    if (gold != null) {
      if (gold < zero) score += 26;
      else if (gold < zero * 1.008) score += 12;
      if (gold < wall && gex < 0) score += 18;
      else if (Math.abs(gold - wall) / wall < 0.004) score += 8;
    }

    if (dayPct != null && gex < 0 && dayPct <= -1) score += 12;
    if (iv != null) {
      if (iv >= 25) score += 8;
      else if (iv >= 18) score += 4;
    }
    if (skew === "put_rich") score += 6;
    else if (skew === "call_rich") score += 2;

    return clamp(Math.round(score), 0, 100);
  }

  function macroStress(state, ratios) {
    const parts = [];
    const dxyChg = num(state.dxyChangePct);
    const y30Chg = num(state.y30ChangeBp);
    const tipsChg = num(state.tipsChangeBp);
    const move = num(state.move);
    const hike = num(state.fomcHikePct);
    const crack = ratios.dieselCrack;
    const goldDay = num(state.goldDayPct);

    if (dxyChg != null) {
      if (dxyChg >= 0.4) parts.push(22);
      else if (dxyChg >= 0.1) parts.push(10);
      else if (dxyChg <= -0.2) parts.push(0);
      else parts.push(4);
    }
    if (y30Chg != null) {
      if (y30Chg >= 8) parts.push(20);
      else if (y30Chg >= 3) parts.push(10);
      else if (y30Chg <= -3) parts.push(0);
      else parts.push(5);
    }
    if (tipsChg != null) {
      if (tipsChg >= 5) parts.push(22);
      else if (tipsChg >= 2) parts.push(12);
      else if (tipsChg <= -2) parts.push(0);
      else parts.push(6);
    }
    if (move != null) {
      if (move >= 90) parts.push(24);
      else if (move >= 80) parts.push(14);
      else if (move >= 70) parts.push(6);
      else parts.push(2);
    }
    if (hike != null) {
      if (hike >= 50) parts.push(16);
      else if (hike >= 35) parts.push(10);
      else parts.push(3);
    }
    if (crack != null) {
      if (crack >= 100) parts.push(12);
      else if (crack >= 70) parts.push(8);
      else parts.push(2);
    }
    if (goldDay != null && goldDay < 0) parts.push(8);
    else if (goldDay != null) parts.push(0);

    if (!parts.length) return null;
    const avg = parts.reduce((a, b) => a + b, 0) / parts.length;
    return clamp(Math.round(avg * (100 / 24)), 0, 100);
  }

  function fiscalScore(state, ratios) {
    const goldDay = num(state.goldDayPct);
    const dxyChg = num(state.dxyChangePct);
    const y30Chg = num(state.y30ChangeBp);
    const y30 = num(state.y30);
    const move = num(state.move);
    const buyback = !!state.buybackActive;
    let score = 0;

    const goldUp = goldDay != null && goldDay > 0;
    const dxyDown = dxyChg != null && dxyChg < 0;
    const y30Up = y30Chg != null && y30Chg > 0;
    if (goldUp && dxyDown && y30Up) score += 44;
    else {
      if (goldUp) score += 12;
      if (dxyDown) score += 12;
      if (y30Up) score += 16;
    }
    if (move != null) {
      if (move >= 90) score += 18;
      else if (move >= 80) score += 8;
    }
    if (y30 != null) {
      if (y30 >= 5.3) score += 12;
      else if (y30 >= 5.0) score += 7;
    }
    if (buyback) score += 10;
    if (ratios.curve30_2Bp != null && ratios.curve30_2Bp >= 80) score += 6;
    return clamp(score, 0, 100);
  }

  function valuationScore(state, ratios) {
    let score = 0;
    const gs = ratios.goldSilver;
    const gw = ratios.goldWti;
    const gc = ratios.goldCopper;
    if (gs != null) {
      if (gs >= 80) score += 28;
      else if (gs >= 70) score += 20;
      else if (gs >= 60) score += 12;
      else score += 4;
    }
    if (gw != null) {
      if (gw >= 50) score += 40;
      else if (gw >= 40) score += 28;
      else if (gw >= 30) score += 16;
      else score += 6;
    }
    if (gc != null) {
      if (gc >= 700) score += 18;
      else if (gc >= 600) score += 10;
      else score += 4;
    }
    if (!gs && !gw && !gc) return null;
    return clamp(score, 0, 100);
  }

  function signalStatus(ok, missing) {
    if (missing) return { status: "unknown", label: "数据不足" };
    return ok
      ? { status: "triggered", label: "触发" }
      : { status: "idle", label: "未触发" };
  }

  function signals(state, ratios) {
    const gex = num(state.netGexBn);
    const gexPrev = num(state.netGexPrevBn);
    const gold = num(state.gold);
    const dayPct = num(state.goldDayPct);
    const zero = num(state.zeroGamma);
    const wall = num(state.callWall);
    const dxyChg = num(state.dxyChangePct);
    const tipsChg = num(state.tipsChangeBp);

    const a = signalStatus(
      gexPrev != null && gex != null && gexPrev > 0 && gex < 0,
      gex == null || gexPrev == null
    );
    const b = signalStatus(
      gex != null && gex < 0 && dayPct != null && dayPct <= -1,
      gex == null || dayPct == null
    );
    const brokeLevel =
      gold != null &&
      ((zero != null && gold < zero) || (wall != null && gold < wall));
    const c = signalStatus(
      gex != null && gex < 0 && brokeLevel,
      gex == null || gold == null || (zero == null && wall == null)
    );
    const d = signalStatus(
      gex != null &&
        gex < 0 &&
        dayPct != null &&
        dayPct < 0 &&
        dxyChg != null &&
        dxyChg > 0 &&
        tipsChg != null &&
        tipsChg > 0,
      gex == null || dayPct == null || dxyChg == null || tipsChg == null
    );

    return { a, b, c, d, ratios };
  }

  function overallLight(state, scores) {
    const goldDay = num(state.goldDayPct) || 0;
    const dxyChg = num(state.dxyChangePct) || 0;
    const tipsChg = num(state.tipsChangeBp) || 0;
    const move = num(state.move);
    const gamma = scores.gamma;
    const val = scores.valuation || 0;
    const macro = scores.macro || 0;

    if (gamma != null && gamma >= 80 && goldDay < 0) {
      return {
        level: "red",
        emoji: "🔴",
        title: "Reverse Gamma 警报",
        note: "负Gamma且金价下跌，机械对冲可能放大回撤。",
      };
    }
    if (gamma != null && gamma >= 60 && goldDay < 0 && (dxyChg > 0 || tipsChg > 0)) {
      return {
        level: "red",
        emoji: "🔴",
        title: "负Gamma + 宏观补刀",
        note: "期权结构脆弱，同时出现美元或实际利率走强。",
      };
    }
    if (gamma != null && gamma < 30 && goldDay >= 0 && dxyChg < 0.15 && tipsChg <= 0 && val < 55) {
      return {
        level: "green",
        emoji: "🟢",
        title: "相对健康",
        note: "正Gamma或稳定，金价向上，宏观未形成利空共振。",
      };
    }

    const reasons = [];
    if (gamma == null) reasons.push("Gamma核心数据缺失");
    if (goldDay > 0) reasons.push("趋势仍强");
    if (val >= 55) reasons.push("相对估值偏贵");
    if (macro >= 45) reasons.push("宏观压力上升");
    else if (dxyChg > 0 && goldDay > 0) reasons.push("金价与美元同日走强，需观察分化");
    if (move != null && move < 80) reasons.push("债市波动尚未失控");

    return {
      level: "yellow",
      emoji: "🟡",
      title: "容易剧烈波动 / 观察",
      note: reasons.join("；") + "。",
    };
  }

  function machineState(state, scores) {
    const light = overallLight(state, scores);
    if (light.level === "red") return "reverse";
    if (light.level === "green") return "healthy";
    return "fragile";
  }

  function evaluate(state) {
    const ratios = computeRatios(state);
    const gamma = gammaStress(state);
    const macro = macroStress(state, ratios);
    const fiscal = fiscalScore(state, ratios);
    const valuation = valuationScore(state, ratios);
    const scores = { gamma, macro, fiscal, valuation };
    const sig = signals(state, ratios);
    const light = overallLight(state, scores);
    return {
      ratios,
      scores,
      signals: sig,
      light,
      machine: machineState(state, scores),
      gammaLabel:
        gamma == null
          ? "暂不评分"
          : gamma >= 80
            ? "Reverse Squeeze 高风险"
            : gamma >= 60
              ? "Negative Gamma"
              : gamma >= 30
                ? "Gamma 脆弱"
                : "正 Gamma",
    };
  }

  function stateFromSnapshot(snapshot) {
    const f = snapshot.fields || {};
    const pick = (key) => (f[key] && f[key].value !== undefined ? f[key].value : null);
    return {
      gold: pick("gold"),
      goldDayPct: pick("goldDayPct"),
      gold5dPct: pick("gold5dPct"),
      gold20dPct: pick("gold20dPct"),
      netGexBn: pick("netGexBn"),
      netGexPrevBn: pick("netGexPrevBn"),
      zeroGamma: pick("zeroGamma"),
      callWall: pick("callWall"),
      iv1m: pick("iv1m"),
      skew: pick("skew") || "",
      move: pick("move"),
      y30: pick("y30"),
      y2: pick("y2"),
      y30ChangeBp: pick("y30ChangeBp"),
      y2ChangeBp: pick("y2ChangeBp"),
      tips: pick("tips"),
      tipsChangeBp: pick("tipsChangeBp"),
      dxy: pick("dxy"),
      dxyChangePct: pick("dxyChangePct"),
      heatingOil: pick("heatingOil"),
      wti: pick("wti"),
      silver: pick("silver"),
      copper: pick("copper"),
      fomcHoldPct: pick("fomcHoldPct"),
      fomcHikePct: pick("fomcHikePct"),
      buybackActive: !!(f.buyback && f.buyback.value),
    };
  }

  return {
    num,
    round,
    computeRatios,
    gammaStress,
    evaluate,
    stateFromSnapshot,
  };
});
