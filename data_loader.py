import yfinance as yf
import pandas as pd
from datetime import date, timedelta

# ETFs selected for the analysis
ETFS = {
    "S&P 500": "SPY",
    "MSCI World": "URTH",
    "Nasdaq 100": "QQQ"
}


def load_market_data():
    """
    Download historical adjusted ETF prices.
    """

    tickers = list(ETFS.values())

    data = yf.download(
        tickers,
        start="2015-01-01",
        end=(date.today() + timedelta(days=1)).isoformat(),
        auto_adjust=True,
        progress=False
    )

    prices = data["Close"]

    prices = prices.rename(
        columns={ticker: name for name, ticker in ETFS.items()}
    )

    prices = prices.dropna()

    return prices


if __name__ == "__main__":

    prices = load_market_data()

    print("\nINVESTMENT PORTFOLIO ANALYZER")
    print("-----------------------------")

    print("\nFirst observations:")
    print(prices.head())

    print("\nLatest observations:")
    print(prices.tail())

    print("\nDataset dimensions:")
    print(prices.shape)