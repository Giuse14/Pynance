import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.gridspec import GridSpec

# def plot_prices(data):
#     """Zeigt Kursverläufe aller Aktien."""
#     plt.figure(figsize=(12, 6))
#     for t, df in data.items():
#         plt.plot(df["Close"], label=t)
#     plt.legend()
#     plt.title("Historische Kurse")
#     plt.xlabel("Datum")
#     plt.ylabel("Preis ($)")
#     plt.grid(True, alpha=0.3)
#     plt.tight_layout()
#     plt.show()

def plot_prediction(y_test, pred):
    """Zeigt echte vs vorhergesagte Preise."""
    plt.figure(figsize=(12, 6))
    plt.plot(y_test, label="Echt")
    plt.plot(pred, label="Vorhersage")
    plt.legend()
    plt.title("ML-Vorhersage")
    plt.xlabel("Zeit")
    plt.ylabel("Portfoliowert")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

def plot_scenario(scenario):
    """Zeigt simulierte Szenarien."""
    plt.figure(figsize=(12, 6))
    for t, df in scenario.items():
        plt.plot(df["Close"], label=f"{t} (Szenario)")
    plt.legend()
    plt.title("Simuliertes Marktszenario")
    plt.xlabel("Datum")
    plt.ylabel("Preis ($)")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

