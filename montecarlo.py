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
    mu = logret.mean().values
    cov = logret.cov().values

    n_assets = price_df.shape[1]
    dt = 1 / 252  # daily timestep
    n_steps = T_days

    # starting price vector
    S0 = price_df.iloc[-1].values.astype(float)

    # Cholesky for correlation
    L = np.linalg.cholesky(cov)

    sigma_sq = np.diag(cov)
    drift = (mu - 0.5 * sigma_sq) * dt
    sqrt_dt = np.sqrt(dt)

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

def plot_montecarlo_results(result):
    """Plot fan chart and terminal return histogram."""

    portfolio = result["portfolio_paths"]
    dates = result["dates"]

    fig, ax = plt.subplots(1, 2, figsize=(14, 5), gridspec_kw={'width_ratios': [3, 1]})

    # ----- Left plot: Fan chart -----
    fan_ax = ax[0]

    percentiles = [5, 25, 50, 75, 95]
    perc = np.percentile(portfolio, percentiles, axis=1)

    # Percentile bands shading
    fan_ax.fill_between(dates, perc[0], perc[-1], color="lightgray", alpha=0.5, label="5%–95% band")
    fan_ax.fill_between(dates, perc[1], perc[-2], color="gray", alpha=0.6, label="25%–75% band")

    # Median line
    fan_ax.plot(dates, perc[2], color="black", linewidth=2, label="Median")

    fan_ax.set_title("Monte Carlo Portfolio Simulation")
    fan_ax.set_xlabel("Date")
    fan_ax.set_ylabel("Portfolio Value")
    fan_ax.grid(alpha=0.3)
    fan_ax.legend()

    # ----- Right plot: Terminal returns -----
    hist_ax = ax[1]
    terminal_returns = result["terminal_returns"]

    hist_ax.hist(terminal_returns, bins=30, density=True, color="steelblue", alpha=0.7)
    hist_ax.set_title("Terminal Return Distribution")
    hist_ax.set_xlabel("Return")
    hist_ax.grid(alpha=0.3)

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

    # Plot everything
    plot_montecarlo_results(result)

    print("\nSimulation complete.\n")
