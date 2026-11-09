"""
INVESTMENT PORTFOLIO ANALYZER
Version 6.1

A financial analytics application developed with:
- Python
- Streamlit
- Pandas
- NumPy
- Plotly
- SciPy
- yfinance

Features:
1. Overview
2. Market Analysis
3. Portfolio Simulator
4. Risk Analytics
5. Portfolio Insights
6. Portfolio Comparison
7. Portfolio Optimization

Historical analysis for educational purposes.
Not financial advice.
"""

import html
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf

from scipy.optimize import minimize


# ============================================================
# 01. CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Investment Portfolio Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

CSS_PATH = Path(__file__).parent / "styles.css"

if CSS_PATH.exists():
    st.html(
        "<style>"
        + CSS_PATH.read_text(encoding="utf-8")
        + "</style>"
    )


# ============================================================
# 02. DESIGN
# ============================================================

BACKGROUND = "#0B111D"
PANEL = "#121E2E"
PANEL_LIGHT = "#18283B"

TEXT = "#EDF4FA"
MUTED = "#AABDD1"

TEAL = "#49D7C2"
BLUE = "#79AFFF"
GOLD = "#E9B96E"
RED = "#F07985"

GRID = "rgba(160,180,205,0.12)"

COLORS = {
    "S&P 500": TEAL,
    "MSCI World": BLUE,
    "Nasdaq 100": GOLD,
    "Portfolio": TEAL,
    "Portfolio A": TEAL,
    "Portfolio B": BLUE,
    "Invested Capital": GOLD,
    "Minimum Volatility": BLUE,
    "Maximum Sharpe": GOLD
}

TICKERS = {
    "S&P 500": "SPY",
    "MSCI World": "URTH",
    "Nasdaq 100": "QQQ"
}

ASSETS = list(TICKERS.keys())

TRADING_DAYS = 252

# Illustrative assumption, not a historical rate series.
RISK_FREE_RATE = 0.02

START_DATE = "2015-01-01"


# ============================================================
# 03. FORMAT HELPERS
# ============================================================

def money(value):
    if pd.isna(value):
        return "N/A"
    return f"${value:,.2f}"


def percent(value):
    if pd.isna(value):
        return "N/A"
    return f"{value:.2%}"


def decimal(value):
    if pd.isna(value):
        return "N/A"
    return f"{value:.2f}"


def safe(value):
    return html.escape(str(value), quote=True)


# ============================================================
# 04. HTML COMPONENTS
# ============================================================

def render_html(content):
    """
    Render HTML without Markdown interpreting
    indented HTML as a code block.
    """
    st.html(content)


def section(label, title, description=""):

    render_html(
        '<div class="section-heading">'
        f'<span class="section-index">{safe(label)}</span>'
        f'<span class="section-title">{safe(title)}</span>'
        '</div>'
    )

    if description:
        st.write(description)


def notice(message, kind="info"):

    if kind not in ("info", "success", "warning"):
        kind = "info"

    render_html(
        f'<div class="notice notice-{kind}">'
        f'{safe(message)}'
        '</div>'
    )


def insight_card(
    title,
    observation,
    explanation,
    consideration=None,
    accent="teal"
):

    if accent not in ("teal", "blue", "gold", "red"):
        accent = "teal"

    consideration_html = ""

    if consideration:
        consideration_html = (
            '<div class="insight-consideration">'
            '<div class="insight-label">WHAT TO CONSIDER</div>'
            f'<p>{safe(consideration)}</p>'
            '</div>'
        )

    content = (
        f'<div class="insight-card accent-{accent}">'
        f'<div class="insight-title">{safe(title)}</div>'
        f'<div class="insight-observation">'
        f'{safe(observation)}'
        '</div>'
        '<div class="insight-separator"></div>'
        '<div class="insight-label">FINANCIAL INTERPRETATION</div>'
        f'<p class="insight-explanation">{safe(explanation)}</p>'
        f'{consideration_html}'
        '</div>'
    )

    render_html(content)


def metric_row(metrics):

    columns = st.columns(len(metrics))

    for column, (label, value) in zip(
        columns,
        metrics.items()
    ):
        with column:
            st.metric(label, value)


# ============================================================
# 05. PROFESSIONAL HTML TABLES
# ============================================================

METRIC_INFO = {
    "Cumulative Return":
        "Total return over the observation period",

    "Annualized Return":
        "Equivalent compounded yearly return",

    "Annualized Volatility":
        "Annualized variability of investment returns",

    "Maximum Drawdown":
        "Largest historical decline from a previous peak",

    "Sharpe Ratio":
        "Estimated excess return relative to volatility",

    "Final Value":
        "Investment value at the end of the period"
}

PERCENT_METRICS = {
    "Cumulative Return",
    "Annualized Return",
    "Annualized Volatility",
    "Maximum Drawdown"
}


def format_table_value(metric, value):

    if not isinstance(
        value,
        (int, float, np.number)
    ):
        return safe(value)

    if metric in PERCENT_METRICS:
        return percent(value)

    if metric == "Final Value":
        return money(value)

    return decimal(value)


def financial_table(data, title=None):

    if title:
        st.subheader(title)

    headers = "".join(
        f"<th>{safe(column)}</th>"
        for column in data.columns
    )

    rows = []

    for metric, row in data.iterrows():

        description = METRIC_INFO.get(metric, "")

        cells = []

        values = [
            float(value)
            for value in row.values
            if isinstance(
                value,
                (int, float, np.number)
            )
            and pd.notna(value)
        ]

        best_value = None

        if len(values) > 1:

            if metric == "Annualized Volatility":
                best_value = min(values)

            elif metric in {
                "Cumulative Return",
                "Annualized Return",
                "Maximum Drawdown",
                "Sharpe Ratio",
                "Final Value"
            }:
                best_value = max(values)

        for value in row.values:

            css_class = "financial-value"

            if (
                best_value is not None
                and isinstance(
                    value,
                    (int, float, np.number)
                )
                and pd.notna(value)
                and np.isclose(
                    float(value),
                    best_value
                )
            ):
                css_class += " best-value"

            cells.append(
                f'<td class="{css_class}">'
                f'{format_table_value(metric, value)}'
                '</td>'
            )

        rows.append(
            '<tr>'
            '<th>'
            f'<span class="metric-name">{safe(metric)}</span>'
            f'<span class="metric-description">'
            f'{safe(description)}'
            '</span>'
            '</th>'
            + "".join(cells)
            + '</tr>'
        )

    content = (
        '<div class="table-container">'
        '<div class="table-scroll">'
        '<table class="financial-table">'
        '<thead><tr>'
        '<th>FINANCIAL INDICATOR</th>'
        + headers
        + '</tr></thead>'
        '<tbody>'
        + "".join(rows)
        + '</tbody>'
        '</table>'
        '</div>'
        '</div>'
    )

    render_html(content)


