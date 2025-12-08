from data_loader import load_data
from portfolio_analysis import analyze_portfolio, generate_analysis_report
from prediction import train_model, forecast_future_days, plot_with_predictions
from simulation import run_scenario
from visualisation import plot_prediction, plot_scenario, plot_portfolio_analysis, plot_drawdown, interactive_toggle_plot
from get_user_portfolio import get_user_portfolio
from portfolio_builder import build_portfolio_series
from gui_portfolio_selector import select_portfolio_gui
from montecarlo import run_monte_carlo_simulation

import pandas as pd



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
    current_period = "10y"  # Default period

    while True:
        print("\n========== PORTFOLIO MANAGER ==========")
        print("1) Load portfolio & market data")
        print("2) Analyze portfolio (Text Report)")
        print("3) Visualize portfolio analysis")
        print("4) Plot drawdown analysis")
        print("5) Train & Forecast model")
        print("6) Monte Carlo Simulation")
        print("7) Run scenario analysis")
        print("8) Plot price history")
        print("9) Exit")
        print("========================================")

        choice = input("Choose an option (1-9): ").strip()

        # --------------------------------------------------------
        # 1) Load portfolio
        # --------------------------------------------------------
        if choice == "1":
            tickers, weights = select_portfolio_gui()
            data = load_data(tickers, period=current_period)
            portfolio_series = build_portfolio_series(data, tickers, weights)
            print(f"\nPortfolio successfully loaded: {tickers}")
            print(f"Data period: {current_period}")

        # --------------------------------------------------------
        # 2) Analyze portfolio (Text Report)
        # --------------------------------------------------------
        elif choice == "2":
            if portfolio_series is None or data is None:
                print("Error: Load portfolio first (option 1).")
                continue

            # Allow user to select analysis period
            print("\nSelect analysis period:")
            print("1) 5 years (5y)")
            print("2) 10 years (10y) - Recommended")
            print("3) 15 years (15y)")
            print("4) Maximum available (max)")
            print("5) Keep current period")
            
            period_choice = input("Choose period (1-5): ").strip()
            period_map = {
                "1": "5y",
                "2": "10y", 
                "3": "15y",
                "4": "max",
                "5": current_period
            }
            
            if period_choice in period_map:
                selected_period = period_map[period_choice]
                if selected_period != current_period:
                    print(f"Loading data for {selected_period} period...")
                    data = load_data(tickers, period=selected_period)
                    portfolio_series = build_portfolio_series(data, tickers, weights)
                    current_period = selected_period
            else:
                print("Invalid choice, using current period.")

            print(f"\nRunning comprehensive portfolio analysis ({current_period})...")
            analysis = analyze_portfolio(data, weights)
            report = generate_analysis_report(analysis, tickers, weights)
            print(report)

        # --------------------------------------------------------
        # 3) Visualize portfolio analysis
        # --------------------------------------------------------
        elif choice == "3":
            if data is None:
                print("Error: Load portfolio first (option 1).")
                continue

            analysis = analyze_portfolio(data, weights)
            plot_portfolio_analysis(analysis, tickers, weights)

        # --------------------------------------------------------
        # 4) Plot drawdown analysis
        # --------------------------------------------------------
        elif choice == "4":
            if data is None:
                print("Error: Load portfolio first (option 1).")
                continue

            plot_drawdown(data, weights)

        # --------------------------------------------------------
        # 5) Train & Forecast model  (NEUE VERSION)
        # --------------------------------------------------------
        elif choice == "5":
            if portfolio_series is None:
                print("Error: Load portfolio first (option 1).")
                continue

            # Modell trainieren (aus neuer prediction.py)
            model, X_test, y_test = train_model(portfolio_series)

            # Benutzer nach Prognosezeitraum fragen
            try:
                years_to_predict = int(input("Wie viele Jahre sollen prognostiziert werden? "))
                if years_to_predict <= 0:
                    print("Please enter a positive number.")
                    continue
            except ValueError:
                print("Invalid input. Please enter a positive integer.")
                continue

            # Zukunft prognostizieren
            future_predictions = forecast_future_days(model, portfolio_series, years_to_predict)

            # Neues Plot mit Jahresachse + Zukunft aus prediction.py
            plot_with_predictions(portfolio_series, future_predictions, years_to_predict)

        # --------------------------------------------------------
        # 6) Run scenario
        # --------------------------------------------------------
        elif choice == "6":
            if data is None:
                print("Error: Load portfolio first (option 1).")
                continue

            # Build price DataFrame for MC
            price_df = pd.concat([data[t]["Close"] for t in tickers], axis=1)
            price_df.columns = tickers

            run_monte_carlo_simulation(price_df, weights)
            


        # --------------------------------------------------------
        # 7) Run scenario
        # --------------------------------------------------------
        elif choice == "7":
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
        # 8) Plot historical prices
        # --------------------------------------------------------
        elif choice == "8":
            if data is None:
                print("Load portfolio first.")
                continue
            interactive_toggle_plot(data, weights)


        # --------------------------------------------------------
        # 9) Exit
        # --------------------------------------------------------
        elif choice == "9":
            print("Goodbye!")
            break

        else:
            print("Invalid choice. Please select a number between 1 and 9.")


if __name__ == "__main__":
    main()