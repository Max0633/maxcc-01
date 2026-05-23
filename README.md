# NASDAQ Composite Index Historical Data

Complete daily K-line data for the NASDAQ Composite Index (^IXIC) from its inception to present.

## Dataset

- **File**: `nasdaq_complete_1971_2026.csv`
- **Records**: 13,941 trading days
- **Period**: 1971-02-05 to 2026-05-22
- **Columns**: date, open, high, low, close, volume, amount

## Data Sources

| Period | Source | Coverage |
|--------|--------|----------|
| 1971-2003 | FRED | Closing price only |
| 2004-2026 | Sina Finance | Full OHLCV |

## Key Statistics

- Historical low: 54.87 (1974-10-03)
- Historical high: 26,635.22 (2026-05-14)

## Usage

```python
import pandas as pd

df = pd.read_csv('nasdaq_complete_1971_2026.csv')
df['date'] = pd.to_datetime(df['date'])
print(df.head())
```