def data_table(data, formats=None):

    formats = formats or {}

    headers = "".join(
        f"<th>{safe(column)}</th>"
        for column in data.columns
    )

    rows = []

    for _, row in data.iterrows():

        cells = []

        for column, value in row.items():

            if pd.isna(value):
                formatted = "N/A"

            elif column in formats:
                formatted = formats[column](value)

            elif isinstance(
                value,
                (int, float, np.number)
            ):
                formatted = decimal(value)

            else:
                formatted = safe(value)

            cells.append(
                f"<td>{formatted}</td>"
            )

        rows.append(
            "<tr>"
            + "".join(cells)
            + "</tr>"
        )

    content = (
        '<div class="table-container">'
        '<div class="table-scroll">'
        '<table class="financial-table simple-table">'
        '<thead><tr>'
        + headers
        + '</tr></thead>'
        '<tbody>'
        + "".join(rows)
        + '</tbody>'
        '</table>'
        '</div>'
        '</div>'
    )

    render_html(content)


# ============================================================
# 06. CHARTS
# ============================================================

def style_chart(
    fig,
    title,
    height=460,
    hovermode="x unified"
):

    fig.update_layout(
        template="plotly_dark",

        paper_bgcolor=PANEL,
        plot_bgcolor=PANEL,

        height=height,

        title=dict(
            text=title,
            x=0.025,
            font=dict(
                size=18,
                color=TEXT
            )
        ),

        font=dict(
            family="Arial",
            color=MUTED,
            size=12
        ),

        margin=dict(
            l=65,
            r=45,
            t=90,
            b=85
        ),

        hovermode=hovermode,

        hoverlabel=dict(
            bgcolor="#203249",
            font_color=TEXT
        ),

        legend=dict(
            orientation="h",
            x=0,
            y=1.12
        ),

        xaxis=dict(
            showgrid=False,
            zeroline=False,
            automargin=True,
            tickfont=dict(
                size=12,
                color="#BED0E2"
            ),
            tickangle=0,
            ticks="outside",
            ticklen=6,
            tickcolor="#506780"
        ),

        yaxis=dict(
            showgrid=True,
            gridcolor=GRID,
            zeroline=False,
            automargin=True,
            tickfont=dict(
                size=12,
                color="#BED0E2"
            )
        )
    )

    return fig

    fig.update_layout(
        template="plotly_dark",

        paper_bgcolor=PANEL,
        plot_bgcolor=PANEL,

        height=height,

        title=dict(
            text=title,
            x=0.025,
            font=dict(
                size=18,
                color=TEXT
            )
        ),

        font=dict(
            family="Arial",
            color=MUTED,
            size=12
        ),

        margin=dict(
            l=50,
            r=45,
            t=85,
            b=50
        ),

        hovermode=hovermode,

        hoverlabel=dict(
            bgcolor="#203249",
            font_color=TEXT
        ),

        legend=dict(
            orientation="h",
            x=0,
            y=1.13
        )
    )

    fig.update_xaxes(
        showgrid=False,
        zeroline=False
    )

    fig.update_yaxes(
        showgrid=True,
        gridcolor=GRID,
        zeroline=False
    )
    fig.update_xaxes(

    tickformat="%Y",

    dtick="M24",

    ticklabelmode="period",

    automargin=True

)

    return fig


def line_chart(
    data,
    title,
    y_label="Portfolio Value (USD)"
):

    fig = go.Figure()

    for column in data.columns:

        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data[column],
                name=column,
                mode="lines",

                line=dict(
                    color=COLORS.get(column, TEAL),
                    width=2.6
                ),

                hovertemplate=(
                    "%{x|%d %b %Y}<br>"
                    "%{y:,.2f}<extra>%{fullData.name}</extra>"
                )
            )
        )

    fig.update_yaxes(
        title_text=y_label
    )

    return style_chart(fig, title)


def donut_chart(weights, title):

    labels = [
        asset
        for asset in ASSETS
        if weights[asset] > 0
    ]

    values = [
        weights[asset]
        for asset in labels
    ]

    fig = go.Figure()

    fig.add_trace(
        go.Pie(
            labels=labels,
            values=values,
            hole=0.66,

            marker=dict(
                colors=[
                    COLORS[asset]
                    for asset in labels
                ]
            ),

            textinfo="label+percent",
            textfont=dict(size=13),

            hovertemplate=(
                "%{label}<br>"
                "Allocation: %{percent}"
                "<extra></extra>"
            )
        )
    )

    fig.update_layout(
        showlegend=False,

        annotations=[
            dict(
                text="100%<br>ALLOCATED",
                x=0.5,
                y=0.5,
                showarrow=False,

                font=dict(
                    size=17,
                    color=TEXT
                )
            )
        ]
    )

    return style_chart(
        fig,
        title,
        370,
        hovermode="closest"
    )


def bar_chart(data, title, y_label="Return (%)"):

    fig = go.Figure()

    for column in data.columns:

        fig.add_trace(
            go.Bar(
                x=data.index,
                y=data[column],
                name=column,

                marker_color=COLORS.get(
                    column,
                    TEAL
                )
            )
        )

    fig.update_layout(
        barmode="group"
    )

    fig.update_yaxes(
        title_text=y_label
    )

    return style_chart(fig, title)


# ============================================================
# 07. MARKET DATA
# ============================================================

@st.cache_data(ttl=3600, show_spinner=False)
def load_prices():

    downloaded = yf.download(
        tickers=list(TICKERS.values()),
        start=START_DATE,
        auto_adjust=True,
        progress=False,
        threads=False
    )

    if downloaded.empty:
        raise ValueError(
            "No market data was returned."
        )

    if isinstance(
        downloaded.columns,
        pd.MultiIndex
    ):
        prices = downloaded["Close"].copy()

    else:
        prices = downloaded[["Close"]].copy()

    rename_map = {
        ticker: name
        for name, ticker in TICKERS.items()
    }

    prices = prices.rename(
        columns=rename_map
    )

    prices = prices[ASSETS]

    prices = prices.apply(
        pd.to_numeric,
        errors="coerce"
    )

    prices = prices.dropna().sort_index()

    if len(prices) < 100:
        raise ValueError(
            "Insufficient historical price observations."
        )

    if (prices <= 0).any().any():
        raise ValueError(
            "Market data contains invalid prices."
        )

    return prices


# ============================================================
# 08. FINANCIAL CALCULATIONS
# ============================================================

