"""
Triangular Arbitrage Detector
=============================
Fetches live exchange rates and checks all possible triangular paths
for arbitrage opportunities.

Approach:
1. Fetch rates from frankfurter.app (ECB data, free, no API key)
2. Build a full NxN exchange rate matrix
3. For every possible 3-currency loop: A -> B -> C -> A
   check if the product of rates != 1.0
4. Report differentials sorted by magnitude

The "no arbitrage" condition: rate(A->B) * rate(B->C) * rate(C->A) = 1.0
If product > 1.0: profit going A -> B -> C -> A
If product < 1.0: profit going the reverse direction A -> C -> B -> A
"""

import urllib.request
import json
from itertools import permutations

# Currencies to analyze
CURRENCIES = ["USD", "EUR", "GBP", "MXN", "JPY", "CHF", "CAD", "AUD"]

def fetch_rates(base, targets):
    """Fetch exchange rates from frankfurter.app"""
    symbols = ",".join(targets)
    url = f"https://api.frankfurter.dev/v1/latest?base={base}&symbols={symbols}"
    req = urllib.request.Request(url, headers={"User-Agent": "Python/3"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode())
    return data

def build_rate_matrix(currencies):
    """Build full NxN rate matrix by fetching rates for each base currency"""
    matrix = {}
    raw_data = {}

    for base in currencies:
        targets = [c for c in currencies if c != base]
        print(f"  Fetching rates for base: {base}...")
        data = fetch_rates(base, targets)
        raw_data[base] = data

        matrix[(base, base)] = 1.0
        for target, rate in data["rates"].items():
            if target in currencies:
                matrix[(base, target)] = rate

    return matrix, raw_data

def find_triangular_arbitrage(currencies, matrix, starting_amount=10000):
    """
    Check all triangular paths for arbitrage.
    For each permutation of 3 currencies (A, B, C):
      Start with `starting_amount` of A
      Buy B with A
      Buy C with B
      Buy A with C
      Check if we end up with more than we started
    """
    results = []

    for a, b, c in permutations(currencies, 3):
        rate_ab = matrix.get((a, b))
        rate_bc = matrix.get((b, c))
        rate_ca = matrix.get((c, a))

        if rate_ab is None or rate_bc is None or rate_ca is None:
            continue

        # Product of rates - should equal 1.0 if no arbitrage
        product = rate_ab * rate_bc * rate_ca

        # Simulate the trade
        step1 = starting_amount * rate_ab      # A -> B
        step2 = step1 * rate_bc                 # B -> C
        step3 = step2 * rate_ca                 # C -> A (back to starting currency)

        profit = step3 - starting_amount
        profit_pct = (profit / starting_amount) * 100

        results.append({
            "path": f"{a} -> {b} -> {c} -> {a}",
            "product": product,
            "start": starting_amount,
            "end": round(step3, 4),
            "profit": round(profit, 4),
            "profit_pct": round(profit_pct, 6),
            "rates": {
                f"{a}->{b}": rate_ab,
                f"{b}->{c}": rate_bc,
                f"{c}->{a}": rate_ca,
            }
        })

    # Sort by absolute profit descending
    results.sort(key=lambda x: abs(x["profit"]), reverse=True)
    return results

def find_negative_cycles_bellman_ford(currencies, matrix):
    """
    Bellman-Ford approach: convert to log space, find negative cycles.
    -log(rate) transforms multiplication into addition.
    A negative cycle in this space = an arbitrage opportunity.
    """
    import math

    n = len(currencies)
    idx = {c: i for i, c in enumerate(currencies)}

    # Build edge list with -log(rate) weights
    edges = []
    for (src, dst), rate in matrix.items():
        if src != dst and rate > 0:
            weight = -math.log(rate)
            edges.append((idx[src], idx[dst], weight, src, dst))

    # Run Bellman-Ford from each source
    cycles_found = []

    for source in range(n):
        dist = [float('inf')] * n
        pred = [-1] * n
        dist[source] = 0

        # Relax edges n-1 times
        for _ in range(n - 1):
            for u, v, w, _, _ in edges:
                if dist[u] + w < dist[v]:
                    dist[v] = dist[u] + w
                    pred[v] = u

        # Check for negative cycles (one more relaxation)
        for u, v, w, src_name, dst_name in edges:
            if dist[u] + w < dist[v] - 1e-10:  # small epsilon for float comparison
                cycles_found.append({
                    "detected_at": f"{src_name} -> {dst_name}",
                    "improvement": -(dist[u] + w - dist[v]),
                    "source": currencies[source]
                })

    return cycles_found

def main():
    print("=" * 70)
    print("TRIANGULAR ARBITRAGE DETECTOR")
    print("=" * 70)
    print(f"\nCurrencies: {', '.join(CURRENCIES)}")
    print(f"Possible triangular paths: {len(list(permutations(CURRENCIES, 3)))}")

    # Step 1: Fetch rates
    print("\n--- Fetching Live Rates ---")
    matrix, raw_data = build_rate_matrix(CURRENCIES)

    # Print the date of rates
    sample_date = list(raw_data.values())[0].get("date", "unknown")
    print(f"\nRate date: {sample_date}")

    # Print rate matrix
    print("\n--- Exchange Rate Matrix ---")
    header = f"{'':>6}" + "".join(f"{c:>12}" for c in CURRENCIES)
    print(header)
    for a in CURRENCIES:
        row = f"{a:>6}"
        for b in CURRENCIES:
            rate = matrix.get((a, b), 0)
            row += f"{rate:>12.4f}"
        print(row)

    # Step 2: Find triangular arbitrage
    print("\n--- Triangular Arbitrage Analysis (starting with $10,000) ---")
    results = find_triangular_arbitrage(CURRENCIES, matrix)

    # Show top 20 results
    print(f"\nTop 20 paths by absolute profit:")
    print(f"{'Path':<30} {'Product':>10} {'End ($)':>12} {'Profit ($)':>12} {'Profit %':>10}")
    print("-" * 76)
    for r in results[:20]:
        print(f"{r['path']:<30} {r['product']:>10.6f} {r['end']:>12.4f} {r['profit']:>12.4f} {r['profit_pct']:>10.6f}")

    # Step 3: Bellman-Ford negative cycle detection
    print("\n--- Bellman-Ford Negative Cycle Detection ---")
    cycles = find_negative_cycles_bellman_ford(CURRENCIES, matrix)
    if cycles:
        print(f"Found {len(cycles)} negative cycle indicators:")
        for c in cycles[:10]:
            print(f"  Source: {c['source']}, Edge: {c['detected_at']}, Improvement: {c['improvement']:.8f}")
    else:
        print("No negative cycles detected (market is arbitrage-free at this snapshot)")

    # Step 4: Summary
    print("\n--- Summary ---")
    profitable = [r for r in results if r["profit"] > 0]
    if profitable:
        best = profitable[0]
        print(f"Best path: {best['path']}")
        print(f"  Product: {best['product']:.8f} (should be 1.0 if no arbitrage)")
        print(f"  Start: ${best['start']:,.2f}")
        print(f"  End:   ${best['end']:,.2f}")
        print(f"  Profit: ${best['profit']:,.4f} ({best['profit_pct']:.6f}%)")
        print(f"  Rates: {best['rates']}")

        print(f"\nTotal profitable paths: {len(profitable)} out of {len(results)}")
        total_range = max(r['profit_pct'] for r in results) - min(r['profit_pct'] for r in results)
        print(f"Profit range: {min(r['profit_pct'] for r in results):.6f}% to {max(r['profit_pct'] for r in results):.6f}%")
    else:
        print("No profitable triangular arbitrage paths found at current rates.")
        print("(This is expected for ECB daily rates — differentials exist at the tick level)")

if __name__ == "__main__":
    main()
