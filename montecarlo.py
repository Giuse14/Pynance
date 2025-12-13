import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# =====================================================================
# =============== 1. CORE MONTE CARLO SIMULATION ======================
# =====================================================================

def simulate_correlated_gbm(price_df, weights, T_days=252, n_sims=5000, seed=None):
    """Run correlated GBM Monte Carlo simulations on portfolio assets."""

    rng = np.random.default_rng(seed)

    # ----- 1) Estimate parameters from historical log returns -----
    logret = np.log(price_df / price_df.shift(1)).dropna()
    mu = np.minimum(logret.mean().values, 0.0003)  # cap optimism
    cov = logret.cov().values

    n_assets = price_df.shape[1]
    dt = 1
    n_steps = T_days

    # starting price vector
    S0 = price_df.iloc[-1].values.astype(float)

    # Cholesky for correlation
    L = np.linalg.cholesky(cov)

    sigma_sq = np.diag(cov)
    drift = mu - 0.5 * sigma_sq
    sqrt_dt = 1.0

    # shape: (assets, time, sims)
    asset_paths = np.empty((n_assets, n_steps + 1, n_sims))
    asset_paths[:, 0, :] = S0[:, None]

    for t in range(1, n_steps + 1):
        Z = rng.standard_normal((n_assets, n_sims))
        correlated = L @ Z
        increment = drift[:, None] + correlated * sqrt_dt
        asset_paths[:, t, :] = asset_paths[:, t - 1, :] * np.exp(increment)

    # ----- 2) Portfolio paths -----
    weights = np.array(weights)
    portfolio_paths = np.tensordot(asset_paths, weights, axes=(0, 0))

    # ----- 3) Derived statistics -----
    terminal_vals = portfolio_paths[-1]
    initial_vals = portfolio_paths[0]
    terminal_returns = terminal_vals / initial_vals - 1


    # VaR / CVaR at 95%
    losses = -terminal_returns
    var95 = np.percentile(losses, 95)
    cvar95 = losses[losses >= var95].mean()

    # Time index
    last_date = price_df.index[-1]
    sim_dates = pd.bdate_range(start=last_date, periods=n_steps + 1)

    return {
        "asset_paths": asset_paths,
        "portfolio_paths": portfolio_paths,
        "terminal_returns": terminal_returns,
        "VaR_95": var95,
        "CVaR_95": cvar95,
        "dates": sim_dates,
    }


# =====================================================================
# =============== 2. PLOTTING (FAN CHART + HISTOGRAM) =================
# =====================================================================

def plot_montecarlo_results(result, historical_prices, historical_dates, max_spaghetti=300):
    """
    Plot:
    1) Spaghetti chart (history + future paths)
    2) Fan chart
    3) Terminal return histogram
    """

    portfolio = result["portfolio_paths"]
    dates = result["dates"]
    terminal_returns = result["terminal_returns"]
    best_return = np.max(result["terminal_returns"])
    worst_return = np.min(result["terminal_returns"])


    # --- Figure layout ---
    fig = plt.figure(figsize=(14, 10))
    gs = fig.add_gridspec(2, 2, height_ratios=[2, 1], width_ratios=[3, 1])

    ax_spaghetti = fig.add_subplot(gs[0, :])
    ax_fan = fig.add_subplot(gs[1, 0])
    ax_hist = fig.add_subplot(gs[1, 1])

    # ======================================================
    # 1) Spaghetti chart
    # ======================================================

    ax_spaghetti.plot(
        historical_dates,
        historical_prices,
        linewidth=2.5,
        label="Historical Portfolio"
    )

    # Limit number of paths for readability
    n_paths = min(max_spaghetti, portfolio.shape[1])
    idx = np.random.choice(portfolio.shape[1], n_paths, replace=False)

    for i in idx:
        ax_spaghetti.plot(
            dates,
            portfolio[:, i],
            linewidth=0.7,
            alpha=0.5
        )

    ax_spaghetti.axvline(historical_dates[-1], linestyle="--", alpha=0.6)
    ax_spaghetti.set_title("Monte Carlo Spaghetti Plot")
    ax_spaghetti.set_ylabel("Portfolio Value [USD]")
    ax_spaghetti.grid(alpha=0.3)
    ax_spaghetti.legend()

    # ======================================================
    # 2) Fan chart
    # ======================================================

    percentiles = [5, 25, 50, 75, 95]
    perc = np.percentile(portfolio, percentiles, axis=1)

    ax_fan.fill_between(dates, perc[0], perc[-1], alpha=0.3, label="5–95%")
    ax_fan.fill_between(dates, perc[1], perc[-2], alpha=0.5, label="25–75%")
    ax_fan.plot(dates, perc[2], linewidth=2, label="Median")

    ax_fan.set_title("Monte Carlo - Fan Chart")
    ax_fan.set_ylabel("Portfolio Value [USD]")
    ax_fan.grid(alpha=0.3)
    ax_fan.legend()

    # ======================================================
    # 3) Terminal return histogram
    # ======================================================

    ax_hist.hist(terminal_returns, bins=30, density=True, alpha=0.7)
    ax_hist.axvline(np.percentile(terminal_returns, 5), linestyle="--", label="5% quantile")
    ax_hist.set_title("Terminal Return Distribution")
    ax_hist.set_xlabel("Return")
    ax_hist.grid(alpha=0.3)
    ax_hist.legend()

    plt.tight_layout()
    plt.show()



# =====================================================================
# =============== 3. USER-FACING FUNCTION (CALL FROM MAIN) ============
# =====================================================================

def run_monte_carlo_simulation(price_df, weights):
    """High-level: Ask user for settings, run MC, show results."""

    print("\n===== Monte Carlo Simulation =====")
    
    # Ask user how far to simulate
    years = int(input("How many years to simulate? (e.g. 1, 5, 10): ").strip())
    sims = int(input("How many simulations? (500–20000 recommended): ").strip())

    historical_prices = price_df.values @ np.array(weights)
    historical_dates = price_df.index

    days = years * 252

    print(f"\nRunning Monte Carlo for {years} years with {sims} paths...")

    result = simulate_correlated_gbm(
        price_df=price_df,
        weights=weights,
        T_days=days,
        n_sims=sims,
        seed=42
    )

    # Print results
    print("\nMonte Carlo Results:")
    print(f"95% VaR  (portfolio loss): {result['VaR_95']:.3f}")
    print(f"95% CVaR (expected shortfall): {result['CVaR_95']:.3f}")
    print(f"Probability of loss: {np.mean(result['terminal_returns'] < 0)*100:.2f}%")
    print(f"Best case return:  {np.max(result["terminal_returns"])*100:.2f}%")
    print(f"Worst case return: {np.min(result["terminal_returns"])*100:.2f}%")


    # Plot everything
    plot_montecarlo_results(result, historical_prices, historical_dates)

    print("\nSimulation complete.\n")
