import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# =====================================================================
# =============== 1. CORE MONTE CARLO SIMULATION ======================
# =====================================================================

def simulate_correlated_gbm(price_df, weights, T_days=252, n_sims=5000, seed=None):
    """
    Simulate future portfolio values using a correlated
    Geometric Brownian Motion (GBM) model.
    """

    # Random number generator for reproducibility
    rng = np.random.default_rng(seed)

    # Compute daily log-returns from historical prices
    logret = np.log(price_df / price_df.shift(1)).dropna()

    # Estimate drift and cap it to avoid unrealistically optimistic growth
    mu = np.minimum(logret.mean().values, 0.0003)

    # Covariance captures volatility and correlation between assets
    cov = logret.cov().values

    n_assets = price_df.shape[1]
    n_steps = T_days  # number of trading days to simulate

    # Last observed prices are used as starting point
    S0 = price_df.iloc[-1].values.astype(float)

    # Cholesky decomposition to introduce asset correlations
    L = np.linalg.cholesky(cov)

    # GBM drift term (Ito correction included)
    sigma_sq = np.diag(cov)
    drift = mu - 0.5 * sigma_sq

    # Preallocate array for efficiency
    asset_paths = np.empty((n_assets, n_steps + 1, n_sims))
    asset_paths[:, 0, :] = S0[:, None]

    # Simulate asset price paths
    for t in range(1, n_steps + 1):
        Z = rng.standard_normal((n_assets, n_sims))
        correlated = L @ Z
        asset_paths[:, t, :] = asset_paths[:, t - 1, :] * np.exp(drift[:, None] + correlated)

    # Aggregate asset paths into portfolio paths
    weights = np.array(weights)
    portfolio_paths = np.tensordot(asset_paths, weights, axes=(0, 0))

    # Compute terminal portfolio returns
    terminal_vals = portfolio_paths[-1]
    initial_vals = portfolio_paths[0]
    terminal_returns = terminal_vals / initial_vals - 1
    terminal_log_returns = np.log(terminal_vals / initial_vals)

    # Risk metrics based on terminal losses
    losses = -terminal_log_returns
    var95 = np.percentile(losses, 95)
    cvar95 = losses[losses >= var95].mean()


    # Business-day time index for plotting
    last_date = price_df.index[-1]
    sim_dates = pd.bdate_range(start=last_date, periods=n_steps + 1)

    return {
        "asset_paths": asset_paths,
        "portfolio_paths": portfolio_paths,
        "terminal_log_returns": terminal_log_returns,
        "terminal_returns": terminal_returns,
        "VaR_95": var95,
        "CVaR_95": cvar95,
        "dates": sim_dates,
    }


# =====================================================================
# =============== 2. PLOTTING (SPAGHETTI + FAN + HIST) =================
# =====================================================================

def plot_montecarlo_results(result, historical_prices, historical_dates, max_spaghetti=300):
    """
    Visualize Monte Carlo results using:
    - Spaghetti plot for path intuition
    - Fan chart for risk bands
    - Histogram for terminal outcomes
    """

    portfolio = result["portfolio_paths"]
    dates = result["dates"]
    terminal_returns = result["terminal_returns"]

    # Figure layout: large top plot, two smaller bottom plots
    fig = plt.figure(figsize=(14, 10))
    gs = fig.add_gridspec(2, 2, height_ratios=[2, 1], width_ratios=[3, 1])

    ax_spaghetti = fig.add_subplot(gs[0, :])
    ax_fan = fig.add_subplot(gs[1, 0])
    ax_hist = fig.add_subplot(gs[1, 1])

    # -------------------------------
    # 1) Spaghetti plot
    # -------------------------------

    # Plot historical portfolio performance
    ax_spaghetti.plot(
        historical_dates,
        historical_prices,
        linewidth=2.5,
        label="Historical Portfolio"
    )

    # Randomly select paths to avoid overplotting
    n_paths = min(max_spaghetti, portfolio.shape[1])
    idx = np.random.choice(portfolio.shape[1], n_paths, replace=False)

    for i in idx:
        ax_spaghetti.plot(dates, portfolio[:, i], linewidth=0.7, alpha=0.5)

    # Visual separation between past and future
    ax_spaghetti.axvline(historical_dates[-1], linestyle="--", alpha=0.6)

    ax_spaghetti.set_title("Monte Carlo Spaghetti Plot")
    ax_spaghetti.set_ylabel("Portfolio Value [USD]")
    ax_spaghetti.grid(alpha=0.3)
    ax_spaghetti.legend()

    # -------------------------------
    # 2) Fan chart
    # -------------------------------

    # Percentile bands summarize distribution over time
    percentiles = [5, 25, 50, 75, 95]
    perc = np.percentile(portfolio, percentiles, axis=1)

    ax_fan.fill_between(dates, perc[0], perc[-1], alpha=0.3, label="5–95%")
    ax_fan.fill_between(dates, perc[1], perc[-2], alpha=0.5, label="25–75%")
    ax_fan.plot(dates, perc[2], linewidth=2, label="Median")

    ax_fan.set_title("Monte Carlo – Fan Chart")
    ax_fan.set_ylabel("Portfolio Value [USD]")
    ax_fan.grid(alpha=0.3)
    ax_fan.legend()

    # -------------------------------
    # 3) Terminal return histogram
    # -------------------------------

    ax_hist.hist(result["terminal_log_returns"], bins=40, label="Simulated outcomes")
    ax_hist.set_xlabel("Log return")
    ax_hist.set_ylabel("Number of simulations")
    ax_hist.set_title("Terminal Log-Return Distribution")

    ax_hist.grid(alpha=0.3)
    ax_hist.legend()

    plt.tight_layout()
    plt.show()


# =====================================================================
# =============== 3. USER-FACING FUNCTION =============================
# =====================================================================

def run_monte_carlo_simulation(price_df, weights):
    """
    High-level function that runs the Monte Carlo simulation
    and presents numerical and visual results.
    """

    print("\n===== Monte Carlo Simulation =====")

    # User-defined simulation horizon and number of paths
    years = int(input("How many years to simulate? (e.g. 1, 5, 10): ").strip())
    sims = int(input("How many simulations? (500–20000 recommended): ").strip())

    # Historical portfolio series for comparison with simulations
    historical_prices = price_df.values @ np.array(weights)
    historical_dates = price_df.index

    days = years * 252  # convert years to trading days

    print(f"\nRunning Monte Carlo for {years} years with {sims} paths...")

    result = simulate_correlated_gbm(
        price_df=price_df,
        weights=weights,
        T_days=days,
        n_sims=sims,
        seed=42
    )

    # Summary risk metrics
    print("\nMonte Carlo Results:")
    print(f"95% VaR  (portfolio loss): {result['VaR_95']:.3f}")
    print(f"95% CVaR (expected shortfall): {result['CVaR_95']:.3f}")
    print(f"Probability of loss: {np.mean(result['terminal_returns'] < 0)*100:.2f}%")
    print(f"Median return: {np.median(result['terminal_returns'])*100:.2f}%")
    print(f"Best case return:  {np.max(result['terminal_returns'])*100:.2f}%")
    print(f"Worst case return: {np.min(result['terminal_returns'])*100:.2f}%")

    # Visualize simulation results
    plot_montecarlo_results(result, historical_prices, historical_dates)

    print("\nSimulation complete.\n")