def calculate_cagr(series):

    years = (
        series.index[-1] -
        series.index[0]
    ).days / 365.25

    if years <= 0:
        return np.nan

    initial = float(series.iloc[0])
    final = float(series.iloc[-1])

    if initial <= 0 or final <= 0:
        return np.nan

    return (final / initial) ** (1 / years) - 1


def calculate_drawdown(series):

    running_max = series.cummax()

    return series / running_max - 1


def calculate_metrics(series):

    returns = series.pct_change().dropna()

    cumulative_return = (
        series.iloc[-1] / series.iloc[0]
    ) - 1

    annualized_return = calculate_cagr(
        series
    )

    volatility = (
        returns.std(ddof=1)
        * np.sqrt(TRADING_DAYS)
    )

    maximum_drawdown = (
        calculate_drawdown(series).min()
    )

    annualized_arithmetic_return = (
        returns.mean() * TRADING_DAYS
    )

    sharpe = (
        (
            annualized_arithmetic_return
            - RISK_FREE_RATE
        ) / volatility
        if volatility > 0
        else np.nan
    )

    return {
        "Cumulative Return": cumulative_return,
        "Annualized Return": annualized_return,
        "Annualized Volatility": volatility,
        "Maximum Drawdown": maximum_drawdown,
        "Sharpe Ratio": sharpe,
        "Final Value": float(series.iloc[-1])
    }


def normalize_prices(prices, capital=10000):

    return (
        prices.div(prices.iloc[0])
        * capital
    )


def asset_metrics(prices):

    normalized = normalize_prices(prices)

    results = {}

    for asset in ASSETS:
        results[asset] = calculate_metrics(
            normalized[asset]
        )

    return pd.DataFrame(results)


# ============================================================
# 09. PORTFOLIO SIMULATION
# ============================================================

def simulate_portfolio(
    prices,
    weights,
    initial_capital=10000,
    monthly_contribution=0
):
    """
    Buy-and-hold portfolio with optional monthly deposits.

    Initial capital is allocated using selected weights.

    New contributions are invested on the first
    available trading day of each new month.

    Existing shares are not rebalanced.

    Returns are calculated before adding new cash
    so that deposits do not appear as investment gains.

    Returns:
        portfolio_value
        invested_capital
        time_weighted_index
    """

    weight_array = np.array(
        [weights[asset] for asset in ASSETS],
        dtype=float
    )

    if not np.isclose(weight_array.sum(), 1):
        raise ValueError(
            "Portfolio weights must total 100%."
        )

    shares = (
        initial_capital
        * weight_array
        / prices.iloc[0].to_numpy()
    )

    invested_total = float(initial_capital)

    values = []
    invested_values = []
    twr_values = []

    previous_value = None
    previous_month = None

    twr_index = 10000.0

    for date, row in prices.iterrows():

        current_prices = row.to_numpy(
            dtype=float
        )

        month = date.to_period("M")

        # Value before any new contribution.
        value_before_deposit = float(
            np.dot(shares, current_prices)
        )

        # Market performance excluding deposits.
        if previous_value is not None:

            daily_return = (
                value_before_deposit
                / previous_value
            ) - 1

            twr_index *= (1 + daily_return)

        # Invest contributions on the first
        # available trading day of each new month.
        if (
            previous_month is not None
            and month != previous_month
            and monthly_contribution > 0
        ):

            new_shares = (
                monthly_contribution
                * weight_array
                / current_prices
            )

            shares += new_shares

            invested_total += monthly_contribution

        current_value = float(
            np.dot(shares, current_prices)
        )

        values.append(current_value)
        invested_values.append(invested_total)
        twr_values.append(twr_index)

        previous_value = current_value
        previous_month = month

    index = prices.index

    portfolio_value = pd.Series(
        values,
        index=index,
        name="Portfolio"
    )

    invested_capital = pd.Series(
        invested_values,
        index=index,
        name="Invested Capital"
    )

    time_weighted_index = pd.Series(
        twr_values,
        index=index,
        name="Portfolio"
    )

    return (
        portfolio_value,
        invested_capital,
        time_weighted_index
    )


# ============================================================
# 10. RETURN CONTRIBUTIONS
# ============================================================

def return_contributions(prices, weights):

    asset_total_returns = (
        prices.iloc[-1]
        / prices.iloc[0]
    ) - 1

    contributions = (
        asset_total_returns
        * pd.Series(weights)
    )

    return contributions.sort_values(
        ascending=False
    )


# ============================================================
# 11. HISTORICAL STRESS TESTING
# ============================================================

STRESS_SCENARIOS = {
    "COVID-19 Market Shock": (
        "2020-02-19",
        "2020-04-30"
    ),

    "2022 Equity Market Decline": (
        "2022-01-03",
        "2022-12-30"
    )
}


def stress_testing(series):

    results = []

    for scenario, dates in STRESS_SCENARIOS.items():

        start, end = dates

        period = series.loc[start:end]

        if len(period) < 2:
            continue

        total_return = (
            period.iloc[-1]
            / period.iloc[0]
        ) - 1

        max_drawdown = (
            calculate_drawdown(period).min()
        )

        results.append({
            "Scenario": scenario,
            "Period Return": total_return,
            "Maximum Drawdown": max_drawdown
        })

    return pd.DataFrame(results)


# ============================================================
# 12. MATHEMATICAL OPTIMIZATION
# ============================================================

def optimize_weights(prices, objective):

    daily_returns = (
        prices.pct_change().dropna()
    )

    expected_returns = (
        daily_returns.mean()
        * TRADING_DAYS
    ).to_numpy()

    covariance = (
        daily_returns.cov()
        * TRADING_DAYS
    ).to_numpy()

    n_assets = len(ASSETS)

    initial_guess = (
        np.ones(n_assets) / n_assets
    )

    bounds = [
        (0.0, 1.0)
        for _ in range(n_assets)
    ]

    constraints = [{
        "type": "eq",
        "fun": lambda w: np.sum(w) - 1.0
    }]

    def portfolio_volatility(w):

        variance = (
            w.T @ covariance @ w
        )

        return np.sqrt(
            max(variance, 0.0)
        )

    def negative_sharpe(w):

        volatility = portfolio_volatility(w)

        if volatility < 1e-10:
            return 1e6

        expected_return = (
            w @ expected_returns
        )

        return -(
            (
                expected_return
                - RISK_FREE_RATE
            ) / volatility
        )

    if objective == "Minimum Volatility":

        objective_function = (
            portfolio_volatility
        )

    else:

        objective_function = negative_sharpe

    result = minimize(
        objective_function,
        initial_guess,

        method="SLSQP",

        bounds=bounds,
        constraints=constraints,

        options={
            "maxiter": 2000,
            "ftol": 1e-10
        }
    )

    if not result.success:
        raise RuntimeError(
            result.message
        )

    weights = np.clip(
        result.x,
        0,
        1
    )

    weights /= weights.sum()

    return dict(zip(ASSETS, weights))


