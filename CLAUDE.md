# CLAUDE.md

**Vault:** `C:\Users\Chris.Isaacson\Vault\projects\triangular-arbitrage\README.md`

## Project Overview

Triangular arbitrage detection and analysis across currency and crypto markets. The core question: can we exploit differentials in cross-rates for profit? The math says yes -- differentials are real and detectable. The question is infrastructure and execution.

Three approaches explored: full triangular loops (3 legs), single-leg trades (cheapest), and DeFi flash loans (no capital needed).

## Tech Stack

- **Python 3** (stdlib only -- no external dependencies)
- `urllib.request` + `json` for API calls
- `itertools.permutations` for path enumeration
- **frankfurter.app** API (ECB daily rates, free, no API key)

## Project Structure

| File | Purpose |
|------|---------|
| `detect_arbitrage.py` | Core detector. Fetches live rates, builds NxN matrix, checks all 3-currency loops, runs Bellman-Ford negative cycle detection |
| `single_leg_analysis.py` | Compares each direct rate vs implied cross-rates through all intermediaries. Finds the single mispriced pair -- 1/3 the tx cost of full triangular |
| `roi_analysis.py` | Business case. Compares ROI across 4 scenarios: Forex Institutional, Crypto CEX, DeFi Solana (conservative), DeFi Solana (optimistic) |
| `README.md` | Full writeup with findings, framework validation, and next steps |

## How to Run

Each script is standalone. No dependencies beyond Python 3 stdlib.

```bash
# Full triangular arbitrage detection (fetches live ECB rates)
python detect_arbitrage.py

# Single-leg cross-rate deviation analysis
python single_leg_analysis.py

# ROI comparison across all scenarios (no API calls, just math)
python roi_analysis.py
```

All scripts fetch from `api.frankfurter.dev` except `roi_analysis.py` which is pure calculation.

## Key Concepts

- **No-arbitrage condition:** `rate(A->B) * rate(B->C) * rate(C->A) = 1.0`. Product > 1.0 means profit.
- **Cross-rate / synthetic rate:** The implied rate between A and B calculated via intermediary C: `rate(A->C) * rate(C->B)`. Deviation from the direct rate reveals mispricing.
- **Bellman-Ford detection:** Convert rates to `-log(rate)` space, turning multiplication into addition. Negative cycles = arbitrage opportunities.
- **Single-leg optimization:** Instead of executing all 3 legs, identify which single pair is mispriced and trade only that one. 1/3 the transaction cost.
- **Flash loans (DeFi):** Borrow and repay in a single atomic transaction. No capital needed. If the trade isn't profitable, the tx reverts and you lose only gas (~$0.00025 on Solana).

## Key Findings

- **264/336** triangular paths show positive profit on live ECB rates across 8 currencies
- Best full-loop: USD -> AUD -> JPY -> USD = **$7.13 on $10K** (0.071%)
- Best single-leg: JPY/GBP at 0.087% deviation = **$86.79 on $100K**
- **JPY is consistently mispriced** -- slower price discovery vs other majors

## Current Status

- **Forex:** Not viable. $135K upfront + $100K capital, 7.5-year breakeven, latency disadvantage vs HFT.
- **Crypto CEX:** Accessible but modest. $300/month profit, transfer time risk between exchanges.
- **DeFi/Solana:** Under investigation. $600 upfront, $170/month, no capital needed (flash loans). Asymmetric risk: capped downside (gas), scalable upside. Key challenge is competing with existing MEV bots and finding pools with the right liquidity/inefficiency balance.

Next steps focus on Solana DEX ecosystem research, flash loan mechanics, and building a detection prototype adapted from the forex matrix math.

## Currencies Analyzed

`USD, EUR, GBP, MXN, JPY, CHF, CAD, AUD` -- configurable via the `CURRENCIES` list in each script.
