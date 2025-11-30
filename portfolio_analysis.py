# portfolio_analysis.py (complete version)
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from asset_database import get_asset_info, get_portfolio_allocation

def analyze_portfolio(data, weights, risk_free_rate=0.02):
    """
    Enhanced portfolio analysis with asset class information
    """
    analysis_results = {}
    
    # Calculate daily returns
    all_returns = []
    tickers = list(data.keys())
    
    for ticker in tickers:
        df = data[ticker]
        returns = df["Close"].pct_change().dropna()
        all_returns.append(returns)
    
    returns_df = pd.concat(all_returns, axis=1)
    returns_df.columns = tickers
    
    # Portfolio returns (weighted)
    weights_array = np.array(weights)
    portfolio_returns = returns_df.dot(weights_array)
    
    # Basic Statistics
    analysis_results['basic_stats'] = {
        'Total Return': (portfolio_returns + 1).prod() - 1,
        'Annualized Return': portfolio_returns.mean() * 252,
        'Annualized Volatility': portfolio_returns.std() * np.sqrt(252),
        'Cumulative Return': (1 + portfolio_returns).cumprod() - 1
    }
    
    # Risk-Adjusted Returns
    analysis_results['risk_adjusted'] = {
        'Sharpe Ratio': (portfolio_returns.mean() * 252 - risk_free_rate) / 
                        (portfolio_returns.std() * np.sqrt(252)),
        'Sortino Ratio': calculate_sortino_ratio(portfolio_returns, risk_free_rate),
        'Calmar Ratio': calculate_calmar_ratio(portfolio_returns)
    }
    
    # Risk Metrics
    analysis_results['risk_metrics'] = {
        'Max Drawdown': calculate_max_drawdown(portfolio_returns),
        'Value at Risk (95%)': calculate_var(portfolio_returns),
        'Conditional VaR (95%)': calculate_cvar(portfolio_returns),
        'Beta': calculate_portfolio_beta(returns_df, weights_array)
    }
    
    # Asset Allocation Analysis
    analysis_results['allocation'] = {
        'By Category': get_portfolio_allocation(tickers, weights),
        'Asset Details': {ticker: get_asset_info(ticker) for ticker in tickers}
    }
    
    # Statistical Analysis
    analysis_results['statistical'] = {
        'Skewness': portfolio_returns.skew(),
        'Kurtosis': portfolio_returns.kurtosis(),
        'Jarque-Bera Test': stats.jarque_bera(portfolio_returns.dropna())[1]  # p-value
    }
    
    # Diversification Analysis
    analysis_results['diversification'] = {
        'Portfolio Variance': calculate_portfolio_variance(returns_df, weights_array),
        'Diversification Ratio': calculate_diversification_ratio(returns_df, weights_array),
        'Correlation Matrix': returns_df.corr()
    }
    
    # Component Analysis
    analysis_results['components'] = {
        'Individual Returns': returns_df.mean() * 252,
        'Individual Volatilities': returns_df.std() * np.sqrt(252),
        'Weight Contribution': calculate_weight_contributions(returns_df, weights_array),
        'Risk Contribution': calculate_risk_contributions(returns_df, weights_array)
    }
    
    return analysis_results

# ========== HELPER FUNCTION DEFINITIONS ==========

def calculate_sortino_ratio(returns, risk_free_rate):
    """Calculate Sortino ratio (only downside risk)"""
    downside_returns = returns[returns < 0]
    if len(downside_returns) == 0:
        return np.nan
    downside_risk = downside_returns.std() * np.sqrt(252)
    excess_return = returns.mean() * 252 - risk_free_rate
    return excess_return / downside_risk if downside_risk != 0 else np.nan

def calculate_calmar_ratio(returns):
    """Calculate Calmar ratio (return vs max drawdown)"""
    max_dd = calculate_max_drawdown(returns)
    annual_return = returns.mean() * 252
    return annual_return / abs(max_dd) if max_dd != 0 else np.nan

def calculate_max_drawdown(returns):
    """Calculate maximum drawdown"""
    cumulative = (1 + returns).cumprod()
    running_max = cumulative.expanding().max()
    drawdown = (cumulative - running_max) / running_max
    return drawdown.min()

def calculate_var(returns, confidence_level=0.05):
    """Calculate Value at Risk"""
    return np.percentile(returns, confidence_level * 100)

def calculate_cvar(returns, confidence_level=0.05):
    """Calculate Conditional Value at Risk (Expected Shortfall)"""
    var = calculate_var(returns, confidence_level)
    return returns[returns <= var].mean()

def calculate_portfolio_beta(returns_df, weights):
    """Calculate portfolio beta relative to market (using SPY as proxy)"""
    try:
        # If SPY is in the portfolio, use it as market proxy
        if 'SPY' in returns_df.columns:
            market_returns = returns_df['SPY']
        else:
            # Use average of all assets as market proxy (simplification)
            market_returns = returns_df.mean(axis=1)
        
        portfolio_returns = returns_df.dot(weights)
        covariance = portfolio_returns.cov(market_returns)
        market_variance = market_returns.var()
        return covariance / market_variance if market_variance != 0 else np.nan
    except:
        return np.nan

def calculate_portfolio_variance(returns_df, weights):
    """Calculate portfolio variance"""
    cov_matrix = returns_df.cov()
    return np.dot(weights.T, np.dot(cov_matrix, weights))

def calculate_diversification_ratio(returns_df, weights):
    """Calculate diversification ratio"""
    weighted_vol = np.sum(weights * returns_df.std())
    portfolio_vol = np.sqrt(calculate_portfolio_variance(returns_df, weights))
    return weighted_vol / portfolio_vol if portfolio_vol != 0 else np.nan