def estimated_portfolio_metrics(prices, weights):

    returns = prices.pct_change().dropna()

    mean_returns = (
        returns.mean() * TRADING_DAYS
    )

    covariance = (
        returns.cov() * TRADING_DAYS
    )

    w = np.array([
        weights[asset]
        for asset in ASSETS
    ])

    expected_return = float(
        w @ mean_returns.to_numpy()
    )

    volatility = float(
        np.sqrt(
            max(
                w.T @ covariance.to_numpy() @ w,
                0
            )
        )
    )

    sharpe = (
        (expected_return - RISK_FREE_RATE)
        / volatility
        if volatility > 0
        else np.nan
    )

    return {
        "Expected Annual Return": expected_return,
        "Estimated Volatility": volatility,
        "Estimated Sharpe": sharpe
    }


# ============================================================
# 13. SESSION STATE
# ============================================================

DEFAULTS = {
    "capital": 10000,
    "monthly_contribution": 0,
    "sp500": 50,
    "world": 30,
    "nasdaq": 20
}

for key, value in DEFAULTS.items():

    if key not in st.session_state:
        st.session_state[key] = value


def get_weights():

    return {
        "S&P 500":
            st.session_state.sp500 / 100,

        "MSCI World":
            st.session_state.world / 100,

        "Nasdaq 100":
            st.session_state.nasdaq / 100
    }


def weights_valid(weights):

    return np.isclose(
        sum(weights.values()),
        1.0
    )


def reset_portfolio():

    for key, value in DEFAULTS.items():
        st.session_state[key] = value


# ============================================================
# 14. SIDEBAR
# ============================================================

render_html(
    '<div class="sidebar-brand">'
    '◈ INVESTMENT INTELLIGENCE'
    '</div>'
)

st.sidebar.caption(
    "FINANCIAL ANALYTICS PLATFORM"
)

st.sidebar.divider()

page = st.sidebar.radio(
    "Navigation",
    [
        "Overview",
        "Market Analysis",
        "Portfolio Simulator",
        "Risk Analytics",
        "Portfolio Insights",
        "Portfolio Comparison",
        "Portfolio Optimization"
    ],
    label_visibility="collapsed"
)

st.sidebar.divider()

st.sidebar.caption(
    "RESEARCH TERMINAL / VERSION 6.1"
)

st.sidebar.caption(
    "Historical market data · Educational use"
)


# ============================================================
# 15. LOAD DATA
# ============================================================

try:

    with st.spinner("Loading historical market data..."):
        prices = load_prices()

except Exception as error:

    st.error(
        f"Market data could not be loaded: {error}"
    )

    st.stop()


# ============================================================
# 16. SHARED CALCULATIONS
# ============================================================

weights = get_weights()

valid_allocation = weights_valid(weights)

portfolio_value = None
invested_capital = None
portfolio_index = None

if valid_allocation:

    (
        portfolio_value,
        invested_capital,
        portfolio_index
    ) = simulate_portfolio(
        prices,
        weights,
        st.session_state.capital,
        st.session_state.monthly_contribution
    )

etf_statistics = asset_metrics(prices)

correlations = (
    prices.pct_change()
    .dropna()
    .corr()
)


# ============================================================
# 17. APPLICATION HEADER
# ============================================================

render_html(
    '<div class="eyebrow">'
    'FINANCIAL RESEARCH / ANALYTICS'
    '</div>'
)

st.title("Investment Portfolio Analyzer")

st.write(
    "Explore historical ETF performance, simulate "
    "investment strategies, evaluate financial risk "
    "and compare portfolio allocations using real "
    "market data."
)

st.caption(
    f"MARKET HISTORY · "
    f"{prices.index[0]:%d %b %Y} — "
    f"{prices.index[-1]:%d %b %Y} · USD"
)

st.divider()


# ============================================================
# PAGE 1. OVERVIEW
# ============================================================

if page == "Overview":

    st.header("Market Overview")

    st.write(
        "This section provides an introduction to "
        "historical investment performance. Select "
        "an ETF to examine its growth, return and "
        "risk characteristics."
    )

    selected_asset = st.selectbox(
        "Select an ETF",
        ASSETS
    )

    normalized = normalize_prices(
        prices[[selected_asset]]
    )

    series = normalized[selected_asset]

    metrics = calculate_metrics(series)

    section(
        "01",
        "Historical Performance"
    )

    metric_row({
        "Cumulative Return":
            percent(metrics["Cumulative Return"]),

        "Annualized Return":
            percent(metrics["Annualized Return"]),

        "Annualized Volatility":
            percent(metrics["Annualized Volatility"])
    })

    st.plotly_chart(
        line_chart(
            normalized,
            "Growth of a $10,000 Investment"
        ),
        use_container_width=True
    )

    insight_card(
        "Historical Performance",

        f"{selected_asset} generated a cumulative "
        f"return of "
        f"{percent(metrics['Cumulative Return'])} "
        "over the available historical period.",

        "Cumulative return measures the total growth "
        "of an investment between two dates. "
        "Annualized return converts this growth "
        "into an equivalent compounded yearly rate. "
        "This makes it easier to compare investments "
        "observed over different time horizons.",

        "Historical growth does not indicate how "
        "smoothly an investment performed. "
        "Volatility and drawdown provide additional "
        "information about the risks experienced."
    )

    section(
        "02",
        "Understanding Investment Risk"
    )

    metric_row({
        "Maximum Drawdown":
            percent(metrics["Maximum Drawdown"]),

        "Sharpe Ratio":
            decimal(metrics["Sharpe Ratio"])
    })

    insight_card(
        "Risk Interpretation",

        f"The ETF recorded annualized volatility "
        f"of {percent(metrics['Annualized Volatility'])} "
        f"and a maximum historical drawdown of "
        f"{percent(metrics['Maximum Drawdown'])}.",

        "Volatility describes the variability of "
        "investment returns. Maximum drawdown measures "
        "the largest decline from a previous historical "
        "peak. These indicators are complementary: "
        "an investment may have moderate day-to-day "
        "volatility but still experience a substantial "
        "loss during a prolonged market downturn.",

        "The Sharpe Ratio uses an illustrative "
        "2% annual risk-free-rate assumption. "
        "It should not be interpreted as a guarantee "
        "of future risk-adjusted performance.",

        "gold"
    )


# ============================================================
# PAGE 2. MARKET ANALYSIS
# ============================================================

