from data_loader import load_data
from portfolio_analysis import analyze_portfolio
from prediction import train_model, forecast
from simulation import run_scenario
from visualisation import plot_prices, plot_prediction, plot_scenario

def main():
    # 1. Daten laden
    tickers = ["AAPL", "MSFT", "GOOGL"]
    data = load_data(tickers, period="2y")

    # 2. Portfolio analysieren
    analysis_results = analyze_portfolio(data)
    print("Portfolioanalyse:")
    print(analysis_results)

    # 3. ML-Modell trainieren
    close_series = data["AAPL"]["Close"].squeeze()   # macht 1D
    model, X_test, y_test = train_model(close_series)
    pred = forecast(model, X_test)

    # 4. Marktszenario simulieren
    scenario = run_scenario(data, scenario_type="AI_BUBBLE")

    # 5. Visualisierung
    plot_prices(data)
    plot_prediction(y_test, pred)
    plot_scenario(scenario)

if __name__ == "__main__":
    main()