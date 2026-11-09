# Investment Portfolio Analyzer

### 🚀 [Launch Live Application](https://investment-portfolio-analyzer-et9shvgr2ahbsuazd9hz74.streamlit.app)

**Try the interactive platform online — no installation required.**

[![Live Demo](https://img.shields.io/badge/Live_Demo-Launch_Application-00C9A7?style=for-the-badge)](https://investment-portfolio-analyzer-et9shvgr2ahbsuazd9hz74.streamlit.app)

### Financial Analytics | Portfolio Simulation | Risk Assessment | Mathematical Optimization

An interactive financial analytics platform developed with Python and Streamlit to help investors analyze historical market performance, simulate investment strategies, evaluate portfolio risk, and explore mathematically optimized asset allocations.

---

## 1. The Problem

Building an investment portfolio involves more than selecting assets with high historical returns.

Investors must understand how different asset allocations affect long-term portfolio growth, how much risk they are taking, and how recurring investments influence their financial results.

However, financial information is often fragmented across multiple platforms, making it difficult to evaluate investment strategies consistently.

**Investment Portfolio Analyzer addresses this problem by combining portfolio simulation, risk analytics, performance comparison, and mathematical optimization in a single interactive application.**

The objective is to help users make more informed investment decisions by understanding the relationship between risk, return, diversification, and investment contributions.

---

## 2. Key Features

### Market Analysis

Explore the historical performance of major equity ETFs using interactive financial charts and performance indicators.

The application analyzes three ETFs:

| ETF | Ticker | Market Exposure |
|-----|--------|-----------------|
| S&P 500 | SPY | Large-cap US equities |
| MSCI World | URTH | Developed-market equities |
| Nasdaq 100 | QQQ | Large-cap Nasdaq-listed non-financial companies |

### Portfolio Simulator

Create and customize an investment portfolio by adjusting:

- Initial investment capital.
- Portfolio allocation percentages.
- Monthly investment contributions.

The simulator calculates:

- Final portfolio value.
- Total invested capital.
- Investment gains and losses.
- Historical portfolio growth.
- Performance relative to invested capital.

### Risk Analytics

Evaluate the risk associated with different investment allocations.

Financial indicators include:

- Annualized volatility.
- Maximum drawdown.
- Asset correlation.
- Risk-adjusted performance.

### Portfolio Insights

Understand financial results through automated interpretations.

The application provides insights into:

- Historical investment performance.
- Return contribution by ETF.
- Portfolio concentration.
- Diversification considerations.
- Historical downside risk.

### Portfolio Comparison

Compare two investment portfolios with different asset allocations.

The comparison includes:

- Historical portfolio growth.
- Cumulative returns.
- Annualized returns.
- Annualized volatility.
- Maximum drawdown.
- Sharpe Ratio.

### Portfolio Optimization

Explore mathematically optimized investment allocations.

The application supports two optimization objectives:

**Minimum Volatility**

Identifies the portfolio allocation that minimizes estimated annualized volatility.

**Maximum Sharpe Ratio**

Identifies the portfolio allocation that maximizes estimated risk-adjusted returns.

The optimization process uses historical ETF returns, covariance matrices, and SciPy's SLSQP optimization algorithm.

Portfolio weights must be non-negative and sum to 100%.

---

## 3. Technologies Used

| Technology | Application |
|------------|-------------|
| Python | Application development and financial calculations |
| Streamlit | Interactive web application |
| Pandas | Financial data processing |
| NumPy | Numerical calculations |
| Plotly | Interactive financial visualizations |
| SciPy | Mathematical portfolio optimization |
| yfinance | Historical financial market data |
| CSS | Interface customization and visual design |

---

## 4. Project Structure

```text
Investment-Portfolio-Analyzer/
│
├── app.py
├── data_loader.py
├── financial_analysis.py
├── portfolio_engine.py
├── styles.css
├── requirements.txt
├── .gitignore
├── README.md
│
└── .streamlit/
    └── config.toml
```

---

## 5. Installation

### Step 1: Clone the repository

```bash
git clone <repository-url>
cd Investment-Portfolio-Analyzer
```

### Step 2: Create a virtual environment

```bash
python -m venv .venv
```

### Step 3: Activate the virtual environment

On macOS or Linux:

```bash
source .venv/bin/activate
```

On Windows:

```bash
.venv\Scripts\activate
```

### Step 4: Install dependencies

```bash
python -m pip install -r requirements.txt
```

### Step 5: Run the application

```bash
python -m streamlit run app.py
```

The application will open in your browser.

---

## 6. Financial Methodology

The platform uses historical ETF prices to calculate investment performance and portfolio statistics.

### Portfolio Returns

Portfolio performance is calculated using historical asset returns and the selected investment allocations.

### Annualized Return

Annualized return expresses historical investment growth as an equivalent yearly compounded rate.

### Annualized Volatility

Volatility measures the variability of historical investment returns.

### Maximum Drawdown

Maximum drawdown measures the largest observed percentage decline from a previous portfolio peak.

### Sharpe Ratio

The Sharpe Ratio evaluates estimated excess return relative to portfolio volatility.

### Portfolio Optimization

The optimization model estimates expected annual returns and covariance relationships using historical daily ETF returns.

SciPy's SLSQP algorithm identifies portfolio weights that satisfy the selected mathematical objective.

---

## 7. Data Sources

Historical financial market data is obtained from Yahoo Finance using the Python `yfinance` library.

The application analyzes historical price series for:

- SPY — SPDR S&P 500 ETF Trust.
- URTH — iShares MSCI World ETF.
- QQQ — Invesco QQQ Trust.

Financial calculations are performed using historical adjusted price data.

---

## 8. Limitations

This project is designed for financial research and educational purposes.

Important limitations include:

- Historical returns do not guarantee future performance.
- Portfolio optimization relies on historical estimates.
- Optimization results are evaluated in-sample.
- The model does not independently validate optimized allocations using future market data.
- Taxes, transaction costs, and currency conversion costs are excluded.
- Financial results depend on the historical period and assumptions used.
- ETF diversification does not necessarily eliminate overlapping exposure to underlying companies.

**This application does not provide personalized financial or investment advice.**

---

## 9. Project Value

Investment Portfolio Analyzer demonstrates how financial data, quantitative analysis, and software development can be combined to address a real investment decision-making problem.

The platform allows users to:

- Compare investment strategies.
- Understand historical risk and return.
- Evaluate portfolio diversification.
- Analyze the impact of recurring contributions.
- Explore mathematical portfolio optimization.
- Interpret financial results through an accessible interactive interface.

The project combines financial analytics, quantitative modeling, data visualization, and interactive application development.

---

## 10. Future Improvements

Potential future developments include:

- Additional ETFs and asset classes.
- Customizable historical analysis periods.
- Portfolio optimization with additional constraints.
- Out-of-sample performance evaluation.
- Inflation-adjusted investment analysis.
- Transaction cost modeling.
- Portfolio report generation.

---

## 11. Author

**Emigdio Luque**

Business Analytics Student  
Universidad CEU San Pablo — Madrid, Spain

**GitHub:** EmigdioLuque

**LinkedIn:** Emigdio Luque

---

*Investment Portfolio Analyzer — Historical financial research and educational use only.*
