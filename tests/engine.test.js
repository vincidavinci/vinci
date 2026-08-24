const assert = require("assert");
const Engine = require("../assets/engine.js");

function nearly(a, b, eps) {
  assert.ok(Math.abs(a - b) <= (eps || 1e-9), `${a} !~= ${b}`);
}

const snapshot = require("../data/snapshot.json");
const live = Engine.stateFromSnapshot(snapshot);
const ev = Engine.evaluate(live);

assert.strictEqual(ev.scores.gamma, null, "gamma must not score without GEX/flip/wall");
assert.ok(ev.scores.macro != null && ev.scores.macro < 55, "macro should be moderate");
assert.ok(ev.scores.fiscal != null && ev.scores.fiscal < 60, "fiscal triad not complete");
assert.ok(ev.scores.valuation >= 70, "valuation should be high given Gold/WTI");
assert.strictEqual(ev.signals.a.status, "unknown");
assert.strictEqual(ev.signals.b.status, "unknown");
assert.strictEqual(ev.signals.c.status, "unknown");
assert.strictEqual(ev.signals.d.status, "unknown");
assert.strictEqual(ev.light.level, "yellow");
assert.strictEqual(ev.machine, "fragile");
nearly(ev.ratios.goldSilver, 4693.6 / 68.55, 0.02);
nearly(ev.ratios.goldWti, 4693.6 / 85.25, 0.02);
nearly(ev.ratios.dieselCrack, 4.1838 * 42 - 85.25, 0.05);
nearly(ev.ratios.curve30_2Bp, (5.231 - 4.24) * 100, 0.05);
assert.ok(ev.ratios.goldCopper > 700);

const reverse = Engine.evaluate({
  gold: 4500,
  goldDayPct: -1.4,
  netGexBn: -1.2,
  netGexPrevBn: 0.8,
  zeroGamma: 4580,
  callWall: 4620,
  dxyChangePct: 0.4,
  tipsChangeBp: 6,
  y30: 5.4,
  y30ChangeBp: 8,
  y2: 4.2,
  move: 96,
  wti: 85,
  silver: 68,
  copper: 6.6,
  heatingOil: 4.2,
  fomcHikePct: 55,
  buybackActive: true,
  skew: "put_rich",
  iv1m: 28,
});
assert.ok(reverse.scores.gamma >= 80, "reverse gamma should be extreme");
assert.strictEqual(reverse.signals.a.status, "triggered");
assert.strictEqual(reverse.signals.b.status, "triggered");
assert.strictEqual(reverse.signals.c.status, "triggered");
assert.strictEqual(reverse.signals.d.status, "triggered");
assert.strictEqual(reverse.light.level, "red");

const healthy = Engine.evaluate({
  gold: 4200,
  goldDayPct: 0.6,
  netGexBn: 1.8,
  netGexPrevBn: 1.5,
  zeroGamma: 4000,
  callWall: 4300,
  dxyChangePct: -0.3,
  tipsChangeBp: -3,
  y30: 4.8,
  y30ChangeBp: -5,
  y2: 4.2,
  move: 62,
  wti: 90,
  silver: 80,
  copper: 8,
  heatingOil: 2.4,
  fomcHikePct: 10,
  buybackActive: false,
  skew: "neutral",
  iv1m: 12,
});
assert.ok(healthy.scores.gamma < 30);
assert.strictEqual(healthy.signals.b.status, "idle");
assert.strictEqual(healthy.signals.d.status, "idle");
assert.strictEqual(healthy.light.level, "green");

assert.strictEqual(Engine.num(""), null);
assert.strictEqual(Engine.num("1,234.5"), 1234.5);

console.log("engine tests passed");
console.log(JSON.stringify({
  liveGamma: ev.scores.gamma,
  liveMacro: ev.scores.macro,
  liveFiscal: ev.scores.fiscal,
  liveVal: ev.scores.valuation,
  liveLight: ev.light.level,
  reverseGamma: reverse.scores.gamma,
}, null, 2));
