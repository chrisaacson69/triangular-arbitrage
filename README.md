# Triangular Arbitrage — Currency & Crypto Market Differentials
> Can we exploit differentials in cross-rates for profit? Math says yes. The question is infrastructure.

**Status:** active — DeFi/Solana path under investigation
**Created:** 2026-02-12
**Vault:** `C:\Users\Chris.Isaacson\Vault\projects\triangular-arbitrage\README.md`

## The Idea

Exploit differentials in exchange rates across currencies or tokens. If the product of rates around a loop ≠ 1.0, there's a profit opportunity. Multiple approaches from full triangular loops to single-leg trades to DeFi flash loans.

## Phase 1: The Math — Do Differentials Exist?

### Full Triangular Arbitrage

Using live ECB daily rates (2026-02-12) across 8 currencies (USD, EUR, GBP, MXN, JPY, CHF, CAD, AUD):

- **264 out of 336** triangular paths show positive profit
- Best full-loop path: USD → AUD → JPY → USD yields **$7.13 on $10,000** (0.071%)
- Bellman-Ford found **224 negative cycle indicators**
- **JPY is consistently the mispriced currency** — slower price discovery (confirmed by academic research)

### Single-Leg Optimization

Instead of executing all 3 legs, identify which single pair is mispriced vs implied cross-rates:

- Best single-leg: **JPY/GBP** at 0.087% deviation — **$86.79 profit on $100K**
- 2 pairs beat retail spreads (JPY/GBP, JPY/USD)
- 33 pairs beat institutional spreads
- **1/3 the transaction cost** of full triangular execution

**Conclusion:** Differentials are real and detectable. The math works.

## Phase 2: The Business Case — ROI Analysis

We initially concluded "not viable" based on assumptions about infrastructure costs. That was the accountant talking, not the CEO. So we actually researched the numbers.

### Scenario Comparison

| Scenario | Upfront | Monthly Cost | Monthly Profit | Capital Needed | Break Even |
|----------|---------|-------------|----------------|----------------|------------|
| **Forex Institutional** | $135,000 | $1,800 | $1,500 | $100,000 | 90 months |
| **Crypto CEX (Cross-Exchange)** | $0 | $150 | $300 | $10,000 | Immediate |
| **DeFi Solana (Conservative)** | $600 | $170 | $430 | $0 | 1.4 months |
| **DeFi Solana (Optimistic Niche)** | $600 | $170 | $2,830 | $0 | 6 days |

### Forex: Not Viable

- $135K upfront (Cayman Islands license + FIX API deposit)
- $100K working capital on top of that
- 7.5 years to break even
- Ongoing ROI is decent (83%) but barrier to entry is a wall
- Latency disadvantage vs. HFT firms with dedicated hardware
- **CEO Decision: No.** The infrastructure bet doesn't pencil out at our scale.

### Centralized Crypto: Accessible but Modest

- Zero upfront, $150/month operating
- $10K capital split across exchanges
- $300/month profit — steady but small
- **Key risk:** Transfer times between exchanges (minutes to hours). Price can move while your assets are in transit.
- **CEO Decision: Maybe.** Low risk, low reward. Could be a learning exercise.

### DeFi on Solana: The Interesting Path

- **$600 upfront, $170/month** — radically low barrier to entry
- **No trading capital needed** — flash loans borrow and repay in a single atomic transaction
- **Failed trades cost almost nothing** — unprofitable tx simply reverts, you lose only gas (~$0.00025)
- Break even in 1.4 months (conservative) to 6 days (optimistic)
- 240,000+ successful DeFi arbs identified in 1 year ($868M volume across chains)
- **Asymmetric risk profile:** capped downside (gas on failed txs), scalable upside

**Key risks:**
- **Liquidity risk** — the same thin pools that create wide spreads (bigger arb opportunities) are the ones where your own trade moves the price. Flash loans amplify this: borrowing large amounts to capture small differentials means slippage can eat your profit. Thick pools are safe but have tiny spreads; thin pools have big spreads but can't absorb your trade. The sweet spot — liquid enough to execute, inefficient enough to profit — is the real thing you're searching for.
- 86% of crypto trading already automated — highly competitive
- Institutional MEV bots operate in milliseconds
- Smart contract bugs = potential total loss
- Need MEV protection (Jito on Solana) to avoid sandwich attacks

**Key advantages:**
- Flash loans = zero capital requirement
- Solana gas = near-zero cost per attempt
- Open-source bot templates exist (ExtropyIO, etc.)
- New token launches/pools constantly create fresh niche opportunities
- Failed attempts are essentially free — you can try thousands of times

**CEO Decision: Worth investigating further.** The risk/reward asymmetry is favorable. Low downside, meaningful upside, and the competitive moat question ("can we find arbs others aren't harvesting?") is an entrepreneurial bet worth making at $600.

## Phase 3: Next Steps (If Pursuing)

1. **Research Solana DEX ecosystem** — Orca, Raydium, Jupiter. Map token pairs, pool sizes, existing bot activity
2. **Study flash loan mechanics** — how they work on Solana, Jito integration, revert behavior
3. **Build detection prototype** — adapt our matrix math to scan DEX pool prices instead of forex rates
4. **Estimate real opportunity frequency** — how many arbs/day exist on Solana DEXes, what's the average profit
5. **Smart contract development** — build or adapt from open-source templates, security audit
6. **Paper trading** — run detection without execution to measure what we *would* have caught
7. **Deploy with minimal capital** — start small, measure, iterate

## What This Project Taught Us (Framework Validation)

This project validated every layer of our theoretical framework:

| Theory | What Happened |
|--------|--------------|
| **Utility/Trade** | Differentials are real — the math proves value gaps exist |
| **Risk** | Forex: capability risk killed it. DeFi: asymmetric risk profile favors the bet |
| **COO vs CEO** | Detection = COO (math, solved). Strategy = CEO (should we invest? investigate first) |
| **Cognitive vs Motor** | Forex bottleneck is execution speed (motor). DeFi bottleneck is smart contract quality (cognitive) |
| **Grounding** | Real money, real markets — can't be talked out of a loss |
| **Honest Assessment** | We initially skipped the CEO step and assumed "too expensive." Actual research changed the picture. |

## Files

- [detect_arbitrage.py](./detect_arbitrage.py) — Full triangular arbitrage detector with Bellman-Ford
- [single_leg_analysis.py](./single_leg_analysis.py) — Single-leg implied cross-rate deviation analysis
- [roi_analysis.py](./roi_analysis.py) — ROI comparison across all four scenarios

## Tags
economics, risk, praxis, agents, crypto, defi
