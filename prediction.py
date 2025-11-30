import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor


##### Hilfsfunktionen

def create_features(series):
    df = pd.DataFrame()
    df["price"] = series
    df["return"] = series.pct_change()

    df["roll_mean_5"] = df["return"].rolling(5).mean()  #5-Tage gleitender Durchschnitt
    df["roll_std_5"] = df["return"].rolling(5).std() #5-Tage Votalität

    df["roll_mean_20"] = df["return"].rolling(20).mean() #20-Tage gleitender Durchschnitt
    df["roll_std_20"] = df["return"].rolling(20).std() #20-Tage Votalität

    df["momentum_10"] = series / series.shift(10) #Preis/Preis vor 10 Tagen
    df["momentum_20"] = series / series.shift(20) #Preis/Preis vor 20 Tagen

    df = df.dropna()
    return df


##### Dataset erstellen

def make_dataset(series):
    df = create_features(series)

    X = df.drop(columns=["price"]).values
    y = df["return"].shift(-1).dropna().values
    X = X[:-1]

    return X, y, df.index[:-1]


##### Modell trainieren

def train_model(series):
    X, y, idx = make_dataset(series)

    split = int(len(X) * 0.8)

    model = RandomForestRegressor(
        n_estimators=400,
        max_depth=12,
        random_state=42
    )

    model.fit(X[:split], y[:split])

    X_test = X[split:]
    y_test = y[split:]

    return model, X_test, y_test


##### Zukunft prediction

def forecast_future_days(model, series, years, noise_factor=0.5):
    days = years * 365

    df = create_features(series)
    last_row = df.iloc[-1].copy()
    last_price = series.values[-1]

    predicted_prices = []

    for _ in range(days):
        X = last_row.drop(labels="price").values.reshape(1, -1)
        predicted_return = model.predict(X)[0]

        # Realismus: Rauschen hinzufügen → kein perfekter Aufwärtstrend
        predicted_return += np.random.normal(0, noise_factor * 0.0005)

        # Preis aktualisieren
        last_price *= (1 + predicted_return)
        predicted_prices.append(last_price)

        # Neue Features simulieren
        new_row = {
            "price": last_price,
            "return": predicted_return,
        }

        # einfaches Rolling-Update
        for col in ["roll_mean_5", "roll_std_5",
                    "roll_mean_20", "roll_std_20"]:
            new_row[col] = last_row[col]  # leichte Näherung

        new_row["momentum_10"] = last_price / df["price"].iloc[-10]
        new_row["momentum_20"] = last_price / df["price"].iloc[-20]

        df.loc[df.index[-1] + pd.Timedelta(days=1)] = new_row

        df = df.tail(200)  # Speicher Limit
        last_row = df.iloc[-1]

    return predicted_prices



##### Plot

def plot_with_predictions(series, predictions, years):
    last_date = series.index[-1]

    future_dates = pd.date_range(
        start=last_date + pd.Timedelta(days=1),
        periods=years * 365,
        freq="D"
    )

    pred_series = pd.Series(predictions, index=future_dates)

    plt.figure(figsize=(14, 6))
    plt.plot(series.index, series.values, label="Historische Daten")
    plt.plot(pred_series.index, pred_series.values, label="Vorhersage", alpha=0.8)

    # X-Achse formattieren → nur Jahreszahlen anzeigen
    plt.gca().xaxis.set_major_formatter(
        plt.matplotlib.dates.DateFormatter('%Y')
    )

    plt.title(f"Historische Daten + {years} Jahre tägliche Prognose")
    plt.xlabel("Jahr")
    plt.ylabel("Preis")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()