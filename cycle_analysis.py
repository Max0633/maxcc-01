"""
NASDAQ 牛熊周期分析
识别牛熊市场、周期统计、复苏分析、当前状态判断
"""

import pandas as pd
import numpy as np

DATA_PATH = r"E:\cc\maxs 01\nasdaq_complete_1971_2026.csv"


def load_data():
    df = pd.read_csv(DATA_PATH)
    df['date'] = pd.to_datetime(df['date'])
    return df


def identify_bull_bear_markets(prices, dates, threshold=-0.20):
    """识别牛熊市场区间"""
    running_max = prices.expanding().max()
    drawdown = (prices - running_max) / running_max * 100

    cycles = []
    in_bear = False
    peak_price = None
    peak_date = None

    for i in range(len(prices)):
        dd = drawdown.iloc[i]
        price = prices.iloc[i]
        date = dates.iloc[i]

        if dd <= threshold and not in_bear:
            in_bear = True
            peak_price = running_max.iloc[i]
            peak_date = date
            bear_start = i
            bear_start_date = date
            bear_min_dd = dd
            bear_min_date = date
        elif in_bear:
            if dd < bear_min_dd:
                bear_min_dd = dd
                bear_min_date = date
            if dd >= 0:
                # 熊市结束
                cycles.append({
                    'period_type': 'bear',
                    'start_date': bear_start_date,
                    'end_date': date,
                    'duration_days': (date - bear_start_date).days,
                    'start_price': peak_price,
                    'end_price': price,
                    'return_pct': (price - peak_price) / peak_price * 100,
                    'max_drawdown': bear_min_dd
                })
                # 牛市开始
                cycles.append({
                    'period_type': 'bull',
                    'start_date': date,
                    'end_date': None,
                    'duration_days': None,
                    'start_price': price,
                    'end_price': None,
                    'return_pct': None,
                    'max_drawdown': None
                })
                in_bear = False

    # 如果当前仍在熊市
    if in_bear:
        cycles.append({
            'period_type': 'bear',
            'start_date': bear_start_date,
            'end_date': dates.iloc[-1],
            'duration_days': (dates.iloc[-1] - bear_start_date).days,
            'start_price': peak_price,
            'end_price': prices.iloc[-1],
            'return_pct': (prices.iloc[-1] - peak_price) / peak_price * 100,
            'max_drawdown': bear_min_dd
        })

    # 更新最后一个牛市的结束信息
    if cycles and cycles[-1]['period_type'] == 'bull':
        cycles[-1]['end_date'] = dates.iloc[-1]
        cycles[-1]['duration_days'] = (dates.iloc[-1] - cycles[-1]['start_date']).days
        cycles[-1]['end_price'] = prices.iloc[-1]
        cycles[-1]['return_pct'] = (prices.iloc[-1] - cycles[-1]['start_price']) / cycles[-1]['start_price'] * 100

    return pd.DataFrame(cycles)


def compute_cycle_statistics(cycles):
    """牛熊周期统计"""
    bulls = cycles[cycles['period_type'] == 'bull']
    bears = cycles[cycles['period_type'] == 'bear']

    stats = {
        'bull_count': len(bulls),
        'bear_count': len(bears),
        'avg_bull_duration': bulls['duration_days'].mean() if len(bulls) > 0 else 0,
        'avg_bear_duration': bears['duration_days'].mean() if len(bears) > 0 else 0,
        'avg_bull_return': bulls['return_pct'].mean() if len(bulls) > 0 else 0,
        'avg_bear_return': bears['return_pct'].mean() if len(bears) > 0 else 0,
        'longest_bull': bulls.loc[bulls['duration_days'].idxmax()] if len(bulls) > 0 else None,
        'shortest_bull': bulls.loc[bulls['duration_days'].idxmin()] if len(bulls) > 0 else None,
        'longest_bear': bears.loc[bears['duration_days'].idxmax()] if len(bears) > 0 else None,
        'shortest_bear': bears.loc[bears['duration_days'].idxmin()] if len(bears) > 0 else None,
    }
    return stats