def calculate_weight_contributions(returns_df, weights):
    """Calculate contribution of each asset to portfolio return"""
    individual_returns = returns_df.mean() * 252
    return weights * individual_returns

def calculate_risk_contributions(returns_df, weights):
    """Calculate risk contribution of each asset"""
    cov_matrix = returns_df.cov()
    portfolio_vol = np.sqrt(calculate_portfolio_variance(returns_df, weights))
    marginal_contributions = np.dot(cov_matrix, weights)
    return (weights * marginal_contributions) / portfolio_vol if portfolio_vol != 0 else np.nan

def generate_analysis_report(analysis_results, tickers, weights):
    """Generate a comprehensive text report of the analysis"""
    report = []
    
    # Basic Stats
    basic = analysis_results['basic_stats']
    report.append("=" * 60)
    report.append("PORTFOLIO ANALYSIS REPORT")
    report.append("=" * 60)
    report.append(f"Total Return: {basic['Total Return']:.2%}")
    report.append(f"Annualized Return: {basic['Annualized Return']:.2%}")
    report.append(f"Annualized Volatility: {basic['Annualized Volatility']:.2%}")
    
    # Asset Allocation
    allocation = analysis_results['allocation']['By Category']
    report.append("\n--- ASSET ALLOCATION ---")
    for category, weight in sorted(allocation.items(), key=lambda x: x[1], reverse=True):
        report.append(f"{category}: {weight:.1%}")
    
    # Risk-Adjusted Returns
    risk_adj = analysis_results['risk_adjusted']
    report.append("\n--- RISK-ADJUSTED RETURNS ---")
    report.append(f"Sharpe Ratio: {risk_adj['Sharpe Ratio']:.2f}")
    report.append(f"Sortino Ratio: {risk_adj['Sortino Ratio']:.2f}")
    report.append(f"Calmar Ratio: {risk_adj['Calmar Ratio']:.2f}")
    
    # Risk Metrics
    risk = analysis_results['risk_metrics']
    report.append("\n--- RISK METRICS ---")
    report.append(f"Max Drawdown: {risk['Max Drawdown']:.2%}")
    report.append(f"Value at Risk (95%): {risk['Value at Risk (95%)']:.2%}")
    report.append(f"Conditional VaR (95%): {risk['Conditional VaR (95%)']:.2%}")
    report.append(f"Portfolio Beta: {risk['Beta']:.2f}")
    
    # Statistical Analysis
    stats = analysis_results['statistical']
    report.append("\n--- STATISTICAL ANALYSIS ---")
    report.append(f"Skewness: {stats['Skewness']:.2f}")
    report.append(f"Kurtosis: {stats['Kurtosis']:.2f}")
    report.append(f"Normality (Jarque-Bera p-value): {stats['Jarque-Bera Test']:.3f}")
    
    # Diversification
    divers = analysis_results['diversification']
    report.append("\n--- DIVERSIFICATION ---")
    report.append(f"Portfolio Variance: {divers['Portfolio Variance']:.6f}")
    report.append(f"Diversification Ratio: {divers['Diversification Ratio']:.2f}")
    
    # Component Analysis
    report.append("\n--- COMPONENT ANALYSIS ---")
    for i, ticker in enumerate(tickers):
        asset_info = analysis_results['allocation']['Asset Details'][ticker]
        report.append(f"{ticker} ({asset_info['type']}): {weights[i]:.1%} weight | "
                     f"Return: {analysis_results['components']['Individual Returns'][ticker]:.2%} | "
                     f"Vol: {analysis_results['components']['Individual Volatilities'][ticker]:.2%}")
    
    ###### CSV EXPORT

    csv_rows = []
    individual_returns = analysis_results['components']['Individual Returns']
    individual_vols = analysis_results['components']['Individual Volatilities']
    weight_contrib = analysis_results['components']['Weight Contribution']
    risk_contrib = analysis_results['components']['Risk Contribution']

    for i, ticker in enumerate(tickers):
        csv_rows.append({
            "Wertpapier": ticker,
            "Gewichtung": weights[i],
            "Annualisierte Rendite": individual_returns[ticker],
            "Annualisierte Volatilität": individual_vols[ticker],
            "Renditebeitrag": weight_contrib[i],
            "Risikobeitrag": risk_contrib[i]
        })

    df_export = pd.DataFrame(csv_rows)
    df_export.to_csv("portfolio_analyse_zusammenfassung.csv", index=False)
    
    return "\n".join(report)

def plot_asset_allocation(analysis_results, tickers, weights):
    """Plot asset allocation by category"""
    allocation = analysis_results['allocation']['By Category']
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Pie chart by category
    colors = plt.cm.Set3(np.linspace(0, 1, len(allocation)))
    wedges, texts, autotexts = ax1.pie(allocation.values(), labels=allocation.keys(), 
                                      autopct='%1.1f%%', colors=colors, startangle=90)
    ax1.set_title('Asset Allocation by Category', fontweight='bold')
    
    # Bar chart by individual assets
    asset_types = {}
    for i, ticker in enumerate(tickers):
        asset_info = analysis_results['allocation']['Asset Details'][ticker]
        asset_type = asset_info['type']
        if asset_type not in asset_types:
            asset_types[asset_type] = 0
        asset_types[asset_type] += weights[i]
    
    ax2.bar(asset_types.keys(), asset_types.values(), color=colors[:len(asset_types)])
    ax2.set_title('Asset Allocation by Type', fontweight='bold')
    ax2.set_ylabel('Weight')
    plt.xticks(rotation=45, ha='right')
    
    plt.tight_layout()
    plt.show()