elif page == "Market Analysis":

    st.header("Market Analysis")

    st.write(
        "Compare the historical performance of "
        "three exchange-traded funds representing "
        "different equity market exposures."
    )

    section(
        "01",
        "Comparative Investment Growth"
    )

    normalized = normalize_prices(prices)

    st.plotly_chart(
        line_chart(
            normalized,
            "Historical Growth of $10,000"
        ),
        use_container_width=True
    )

    insight_card(
        "How to Interpret This Chart",

        "Each ETF starts with the same hypothetical "
        "investment of $10,000.",

        "Normalizing the starting value removes "
        "differences in ETF share prices and allows "
        "direct comparison of historical growth. "
        "The ETF with the highest ending value "
        "generated the strongest cumulative return "
        "during the selected period.",

        "A stronger historical return does not "
        "automatically mean an ETF offered a better "
        "investment experience. Risk indicators "
        "must also be considered."
    )

    section(
        "02",
        "ETF Financial Scorecard"
    )

    financial_table(
        etf_statistics.drop(
            index="Final Value"
        )
    )

    insight_card(
        "Understanding the Scorecard",

        "The table combines return and risk "
        "indicators for all three ETFs.",

        "Cumulative return measures total historical "
        "growth. Annualized return expresses that "
        "growth on a yearly compounded basis. "
        "Volatility measures return variability, "
        "maximum drawdown measures the deepest "
        "historical decline and the Sharpe Ratio "
        "compares estimated excess return with "
        "volatility.",

        "Green values highlight the strongest "
        "relative result for each metric. "
        "They do not constitute investment "
        "recommendations.",

        "blue"
    )

    section(
        "03",
        "Calendar-Year Returns"
    )

    year_end_prices = prices.resample(
        "YE"
    ).last()

    baseline = prices.iloc[[0]]

    annual_prices = pd.concat([
        baseline,
        year_end_prices
    ])

    annual_returns = (
        annual_prices.pct_change()
        .dropna()
        * 100
    )

    annual_returns.index = (
        annual_returns.index.year
    )

    st.plotly_chart(
        bar_chart(
            annual_returns,
            "Annual ETF Performance"
        ),
        use_container_width=True
    )

    insight_card(
        "Annual Return Analysis",

        "The annual return chart highlights "
        "differences in performance between years.",

        "Long-term cumulative returns can conceal "
        "periods of substantial losses. "
        "Examining individual years helps identify "
        "how consistently an ETF performed and "
        "how strongly it reacted to changing "
        "market conditions.",

        "The first and final calendar years "
        "may be partial periods. Their returns "
        "should not be treated as full-year "
        "performance figures.",

        "gold"
    )


# ============================================================
# PAGE 3. PORTFOLIO SIMULATOR
# ============================================================

