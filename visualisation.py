import matplotlib.pyplot as plt

def plot_prices(data):
    """Zeigt Kursverläufe aller Aktien."""
    plt.figure()
    for t, df in data.items():
        plt.plot(df["Close"], label=t)
    plt.legend()
    plt.title("Historische Kurse")
    plt.show()

def plot_prediction(y_test, pred):
    """Zeigt echte vs vorhergesagte Preise."""
    plt.figure()
    plt.plot(y_test, label="Echt")
    plt.plot(pred, label="Vorhersage")
    plt.legend()
    plt.title("ML-Vorhersage")
    plt.show()

def plot_scenario(scenario):
    """Zeigt simulierte Szenarien."""
    plt.figure()
    for t, df in scenario.items():
        plt.plot(df["Close"], label=f"{t} (Szenario)")
    plt.legend()
    plt.title("Simuliertes Marktszenario")
    plt.show()