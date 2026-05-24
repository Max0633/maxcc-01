"""
NASDAQ 技术指标分析（仅 2004+ 有效 OHLCV 数据）
SMA、金叉死叉、RSI、MACD、布林带、成交量分析
"""

import pandas as pd
import numpy as np

DATA_PATH = r"E:\cc\maxs 01\nasdaq_complete_1971_2026.csv"


def load_data():
    df = pd.read_csv(DATA_PATH)
    df['date'] = pd.to_datetime(df['date'])
    return df


def prepare_ohlcv(df):
    """过滤 2004+ 数据，处理零成交量异常值"""
    ohlcv = df[df['date'] >= '2004-01-01'].copy()
    ohlcv = ohlcv.set_index('date')
    ohlcv['volume'] = ohlcv['volume'].replace(0, np.nan).ffill()
    return ohlcv


def compute_sma(ohlcv, periods=None):
    """计算简单移动平均"""
    if periods is None:
        periods = [50, 200]
    result = ohlcv.copy()
    for p in periods:
        result[f'sma_{p}'] = result['close'].rolling(window=p).mean()
    return result


def compute_golden_death_crosses(ohlcv):
    """检测金叉/死叉事件"""
    df = compute_sma(ohlcv, [50, 200])
    df = df.dropna(subset=['sma_50', 'sma_200'])

    crosses = []
    prev_diff = df['sma_50'].iloc[0] - df['sma_200'].iloc[0]

    for i in range(1, len(df)):
        curr_diff = df['sma_50'].iloc[i] - df['sma_200'].iloc[i]
        if prev_diff < 0 and curr_diff >= 0:
            crosses.append({
                'date': df.index[i],
                'type': 'golden',
                'close': df['close'].iloc[i]
            })
        elif prev_diff > 0 and curr_diff <= 0:
            crosses.append({
                'date': df.index[i],
                'type': 'death',
                'close': df['close'].iloc[i]
            })
        prev_diff = curr_diff

    return pd.DataFrame(crosses)


def compute_rsi(ohlcv, period=14):
    """计算 RSI（Wilder 平滑法）"""
    result = ohlcv.copy()
    delta = result['close'].diff()
    gain = delta.clip(lower=0)
    loss = (-delta).clip(lower=0)

    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()

    for i in range(period, len(avg_gain)):
        if pd.isna(avg_gain.iloc[i - 1]):
            continue
        avg_gain.iloc[i] = (avg_gain.iloc[i - 1] * (period - 1) + gain.iloc[i]) / period
        avg_loss.iloc[i] = (avg_loss.iloc[i - 1] * (period - 1) + loss.iloc[i]) / period

    rs = avg_gain / avg_loss
    result['rsi_14'] = 100 - (100 / (1 + rs))
    return result


def compute_macd(ohlcv, fast=12, slow=26, signal=9):
    """计算 MACD"""
    result = ohlcv.copy()
    ema_fast = result['close'].ewm(span=fast, adjust=False).mean()
    ema_slow = result['close'].ewm(span=slow, adjust=False).mean()
    result['macd'] = ema_fast - ema_slow
    result['macd_signal'] = result['macd'].ewm(span=signal, adjust=False).mean()
    result['macd_histogram'] = result['macd'] - result['macd_signal']
    return result


def compute_bollinger_bands(ohlcv, period=20, num_std=2):
    """计算布林带"""
    result = ohlcv.copy()
    result['bb_middle'] = result['close'].rolling(window=period).mean()
    bb_std = result['close'].rolling(window=period).std()
    result['bb_upper'] = result['bb_middle'] + num_std * bb_std
    result['bb_lower'] = result['bb_middle'] - num_std * bb_std
    return result


def compute_volume_analysis(ohlcv):
    """成交量分析"""
    result = ohlcv.copy()
    result['volume_sma_20'] = result['volume'].rolling(window=20).mean()
    result['relative_volume'] = result['volume'] / result['volume_sma_20']
    result['high_volume'] = result['relative_volume'] > 2.0
    return result


def print_report(ohlcv):
    """打印技术分析报告"""
    print("=" * 60)
    print("NASDAQ 技术指标分析 (2004+)")
    print("=" * 60)

    # 最新指标
    df = compute_sma(ohlcv, [50, 200])
    df = compute_rsi(df)
    df = compute_macd(df)
    df = compute_bollinger_bands(df)

    latest = df.iloc[-1]
    print(f"\n最新数据: {df.index[-1].strftime('%Y-%m-%d')}")
    print(f"  收盘价: {latest['close']:.2f}")
    print(f"  SMA50:  {latest['sma_50']:.2f}")
    print(f"  SMA200: {latest['sma_200']:.2f}")
    print(f"  RSI14:  {latest['rsi_14']:.1f}")
    print(f"  MACD:   {latest['macd']:.2f}")
    print(f"  布林上轨: {latest['bb_upper']:.2f}")
    print(f"  布林下轨: {latest['bb_lower']:.2f}")

    # 金叉死叉
    crosses = compute_golden_death_crosses(ohlcv)
    print(f"\n金叉/死叉事件 (共 {len(crosses)} 次):")
    for _, c in crosses.iterrows():
        label = "金叉" if c['type'] == 'golden' else "死叉"
        print(f"  {c['date'].strftime('%Y-%m-%d')} {label}  价格: {c['close']:.2f}")

    # RSI 极端值
    print(f"\nRSI 极端值:")
    rsi_df = compute_rsi(ohlcv)
    overbought = rsi_df[rsi_df['rsi_14'] > 70]
    oversold = rsi_df[rsi_df['rsi_14'] < 30]
    print(f"  超买 (>70) 天数: {len(overbought)}")
    print(f"  超卖 (<30) 天数: {len(oversold)}")


def main():
    df = load_data()
    ohlcv = prepare_ohlcv(df)
    print_report(ohlcv)


if __name__ == "__main__":
    main()