elif page == "Portfolio Simulator":

    st.header("Portfolio Simulator")

    st.write(
        "Create a hypothetical investment portfolio "
        "by selecting an initial investment, monthly "
        "contributions and ETF allocation percentages. "
        "The simulator uses historical market prices "
        "to calculate how the strategy would have evolved."
    )

    section(
        "01",
        "Investment Configuration"
    )

    col1, col2 = st.columns(2)

    with col1:

        st.number_input(
            "Initial Investment (USD)",
            min_value=1000,
            max_value=1000000,
            step=1000,
            key="capital"
        )

    with col2:

        st.number_input(
            "Monthly Contribution (USD)",
            min_value=0,
            max_value=10000,
            step=50,
            key="monthly_contribution"
        )

    section(
        "02",
        "Asset Allocation"
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.slider(
            "S&P 500 (%)",
            0,
            100,
            key="sp500"
        )

    with col2:

        st.slider(
            "MSCI World (%)",
            0,
            100,
            key="world"
        )

    with col3:

        st.slider(
            "Nasdaq 100 (%)",
            0,
            100,
            key="nasdaq"
        )

    st.button(
    "Reset Portfolio",
    on_click=reset_portfolio
)

    weights = get_weights()

    if not weights_valid(weights):

        notice(
            f"Current allocation: "
            f"{sum(weights.values()) * 100:.0f}%. "
            "Adjust the weights until they total 100%.",
            "warning"
        )

    else:

        notice(
            "Portfolio allocation validated. "
            "100% of the investment is allocated.",
            "success"
        )

        (
            portfolio_value,
            invested_capital,
            portfolio_index
        ) = simulate_portfolio(
            prices,
            weights,
            st.session_state.capital,
            st.session_state.monthly_contribution
        )

        st.plotly_chart(
            donut_chart(
                weights,
                "Portfolio Allocation"
            ),
            use_container_width=True
        )

        insight_card(
            "Understanding Asset Allocation",

            "Your investment is distributed between "
            "the three selected ETFs according to "
            "the percentages shown above.",

            "Asset allocation determines how much "
            "capital is invested in each instrument. "
            "A higher allocation increases the "
            "influence of that ETF on the portfolio's "
            "overall performance. Monthly contributions "
            "are invested using the same target "
            "percentages, while existing holdings "
            "are not automatically rebalanced.",

            "Different ETFs may hold many of the "
            "same underlying companies. "
            "Diversification depends on actual "
            "exposures, not only on the number "
            "of funds included.",

            "blue"
        )

        section(
            "03",
            "Portfolio Results"
        )

        final_value = portfolio_value.iloc[-1]

        total_invested = invested_capital.iloc[-1]

        gain = final_value - total_invested

        gain_percentage = (
            gain / total_invested
            if total_invested > 0
            else np.nan
        )

        metric_row({
            "Final Portfolio Value":
                money(final_value),

            "Total Capital Invested":
                money(total_invested),

            "Investment Gain / Loss":
                money(gain)
        })

        notice(
            "Gain relative to total contributions: "
            f"{percent(gain_percentage)}. "
            "This is not an annualized return.",
            "info"
        )

        section(
            "04",
            "Historical Portfolio Growth"
        )

        growth_data = pd.DataFrame({
            "Portfolio": portfolio_value,
            "Invested Capital": invested_capital
        })

        st.plotly_chart(
            line_chart(
                growth_data,
                "Portfolio Value vs Invested Capital"
            ),
            use_container_width=True
        )

        insight_card(
            "Interpreting Portfolio Growth",

            f"The simulated portfolio finished at "
            f"{money(final_value)} after total "
            f"contributions of {money(total_invested)}.",

            "The distance between the portfolio "
            "value and invested capital represents "
            "the historical investment gain or loss. "
            "When recurring contributions are enabled, "
            "the portfolio grows through two separate "
            "mechanisms: additional invested capital "
            "and market performance.",

            "The simulation assumes contributions "
            "are invested on the first available "
            "trading day of each new month. "
            "Transaction costs, taxes and currency "
            "conversion costs are excluded."
        )

        section(
            "05",
            "Cash-Flow-Adjusted Performance"
        )

        metrics = calculate_metrics(
            portfolio_index
        )

        metric_row({
            "Time-Weighted Return":
                percent(metrics["Cumulative Return"]),

            "Annualized Return":
                percent(metrics["Annualized Return"]),

            "Annualized Volatility":
                percent(metrics["Annualized Volatility"])
        })

        insight_card(
            "Why Time-Weighted Returns Matter",

            "The time-weighted performance index "
            "separates investment returns from "
            "additional deposits.",

            "Without this adjustment, a monthly "
            "contribution could appear as a sudden "
            "increase in investment performance. "
            "Time-weighted returns measure how the "
            "investment strategy performed independently "
            "of the timing and size of external "
            "cash contributions.",

            "The time-weighted return is different "
            "from the investor's money-weighted "
            "return, which depends on when capital "
            "was actually invested.",

            "gold"
        )


# ============================================================
# PAGE 4. RISK ANALYTICS
# ============================================================

elif page == "Risk Analytics":

    st.header("Risk Analytics")

    st.write(
        "Analyze the historical downside risk "
        "of your selected portfolio, investigate "
        "relationships between ETFs and examine "
        "how the portfolio behaved during "
        "periods of market stress."
    )

    if not valid_allocation:

        notice(
            "Set a valid 100% allocation "
            "in Portfolio Simulator.",
            "warning"
        )

    else:

        (
            risk_value,
            _,
            risk_index
        ) = simulate_portfolio(
            prices,
            weights,
            10000,
            0
        )

        metrics = calculate_metrics(risk_index)

        section(
            "01",
            "Historical Drawdown"
        )

        drawdown = (
            calculate_drawdown(risk_index)
            * 100
        )

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=drawdown.index,
                y=drawdown.values,

                name="Drawdown",

                line=dict(
                    color=RED,
                    width=2.5
                ),

                fill="tozeroy",

                fillcolor="rgba(240,121,133,0.15)"
            )
        )

        fig.update_yaxes(
            title_text="Drawdown (%)"
        )

        st.plotly_chart(
            style_chart(
                fig,
                "Historical Portfolio Drawdown"
            ),
            use_container_width=True
        )

        insight_card(
            "Historical Loss Exposure",

            f"The portfolio experienced a maximum "
            f"historical drawdown of "
            f"{percent(metrics['Maximum Drawdown'])}.",

            "Drawdown measures the decline in value "
            "from a previous portfolio peak. "
            "Unlike volatility, which measures "
            "general fluctuations, drawdown focuses "
            "specifically on losses relative to "
            "previous highs. It helps investors "
            "understand the magnitude of declines "
            "they might have needed to tolerate.",

            "Historical drawdown is not the maximum "
            "possible future loss. More severe "
            "market conditions could produce "
            "larger declines.",

            "red"
        )

        section(
            "02",
            "ETF Correlation Analysis"
        )

        fig = go.Figure()

        fig.add_trace(
            go.Heatmap(
                z=correlations.values,

                x=correlations.columns,
                y=correlations.index,

                zmin=-1,
                zmax=1,

                colorscale=[
                    [0.0, RED],
                    [0.5, "#203249"],
                    [1.0, TEAL]
                ],

                text=np.round(
                    correlations.values,
                    2
                ),

                texttemplate="%{text:.2f}",

                hovertemplate=(
                    "%{x} / %{y}<br>"
                    "Correlation: %{z:.2f}"
                    "<extra></extra>"
                )
            )
        )

        st.plotly_chart(
            style_chart(
                fig,
                "ETF Correlation Matrix",
                420,
                "closest"
            ),
            use_container_width=True
        )

        off_diagonal = correlations.where(
            ~np.eye(
                len(correlations),
                dtype=bool
            )
        )

        highest_correlation = (
            off_diagonal.max().max()
        )

        insight_card(
            "Diversification Assessment",

            f"The highest observed correlation "
            f"between two different ETFs was "
            f"{highest_correlation:.2f}.",

            "Correlation measures the degree "
            "to which two assets have historically "
            "moved together. Values near +1 "
            "indicate strong positive relationships. "
            "Values close to zero indicate weaker "
            "linear relationships, while negative "
            "values indicate a tendency to move "
            "in opposite directions.",

            "High correlation can reduce the "
            "diversification benefits of holding "
            "multiple ETFs. Correlations may "
            "also change during market crises.",

            "blue"
        )

        section(
            "03",
            "Historical Stress Testing"
        )

        stress_results = stress_testing(
            risk_index
        )

        if not stress_results.empty:

            data_table(
                stress_results,

                formats={
                    "Period Return": percent,
                    "Maximum Drawdown": percent
                }
            )

            insight_card(
                "Understanding Market Stress",

                "The table summarizes how the "
                "portfolio performed during "
                "selected historical market downturns.",

                "Period return measures the change "
                "between the first and last available "
                "observations within each scenario. "
                "Maximum drawdown measures the deepest "
                "decline from a previous peak within "
                "that same window. These two indicators "
                "can differ because a portfolio may "
                "recover part of its losses before "
                "the selected period ends.",

                "These scenarios are historical "
                "observations, not forecasts "
                "of future crises.",

                "gold"
            )


# ============================================================
# PAGE 5. PORTFOLIO INSIGHTS
# ============================================================

