import numpy as np
import pandas as pd


def calculate_portfolio(prices, weights, initial_capital):
    """
    Calculate the historical performance and risk
    of a buy-and-hold investment portfolio.
    """

    # Convert portfolio weights into a Pandas Series
    weights = pd.Series(weights)

    # Calculate historical investment values
    portfolio_assets = (
        prices.div(prices.iloc[0])
        .mul(initial_capital)
        .mul(weights, axis=1)
    )

    # Calculate total portfolio value
    portfolio_value = portfolio_assets.sum(axis=1)

    # Final portfolio value
    final_value = portfolio_value.iloc[-1]

    # Cumulative return
    portfolio_return = (
        final_value / initial_capital
    ) - 1

    # Daily returns
    portfolio_daily_returns = (
        portfolio_value.pct_change().dropna()
    )

    # Annualized volatility
    portfolio_volatility = (
        portfolio_daily_returns.std() * np.sqrt(252)
    )

    # Portfolio drawdowns
    portfolio_running_max = portfolio_value.cummax()

    portfolio_drawdowns = (
        portfolio_value / portfolio_running_max
    ) - 1

    # Maximum drawdown
    portfolio_max_drawdown = portfolio_drawdowns.min()

    # Return calculated results
    return {
        "portfolio_assets": portfolio_assets,
        "portfolio_value": portfolio_value,
        "final_value": final_value,
        "portfolio_return": portfolio_return,
        "portfolio_daily_returns": portfolio_daily_returns,
        "portfolio_volatility": portfolio_volatility,
        "portfolio_drawdowns": portfolio_drawdowns,
        "portfolio_max_drawdown": portfolio_max_drawdown
    }