def identify_current_regime(prices, dates, cycles):
    """判断当前所处市场状态"""
    current_price = prices.iloc[-1]
    current_date = dates.iloc[-1]

    # 找最后一个完整的熊市
    bears = cycles[cycles['period_type'] == 'bear']
    if len(bears) > 0:
        last_bear = bears.iloc[-1]
        last_bear_recovery = last_bear['end_date']
    else:
        last_bear_recovery = dates.iloc[0]

    # 判断当前是牛市还是熊市
    running_max = prices.expanding().max()
    current_dd = (current_price - running_max.iloc[-1]) / running_max.iloc[-1] * 100

    if current_dd <= -20:
        # 找当前熊市的开始
        bear_start_idx = None
        for i in range(len(prices) - 1, -1, -1):
            dd = (prices.iloc[i] - running_max.iloc[i]) / running_max.iloc[i] * 100
            if dd > -5:
                bear_start_idx = i + 1
                break
        if bear_start_idx is None:
            bear_start_idx = 0

        return {
            'regime': 'bear',
            'start_date': dates.iloc[bear_start_idx],
            'duration_days': (current_date - dates.iloc[bear_start_idx]).days,
            'start_price': prices.iloc[bear_start_idx],
            'current_drawdown': current_dd
        }
    else:
        # 牛市 - 找上一个熊市结束点
        return {
            'regime': 'bull',
            'start_date': last_bear_recovery,
            'duration_days': (current_date - last_bear_recovery).days,
            'start_price': current_price / (1 + current_dd / 100),
            'current_gain': current_dd
        }


def print_report(df):
    """打印牛熊周期分析报告"""
    prices = df['close'].values
    prices_s = pd.Series(prices)
    dates = df['date']

    cycles = identify_bull_bear_markets(prices_s, dates)
    stats = compute_cycle_statistics(cycles)
    current = identify_current_regime(prices_s, dates, cycles)

    print("=" * 60)
    print("NASDAQ 牛熊周期分析")
    print("=" * 60)

    print(f"\n牛市次数: {stats['bull_count']}")
    print(f"熊市次数: {stats['bear_count']}")
    print(f"平均牛市持续: {stats['avg_bull_duration']:.0f}天 ({stats['avg_bull_duration']/365:.1f}年)")
    print(f"平均熊市持续: {stats['avg_bear_duration']:.0f}天 ({stats['avg_bear_duration']/365:.1f}年)")
    print(f"平均牛市收益: {stats['avg_bull_return']:+.1f}%")
    print(f"平均熊市跌幅: {stats['avg_bear_return']:+.1f}%")

    if stats['longest_bull'] is not None:
        b = stats['longest_bull']
        print(f"\n最长牛市: {b['start_date'].strftime('%Y-%m-%d')} -> {b['end_date'].strftime('%Y-%m-%d')} ({b['duration_days']}天, {b['return_pct']:+.1f}%)")

    if stats['longest_bear'] is not None:
        b = stats['longest_bear']
        rec = f"-> {b['end_date'].strftime('%Y-%m-%d')}" if pd.notna(b['end_date']) else "(进行中)"
        print(f"最长熊市: {b['start_date'].strftime('%Y-%m-%d')} {rec} ({b['duration_days']}天, {b['return_pct']:+.1f}%)")

    print(f"\n当前状态: {'熊市' if current['regime'] == 'bear' else '牛市'}")
    print(f"  起始: {current['start_date'].strftime('%Y-%m-%d')}")
    print(f"  持续: {current['duration_days']}天")
    if current['regime'] == 'bear':
        print(f"  回撤: {current['current_drawdown']:.1f}%")
    else:
        print(f"  涨幅: {current['current_gain']:+.1f}%")


def main():
    df = load_data()
    print_report(df)


if __name__ == "__main__":
    main()