elif page == "Portfolio Insights":

    st.header("Portfolio Insights")

    st.write(
        "This section translates portfolio "
        "statistics into practical observations. "
        "The objective is to help users understand "
        "which assets drive performance, how "
        "concentrated the allocation is and "
        "what risks appear in the historical data."
    )

    if not valid_allocation:

        notice(
            "Configure a valid allocation first.",
            "warning"
        )

    else:

        (
            insight_value,
            _,
            insight_index
        ) = simulate_portfolio(
            prices,
            weights,
            10000,
            0
        )

        metrics = calculate_metrics(
            insight_index
        )

        section(
            "01",
            "Performance Intelligence"
        )

        metric_row({
            "Cumulative Return":
                percent(metrics["Cumulative Return"]),

            "Annualized Return":
                percent(metrics["Annualized Return"]),

            "Annualized Volatility":
                percent(metrics["Annualized Volatility"])
        })

        insight_card(
            "Integrated Performance Assessment",

            f"The portfolio achieved a cumulative "
            f"return of "
            f"{percent(metrics['Cumulative Return'])} "
            f"and an annualized return of "
            f"{percent(metrics['Annualized Return'])}.",

            "The cumulative return describes "
            "the total growth of the initial "
            "investment, while annualized return "
            "expresses this performance as an "
            "equivalent yearly compounded rate. "
            "These figures should be interpreted "
            "together with volatility, because "
            "strong returns can be accompanied "
            "by substantial fluctuations.",

            "A historical return is an observed "
            "result, not an estimate of what "
            "the investment will earn in the future."
        )

        section(
            "02",
            "Return Contribution Breakdown"
        )

        contributions = return_contributions(
            prices,
            weights
        )

        contribution_data = pd.DataFrame({
            "ETF": contributions.index,

            "Return Contribution (pp)":
                contributions.values * 100,

            "Initial Weight (%)": [
                weights[asset] * 100
                for asset in contributions.index
            ]
        })

        data_table(
            contribution_data,

            formats={
                "Return Contribution (pp)":
                    lambda x: f"{x:+.2f}",

                "Initial Weight (%)":
                    lambda x: f"{x:.1f}%"
            }
        )

        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                x=contributions.values * 100,
                y=contributions.index,

                orientation="h",

                marker_color=[
                    TEAL if value >= 0 else RED
                    for value in contributions.values
                ],

                text=[
                    f"{value * 100:+.2f} pp"
                    for value in contributions.values
                ],

                textposition="outside"
            )
        )

        fig.update_xaxes(
            title_text="Contribution (percentage points)"
        )

        st.plotly_chart(
            style_chart(
                fig,
                "Contribution to Cumulative Return",
                350
            ),
            use_container_width=True
        )

        main_contributor = contributions.idxmax()

        insight_card(
            "Main Performance Contributor",

            f"{main_contributor} contributed "
            f"{contributions[main_contributor] * 100:+.2f} "
            "percentage points to the portfolio's "
            "cumulative historical return.",

            "Return attribution combines the "
            "initial allocation of each ETF "
            "with its individual cumulative return. "
            "An ETF can contribute substantially "
            "because it generated strong returns, "
            "because it received a large allocation "
            "or because of both factors.",

            "These contributions describe a "
            "buy-and-hold portfolio without "
            "additional deposits. They should "
            "not be applied unchanged to a "
            "strategy with recurring contributions.",

            "blue"
        )

        section(
            "03",
            "Concentration Assessment"
        )

        largest_asset = max(
            weights,
            key=weights.get
        )

        largest_weight = weights[
            largest_asset
        ]

        if largest_weight >= 0.70:

            concentration_text = (
                "The allocation is relatively "
                "concentrated in one ETF."
            )

            accent = "gold"

        else:

            concentration_text = (
                "The allocation is distributed "
                "across multiple ETFs."
            )

            accent = "teal"

        insight_card(
            "Portfolio Concentration",

            f"{largest_asset} represents "
            f"{percent(largest_weight)} of the "
            f"initial allocation. "
            f"{concentration_text}",

            "Concentration measures how strongly "
            "a portfolio depends on particular "
            "investments. A large ETF allocation "
            "can increase dependence on that fund, "
            "although an ETF may itself contain "
            "hundreds of securities. "
            "The number of ETFs alone is not "
            "a sufficient measure of diversification.",

            "SPY, URTH and QQQ have overlapping "
            "exposure to large US companies. "
            "Their underlying holdings should "
            "be considered when evaluating "
            "portfolio diversification.",

            accent
        )

        section(
            "04",
            "Downside Risk"
        )

        insight_card(
            "Historical Loss Exposure",

            f"The maximum observed portfolio "
            f"drawdown was "
            f"{percent(metrics['Maximum Drawdown'])}.",

            "Maximum drawdown measures the "
            "largest percentage decline from "
            "a previous historical peak. "
            "It is particularly useful because "
            "long-term investment growth can "
            "hide significant temporary losses. "
            "An investor may need to tolerate "
            "substantial declines before "
            "the portfolio recovers.",

            "Drawdown is based on the historical "
            "sample and cannot establish a "
            "limit on future losses.",

            "red"
        )


# ============================================================
# PAGE 6. PORTFOLIO COMPARISON
# ============================================================

elif page == "Portfolio Comparison":

    st.header("Portfolio Comparison")

    st.write(
        "Compare two hypothetical portfolios "
        "using the same historical prices, "
        "starting capital and observation period. "
        "This helps evaluate the trade-off "
        "between return and risk."
    )

    section(
        "01",
        "Configure Both Portfolios"
    )

    col_a, col_b = st.columns(2)

    def portfolio_inputs(
        container,
        name,
        defaults
    ):

        result = {}

        with container:

            st.subheader(name)

            for asset, default in zip(
                ASSETS,
                defaults
            ):

                result[asset] = (
                    st.slider(
                        f"{asset} (%) — {name}",
                        0,
                        100,
                        default,
                        key=f"{name}_{asset}"
                    ) / 100
                )

        return result

    weights_a = portfolio_inputs(
        col_a,
        "Portfolio A",
        [50, 30, 20]
    )

    weights_b = portfolio_inputs(
        col_b,
        "Portfolio B",
        [20, 60, 20]
    )

    if not (
        weights_valid(weights_a)
        and weights_valid(weights_b)
    ):

        notice(
            "Both portfolios must total 100%.",
            "warning"
        )

    else:

        (
            portfolio_a,
            _,
            index_a
        ) = simulate_portfolio(
            prices,
            weights_a,
            10000,
            0
        )

        (
            portfolio_b,
            _,
            index_b
        ) = simulate_portfolio(
            prices,
            weights_b,
            10000,
            0
        )

        metrics_a = calculate_metrics(index_a)

        metrics_b = calculate_metrics(index_b)

        section(
            "02",
            "Historical Growth Comparison"
        )

        comparison = pd.DataFrame({
            "Portfolio A": portfolio_a,
            "Portfolio B": portfolio_b
        })

        st.plotly_chart(
            line_chart(
                comparison,
                "Growth of Two $10,000 Portfolios"
            ),
            use_container_width=True
        )

        section(
            "03",
            "Financial Scorecard"
        )

        scorecard = pd.DataFrame({
            "Portfolio A": metrics_a,
            "Portfolio B": metrics_b
        })

        financial_table(scorecard)

        section(
            "04",
            "Comparative Interpretation"
        )

        return_a = metrics_a[
            "Annualized Return"
        ]

        return_b = metrics_b[
            "Annualized Return"
        ]

        volatility_a = metrics_a[
            "Annualized Volatility"
        ]

        volatility_b = metrics_b[
            "Annualized Volatility"
        ]

        if np.isclose(return_a, return_b):

            return_message = (
                "Both portfolios generated "
                "similar annualized returns."
            )

        elif return_a > return_b:

            return_message = (
                "Portfolio A generated the "
                "higher annualized return."
            )

        else:

            return_message = (
                "Portfolio B generated the "
                "higher annualized return."
            )

        insight_card(
            "Return Comparison",

            return_message,

            f"Portfolio A achieved an annualized "
            f"return of {percent(return_a)}, "
            f"compared with {percent(return_b)} "
            "for Portfolio B. The difference "
            "reflects the influence of asset "
            "allocation on historical investment "
            "performance.",

            "A higher return does not necessarily "
            "indicate a superior portfolio. "
            "Consider the additional risk required "
            "to achieve that return."
        )

        if np.isclose(
            volatility_a,
            volatility_b
        ):

            risk_message = (
                "Both portfolios experienced "
                "similar historical volatility."
            )

        elif volatility_a < volatility_b:

            risk_message = (
                "Portfolio A experienced "
                "lower historical volatility."
            )

        else:

            risk_message = (
                "Portfolio B experienced "
                "lower historical volatility."
            )

        insight_card(
            "Risk Comparison",

            risk_message,

            f"Portfolio A recorded annualized "
            f"volatility of {percent(volatility_a)}, "
            f"while Portfolio B recorded "
            f"{percent(volatility_b)}. "
            "Lower volatility indicates smaller "
            "historical fluctuations in returns, "
            "although it does not eliminate "
            "the possibility of substantial losses.",

            "Compare volatility, maximum drawdown "
            "and Sharpe Ratio together rather "
            "than relying on a single indicator.",

            "blue"
        )


