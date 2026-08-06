/* CFA Level I practice bank — educational use. Not affiliated with CFA Institute. */
window.CFA_QUESTIONS = [
  {
    id: "eth-01",
    topic: "Ethics",
    level: "I",
    difficulty: "medium",
    stem: "According to the CFA Institute Code of Ethics, members and candidates must:",
    choices: [
      "Place their own interests above client interests when conflicts cannot be avoided.",
      "Act with integrity, competence, diligence, and respect, and in an ethical manner.",
      "Guarantee investment performance if they disclose all material risks.",
      "Follow local law only when it is stricter than the Code and Standards."
    ],
    answer: 1,
    explanation: "The Code requires acting with integrity, competence, diligence, respect, and in an ethical manner with the public, clients, prospects, employers, employees, colleagues, and other market participants. Client interests come first; performance guarantees are not permitted."
  },
  {
    id: "eth-02",
    topic: "Ethics",
    level: "I",
    difficulty: "medium",
    stem: "A candidate learns of a material nonpublic acquisition before it is announced. The most appropriate action is to:",
    choices: [
      "Trade for personal accounts only after telling close family members.",
      "Recommend the stock to clients with a disclaimer that information may be incomplete.",
      "Not trade or cause others to trade until the information is public.",
      "Trade only in related industry ETFs to avoid trading the issuer directly."
    ],
    answer: 2,
    explanation: "Standard II(A) Material Nonpublic Information prohibits acting or causing others to act on material nonpublic information. Waiting until the information is public (and, where relevant, absorbed by the market) is required."
  },
  {
    id: "eth-03",
    topic: "Ethics",
    level: "I",
    difficulty: "hard",
    stem: "Under Standard III(B) Fair Dealing, which practice is most consistent with the Standard?",
    choices: [
      "Disseminating a change in recommendation to large accounts first, then smaller accounts.",
      "Giving all clients an opportunity to act on changes in recommendations in a fair manner.",
      "Allowing portfolio managers to trade ahead of client orders in the same security.",
      "Restricting new IPO allocations exclusively to the firm’s largest fee-paying clients."
    ],
    answer: 1,
    explanation: "Fair Dealing requires fair and objective treatment. Changes in recommendations and investment actions should be disseminated so that all clients have a fair opportunity to act. Preferential treatment that disadvantages other clients violates the Standard."
  },
  {
    id: "eth-04",
    topic: "Ethics",
    level: "I",
    difficulty: "medium",
    stem: "Gifts from a broker that could reasonably be expected to compromise independence should be:",
    choices: [
      "Accepted if valued under USD 100 and not disclosed.",
      "Accepted only if used for entertainment of the broker’s clients.",
      "Refused or disclosed and managed under the firm’s policies so independence is preserved.",
      "Accepted freely because soft-dollar arrangements always cover gifts."
    ],
    answer: 2,
    explanation: "Standard I(B) Independence and Objectivity requires members to use reasonable care and judgment to maintain independence. Gifts that could compromise objectivity should be refused or handled under clear policies with disclosure as appropriate."
  },
  {
    id: "qua-01",
    topic: "Quantitative Methods",
    level: "I",
    difficulty: "easy",
    stem: "An investment grows from 100 to 121 over two years. The annual compound growth rate is closest to:",
    choices: ["10.0%", "10.5%", "21.0%", "11.0%"],
    answer: 0,
    explanation: "121/100 = 1.21. The two-year compound factor implies (1 + r)^2 = 1.21 ⇒ 1 + r = √1.21 = 1.10 ⇒ r = 10%."
  },
  {
    id: "qua-02",
    topic: "Quantitative Methods",
    level: "I",
    difficulty: "medium",
    stem: "If events A and B are independent, which statement is true?",
    choices: [
      "P(A|B) = P(A) + P(B)",
      "P(A and B) = P(A) × P(B)",
      "P(A or B) = P(A) × P(B)",
      "P(A|B) = 0"
    ],
    answer: 1,
    explanation: "Independence means the joint probability equals the product of the marginals: P(A ∩ B) = P(A)P(B). Also P(A|B) = P(A) when P(B) > 0."
  },
  {
    id: "qua-03",
    topic: "Quantitative Methods",
    level: "I",
    difficulty: "medium",
    stem: "A normal distribution has mean 8% and standard deviation 4%. The approximate 95% confidence interval for a single observation is:",
    choices: [
      "4% to 12%",
      "0% to 16%",
      "−4% to 20%",
      "2% to 14%"
    ],
    answer: 1,
    explanation: "For a normal distribution, about 95% of observations lie within mean ± 2σ. Here 8% ± 2×4% ⇒ 0% to 16%."
  },
  {
    id: "qua-04",
    topic: "Quantitative Methods",
    level: "I",
    difficulty: "hard",
    stem: "In hypothesis testing, failing to reject a false null hypothesis is:",
    choices: [
      "A Type I error",
      "A Type II error",
      "The power of the test",
      "Evidence that the null is true"
    ],
    answer: 1,
    explanation: "Type I error: reject a true null. Type II error: fail to reject a false null. Power is 1 − P(Type II)."
  },
  {
    id: "qua-05",
    topic: "Quantitative Methods",
    level: "I",
    difficulty: "medium",
    stem: "The Sharpe ratio of a portfolio is most accurately described as:",
    choices: [
      "Excess return per unit of systematic risk",
      "Excess return per unit of total risk",
      "Total return per unit of downside risk",
      "Alpha divided by residual risk"
    ],
    answer: 1,
    explanation: "Sharpe ratio = (Rp − Rf) / σp, i.e., excess return per unit of total (stand-alone) risk. Treynor uses beta; information ratio uses residual risk."
  },
  {
    id: "eco-01",
    topic: "Economics",
    level: "I",
    difficulty: "easy",
    stem: "All else equal, an increase in the money supply in the short run is most likely to:",
    choices: [
      "Increase interest rates and decrease aggregate demand",
      "Decrease interest rates and increase aggregate demand",
      "Increase interest rates and increase unemployment",
      "Have no effect on output under sticky prices"
    ],
    answer: 1,
    explanation: "In the short-run Keynesian framework, higher money supply lowers interest rates, stimulates investment/consumption, and raises aggregate demand and output."
  },
  {
    id: "eco-02",
    topic: "Economics",
    level: "I",
    difficulty: "medium",
    stem: "If the price elasticity of demand is −2.0, a 5% price increase causes quantity demanded to:",
    choices: [
      "Fall by about 2.5%",
      "Fall by about 5%",
      "Fall by about 10%",
      "Rise by about 10%"
    ],
    answer: 2,
    explanation: "%ΔQ ≈ elasticity × %ΔP = (−2) × 5% = −10%. Quantity demanded falls about 10%."
  },
  {
    id: "eco-03",
    topic: "Economics",
    level: "I",
    difficulty: "medium",
    stem: "Under purchasing power parity (PPP), if domestic inflation exceeds foreign inflation, the domestic currency should:",
    choices: [
      "Appreciate in the long run",
      "Depreciate in the long run",
      "Remain unchanged by definition",
      "Appreciate only if interest rates also rise"
    ],
    answer: 1,
    explanation: "Relative PPP: higher inflation currencies depreciate so that real exchange rates are stable over the long run."
  },
  {
    id: "eco-04",
    topic: "Economics",
    level: "I",
    difficulty: "hard",
    stem: "A monopolist maximizes profit where:",
    choices: [
      "Price equals marginal cost",
      "Marginal revenue equals marginal cost",
      "Average revenue equals average total cost",
      "Price equals average variable cost"
    ],
    answer: 1,
    explanation: "Profit maximization for any firm with market power occurs where MR = MC. For a monopolist, P > MR, so P > MC at the optimum."
  },
  {
    id: "fra-01",
    topic: "Financial Reporting",
    level: "I",
    difficulty: "easy",
    stem: "Which financial statement reports a company’s financial position at a point in time?",
    choices: [
      "Income statement",
      "Statement of cash flows",
      "Balance sheet",
      "Statement of comprehensive income"
    ],
    answer: 2,
    explanation: "The balance sheet (statement of financial position) shows assets, liabilities, and equity at a specific date. The income statement covers a period."
  },
  {
    id: "fra-02",
    topic: "Financial Reporting",
    level: "I",
    difficulty: "medium",
    stem: "Under IFRS, development costs may be capitalized when:",
    choices: [
      "Research begins, if management intends to continue the project",
      "Technical feasibility is established and other capitalization criteria are met",
      "The product is marketed, regardless of feasibility",
      "They can never be capitalized; all R&D is expensed"
    ],
    answer: 1,
    explanation: "IFRS requires expensing research. Development may be capitalized once technical feasibility and other criteria (intention, ability, probable future benefits, reliable measurement) are met. US GAAP generally expenses both."
  },
  {
    id: "fra-03",
    topic: "Financial Reporting",
    level: "I",
    difficulty: "medium",
    stem: "An increase in accounts receivable, holding sales constant, most likely indicates:",
    choices: [
      "Improving cash conversion",
      "Deteriorating collection efficiency or looser credit",
      "Higher inventory turnover",
      "Lower days sales outstanding"
    ],
    answer: 1,
    explanation: "With flat sales, rising A/R implies customers are paying more slowly (higher DSO), often from weaker collections or easier credit terms."
  },
  {
    id: "fra-04",
    topic: "Financial Reporting",
    level: "I",
    difficulty: "hard",
    stem: "Compared with FIFO in a period of rising prices, LIFO inventory (where permitted) typically results in:",
    choices: [
      "Higher COGS and lower taxes",
      "Lower COGS and higher taxes",
      "Higher ending inventory and higher taxes",
      "Identical COGS if turnover is high"
    ],
    answer: 0,
    explanation: "Rising prices: LIFO assigns newer, higher costs to COGS → higher COGS, lower taxable income/taxes, and lower ending inventory versus FIFO."
  },
  {
    id: "fra-05",
    topic: "Financial Reporting",
    level: "I",
    difficulty: "medium",
    stem: "Free cash flow to the firm (FCFF) starts from NOPAT and then:",
    choices: [
      "Adds non-cash charges, subtracts investments in working capital and fixed capital",
      "Subtracts after-tax interest and adds net borrowing",
      "Equals net income plus depreciation only",
      "Ignores capital expenditures by definition"
    ],
    answer: 0,
    explanation: "A common FCFF formulation: NOPAT + non-cash charges − WCInv − FCInv. FCFE further adjusts for after-tax interest and net borrowing."
  },
  {
    id: "cfa-01",
    topic: "Corporate Finance",
    level: "I",
    difficulty: "medium",
    stem: "The weighted average cost of capital (WACC) is most appropriately used to discount:",
    choices: [
      "Equity cash flows when leverage changes each year",
      "Free cash flows to the firm at the firm’s target capital structure",
      "Dividends when the firm has no debt",
      "After-tax earnings without regard to risk"
    ],
    answer: 1,
    explanation: "WACC discounts FCFF when the capital structure weights reflect the financing mix applicable to the project/firm (often target weights)."
  },
  {
    id: "cfa-02",
    topic: "Corporate Finance",
    level: "I",
    difficulty: "easy",
    stem: "A project’s NPV is positive. This most likely means:",
    choices: [
      "IRR is less than the cost of capital",
      "The project earns more than the required return",
      "Payback is longer than the project’s life",
      "Accounting rate of return equals zero"
    ],
    answer: 1,
    explanation: "NPV > 0 implies the present value of inflows exceeds outflows at the discount rate, so the project earns more than the required return (IRR > cost of capital for conventional projects)."
  },
  {
    id: "cfa-03",
    topic: "Corporate Finance",
    level: "I",
    difficulty: "medium",
    stem: "Modigliani–Miller Proposition I without taxes states that:",
    choices: [
      "Firm value rises with leverage",
      "Firm value is independent of capital structure",
      "WACC rises linearly with the debt ratio",
      "Equity cost is constant as leverage rises"
    ],
    answer: 1,
    explanation: "MM I (no taxes, perfect markets): capital structure does not affect firm value. Equity cost rises with leverage, offsetting cheaper debt so WACC is constant."
  },
  {
    id: "cfa-04",
    topic: "Corporate Finance",
    level: "I",
    difficulty: "hard",
    stem: "The primary agency conflict between shareholders and managers is best mitigated by:",
    choices: [
      "Maximizing short-term reported earnings only",
      "Aligning compensation with long-term shareholder value",
      "Eliminating all debt to avoid creditor monitoring",
      "Allowing unrestricted use of corporate jets without disclosure"
    ],
    answer: 1,
    explanation: "Aligning incentives (equity-based pay, performance metrics tied to long-term value), board oversight, and monitoring reduce manager–shareholder agency costs."
  },
  {
    id: "eq-01",
    topic: "Equity Investments",
    level: "I",
    difficulty: "easy",
    stem: "In the Gordon growth model, value equals next year’s dividend divided by:",
    choices: [
      "Required return minus growth rate",
      "Required return plus growth rate",
      "Dividend yield minus growth",
      "ROE minus payout ratio"
    ],
    answer: 0,
    explanation: "P0 = D1 / (r − g), assuming constant growth forever and r > g."
  },
  {
    id: "eq-02",
    topic: "Equity Investments",
    level: "I",
    difficulty: "medium",
    stem: "A stock’s beta measures:",
    choices: [
      "Total volatility relative to its peer group",
      "Sensitivity of returns to market returns (systematic risk)",
      "Idiosyncratic risk that diversification cannot reduce",
      "Liquidity relative to average daily volume"
    ],
    answer: 1,
    explanation: "Beta is the slope in the market model / CAPM: exposure to market (systematic) risk. Diversifiable risk is not rewarded in CAPM."
  },
  {
    id: "eq-03",
    topic: "Equity Investments",
    level: "I",
    difficulty: "medium",
    stem: "Relative to passive indexing, active equity management seeks to:",
    choices: [
      "Match a benchmark’s return before fees",
      "Earn positive alpha after adjusting for risk",
      "Eliminate all systematic risk",
      "Hold every security in market-cap weights"
    ],
    answer: 1,
    explanation: "Active managers deviate from benchmarks to generate alpha (risk-adjusted excess return), at the cost of fees and active risk."
  },
  {
    id: "eq-04",
    topic: "Equity Investments",
    level: "I",
    difficulty: "hard",
    stem: "Justified leading P/E based on fundamentals increases when, all else equal:",
    choices: [
      "Required return increases",
      "Payout ratio decreases and growth is unchanged",
      "Expected growth increases (with r − g still positive)",
      "Risk-free rate rises while equity risk premium is unchanged"
    ],
    answer: 2,
    explanation: "Justified leading P/E ≈ (payout) / (r − g). Higher g (without collapsing r − g) raises the multiple; higher r lowers it."
  },
  {
    id: "fi-01",
    topic: "Fixed Income",
    level: "I",
    difficulty: "easy",
    stem: "If market yields rise, the price of an option-free bond will:",
    choices: [
      "Rise",
      "Fall",
      "Remain unchanged",
      "Rise only if coupon is floating"
    ],
    answer: 1,
    explanation: "Bond prices and yields move inversely for option-free bonds. Higher discount rates reduce the PV of promised cash flows."
  },
  {
    id: "fi-02",
    topic: "Fixed Income",
    level: "I",
    difficulty: "medium",
    stem: "Macaulay duration is best interpreted as:",
    choices: [
      "The bond’s remaining legal maturity",
      "The weighted-average time to receipt of cash flows",
      "The percentage price change for a 1% yield change exactly",
      "Credit spread duration only"
    ],
    answer: 1,
    explanation: "Macaulay duration is the PV-weighted average maturity of cash flows. Modified duration ≈ −(%ΔP)/Δy approximates interest-rate sensitivity."
  },
  {
    id: "fi-03",
    topic: "Fixed Income",
    level: "I",
    difficulty: "medium",
    stem: "Convexity adjustment is most important when:",
    choices: [
      "Yield changes are very small and linear approximation is exact",
      "Estimating price changes for large yield moves",
      "Pricing a floater at a reset date",
      "Duration is zero"
    ],
    answer: 1,
    explanation: "Duration is a linear (first-order) approximation. Convexity improves the estimate for larger yield changes because the price–yield curve is curved."
  },
  {
    id: "fi-04",
    topic: "Fixed Income",
    level: "I",
    difficulty: "hard",
    stem: "For a given duration, which bond typically has greater convexity?",
    choices: [
      "A barbell portfolio versus a bullet with similar duration",
      "A zero-coupon bond versus a barbell with same duration",
      "A floating-rate note right after a reset versus a long zero",
      "Any callable bond versus an otherwise identical option-free bond"
    ],
    answer: 0,
    explanation: "Dispersed cash flows (barbell) produce higher convexity than concentrated cash flows (bullet) at similar duration. Callables have negative convexity in some regions."
  },
  {
    id: "fi-05",
    topic: "Fixed Income",
    level: "I",
    difficulty: "medium",
    stem: "Credit spread risk is the risk that:",
    choices: [
      "Benchmarks yields fall while spreads stay constant",
      "Spreads widen, reducing the bond’s price for a given benchmark yield",
      "The issuer prepays mortgages faster",
      "Inflation unexpectedly declines"
    ],
    answer: 1,
    explanation: "Credit (or Z) spread widening increases the bond’s yield relative to the benchmark and lowers price, even if benchmark rates are unchanged."
  },
  {
    id: "der-01",
    topic: "Derivatives",
    level: "I",
    difficulty: "easy",
    stem: "The buyer of a European call option has:",
    choices: [
      "The obligation to buy the underlying at expiration",
      "The right to buy the underlying at the strike at expiration",
      "The right to sell the underlying at any time",
      "Unlimited downside and capped upside"
    ],
    answer: 1,
    explanation: "A call gives the right to buy at the strike. European style: exercise only at expiration. Long call payoff is capped downside (premium) with unlimited upside."
  },
  {
    id: "der-02",
    topic: "Derivatives",
    level: "I",
    difficulty: "medium",
    stem: "In a plain vanilla interest rate swap, the fixed-rate payer:",
    choices: [
      "Benefits when floating rates fall",
      "Benefits when floating rates rise",
      "Receives fixed and pays floating",
      "Has no market risk after inception"
    ],
    answer: 1,
    explanation: "The fixed payer pays fixed and receives floating, so gains when floating rates rise (receive more). Market value still fluctuates with rates."
  },
  {
    id: "der-03",
    topic: "Derivatives",
    level: "I",
    difficulty: "medium",
    stem: "Put–call parity for European options on a non-dividend-paying stock states:",
    choices: [
      "c + PV(X) = p + S0",
      "c + S0 = p + PV(X)",
      "c − p = S0 − PV(X)",
      "Both A and C are equivalent rearrangements"
    ],
    answer: 3,
    explanation: "Standard parity: c + PV(X) = p + S0, which rearranges to c − p = S0 − PV(X). Violations imply arbitrage."
  },
  {
    id: "der-04",
    topic: "Derivatives",
    level: "I",
    difficulty: "hard",
    stem: "An increase in the risk-free rate, holding other Black–Scholes–Merton inputs constant, tends to:",
    choices: [
      "Decrease call values and increase put values",
      "Increase call values and decrease put values",
      "Increase both call and put values equally",
      "Have no effect on option values"
    ],
    answer: 1,
    explanation: "Higher r raises the forward price / reduces PV of strike, which increases calls and decreases puts, all else equal."
  },
  {
    id: "alt-01",
    topic: "Alternative Investments",
    level: "I",
    difficulty: "medium",
    stem: "Compared with public equities, private equity investments typically have:",
    choices: [
      "Higher liquidity and lower fees",
      "Lower liquidity and longer investment horizons",
      "Daily NAV marking with no lockups",
      "Identical risk profiles once diversified"
    ],
    answer: 1,
    explanation: "PE is illiquid, often with multi-year lockups/commitments, higher fees, and appraisal-based valuations that can understate volatility."
  },
  {
    id: "alt-02",
    topic: "Alternative Investments",
    level: "I",
    difficulty: "easy",
    stem: "A hedge fund using a long–short equity strategy primarily seeks to:",
    choices: [
      "Replicate market beta cheaply",
      "Earn returns from security selection while reducing net market exposure",
      "Avoid short selling by regulation",
      "Hold only government bonds"
    ],
    answer: 1,
    explanation: "Long–short equity goes long undervalued and short overvalued names, aiming for alpha with controlled beta/net exposure."
  },
  {
    id: "alt-03",
    topic: "Alternative Investments",
    level: "I",
    difficulty: "medium",
    stem: "Real estate investment trusts (REITs) are often attractive in portfolios because they may provide:",
    choices: [
      "Guaranteed principal protection",
      "Income and potential diversification relative to stocks and bonds",
      "Zero correlation with equities at all horizons",
      "Exemption from all market risk"
    ],
    answer: 1,
    explanation: "REITs can offer income and partial diversification benefits, though correlations with equities can rise in crises and they remain risky assets."
  },
  {
    id: "pm-01",
    topic: "Portfolio Management",
    level: "I",
    difficulty: "easy",
    stem: "Diversification reduces portfolio risk most effectively when asset returns are:",
    choices: [
      "Perfectly positively correlated",
      "Less than perfectly correlated",
      "Identical in every period",
      "Independent of volatility"
    ],
    answer: 1,
    explanation: "Risk-reduction benefits of diversification increase as correlations fall below +1. Perfect positive correlation yields no diversification benefit."
  },
  {
    id: "pm-02",
    topic: "Portfolio Management",
    level: "I",
    difficulty: "medium",
    stem: "The capital market line (CML) plots expected return against:",
    choices: [
      "Beta",
      "Total risk (standard deviation) for efficient portfolios",
      "Residual risk only",
      "Skewness"
    ],
    answer: 1,
    explanation: "The CML shows combinations of the risk-free asset and the market portfolio in expected return–total risk space. The SML uses beta."
  },
  {
    id: "pm-03",
    topic: "Portfolio Management",
    level: "I",
    difficulty: "medium",
    stem: "According to CAPM, the expected return of a security increases with:",
    choices: [
      "Idiosyncratic volatility",
      "Beta",
      "The stock’s own variance only",
      "Trading volume"
    ],
    answer: 1,
    explanation: "E(Ri) = Rf + βi[E(Rm) − Rf]. Only systematic risk (beta) is priced; idiosyncratic risk is diversified away."
  },
  {
    id: "pm-04",
    topic: "Portfolio Management",
    level: "I",
    difficulty: "hard",
    stem: "Strategic asset allocation is best described as:",
    choices: [
      "Day-trading around news events",
      "Long-term target weights aligned with investor objectives and constraints",
      "Exclusively using technical indicators",
      "Holding only alternative investments"
    ],
    answer: 1,
    explanation: "SAA sets long-term policy weights based on IPS objectives, constraints, and capital market expectations. Tactical allocation makes shorter-term deviations."
  },
  {
    id: "pm-05",
    topic: "Portfolio Management",
    level: "I",
    difficulty: "medium",
    stem: "An investor’s risk tolerance is low and liquidity needs are high. The IPS should most likely emphasize:",
    choices: [
      "Concentrated private equity and locked-up hedge funds",
      "Higher allocations to liquid, lower-volatility fixed income",
      "Maximum use of leverage",
      "Ignoring time horizon"
    ],
    answer: 1,
    explanation: "Low risk tolerance and high liquidity needs point toward more liquid, lower-risk fixed income and cash-like assets within a suitable overall mix."
  },
  {
    id: "qua-06",
    topic: "Quantitative Methods",
    level: "I",
    difficulty: "medium",
    stem: "The coefficient of variation is useful because it:",
    choices: [
      "Measures only downside risk",
      "Allows risk comparison across investments with different means",
      "Equals beta in CAPM",
      "Ignores the standard deviation"
    ],
    answer: 1,
    explanation: "CV = σ / mean (often using expected return). It scales risk by return level, aiding comparison across different magnitudes."
  },
  {
    id: "eco-05",
    topic: "Economics",
    level: "I",
    difficulty: "medium",
    stem: "Stagflation refers to an economy experiencing:",
    choices: [
      "High growth and low inflation",
      "High unemployment and high inflation",
      "Deflation with booming output",
      "A liquidity trap with zero unemployment"
    ],
    answer: 1,
    explanation: "Stagflation combines stagnant growth/high unemployment with elevated inflation—often associated with adverse supply shocks."
  },
  {
    id: "fra-06",
    topic: "Financial Reporting",
    level: "I",
    difficulty: "medium",
    stem: "Operating cash flow under the indirect method starts with net income and adjusts for:",
    choices: [
      "Only cash dividends paid",
      "Non-cash items and changes in operating working capital",
      "Issuance of common stock",
      "Purchases of PPE only"
    ],
    answer: 1,
    explanation: "Indirect CFO: net income ± non-cash items (e.g., depreciation) ± changes in operating WC (A/R, inventory, A/P, etc.). Investing/financing are separate."
  },
  {
    id: "eq-05",
    topic: "Equity Investments",
    level: "I",
    difficulty: "medium",
    stem: "In efficient markets of the semi-strong form, prices reflect:",
    choices: [
      "Only past trading data",
      "All public information, including past prices and fundamental data",
      "All public and private information",
      "No information at all"
    ],
    answer: 1,
    explanation: "Weak form: past market data. Semi-strong: all public info. Strong: public + private. Semi-strong efficiency implies fundamental analysis cannot earn abnormal returns on public info alone."
  },
  {
    id: "fi-06",
    topic: "Fixed Income",
    level: "I",
    difficulty: "easy",
    stem: "A bond quoted at a discount means:",
    choices: [
      "Price equals par",
      "Price is below par because yield exceeds coupon rate (for a fixed coupon)",
      "Coupon rate exceeds yield to maturity",
      "The issuer has defaulted"
    ],
    answer: 1,
    explanation: "For a fixed-coupon option-free bond, if YTM > coupon rate, the bond prices below par (discount)."
  },
  {
    id: "der-05",
    topic: "Derivatives",
    level: "I",
    difficulty: "medium",
    stem: "Marking to market of exchange-traded futures primarily:",
    choices: [
      "Eliminates the need for margins",
      "Settles daily gains/losses and reduces counterparty credit risk",
      "Converts futures into forwards with no cash flows until expiry",
      "Guarantees profits for long positions"
    ],
    answer: 1,
    explanation: "Daily settlement (mark-to-market) plus margins/clearinghouses manage credit risk by realizing P&L each day."
  },
  {
    id: "eth-05",
    topic: "Ethics",
    level: "I",
    difficulty: "medium",
    stem: "When preparing research reports, members must:",
    choices: [
      "Guarantee a price target will be achieved",
      "Use reasonable diligence and have a reasonable basis for recommendations",
      "Include only information that supports a buy thesis",
      "Omit risk factors to keep reports concise"
    ],
    answer: 1,
    explanation: "Standard V(A) Diligence and Reasonable Basis requires thorough analysis and a reasonable basis. Omissions that mislead and unsupported guarantees violate Standards."
  },
  {
    id: "pm-06",
    topic: "Portfolio Management",
    level: "I",
    difficulty: "medium",
    stem: "Rebalancing a portfolio back to strategic weights after market moves is primarily intended to:",
    choices: [
      "Maximize turnover for commission revenue",
      "Control risk drift and maintain the intended risk profile",
      "Eliminate the need for an IPS",
      "Guarantee higher returns than buy-and-hold"
    ],
    answer: 1,
    explanation: "As markets move, weights drift and risk characteristics change. Periodic rebalancing restores target exposures consistent with the IPS."
  },
  {
    id: "cfa-05",
    topic: "Corporate Finance",
    level: "I",
    difficulty: "medium",
    stem: "Floatation costs for new equity are best handled in capital budgeting by:",
    choices: [
      "Ignoring them entirely in all cases",
      "Including them in the initial project outlay (or adjusting project cost) rather than permanently inflating WACC",
      "Adding them only to the cost of debt",
      "Treating them as a reduction in NPV discount rate"
    ],
    answer: 1,
    explanation: "Best practice is to incorporate flotation costs into the project’s initial cash outflow (or an adjusted project cost), not to bake a permanent increase into WACC for all projects."
  },
  {
    id: "qua-07",
    topic: "Quantitative Methods",
    level: "I",
    difficulty: "hard",
    stem: "Bayes’ formula is used to:",
    choices: [
      "Update prior probabilities given new information",
      "Compute sample standard deviation",
      "Test for heteroskedasticity only",
      "Estimate duration of a bond"
    ],
    answer: 0,
    explanation: "Bayes’ theorem updates prior probabilities to posterior probabilities after observing new information/evidence."
  },
  {
    id: "eco-06",
    topic: "Economics",
    level: "I",
    difficulty: "hard",
    stem: "Under the Mundell–Fleming framework with high capital mobility and floating rates, expansionary monetary policy tends to:",
    choices: [
      "Appreciate the currency and reduce net exports",
      "Depreciate the currency and support net exports",
      "Have no effect on the exchange rate",
      "Require a simultaneous fiscal contraction to work"
    ],
    answer: 1,
    explanation: "Easier money lowers rates, capital outflows depreciate the currency under floating rates, which boosts net exports—reinforcing monetary stimulus."
  },
  {
    id: "fra-07",
    topic: "Financial Reporting",
    level: "I",
    difficulty: "hard",
    stem: "Aggressive revenue recognition that pulls sales forward most likely:",
    choices: [
      "Improves long-run cash generation permanently",
      "Raises near-term earnings quality concerns and may reverse later",
      "Has no effect on receivables",
      "Is always required under IFRS 15"
    ],
    answer: 1,
    explanation: "Pulling revenue forward inflates current earnings/receivables and often leads to later reversals or weaker growth—classic earnings-quality red flag."
  },
  {
    id: "eq-06",
    topic: "Equity Investments",
    level: "I",
    difficulty: "hard",
    stem: "Enterprise value is most often defined as:",
    choices: [
      "Equity market cap only",
      "Market value of equity + market value of debt − cash (and equivalents)",
      "Book value of assets minus liabilities",
      "EBITDA × (1 − tax rate)"
    ],
    answer: 1,
    explanation: "EV ≈ market cap + net debt (debt − cash) + other claims (preferred, NCI) as applicable—value of core operating assets to all capital providers."
  },
  {
    id: "alt-04",
    topic: "Alternative Investments",
    level: "I",
    difficulty: "hard",
    stem: "Survivorship bias in hedge fund databases tends to:",
    choices: [
      "Understate historical returns because failed funds remain",
      "Overstate historical returns because failed/closed funds drop out",
      "Have no effect on average returns",
      "Only affect fixed-income indexes"
    ],
    answer: 1,
    explanation: "When poorly performing funds stop reporting and are removed, remaining samples look better—upward bias in reported average performance."
  },
  {
    id: "pm-07",
    topic: "Portfolio Management",
    level: "I",
    difficulty: "hard",
    stem: "The information ratio is defined as:",
    choices: [
      "Active return divided by tracking risk (active risk)",
      "Total return divided by beta",
      "Excess return over Rf divided by total volatility",
      "Alpha divided by market return"
    ],
    answer: 0,
    explanation: "IR = (Rp − Rb) / σ(Rp − Rb). It measures active return per unit of active risk—key for evaluating active managers."
  },
  {
    id: "fi-07",
    topic: "Fixed Income",
    level: "I",
    difficulty: "hard",
    stem: "An upward-sloping spot curve most likely implies that the forward curve lies:",
    choices: [
      "Below the spot curve",
      "Above the spot curve",
      "Exactly on the spot curve always",
      "Unrelated to the spot curve"
    ],
    answer: 1,
    explanation: "When the spot curve slopes upward, implied forward rates generally lie above the spot curve (forwards are ‘above spots’)."
  },
  {
    id: "eth-06",
    topic: "Ethics",
    level: "I",
    difficulty: "hard",
    stem: "Soft-dollar arrangements are acceptable only when:",
    choices: [
      "They benefit the firm’s marketing budget regardless of client impact",
      "Client brokerage pays for research that assists in the investment decision-making process and clients receive full benefit with proper disclosure",
      "The broker is an affiliate and no disclosure is needed",
      "Commissions are higher than principal trades in all cases"
    ],
    answer: 1,
    explanation: "Soft dollars must benefit clients, be for allowable research/brokerage services aiding investment decisions, and be handled with appropriate disclosure and loyalty to clients."
  }
];
