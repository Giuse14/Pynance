import numpy as np
from sklearn.linear_model import LinearRegression

def make_dataset(series, window=30):
    X, y = [], []
    values = series.values
    for i in range(len(values) - window):
        X.append(values[i:i+window])
        y.append(values[i+window])
    return np.array(X), np.array(y)

def train_model(series):
    """Trainiert ein Lineares Regressionsmodell auf Schlusskursen."""
    X, y = make_dataset(series)
    split = int(len(X) * 0.8)
    model = LinearRegression()
    model.fit(X[:split], y[:split])
    return model, X[split:], y[split:]

def forecast(model, X_test):
    """Gibt Vorhersagen zurück."""
    return model.predict(X_test)