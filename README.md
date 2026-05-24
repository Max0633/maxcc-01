# NASDAQ Composite Index — Deep Analysis Dashboard

Interactive Plotly dashboard covering NASDAQ 1971–2026 (13,941 trading days).

**Live Demo:** https://max0633.github.io/maxcc-01/

## Screenshots

Open `dashboard_output.html` in any browser — fully self-contained, no internet required.

## Features

### Major Events Section
- Top 7 largest declines with fundamentals (dot-com crash, 2008 crisis, COVID, etc.)
- Top 7 largest gains with fundamentals (AI boom, QE rally, internet dawn, etc.)
- Each event card: category tag, date range, trigger, fundamentals, key events timeline, lesson

### Charts (9 interactive Plotly charts)
| Chart | Description |
|-------|-------------|
| Price Trend & Volume | Log-scale price with SMA50/200, Bollinger bands, golden/death crosses |
| Historical Drawdown | Drawdown from all-time high with -20% bear threshold |
| Monthly Returns Heatmap | Year × Month heatmap (RdYlGn colorscale) |
| Bull/Bear Cycles | Timeline of market regimes |
| Crash Depth Analysis | Horizontal bar chart of crash magnitudes |
| Crash Comparison | Grouped bars: drawdown %, crash days, recovery days |
| RSI Indicator | 14-day RSI with overbought/oversold zones |
| MACD Indicator | MACD line, signal line, histogram |
| Annual Returns | Yearly return bars with event reason hover text |

### UI Design
- American minimalist style — white background, system-ui fonts
- Sticky navigation bar with anchor links
- Bilingual titles (English headers, Chinese content)
- Responsive layout (mobile-friendly)

## Quick Start

```bash
pip install -r requirements.txt
python dashboard.py
```

Opens `dashboard_output.html` in your browser.

## Project Structure

```
├── dashboard.py            # Main dashboard — generates HTML
├── crash_analysis.py       # Crash detection + knowledge base (7 events)
├── cycle_analysis.py       # Bull/bear market identification
├── risk_metrics.py         # Max drawdown, volatility, Sharpe ratio
├── technical_analysis.py   # SMA, RSI, MACD, Bollinger (2004+ data)
├── seasonal_analysis.py    # Monthly returns, heatmap data
├── analysis.py             # Annual returns console analysis
├── visualization.py        # Static matplotlib charts
├── requirements.txt        # pandas, matplotlib, numpy, plotly
├── dashboard_output.html   # Generated output (8.3 MB, self-contained)
└── index.html              # Copy for GitHub Pages
```

## Data

- **Source:** NASDAQ Composite daily data 1971-02-05 to 2026-05-22
- **Records:** 13,941 trading days
- **Fields:** date, open, high, low, close, volume, amount
- **Quality:** 1971–2003 close-only (OHLC identical, volume=0); 2004+ full OHLCV

## Knowledge Base

### Crash Events (7)
| Event | Category | Max Drawdown |
|-------|----------|-------------|
| 1973–74 Oil Crisis | External Shock | -59.9% |
| 1987 Black Monday | Technical Cascade | -35.9% |
| 2000–02 Dot-com Crash | Bubble Burst | -79.7% |
| 2008 Financial Crisis | Financial Crisis | -55.7% |
| 2020 COVID Crash | External Shock | -30.1% |
| 2022 Rate Hike | Policy Tightening | -36.4% |
| 2025 Tariff Shock | Policy Shock | -24.3% |

### Gain Events (7)
| Event | Category | Gain |
|-------|----------|------|
| 1999 Dot-com Euphoria | Speculative Frenzy | +85.6% |
| 1991 Gulf War Recovery | Post-War Recovery | +56.8% |
| 2003 Post-Bubble Recovery | Post-Bubble Recovery | +49.5% |
| 2009 QE Rally | Quantitative Easing | +43.9% |
| 2020 COVID Stimulus | Liquidity-Driven | +43.6% |
| 2023 AI Revolution | AI Revolution | +43.4% |
| 1995 Internet Dawn | Tech Dawn | +39.9% |

## Tech Stack

- **Python 3.10+**
- **Plotly** — interactive charts (inlined JS, fully offline)
- **Pandas** — data processing
- **NumPy** — numerical computation
- **Matplotlib** — static charts (visualization.py only)
