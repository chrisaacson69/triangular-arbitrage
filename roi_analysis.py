"""
ROI Analysis: Currency/Crypto Arbitrage
========================================
Compare actual infrastructure costs against expected returns
for three approaches: Traditional Forex, Centralized Crypto, DeFi On-Chain.

All figures sourced from 2025-2026 market research.
"""

def format_usd(amount):
    return f"${amount:,.2f}"

def annual_roi(annual_profit, total_investment):
    if total_investment == 0:
        return float('inf')
    return (annual_profit / total_investment) * 100

def months_to_breakeven(total_investment, monthly_profit):
    if monthly_profit <= 0:
        return float('inf')
    return total_investment / monthly_profit

def print_scenario(name, upfront, monthly_costs, monthly_revenue, notes):
    print(f"\n{'='*70}")
    print(f"  {name}")
    print(f"{'='*70}")

    annual_costs = monthly_costs * 12
    annual_revenue = monthly_revenue * 12
    annual_profit = annual_revenue - annual_costs
    total_first_year = upfront + annual_costs
    first_year_profit = annual_revenue - total_first_year
    roi = annual_roi(annual_profit, total_first_year) if first_year_profit != annual_profit else annual_roi(annual_profit, annual_costs)
    breakeven = months_to_breakeven(upfront, monthly_revenue - monthly_costs)

    print(f"\n  COSTS:")
    for label, amount in upfront.items() if isinstance(upfront, dict) else [("Upfront Total", upfront)]:
        pass

    print(f"  {'Upfront Investment:':<35} {format_usd(upfront):>15}")
    print(f"  {'Monthly Operating Costs:':<35} {format_usd(monthly_costs):>15}")
    print(f"  {'Annual Operating Costs:':<35} {format_usd(annual_costs):>15}")
    print(f"  {'Total First Year Cost:':<35} {format_usd(total_first_year):>15}")

    print(f"\n  REVENUE:")
    print(f"  {'Monthly Revenue (est):':<35} {format_usd(monthly_revenue):>15}")
    print(f"  {'Annual Revenue (est):':<35} {format_usd(annual_revenue):>15}")

    print(f"\n  PROFIT:")
    print(f"  {'Monthly Profit:':<35} {format_usd(monthly_revenue - monthly_costs):>15}")
    print(f"  {'First Year Profit:':<35} {format_usd(first_year_profit):>15}")
    print(f"  {'Annual Profit (year 2+):':<35} {format_usd(annual_profit):>15}")

    print(f"\n  ROI:")
    if breakeven < float('inf'):
        print(f"  {'Months to Break Even:':<35} {breakeven:>15.1f}")
    else:
        print(f"  {'Months to Break Even:':<35} {'NEVER':>15}")
    print(f"  {'First Year ROI:':<35} {(first_year_profit/total_first_year*100):>14.1f}%")
    if annual_costs > 0:
        print(f"  {'Ongoing Annual ROI:':<35} {(annual_profit/annual_costs*100):>14.1f}%")

    print(f"\n  NOTES:")
    for note in notes:
        print(f"  - {note}")

