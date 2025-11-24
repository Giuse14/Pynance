import pandas as pd

def run_scenario(data, scenario_type="AI_BUBBLE"):
    """Simuliert einfache Marktereignisse."""
    scenario = {}

    for t, df in data.items():
        sim = df.copy()

        if scenario_type == "AI_BUBBLE":
            sim["Close"] = sim["Close"] * 1.15  # +15%
        elif scenario_type == "CRASH":
            sim["Close"] = sim["Close"] * 0.85  # -15%
        elif scenario_type == "RECOVERY":
            sim["Close"] = sim["Close"] * 1.05  # +5%

        scenario[t] = sim

    return scenario