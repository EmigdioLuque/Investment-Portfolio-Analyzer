import numpy as np
import pandas as pd

from data_loader import load_market_data


def calculate_metrics(prices):
    """
    Calculate historical financial performance and risk metrics.
    """

    # Daily returns
    daily_returns = prices.pct_change().dropna()

    # Cumulative return
    cumulative_return = (prices.iloc[-1] / prices.iloc[0]) - 1

    # Annualized return (CAGR)
    years = (prices.index[-1] - prices.index[0]).days / 365.25
    annualized_return = (
        prices.iloc[-1] / prices.iloc[0]
    ) ** (1 / years) - 1

    # Annualized volatility
    annualized_volatility = daily_returns.std() * np.sqrt(252)

    # Maximum drawdown
    running_max = prices.cummax()
    drawdowns = prices / running_max - 1
    max_drawdown = drawdowns.min()

    # Sharpe ratio (assuming 0% risk-free rate)
    annualized_mean_return = daily_returns.mean() * 252
    sharpe_ratio = annualized_mean_return / annualized_volatility.replace(0, np.nan)

    # Results table
    metrics = pd.DataFrame({
        "Cumulative Return": cumulative_return,
        "Annualized Return": annualized_return,
        "Annualized Volatility": annualized_volatility,
        "Maximum Drawdown": max_drawdown,
        "Sharpe Ratio": sharpe_ratio
    })

    return metrics


if __name__ == "__main__":

    prices = load_market_data()
    metrics = calculate_metrics(prices)

    print("\nINVESTMENT PORTFOLIO ANALYZER")
    print("Financial Performance & Risk Metrics")
    print("------------------------------------")

    print("\nHistorical analysis:")
    print((metrics * 1).round(4))