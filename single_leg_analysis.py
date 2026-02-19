"""
Single-Leg Arbitrage Analysis
==============================
Instead of executing all 3 legs, find which SINGLE currency pair is
mispriced relative to its implied cross-rate from all other paths.

For each pair (A, B):
  - Calculate the IMPLIED rate via every possible intermediate currency C:
    implied_rate(A->B via C) = rate(A->C) * rate(C->B)
  - Compare to the ACTUAL direct rate(A->B)
  - The deviation tells us which pair is mispriced and by how much
  - Trade only that one pair in the direction of the correction

This is 1/3 the transaction cost of full triangular arbitrage.
"""

import urllib.request
import json
from itertools import permutations

CURRENCIES = ["USD", "EUR", "GBP", "MXN", "JPY", "CHF", "CAD", "AUD"]

def fetch_rates(base, targets):
    symbols = ",".join(targets)
    url = f"https://api.frankfurter.dev/v1/latest?base={base}&symbols={symbols}"
    req = urllib.request.Request(url, headers={"User-Agent": "Python/3"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode())
    return data

def build_rate_matrix(currencies):
    matrix = {}
    for base in currencies:
        targets = [c for c in currencies if c != base]
        print(f"  Fetching rates for base: {base}...")
        data = fetch_rates(base, targets)
        matrix[(base, base)] = 1.0
        for target, rate in data["rates"].items():
            if target in currencies:
                matrix[(base, target)] = rate
    return matrix

def analyze_single_leg(currencies, matrix):
    """
    For each direct pair, compare actual rate vs all implied cross rates.
    Find the pairs with the largest deviation.
    """
    results = []

    for a in currencies:
        for b in currencies:
            if a == b:
                continue

            actual = matrix.get((a, b))
            if actual is None:
                continue

            # Calculate implied rate via every intermediary
            implied_rates = []
            for c in currencies:
                if c == a or c == b:
                    continue
                rate_ac = matrix.get((a, c))
                rate_cb = matrix.get((c, b))
                if rate_ac and rate_cb:
                    implied = rate_ac * rate_cb
                    implied_rates.append({
                        "via": c,
                        "implied": implied,
                        "rate_ac": rate_ac,
                        "rate_cb": rate_cb,
                    })

            if not implied_rates:
                continue

            # Average implied rate across all intermediaries
            avg_implied = sum(r["implied"] for r in implied_rates) / len(implied_rates)
            deviation_pct = ((actual - avg_implied) / avg_implied) * 100

            # Best single intermediary (largest deviation from actual)
            best_via = max(implied_rates, key=lambda r: abs(actual - r["implied"]))
            best_deviation = ((actual - best_via["implied"]) / best_via["implied"]) * 100

            results.append({
                "pair": f"{a}/{b}",
                "actual": actual,
                "avg_implied": round(avg_implied, 6),
                "deviation_pct": round(deviation_pct, 6),
                "best_via": best_via["via"],
                "best_implied": round(best_via["implied"], 6),
                "best_deviation_pct": round(best_deviation, 6),
                "all_implied": implied_rates,
            })

    results.sort(key=lambda x: abs(x["deviation_pct"]), reverse=True)
    return results

def analyze_profitability(results, trade_amount=100000):
    """
    For each mispriced pair, calculate:
    - Theoretical profit from the deviation
    - Break-even spread (what spread would eat all the profit)
    - Required volume at various spread levels
    """
    print(f"\n--- Profitability Analysis (trade amount: ${trade_amount:,.0f}) ---")
    print(f"{'Pair':<10} {'Deviation%':>12} {'Gross Profit':>14} {'Break-Even Spread':>20} {'Direction':<10}")
    print("-" * 70)

    for r in results[:20]:
        dev = r["deviation_pct"]
        # If actual > implied: pair is overpriced, sell it (short)
        # If actual < implied: pair is underpriced, buy it (long)
        direction = "SELL" if dev > 0 else "BUY"
        gross_profit = trade_amount * abs(dev) / 100

        # Break-even spread: the spread that would eat all profit
        # On a single leg, spread cost = trade_amount * spread_pct
        break_even_spread_pct = abs(dev)

        print(f"{r['pair']:<10} {dev:>12.6f} ${gross_profit:>13.2f} {break_even_spread_pct:>19.6f}% {direction:<10}")

    # Typical spread analysis
    print(f"\n--- Spread Reality Check ---")
    print(f"Typical retail spreads:")
    print(f"  EUR/USD: ~0.008% (0.8 pips)")
    print(f"  USD/JPY: ~0.010% (1.0 pips)")
    print(f"  GBP/USD: ~0.012% (1.2 pips)")
    print(f"  USD/MXN: ~0.030% (3.0 pips)")
    print(f"  Exotic pairs: ~0.050-0.100%")
    print(f"\nTypical institutional spreads:")
    print(f"  Major pairs: ~0.001-0.003%")
    print(f"  Minor pairs: ~0.005-0.015%")
    print(f"  Exotic pairs: ~0.015-0.050%")

def main():
    print("=" * 70)
    print("SINGLE-LEG ARBITRAGE ANALYSIS")
    print("=" * 70)
    print(f"\nCurrencies: {', '.join(CURRENCIES)}")

    print("\n--- Fetching Live Rates ---")
    matrix = build_rate_matrix(CURRENCIES)

    print("\n--- Cross-Rate Deviation Analysis ---")
    results = analyze_single_leg(CURRENCIES, matrix)

    print(f"\nTop 20 pairs by deviation from implied cross-rate:")
    print(f"{'Pair':<10} {'Actual':>12} {'Avg Implied':>12} {'Deviation%':>12} {'Best Via':>10} {'Best Dev%':>12}")
    print("-" * 70)
    for r in results[:20]:
        print(f"{r['pair']:<10} {r['actual']:>12.6f} {r['avg_implied']:>12.6f} {r['deviation_pct']:>12.6f} {r['best_via']:>10} {r['best_deviation_pct']:>12.6f}")

    # Detailed breakdown of the most mispriced pair
    best = results[0]
    print(f"\n--- Detailed Breakdown: {best['pair']} ---")
    print(f"Actual rate: {best['actual']}")
    print(f"Average implied rate: {best['avg_implied']}")
    print(f"Deviation: {best['deviation_pct']}%")
    print(f"\nImplied rates via each intermediary:")
    for imp in sorted(best["all_implied"], key=lambda x: abs(best["actual"] - x["implied"]), reverse=True):
        dev = ((best["actual"] - imp["implied"]) / imp["implied"]) * 100
        print(f"  via {imp['via']:>4}: {imp['implied']:>12.6f} (deviation: {dev:>+.6f}%)")

    analyze_profitability(results)

    # Summary
    print(f"\n--- Key Findings ---")
    above_retail = [r for r in results if abs(r["deviation_pct"]) > 0.03]
    above_institutional = [r for r in results if abs(r["deviation_pct"]) > 0.005]
    print(f"Pairs with deviation > retail spread (0.03%): {len(above_retail)}")
    print(f"Pairs with deviation > institutional spread (0.005%): {len(above_institutional)}")
    if above_institutional:
        print(f"\nPotentially profitable at institutional level:")
        for r in above_institutional[:10]:
            print(f"  {r['pair']}: {r['deviation_pct']:+.6f}% (via {r['best_via']})")

if __name__ == "__main__":
    main()