def plot_portfolio_analysis(analysis_results, tickers, weights):
    """Comprehensive portfolio analysis visualization"""
    
    # Create a figure with multiple subplots
    fig = plt.figure(figsize=(16, 12))
    gs = GridSpec(3, 3, figure=fig)
    
    # 1. Portfolio Composition (Pie Chart)
    ax1 = fig.add_subplot(gs[0, 0])
    colors = plt.cm.Set3(np.linspace(0, 1, len(tickers)))
    wedges, texts, autotexts = ax1.pie(weights, labels=tickers, autopct='%1.1f%%', 
                                      colors=colors, startangle=90)
    ax1.set_title('Portfolio Composition', fontweight='bold')
    
    # 2. Risk-Return Scatter (Individual Assets)
    ax2 = fig.add_subplot(gs[0, 1])
    individual_returns = analysis_results['components']['Individual Returns']
    individual_volatilities = analysis_results['components']['Individual Volatilities']
    
    for i, ticker in enumerate(tickers):
        ax2.scatter(individual_volatilities[ticker], individual_returns[ticker], 
                   s=100, alpha=0.7, label=ticker, color=colors[i])
        ax2.annotate(ticker, (individual_volatilities[ticker], individual_returns[ticker]),
                    xytext=(5, 5), textcoords='offset points', fontsize=9)
    
    # Add portfolio point
    port_return = analysis_results['basic_stats']['Annualized Return']
    port_vol = analysis_results['basic_stats']['Annualized Volatility']
    ax2.scatter(port_vol, port_return, s=200, marker='*', color='red', 
               label='Portfolio', edgecolors='black')
    ax2.annotate('Portfolio', (port_vol, port_return), xytext=(10, 10),
                textcoords='offset points', fontweight='bold', color='red')
    
    ax2.set_xlabel('Annualized Volatility')
    ax2.set_ylabel('Annualized Return')
    ax2.set_title('Risk-Return Profile', fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    
    # 3. Performance Metrics (Bar Chart)
    ax3 = fig.add_subplot(gs[0, 2])
    metrics = ['Sharpe Ratio', 'Sortino Ratio']
    values = [analysis_results['risk_adjusted']['Sharpe Ratio'], 
             analysis_results['risk_adjusted']['Sortino Ratio']]
    
    bars = ax3.bar(metrics, values, color=['skyblue', 'lightcoral'], alpha=0.7)
    ax3.set_ylabel('Ratio')
    ax3.set_title('Risk-Adjusted Returns', fontweight='bold')
    ax3.grid(True, alpha=0.3, axis='y')
    
    # Add value labels on bars
    for bar, value in zip(bars, values):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height,
                f'{value:.2f}', ha='center', va='bottom')
    
    # 4. Risk Metrics (Bar Chart)
    ax4 = fig.add_subplot(gs[1, 0])
    risk_metrics = ['Max Drawdown', 'VaR (95%)', 'CVaR (95%)']
    risk_values = [
        analysis_results['risk_metrics']['Max Drawdown'],
        analysis_results['risk_metrics']['Value at Risk (95%)'],
        analysis_results['risk_metrics']['Conditional VaR (95%)']
    ]
    
    risk_bars = ax4.bar(risk_metrics, risk_values, color=['lightyellow', 'lightpink', 'lightgreen'], alpha=0.7)
    ax4.set_ylabel('Percentage')
    ax4.set_title('Risk Metrics', fontweight='bold')
    ax4.grid(True, alpha=0.3, axis='y')
    
    # Add value labels
    for bar, value in zip(risk_bars, risk_values):
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height,
                f'{value:.2%}', ha='center', va='bottom')
    
    # 5. Correlation Heatmap
    ax5 = fig.add_subplot(gs[1, 1])
    corr_matrix = analysis_results['diversification']['Correlation Matrix']
    im = ax5.imshow(corr_matrix, cmap='coolwarm', vmin=-1, vmax=1, aspect='auto')
    
    # Set ticks and labels
    ax5.set_xticks(range(len(tickers)))
    ax5.set_yticks(range(len(tickers)))
    ax5.set_xticklabels(tickers, rotation=45)
    ax5.set_yticklabels(tickers)
    
    # Add correlation values as text
    for i in range(len(tickers)):
        for j in range(len(tickers)):
            ax5.text(j, i, f'{corr_matrix.iloc[i, j]:.2f}', 
                    ha='center', va='center', fontsize=8,
                    color='white' if abs(corr_matrix.iloc[i, j]) > 0.5 else 'black')
    
    ax5.set_title('Correlation Matrix', fontweight='bold')
    plt.colorbar(im, ax=ax5)
    
    # 6. Return Contribution vs Risk Contribution
    ax6 = fig.add_subplot(gs[1, 2])
    return_contrib = analysis_results['components']['Weight Contribution']
    risk_contrib = analysis_results['components']['Risk Contribution']
    
    x = np.arange(len(tickers))
    width = 0.35
    
    ax6.bar(x - width/2, return_contrib, width, label='Return Contribution', alpha=0.7, color='lightblue')
    ax6.bar(x + width/2, risk_contrib, width, label='Risk Contribution', alpha=0.7, color='lightcoral')
    
    ax6.set_xlabel('Assets')
    ax6.set_ylabel('Contribution')
    ax6.set_title('Return vs Risk Contribution', fontweight='bold')
    ax6.set_xticks(x)
    ax6.set_xticklabels(tickers, rotation=45)
    ax6.legend()
    ax6.grid(True, alpha=0.3, axis='y')
    
    # 7. Statistical Distribution Analysis
    ax7 = fig.add_subplot(gs[2, :])
    
    # Create some sample return data for distribution (in a real scenario, you'd use actual returns)
    sample_returns = np.random.normal(analysis_results['basic_stats']['Annualized Return'], 
                                     analysis_results['basic_stats']['Annualized Volatility'], 
                                     1000)
    
    ax7.hist(sample_returns, bins=50, density=True, alpha=0.7, color='lightgray', 
             label='Return Distribution')
    
    # Add vertical lines for key metrics
    ax7.axvline(analysis_results['basic_stats']['Annualized Return'], 
                color='red', linestyle='--', linewidth=2, label='Mean Return')
    ax7.axvline(analysis_results['risk_metrics']['Value at Risk (95%)'], 
                color='orange', linestyle='--', linewidth=2, label='VaR (95%)')
    
    ax7.set_xlabel('Returns')
    ax7.set_ylabel('Density')
    ax7.set_title('Return Distribution with Key Metrics', fontweight='bold')
    ax7.legend()
    ax7.grid(True, alpha=0.3)
    
    # Add some key statistics as text
    stats_text = f"Skewness: {analysis_results['statistical']['Skewness']:.2f}\n"
    stats_text += f"Kurtosis: {analysis_results['statistical']['Kurtosis']:.2f}\n"
    stats_text += f"Diversification Ratio: {analysis_results['diversification']['Diversification Ratio']:.2f}"
    
    ax7.text(0.02, 0.98, stats_text, transform=ax7.transAxes, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    plt.show()

# def plot_returns_over_time(data, weights):
#     """Plot cumulative returns over time for portfolio and individual assets"""
#     plt.figure(figsize=(12, 8))
    
#     # Calculate cumulative returns for each asset
#     for ticker, df in data.items():
#         returns = df['Close'].pct_change().dropna()
#         cumulative_returns = (1 + returns).cumprod() - 1
#         plt.plot(cumulative_returns.index, cumulative_returns.values, 
#                 label=ticker, alpha=0.7)
    
#     # Calculate portfolio cumulative returns
#     all_returns = []
#     for df in data.values():
#         ret = df["Close"].pct_change().dropna()
#         all_returns.append(ret)
    
#     returns_df = pd.concat(all_returns, axis=1)
#     returns_df.columns = data.keys()
#     portfolio_returns = returns_df.dot(weights)
#     portfolio_cumulative = (1 + portfolio_returns).cumprod() - 1
    
#     plt.plot(portfolio_cumulative.index, portfolio_cumulative.values, 
#             label='Portfolio', linewidth=3, color='black')
    
#     plt.title('Cumulative Returns Over Time', fontweight='bold')
#     plt.xlabel('Date')
#     plt.ylabel('Cumulative Return')
#     plt.legend()
#     plt.grid(True, alpha=0.3)
#     plt.tight_layout()
#     plt.show()

def plot_drawdown(data, weights):
    """Plot portfolio drawdown over time"""
    plt.figure(figsize=(12, 6))
    
    # Calculate portfolio returns
    all_returns = []
    for df in data.values():
        ret = df["Close"].pct_change().dropna()
        all_returns.append(ret)
    
    returns_df = pd.concat(all_returns, axis=1)
    returns_df.columns = data.keys()
    portfolio_returns = returns_df.dot(weights)
    
    # Calculate drawdown
    cumulative_returns = (1 + portfolio_returns).cumprod()
    running_max = cumulative_returns.expanding().max()
    drawdown = (cumulative_returns - running_max) / running_max
    
    plt.fill_between(drawdown.index, drawdown.values, 0, alpha=0.3, color='red')
    plt.plot(drawdown.index, drawdown.values, color='red', linewidth=1)
    plt.title('Portfolio Drawdown Over Time', fontweight='bold')
    plt.xlabel('Date')
    plt.ylabel('Drawdown')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

def interactive_toggle_plot(data, weights=None):
    """Interactive toggle between PRICE mode and RETURN mode.
       FIXED: Portfolio PRICE is shown in price mode (non-normalized).
    """

    fig, ax = plt.subplots(figsize=(12, 6))
    mode = "price"

    # Build DataFrame of asset prices
    price_df = pd.concat([df["Close"] for df in data.values()], axis=1)
    price_df.columns = data.keys()

    # Daily returns
    returns_df = price_df.pct_change().dropna()

    # --- PORTFOLIO PRICE (REAL, NOT NORMALIZED) ---
    if weights is not None:
        weights = np.array(weights)

        # Weighted portfolio value:
        # portfolio_price[t] = sum_i( weight_i * price_i[t] )
        portfolio_price = price_df.mul(weights, axis=1).sum(axis=1)

        # Portfolio returns (needed only for the return plot)
        portfolio_returns = returns_df.dot(weights)

    # ------------------------------------------------------------
    # PRICE PLOT (real prices, non-normalized)
    # ------------------------------------------------------------
    def plot_price():
        ax.clear()

        # Plot asset prices
        for ticker in price_df.columns:
            ax.plot(price_df.index, price_df[ticker], label=ticker)

        # Plot real portfolio price
        if weights is not None:
            ax.plot(portfolio_price.index,
                    portfolio_price.values,
                    label="Portfolio",
                    color="black",
                    linewidth=3)

        ax.set_title("Historical Prices (Real, Not Normalized)")
        ax.set_xlabel("Date")
        ax.set_ylabel("Price [$]")
        ax.grid(True, alpha=0.3)
        ax.legend()
        fig.canvas.draw_idle()

    # ------------------------------------------------------------
    # RETURN PLOT (cumulative returns)
    # ------------------------------------------------------------
    def plot_return():
        ax.clear()

        # Plot each asset's cumulative return
        for ticker in returns_df.columns:
            cum = (1 + returns_df[ticker]).cumprod() - 1
            ax.plot(cum.index, cum.values, label=ticker)

        # Plot portfolio cumulative returns
        if weights is not None:
            cum_port = (1 + portfolio_returns).cumprod() - 1
            ax.plot(cum_port.index,
                    cum_port.values,
                    label="Portfolio",
                    color="black",
                    linewidth=3)

        ax.set_title("Cumulative Returns Over Time")
        ax.set_xlabel("Date")
        ax.set_ylabel("Cumulative Return [%]")
        ax.grid(True, alpha=0.3)
        ax.legend()
        fig.canvas.draw_idle()

    # ------------------------------------------------------------
    # INITIAL PLOT
    # ------------------------------------------------------------
    plot_price()

    # ------------------------------------------------------------
    # KEYBOARD EVENT
    # ------------------------------------------------------------
    def on_key(event):
        nonlocal mode
        if event.key == "h":
            mode = "price"
            plot_price()
        elif event.key == "r":
            mode = "return"
            plot_return()

    fig.canvas.mpl_connect("key_press_event", on_key)

    print("\nInteractive Plot Controls:")
    print("Press 'h' → Historical Prices (REAL)")
    print("Press 'r' → Cumulative Returns")

    plt.show()
