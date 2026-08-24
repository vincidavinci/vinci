(function () {
  "use strict";

  const STORAGE_KEY = "gold-gamma-dashboard-v4";
  let snapshot = null;
  let baseline = null;

  const $ = (id) => document.getElementById(id);

  function fmt(n, d, suffix) {
    if (n === null || n === undefined || n === "" || Number.isNaN(Number(n))) return "暂无可靠数据";
    const num = Number(n);
    const abs = Math.abs(num);
    const digits = d != null ? d : abs >= 100 ? 2 : abs >= 10 ? 2 : 2;
    const s = num.toLocaleString("en-US", { minimumFractionDigits: digits, maximumFractionDigits: digits });
    return suffix ? s + suffix : s;
  }

  function money(n) {
    if (n == null) return "暂无可靠数据";
    return "$" + Number(n).toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  }

  function signedPct(n, d) {
    if (n == null) return "—";
    const v = Number(n);
    const sign = v > 0 ? "+" : "";
    return sign + v.toFixed(d != null ? d : 2) + "%";
  }

  function signedBp(n) {
    if (n == null) return "—";
    const v = Number(n);
    const sign = v > 0 ? "+" : "";
    return sign + v.toFixed(1) + "bp";
  }

  function toneClass(n, invert) {
    if (n == null) return "";
    const v = invert ? -Number(n) : Number(n);
    if (v > 0.02) return "green";
    if (v < -0.02) return "red";
    return "yellow";
  }

  function vintagePill(field) {
    const v = (field && field.vintage) || "missing";
    const map = {
      live: "盘中",
      intraday: "盘中",
      official: "官方",
      prior_close: "上一日收盘",
      weekly: "最新周度",
      monthly: "月报",
      event: "事件",
      missing: "缺失",
    };
    return `<span class="pill ${v}">${map[v] || v}</span>`;
  }

  function field(stateKey) {
    return (snapshot.fields || {})[stateKey] || { value: null, vintage: "missing" };
  }

  function readForm() {
    const g = (id) => {
      const el = $(id);
      if (!el) return null;
      if (el.tagName === "SELECT") return el.value;
      if (el.type === "checkbox") return el.checked;
      return el.value === "" ? null : el.value;
    };
    return {
      gold: g("f-gold"),
      goldDayPct: g("f-goldDayPct"),
      gold5dPct: g("f-gold5dPct"),
      gold20dPct: g("f-gold20dPct"),
      netGexBn: g("f-netGexBn"),
      netGexPrevBn: g("f-netGexPrevBn"),
      zeroGamma: g("f-zeroGamma"),
      callWall: g("f-callWall"),
      iv1m: g("f-iv1m"),
      skew: g("f-skew"),
      move: g("f-move"),
      y30: g("f-y30"),
      y2: g("f-y2"),
      y30ChangeBp: g("f-y30ChangeBp"),
      y2ChangeBp: g("f-y2ChangeBp"),
      tips: g("f-tips"),
      tipsChangeBp: g("f-tipsChangeBp"),
      dxy: g("f-dxy"),
      dxyChangePct: g("f-dxyChangePct"),
      heatingOil: g("f-heatingOil"),
      wti: g("f-wti"),
      silver: g("f-silver"),
      copper: g("f-copper"),
      fomcHoldPct: g("f-fomcHoldPct"),
      fomcHikePct: g("f-fomcHikePct"),
      buybackActive: $("f-buyback") ? $("f-buyback").checked : true,
    };
  }

  function fillForm(state) {
    const set = (id, v) => {
      const el = $(id);
      if (!el) return;
      if (el.type === "checkbox") el.checked = !!v;
      else el.value = v == null || v === "" ? "" : v;
    };
    set("f-gold", state.gold);
    set("f-goldDayPct", state.goldDayPct);
    set("f-gold5dPct", state.gold5dPct);
    set("f-gold20dPct", state.gold20dPct);
    set("f-netGexBn", state.netGexBn);
    set("f-netGexPrevBn", state.netGexPrevBn);
    set("f-zeroGamma", state.zeroGamma);
    set("f-callWall", state.callWall);
    set("f-iv1m", state.iv1m);
    set("f-skew", state.skew || "");
    set("f-move", state.move);
    set("f-y30", state.y30);
    set("f-y2", state.y2);
    set("f-y30ChangeBp", state.y30ChangeBp);
    set("f-y2ChangeBp", state.y2ChangeBp);
    set("f-tips", state.tips);
    set("f-tipsChangeBp", state.tipsChangeBp);
    set("f-dxy", state.dxy);
    set("f-dxyChangePct", state.dxyChangePct);
    set("f-heatingOil", state.heatingOil);
    set("f-wti", state.wti);
    set("f-silver", state.silver);
    set("f-copper", state.copper);
    set("f-fomcHoldPct", state.fomcHoldPct);
    set("f-fomcHikePct", state.fomcHikePct);
    set("f-buyback", state.buybackActive);
  }

  function sparkline(points) {
    const vals = (points || []).map((p) => p.close).filter((v) => v != null);
    if (vals.length < 2) return "";
    const w = 220, h = 36, pad = 2;
    const min = Math.min.apply(null, vals);
    const max = Math.max.apply(null, vals);
    const span = max - min || 1;
    const d = vals
      .map((v, i) => {
        const x = pad + (i / (vals.length - 1)) * (w - pad * 2);
        const y = h - pad - ((v - min) / span) * (h - pad * 2);
        return (i ? "L" : "M") + x.toFixed(1) + " " + y.toFixed(1);
      })
      .join(" ");
    return `<svg class="spark" viewBox="0 0 ${w} ${h}" aria-hidden="true"><path d="${d}" fill="none" stroke="#d8b45a" stroke-width="2"/></svg>`;
  }

  function coverage(state) {
    const keys = [
      "gold", "goldDayPct", "netGexBn", "zeroGamma", "callWall", "iv1m",
      "move", "y30", "y2", "tips", "dxy", "wti", "silver", "copper", "heatingOil",
    ];
    const filled = keys.filter((k) => GoldEngine.num(state[k]) != null).length;
    return { filled, total: keys.length };
  }

  function riskCell(text, cls) {
    return `<td class="${cls || ""}">${text}</td>`;
  }

  function render(state) {
    const ev = GoldEngine.evaluate(state);
    const r = ev.ratios;
    const f = snapshot.fields;

    $("asOfLabel").textContent = snapshot.asOfLabel;
    $("kpi-gold-value").textContent = money(state.gold);
    $("kpi-gold-sub").innerHTML =
      `<span class="${toneClass(state.goldDayPct)}">${signedPct(state.goldDayPct)} 合约日</span>` +
      ` · 5日 ${signedPct(state.gold5dPct)} · 20日 ${signedPct(state.gold20dPct)}`;
    $("kpi-gold-spark").innerHTML = sparkline(snapshot.goldCloses);

    const gexMissing = GoldEngine.num(state.netGexBn) == null;
    $("kpi-gex-value").innerHTML = gexMissing ? '<span class="missing-val">暂无可靠数据</span>' : fmt(state.netGexBn, 2) + " bn";
    $("kpi-gex-sub").textContent = (f.netGexBn && f.netGexBn.note) || "公开源无法可靠复核 Dealer GEX";
    $("kpi-flip-value").innerHTML = GoldEngine.num(state.zeroGamma) == null ? '<span class="missing-val">暂无可靠数据</span>' : money(state.zeroGamma);
    $("kpi-flip-sub").textContent = (f.zeroGamma && f.zeroGamma.note) || "Zero Gamma / Flip 未可靠更新";
    $("kpi-wall-value").innerHTML = GoldEngine.num(state.callWall) == null ? '<span class="missing-val">暂无可靠数据</span>' : money(state.callWall);
    $("kpi-wall-sub").textContent = (f.callWall && f.callWall.note) || "Call Wall 未可靠更新";

    $("kpi-gamma-value").textContent = ev.gammaLabel;
    $("kpi-gamma-sub").textContent = ev.scores.gamma == null
      ? "缺少 GEX / Flip / Call Wall 核心输入"
      : "0–100 模型分 " + ev.scores.gamma;
    $("kpi-light-value").textContent = ev.light.emoji + " " + ev.light.title;
    $("kpi-light-sub").textContent = ev.light.note;

    const gammaPct = ev.scores.gamma == null ? 0 : ev.scores.gamma;
    $("gamma-meter").classList.toggle("null", ev.scores.gamma == null);
    $("gamma-meter-bar").style.width = gammaPct + "%";
    $("gamma-meter-label").textContent = ev.scores.gamma == null ? "暂不评分（核心输入缺失）" : ev.scores.gamma + " · " + ev.gammaLabel;

    const setLayer = (id, score, suffix) => {
      $(id + "-val").textContent = score == null ? "—" : score;
      $(id + "-bar").style.width = (score || 0) + "%";
      $(id + "-note").textContent = suffix;
    };
    setLayer("macro", ev.scores.macro, "DXY、收益率、MOVE、Crack、FOMC 的可计算层");
    setLayer("fiscal", ev.scores.fiscal, "Dalio 财政共振：30Y↑ + DXY↓ + Gold↑ 今日未齐");
    setLayer("value", ev.scores.valuation, "Gold/Silver、Gold/WTI、Gold/Copper");

    const cov = coverage(state);
    $("coverage").textContent = `可核实输入 ${cov.filled}/${cov.total}`;

    const gexTxt = gexMissing ? "暂无可靠数据" : fmt(state.netGexBn, 2);
    const vsZero = GoldEngine.num(state.gold) != null && GoldEngine.num(state.zeroGamma) != null
      ? (state.gold >= state.zeroGamma ? "上方" : "下方")
      : "暂无可靠数据";
    const vsWall = GoldEngine.num(state.gold) != null && GoldEngine.num(state.callWall) != null
      ? (state.gold >= state.callWall ? "触及/上方" : "下方")
      : "暂无可靠数据";
    const skewLabel = { call_rich: "Call 偏贵", put_rich: "Put 偏贵", neutral: "中性", "": "暂无可靠数据" }[state.skew || ""];

    $("opt-body").innerHTML = `
      <tr><td>Dealer GEX</td><td>${gexTxt}</td>${riskCell(gexMissing ? "—" : (Number(state.netGexBn) < 0 ? "放大" : "刹车"), gexMissing ? "" : (Number(state.netGexBn) < 0 ? "red" : "green"))}</tr>
      <tr><td>Gold vs Zero Gamma</td><td>${vsZero}</td>${riskCell(gexMissing ? "—" : "观察", "yellow")}</tr>
      <tr><td>Gold vs Call Wall</td><td>${vsWall}</td>${riskCell(GoldEngine.num(state.callWall) == null ? "—" : "观察")}</tr>
      <tr><td>Call/Put Skew</td><td>${skewLabel}</td><td>—</td></tr>
      <tr><td>1M IV</td><td>${GoldEngine.num(state.iv1m) == null ? "暂无可靠数据" : fmt(state.iv1m, 1, "%")}</td><td>—</td></tr>
      <tr><td>Vanna / Charm</td><td>暂无可靠数据</td><td>—</td></tr>
      <tr><td>Dealer 对冲压力</td><td>方向敏感</td>${riskCell("观察", "yellow")}</tr>
    `;

    const sigMap = [
      ["A", "GEX Flip", "Net GEX 正→负；随后跟踪 1D / 3D / 5D / 10D / 20D 收益。", ev.signals.a],
      ["B", "负 Gamma + 下跌", "GEX&lt;0 且 Gold 当日跌幅&gt;1%：检测机械卖盘放大。", ev.signals.b],
      ["C", "关键位失守", "GEX&lt;0 + Gold 跌破 Zero Gamma / 关键 Call Wall：Reverse Gamma 核心触发器。", ev.signals.c],
      ["D", "宏观共振", "GEX&lt;0 + Gold↓ + DXY↑ + 10Y TIPS↑：最高优先级风险组合。", ev.signals.d],
    ];
    $("signals").innerHTML = sigMap.map(([k, title, body, st]) => {
      const cls = st.status === "triggered" ? "red" : st.status === "idle" ? "green" : "yellow";
      return `<div class="signal"><b>Signal ${k} · ${title} <span class="pill ${st.status === "unknown" ? "missing" : st.status === "triggered" ? "missing" : "live"}">${st.label}</span></b>${body}<div class="why ${cls}">当前：${st.label}${st.status === "unknown" ? "（缺 GEX/关键位或宏观官方腿）" : ""}</div></div>`;
    }).join("");

    const y30cls = Number(state.y30ChangeBp) < 0 ? "green" : Number(state.y30ChangeBp) > 0 ? "red" : "yellow";
    const y2cls = Number(state.y2ChangeBp) < 0 ? "green" : Number(state.y2ChangeBp) > 0 ? "red" : "yellow";
    const dxyCls = Number(state.dxyChangePct) > 0 ? "yellow" : "green";
    $("macro-body").innerHTML = `
      <tr><td>MOVE</td><td>${GoldEngine.num(state.move) == null ? "暂无可靠8/24值" : fmt(state.move, 1)} · ${field("move").asOf || ""}</td><td>${GoldEngine.num(state.move) != null && state.move < 90 ? "低于90" : "重点看90"}</td></tr>
      <tr><td>30Y Treasury</td><td>${fmt(state.y30, 3)}% · 8/24盘中</td>${riskCell(signedBp(state.y30ChangeBp), y30cls)}</tr>
      <tr><td>2Y Treasury</td><td>${fmt(state.y2, 3)}% · 8/24市场</td>${riskCell(signedBp(state.y2ChangeBp), y2cls)}</tr>
      <tr><td>30Y−2Y</td><td>${r.curve30_2Bp == null ? "—" : signedBp(r.curve30_2Bp).replace("bp", "") + "bp"}</td>${riskCell(r.curve30_2Bp != null && r.curve30_2Bp > 80 ? "曲线很陡" : "观察", "yellow")}</tr>
      <tr><td>10Y TIPS</td><td>${fmt(state.tips, 2)}% · ${field("tips").asOf || ""}</td><td>${field("tips").note || ""}</td></tr>
      <tr><td>DXY</td><td>${fmt(state.dxy, 3)} · 8/24盘中</td>${riskCell(signedPct(state.dxyChangePct), dxyCls)}</tr>
      <tr><td>Diesel Crack</td><td>${r.dieselCrack == null ? "暂无可靠值" : "$" + fmt(r.dieselCrack, 2) + " /bbl"}</td>${riskCell(r.dieselCrack != null && r.dieselCrack >= 70 ? "仍极高" : "—", r.dieselCrack != null && r.dieselCrack >= 70 ? "red" : "")}</tr>
      <tr><td>9月FOMC</td><td>Hold ${fmt(state.fomcHoldPct, 1)}%</td>${riskCell("Hike " + fmt(state.fomcHikePct, 1) + "%", "yellow")}</tr>
    `;

    const triadGold = GoldEngine.num(state.goldDayPct) > 0;
    const triadDxy = GoldEngine.num(state.dxyChangePct) < 0;
    const triadY = GoldEngine.num(state.y30ChangeBp) > 0;
    $("triad").innerHTML = `
      <div>Gold ${triadGold ? "↑" : "↓/平"}<div class="small">${triadGold ? "符合" : "未贡献"}</div></div>
      <div>DXY ${triadDxy ? "↓" : "↑/平"}<div class="small">${triadDxy ? "符合" : "未贡献"}</div></div>
      <div>30Y ${triadY ? "↑" : "↓/平"}<div class="small">${triadY ? "符合" : "未贡献"}</div></div>
    `;
    $("fiscal-body").innerHTML = `
      <tr><td>30Y冲高 + DXY弱 + Gold涨</td><td>8/24未形成：30Y ${signedBp(state.y30ChangeBp)} / DXY ${signedPct(state.dxyChangePct)} / Gold ${signedPct(state.goldDayPct)}</td></tr>
      <tr><td>MOVE &gt; 90</td><td>${GoldEngine.num(state.move) == null ? "8/24暂无可靠实时值" : (state.move > 90 ? "触发" : "未触发（上一日收盘 " + fmt(state.move, 1) + "）")}</td></tr>
      <tr><td>债市状态</td>${riskCell(Number(state.y30ChangeBp) < 0 ? "有序降温：30Y当日回落" : "长端仍紧", Number(state.y30ChangeBp) < 0 ? "green" : "yellow")}</tr>
      <tr><td>黄金主叙事</td>${riskCell("财政/信用余温 + 技术动量", "yellow")}</tr>
      <tr><td>Treasury Buyback</td><td>${state.buybackActive ? "扩容窗口跟踪中（9/9–11/4）" : "未标记"}</td></tr>
      <tr><td>Dalio Fiscal Score</td><td>${ev.scores.fiscal == null ? "—" : ev.scores.fiscal + " / 100"}</td></tr>
    `;

    const gsCls = r.goldSilver != null && r.goldSilver >= 65 ? "yellow" : "";
    const gwCls = r.goldWti != null && r.goldWti >= 40 ? "red" : "";
    const cpiGold = GoldEngine.num(state.gold) != null && f.cpi && f.cpi.value
      ? GoldEngine.round(Number(state.gold) / (f.cpi.value / 100), 1)
      : null;
    const ppiGold = GoldEngine.num(state.gold) != null && f.ppi && f.ppi.value
      ? GoldEngine.round(Number(state.gold) / (f.ppi.value / 100), 1)
      : null;
    $("val-body").innerHTML = `
      <tr><td>Gold / Silver</td><td>${r.goldSilver == null ? "—" : r.goldSilver.toFixed(2) + "x"} · 8/24同刻</td>${riskCell("黄金显著强于白银", gsCls)}</tr>
      <tr><td>Gold / WTI</td><td>${r.goldWti == null ? "—" : r.goldWti.toFixed(2) + "x"} · 8/24同刻</td>${riskCell("极高", gwCls)}</tr>
      <tr><td>Gold / Copper</td><td>${r.goldCopper == null ? "—" : r.goldCopper.toFixed(1) + "x"} · $/oz ÷ $/lb</td>${riskCell(r.goldCopper != null && r.goldCopper >= 700 ? "偏高（已标口径）" : "已标口径", r.goldCopper != null && r.goldCopper >= 700 ? "yellow" : "")}</tr>
      <tr><td>CPI-adjusted Gold</td><td>${cpiGold == null ? "—" : "$" + cpiGold + "（1982-84美元）"}</td><td>CPI ${f.cpi && f.cpi.asOf ? f.cpi.asOf.slice(0, 7) : ""} · 不编造百分位</td></tr>
      <tr><td>PPI-adjusted Gold</td><td>${ppiGold == null ? "—" : "$" + ppiGold + "（1982=100折算）"}</td><td>PPI ${f.ppi && f.ppi.asOf ? f.ppi.asOf.slice(0, 7) : ""} · 不编造百分位</td></tr>
      <tr><td>Relative Valuation Risk</td><td>${ev.scores.valuation >= 70 ? "高" : ev.scores.valuation >= 45 ? "中高" : "中"}</td>${riskCell("Gold/WTI 与名义金价均偏贵", "red")}</tr>
    `;

    $("etf-body").innerHTML = `
      <tr><td>全球黄金ETF净流入/流出</td><td>+${f.etfTonnes.value}吨 / +$${f.etfUsdBn.value}bn</td><td>最新周度 · 截至8/21当周</td></tr>
      <tr><td>总持仓</td><td>${f.etfHoldingsT.value.toLocaleString()}吨（7月末）</td><td>WGC 月报，非本周</td></tr>
      <tr><td>北美</td><td>+$${f.etfNaBn.value}bn</td><td>最新周度</td></tr>
      <tr><td>欧洲</td><td>+$${f.etfEuBn.value}bn</td><td>最新周度</td></tr>
      <tr><td>亚洲</td><td>+$${f.etfAsBn.value}bn</td><td>最新周度</td></tr>
    `;

    const m = ev.machine;
    $("machine-healthy").className = "note" + (m === "healthy" ? "" : " muted");
    $("machine-fragile").className = "note" + (m === "fragile" ? "" : " muted");
    $("machine-reverse").className = "note" + (m === "reverse" ? "" : " muted");
    $("machine-now").textContent = "当前机器状态：" + (m === "healthy" ? "🟢 相对健康" : m === "reverse" ? "🔴 Reverse Gamma 警报" : "🟡 容易剧烈波动 / 观察");
  }

  function persist(state) {
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(state)); } catch (e) { /* ignore */ }
  }

  function bind() {
    $("data-form").addEventListener("input", function () {
      const state = readForm();
      persist(state);
      render(state);
    });
    $("btn-reset").addEventListener("click", function () {
      try { localStorage.removeItem(STORAGE_KEY); } catch (e) { /* ignore */ }
      fillForm(baseline);
      render(baseline);
    });
  }

  function boot(data) {
    snapshot = data;
    baseline = GoldEngine.stateFromSnapshot(data);
    let state = baseline;
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) state = Object.assign({}, baseline, JSON.parse(saved));
    } catch (e) { /* ignore */ }
    fillForm(state);
    bind();
    render(state);
  }

  fetch("data/snapshot.json", { cache: "no-store" })
    .then(function (res) {
      if (!res.ok) throw new Error("snapshot " + res.status);
      return res.json();
    })
    .then(boot)
    .catch(function (err) {
      document.body.insertAdjacentHTML("afterbegin", '<p class="wrap red">无法加载 data/snapshot.json：' + err.message + "</p>");
    });
})();