def main():
    print("=" * 70)
    print("  ARBITRAGE ROI ANALYSIS — REAL COST COMPARISON")
    print("=" * 70)
    print(f"\n  Based on research from 2025-2026 market data")
    print(f"  All revenue estimates are CONSERVATIVE scenarios")

    # =========================================================
    # SCENARIO 1: Traditional Forex (Institutional)
    # =========================================================
    # From our analysis: 0.07% per trade on $10K = $7
    # Institutional: tighter spreads, higher volume
    # Assume $100K capital, 10 trades/day, 0.03% net after spreads
    # Revenue: $100K * 0.0003 * 10 * 22 trading days = $6,600/month

    forex_upfront = 125000 + 10000  # License (Cayman) + FIX API min deposit
    forex_monthly = (
        1000    # FIX API access (mid-range)
        + 500   # VPS/co-location (budget Equinix)
        + 200   # Data feeds
        + 100   # Monitoring/infrastructure
    )
    # Conservative: $100K capital, 0.03% net per trade, 5 trades/day, 22 days
    forex_capital = 100000
    forex_net_per_trade = forex_capital * 0.0003  # $30 per trade after spreads
    forex_trades_per_day = 5
    forex_trading_days = 22
    forex_monthly_rev = forex_net_per_trade * forex_trades_per_day * forex_trading_days

    print_scenario(
        "SCENARIO 1: Traditional Forex (Institutional)",
        forex_upfront,
        forex_monthly,
        forex_monthly_rev,
        [
            f"Trading capital required: {format_usd(forex_capital)} (not included in upfront — it's working capital)",
            f"License: Cayman Islands ($125K min capital requirement)",
            f"FIX API: $300-$1,500/mo + $10K deposit (LMAX, similar)",
            f"Co-location: budget VPS near Equinix NY4/LD4 (~1ms latency)",
            f"Execution speed: <5ms via FIX API",
            f"Assumes 0.03% net profit per trade after spreads",
            f"5 opportunities per day (conservative for institutional)",
            f"RISK: Latency disadvantage vs HFT firms with dedicated hardware",
            f"RISK: License process takes ~3 months",
            f"RISK: Regulatory compliance ongoing costs not modeled",
        ]
    )

    # =========================================================
    # SCENARIO 2: Centralized Crypto Exchange Arbitrage
    # =========================================================
    # Cross-exchange: BTC on Exchange A vs Exchange B
    # Spreads wider than forex, opportunities last longer
    # But: withdrawal times, transfer fees, capital locked on each exchange

    crypto_cex_upfront = 0  # No license needed
    crypto_cex_monthly = (
        100     # Bot platform (Bitsgap/Cryptohopper mid-tier)
        + 50    # VPS hosting
        + 0     # Exchange API access (free with trading account)
    )
    # Need capital on EACH exchange (locked up)
    # Assume $10K across 3 exchanges, 0.05% net per arb, 3 trades/day
    crypto_cex_capital = 10000
    crypto_cex_net_per_trade = crypto_cex_capital * 0.0005  # $5 per trade
    crypto_cex_trades_per_day = 3
    crypto_cex_monthly_rev = crypto_cex_net_per_trade * crypto_cex_trades_per_day * 30

    print_scenario(
        "SCENARIO 2: Centralized Crypto (Cross-Exchange)",
        crypto_cex_upfront,
        crypto_cex_monthly,
        crypto_cex_monthly_rev,
        [
            f"Trading capital required: {format_usd(crypto_cex_capital)} split across exchanges",
            f"No license needed — retail access sufficient",
            f"Bot platforms: $23-$999/month (Bitsgap, Cryptohopper, WunderTrading)",
            f"Exchange APIs: free with account",
            f"Assumes 0.05% net per arb (wider spreads than forex)",
            f"3 opportunities per day across 3+ exchanges",
            f"RISK: Withdrawal/transfer time between exchanges (minutes to hours)",
            f"RISK: Capital locked on each exchange (counterparty risk)",
            f"RISK: Exchange rate can move during transfer",
            f"RISK: 86% of crypto trading already automated — competitive",
        ]
    )

    # =========================================================
    # SCENARIO 3: DeFi On-Chain (Solana)
    # =========================================================
    # Flash loans = borrow capital with no upfront (just gas)
    # Solana gas: $0.00025 per tx
    # Triangular arb across DEXes (Orca, Raydium, Jupiter)
    # MEV protection needed (Jito)

    defi_upfront = (
        500     # Smart contract development/audit
        + 100   # Initial SOL for gas
    )
    defi_monthly = (
        100     # Dedicated RPC node (Helius, QuickNode)
        + 50    # VPS hosting
        + 20    # Jito tips for MEV protection
    )
    # Flash loans: no capital needed, profit = arb minus gas + tip
    # Assume 10 successful arbs/day, $2 net each after gas/tips
    defi_monthly_rev = 10 * 2 * 30  # $600/month

    print_scenario(
        "SCENARIO 3: DeFi On-Chain (Solana + Flash Loans)",
        defi_upfront,
        defi_monthly,
        defi_monthly_rev,
        [
            f"NO trading capital needed — flash loans borrow and repay in same tx",
            f"Solana gas: ~$0.00025 per transaction",
            f"Smart contract: can be built with open-source templates (ExtropyIO, etc.)",
            f"RPC node: $100-200/mo for dedicated low-latency access",
            f"Jito tips: pay for MEV protection to avoid sandwich attacks",
            f"240,000+ successful DeFi arbs identified in 1 year ($868M volume)",
            f"Assumes 10 successful arbs/day at $2 net each (conservative)",
            f"RISK: Highly competitive — institutional MEV bots operate in ms",
            f"RISK: Smart contract bugs = total loss of borrowed funds",
            f"RISK: Flash loan transactions that don't profit simply revert (safe)",
            f"RISK: Solana network congestion during high-volume periods",
            f"UPSIDE: Failed trades cost almost nothing (reverted tx = just gas)",
        ]
    )

    # =========================================================
    # SCENARIO 4: DeFi On-Chain (Solana) — Optimistic
    # =========================================================
    defi_opt_upfront = 600
    defi_opt_monthly = 170
    # If we find a niche pair/pool with less competition: 20 arbs/day, $5 net
    defi_opt_monthly_rev = 20 * 5 * 30  # $3,000/month

    print_scenario(
        "SCENARIO 4: DeFi On-Chain (Solana) — Optimistic Niche",
        defi_opt_upfront,
        defi_opt_monthly,
        defi_opt_monthly_rev,
        [
            f"Same infrastructure as Scenario 3",
            f"Assumes discovery of less-competitive token pairs/pools",
            f"20 arbs/day at $5 net (niche pools with wider spreads)",
            f"This is the 'entrepreneur finds an underserved market' scenario",
            f"RISK: Niche pools have lower liquidity — may not sustain volume",
            f"RISK: Other bots discover the same niche quickly",
            f"UPSIDE: First-mover advantage in new token launches/pools",
        ]
    )

    # =========================================================
    # COMPARISON SUMMARY
    # =========================================================
    print(f"\n{'='*70}")
    print(f"  COMPARISON SUMMARY")
    print(f"{'='*70}")

    scenarios = [
        ("Forex Institutional",    forex_upfront, forex_monthly, forex_monthly_rev, forex_capital),
        ("Crypto CEX",             crypto_cex_upfront, crypto_cex_monthly, crypto_cex_monthly_rev, crypto_cex_capital),
        ("DeFi Solana (Conservative)", defi_upfront, defi_monthly, defi_monthly_rev, 0),
        ("DeFi Solana (Optimistic)",   defi_opt_upfront, defi_opt_monthly, defi_opt_monthly_rev, 0),
    ]

    print(f"\n  {'Scenario':<28} {'Upfront':>10} {'Monthly$':>10} {'Mo.Rev':>10} {'Mo.Profit':>10} {'Capital':>10} {'Breakeven':>10}")
    print(f"  {'-'*88}")
    for name, up, mc, mr, cap in scenarios:
        mp = mr - mc
        be = months_to_breakeven(up, mp) if mp > 0 else float('inf')
        be_str = f"{be:.1f}mo" if be < float('inf') else "NEVER"
        print(f"  {name:<28} {format_usd(up):>10} {format_usd(mc):>10} {format_usd(mr):>10} {format_usd(mp):>10} {format_usd(cap):>10} {be_str:>10}")

    print(f"\n  KEY INSIGHT:")
    print(f"  DeFi on Solana has the lowest barrier to entry by far.")
    print(f"  Flash loans eliminate the need for trading capital.")
    print(f"  Failed trades simply revert — you only pay gas (~$0.00025).")
    print(f"  The question is whether you can find profitable arbs in a")
    print(f"  market where 86% of trading is already automated.")

if __name__ == "__main__":
    main()