# ============================================================
# PAGE 7. PORTFOLIO OPTIMIZATION
# ============================================================

elif page == "Portfolio Optimization":

    st.header("Portfolio Optimization")

    st.write(
        "Use mathematical optimization to explore "
        "how different ETF allocations affect "
        "estimated portfolio risk and return. "
        "The optimization engine uses SciPy "
        "and historical financial data."
    )

    section(
        "01",
        "Optimization Methodology"
    )

    insight_card(
        "How Mathematical Optimization Works",

        "The optimizer searches for ETF weights "
        "that satisfy a defined mathematical objective.",

        "The model estimates expected annual returns "
        "and the covariance matrix from historical "
        "daily ETF returns. It then uses SciPy's "
        "SLSQP optimization algorithm to identify "
        "portfolio weights that minimize estimated "
        "volatility or maximize the estimated "
        "Sharpe Ratio. All weights must be "
        "non-negative and sum to 100%.",

        "The optimizer does not know future returns. "
        "Its output depends on the historical "
        "sample and the assumptions used.",

        "blue"
    )

    section(
        "02",
        "Select Optimization Objective"
    )

    objective = st.selectbox(
        "Optimization Method",
        [
            "Minimum Volatility",
            "Maximum Sharpe Ratio"
        ]
    )

    try:

        optimized_weights = optimize_weights(
            prices,
            objective
        )

        (
            optimized_value,
            _,
            optimized_index
        ) = simulate_portfolio(
            prices,
            optimized_weights,
            10000,
            0
        )

        estimated = estimated_portfolio_metrics(
            prices,
            optimized_weights
        )

        historical = calculate_metrics(
            optimized_index
        )

        section(
            "03",
            "Optimized Asset Allocation"
        )

        st.plotly_chart(
            donut_chart(
                optimized_weights,
                "Optimized Portfolio Allocation"
            ),
            use_container_width=True
        )

        allocation_data = pd.DataFrame({
            "ETF": ASSETS,

            "Allocation (%)": [
                optimized_weights[asset] * 100
                for asset in ASSETS
            ]
        })

        data_table(
            allocation_data,

            formats={
                "Allocation (%)":
                    lambda x: f"{x:.2f}%"
            }
        )

        section(
            "04",
            "Estimated Portfolio Statistics"
        )

        metric_row({
            "Estimated Annual Return":
                percent(
                    estimated["Expected Annual Return"]
                ),

            "Estimated Volatility":
                percent(
                    estimated["Estimated Volatility"]
                ),

            "Estimated Sharpe Ratio":
                decimal(
                    estimated["Estimated Sharpe"]
                )
        })

        notice(
            "These are estimates based on "
            "historical daily returns and "
            "the selected optimization method.",
            "info"
        )

        section(
            "05",
            "Historical Portfolio Performance"
        )

        st.plotly_chart(
            line_chart(
                optimized_value.to_frame(
                    "Portfolio"
                ),
                "Historical Growth of Optimized Allocation"
            ),
            use_container_width=True
        )

        financial_table(
            pd.DataFrame({
                "Optimized Portfolio": historical
            })
        )

        section(
            "06",
            "Optimization Interpretation"
        )

        if objective == "Minimum Volatility":

            insight_card(
                "Minimum Volatility Portfolio",

                "The optimizer identified the "
                "allocation with the lowest "
                "estimated volatility under "
                "the model constraints.",

                "Minimum-volatility optimization "
                "focuses on reducing estimated "
                "portfolio return fluctuations. "
                "It uses the covariance matrix "
                "to account for how the selected "
                "ETFs have historically moved "
                "relative to one another. "
                "The resulting allocation may "
                "sacrifice some expected return "
                "in exchange for lower "
                "estimated volatility.",

                "Minimum volatility does not "
                "mean minimum possible loss. "
                "The portfolio can still "
                "experience substantial drawdowns.",

                "blue"
            )

        else:

            insight_card(
                "Maximum Sharpe Portfolio",

                "The optimizer identified the "
                "allocation with the highest "
                "estimated Sharpe Ratio under "
                "the model constraints.",

                "The Sharpe Ratio compares "
                "estimated excess return with "
                "estimated volatility. "
                "The optimization process searches "
                "for the combination of ETFs "
                "that maximizes this relationship "
                "using historical return estimates "
                "and a fixed illustrative "
                "risk-free-rate assumption.",

                "Maximum-Sharpe portfolios can "
                "be sensitive to small changes "
                "in expected-return estimates. "
                "An allocation that looks optimal "
                "historically may not remain "
                "optimal in the future.",

                "gold"
            )

        section(
            "07",
            "Important Limitations"
        )

        notice(
            "This is an in-sample optimization. "
            "The same historical period is used "
            "to estimate portfolio weights and "
            "display their performance. "
            "The results are not an independent "
            "out-of-sample validation.",
            "warning"
        )

    except Exception as error:

        st.error(
            f"Optimization failed: {error}"
        )


# ============================================================
# 18. FOOTER
# ============================================================

st.divider()

st.caption(
    "Investment Portfolio Analyzer · Version 6.1 · "
    "Historical research and educational use only. "
    "Not investment advice."
)

st.caption(
    "Market data: Yahoo Finance via yfinance. "
    "Historical prices use the provider's "
    "auto-adjusted series. "
    "Taxes, trading costs and currency conversion "
    "costs are not included."
)