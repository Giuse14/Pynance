from data_loader import load_data
from portfolio_analysis import analyze_portfolio
from prediction import train_model, forecast
from simulation import run_scenario
from visualisation import plot_prices, plot_prediction, plot_scenario
from get_user_portfolio import get_user_portfolio
from portfolio_builder import build_portfolio_series
from gui_portfolio_selector import select_portfolio_gui


def main():
    data = None
    tickers = None
    weights = None
    portfolio_series = None
    model = None
    X_test = None
    y_test = None
    pred = None
    scenario = None

    while True:
        print("\n========== PORTFOLIO MANAGER ==========")
        print("1) Load portfolio & market data")
        print("2) Analyze portfolio")
        print("3) Train & Forecast model")
        print("4) Forecast future prices")
        print("5) Plot price history")
        print("6) Exit")
        print("========================================")

        choice = input("Choose an option (1-6): ").strip()

        # --------------------------------------------------------
        # 1) Load portfolio
        # --------------------------------------------------------
        if choice == "1":
            # tickers, weights = get_user_portfolio()
            tickers, weights = select_portfolio_gui()
            data = load_data(tickers, period="2y")
            portfolio_series = build_portfolio_series(data, tickers, weights)
            # print("\nPortfolio loaded successfully!")
            print("\nPortfolio successfully loaded:", tickers)

        # --------------------------------------------------------
        # 2) Analyze portfolio
        # --------------------------------------------------------
        elif choice == "2":
            if portfolio_series is None:
                print("Error: Load portfolio first (option 1).")
                continue

            print("\nPortfolio Analysis:")
            print("Mean return:", portfolio_series.pct_change().mean())
            print("Volatility:", portfolio_series.pct_change().std())

        # --------------------------------------------------------
        # 3) Train & Forecast model 
        # --------------------------------------------------------
        elif choice == "3":
            if portfolio_series is None:
                print("Error: Load portfolio first (option 1).")
                continue

            model, X_test, y_test = train_model(portfolio_series)
            pred = forecast(model, X_test)
            plot_prediction(y_test, pred)

        # --------------------------------------------------------
        # 4) Run scenario
        # --------------------------------------------------------
        elif choice == "4":
            if data is None:
                print("Error: Load portfolio first (option 1).")
                continue

            print("\nChoose scenario:")
            print("1) AI Bubble (+15%)")
            print("2) Crash (-15%)")
            print("3) Recovery (+5%)")
            s_choice = input("Scenario option: ").strip()

            scenario_map = {"1": "AI_BUBBLE", "2": "CRASH", "3": "RECOVERY"}

            if s_choice not in scenario_map:
                print("Invalid scenario.")
                continue

            scenario = run_scenario(data, scenario_type=scenario_map[s_choice])
            plot_scenario(scenario)

        # --------------------------------------------------------
        # 5) Plot historical prices
        # --------------------------------------------------------
        elif choice == "5":
            if data is None:
                print("Error: Load portfolio first (option 1).")
                continue

            plot_prices(data)

        # --------------------------------------------------------
        # 6) Exit
        # --------------------------------------------------------
        elif choice == "6":
            print("Goodbye!")
            break

        else:
            print("Invalid choice. Please select a number between 1 and 6.")


if __name__ == "__main__":
    main()
