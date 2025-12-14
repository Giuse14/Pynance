import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ============================================================
# =============== 1. MONTE-CARLO-SIMULATION ==================
# ============================================================

def simulate_correlated_gbm(price_df, weights, T_days=252, n_sims=5000, seed=None):
    """
    Simuliert zukünftige Portfolioverläufe mit einem
    korrelierten Geometric-Brownian-Motion-(GBM)-Modell.
    """
    ###############################
    #### Einführung Variablen: ####
    ###############################


    rng = np.random.default_rng(seed)                           # Generator Randomzahl  
    logret = np.log(price_df / price_df.shift(1)).dropna()      # Tägliche logarithmischen Renditen
    mu = np.minimum(logret.mean().values, 0.0003)               # Drift  - Schätzung = Begrenzung nach oben (Optimisusmus vermeiden)
    cov = logret.cov().values                                   # Kovarianzmatrix: enthält Volatilitäten und Korrelationen der Assets
    n_assets = price_df.shape[1]                                # Anzahl Assets
    n_steps = T_days                                            # Anzahl Handelstage in der Simulation
    S0 = price_df.iloc[-1].values.astype(float)                 # Letzte beobachtete Preise als Startwerte 
    L = np.linalg.cholesky(cov)                                 # Cholesky-Zerlegung, um Korrelationen zwischen Assets zu erzeugen
    sigma_sq = np.diag(cov) 
    drift = mu - 0.5 * sigma_sq # = μ - 0.5 * σ²                # Drift-Term der GBM = Geometric Brownian Motion
    asset_paths = np.empty((n_assets, n_steps + 1, n_sims))     # Speicher für simulierte Asset-Pfade
    asset_paths[:, 0, :] = S0[:, None]

    # Simulation der Asset-Preispfade
    for t in range(1, n_steps + 1):                             # Von Tag 1 bis Tag 252
        Z = rng.standard_normal((n_assets, n_sims))             # Unkorrelierte Standardnormal-Zufallszahlen
        correlated = L @ Z                                      # Einführung der Korrelationen

        asset_paths[:, t, :] = asset_paths[:, t - 1, :] * np.exp(drift[:, None] + correlated)   # GBM-Update-Gleichung "adjusted" 

    # Aggregation der einzelnen Assets zu Portfolio-Pfaden
    weights = np.array(weights)
    portfolio_paths = np.tensordot(asset_paths, weights, axes=(0, 0))

    # Berechnung der Endrenditen
    terminal_vals = portfolio_paths[-1]
    initial_vals = portfolio_paths[0]

    terminal_returns = terminal_vals / initial_vals - 1
    terminal_log_returns = np.log(terminal_vals / initial_vals)

    # Risikokennzahlen basierend auf Verlusten
    losses = -terminal_log_returns
    var95 = np.percentile(losses, 95)                           # Value at Risk (95 %)
    cvar95 = losses[losses >= var95].mean()                     # Conditional VaR (Expected Shortfall)

    # Zeitachse mit Handelstagen für die Plots
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
# =============== 2. VISUALISIERUNG (SPAGHETTI, FAN, HIST) ============
# =====================================================================

def plot_montecarlo_results(result, historical_prices, historical_dates, max_spaghetti=300):
    """
    Visualisierung der Monte-Carlo-Ergebnisse:
    - Spaghetti-Plot: einzelne Simulationspfade
    - Fan-Chart: Perzentilbänder (Risikoabschätzung)
    - Histogramm: Verteilung der Endrenditen
    """

    portfolio = result["portfolio_paths"]
    dates = result["dates"]
    terminal_returns = result["terminal_returns"]

    # Layout: grosser Plot oben, zwei kleinere unten
    fig = plt.figure(figsize=(14, 10))
    gs = fig.add_gridspec(2, 2, height_ratios=[2, 1], width_ratios=[3, 1])

    ax_spaghetti = fig.add_subplot(gs[0, :])
    ax_fan = fig.add_subplot(gs[1, 0])
    ax_hist = fig.add_subplot(gs[1, 1])

    # -------------------------------
    # 1) Spaghetti-Plot
    # -------------------------------

    # Historische Portfolioentwicklung
    ax_spaghetti.plot(
        historical_dates,
        historical_prices,
        linewidth=2.5,
        label="Historical Portfolio"
    )

    # Zufällige Auswahl von Pfaden, um Überlagerung zu vermeiden
    n_paths = min(max_spaghetti, portfolio.shape[1])
    idx = np.random.choice(portfolio.shape[1], n_paths, replace=False)

    for i in idx:
        ax_spaghetti.plot(dates, portfolio[:, i], linewidth=0.7, alpha=0.5)

    # Visuelle Trennung zwischen Vergangenheit und Zukunft
    ax_spaghetti.axvline(historical_dates[-1], linestyle="--", alpha=0.6)

    ax_spaghetti.set_title("Monte Carlo - Spaghetti Plot")
    ax_spaghetti.set_ylabel("Portfolio Value [USD]")
    ax_spaghetti.grid(alpha=0.3)
    ax_spaghetti.legend()

    # -------------------------------
    # 2) Fan-Chart
    # -------------------------------

    # Perzentile beschreiben die Verteilung über die Zeit
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
    # 3) Histogramm der Endrenditen
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
# =============== 3. BENUTZERFUNKTION =================================
# =====================================================================

def run_monte_carlo_simulation(price_df, weights):
    """
    High-Level-Funktion:
    Führt die Monte-Carlo-Simulation aus und zeigt
    numerische Ergebnisse sowie Grafiken an.
    """

    print("\n===== Monte Carlo Simulation =====")

    # Benutzerdefinierter Zeithorizont und Anzahl Simulationen
    years = int(input("How many years to simulate? (e.g. 1, 5, 10): ").strip())
    sims = int(input("How many simulations? (500–20000 recommended): ").strip())

    # Historische Portfoliozeitreihe zum Vergleich
    historical_prices = price_df.values @ np.array(weights)
    historical_dates = price_df.index

    days = years * 252  # Umrechnung Jahre -> Handelstage

    print(f"\nRunning Monte Carlo for {years} years with {sims} paths...")

    result = simulate_correlated_gbm(
        price_df=price_df,
        weights=weights,
        T_days=days,
        n_sims=sims,
        seed=42
    )

    # Zusammenfassung der Risikokennzahlen
    print("\nMonte Carlo Results:")
    print(f"95% VaR  (portfolio loss): {result['VaR_95']:.3f}")
    print(f"95% CVaR (expected shortfall): {result['CVaR_95']:.3f}")
    print(f"Probability of loss: {np.mean(result['terminal_returns'] < 0)*100:.2f}%")
    print(f"Median return: {np.median(result['terminal_returns'])*100:.2f}%")
    print(f"Best case return:  {np.max(result['terminal_returns'])*100:.2f}%")
    print(f"Worst case return: {np.min(result['terminal_returns'])*100:.2f}%")

    # Visualisierung der Ergebnisse
    plot_montecarlo_results(result, historical_prices, historical_dates)

    print("\nSimulation complete.\n")
