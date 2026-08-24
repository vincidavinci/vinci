# Vinci · Gold Gamma Stress Dashboard

Interactive monitor for gold direction, dealer gamma (when verifiable), macro confirmation, fiscal/Dalio resonance, relative valuation, and gold ETF flows.

Open `index.html` via a local static server:

```bash
python3 -m http.server 8080
```

Then visit `http://localhost:8080`.

## Rules

- Do not invent Dealer GEX, Zero Gamma, Call Wall, skew, 1M IV, Vanna, or Charm.
- Label each field as intraday, official close, weekly, monthly, or missing.
- Gamma Stress Index scores only when GEX, Zero Gamma, and Call Wall are all present.
- Macro / Fiscal / Valuation layers score from available inputs only.

## Snapshot

Latest verified snapshot: `data/snapshot.json` (2026-08-24).

```bash
node tests/engine.test.js
```
