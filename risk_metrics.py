"""
NASDAQ 风险指标分析
计算最大回撤、波动率、夏普比率、熊市识别等关键风险度量
"""

import pandas as pd
import numpy as np

DATA_PATH = r"E:\cc\maxs 01\nasdaq_complete_1971_2026.csv"


def load_data():
    df = pd.read_csv(DATA_PATH)
    df['date'] = pd.to_datetime(df['date'])
    df['year'] = df['date'].dt.year
    return df


def compute_drawdown_series(prices):
    """计算完整回撤时间序列（百分比，负数表示回撤）"""
    running_max = prices.expanding().max()
    drawdown = (prices - running_max) / running_max * 100
    return drawdown


def compute_max_drawdown(prices, dates):
    """计算最大回撤及 peak/trough 日期"""
    running_max = prices.expanding().max()
    drawdown = (prices - running_max) / running_max * 100

    trough_idx = drawdown.idxmin()
    max_dd = drawdown.iloc[trough_idx]

    # 找到高点（回撤前的最高价）
    peak_price = running_max.iloc[trough_idx]
    peak_idx = (prices[:trough_idx + 1]).idxmax()
    peak_date = dates.iloc[peak_idx]
    trough_date = dates.iloc[trough_idx]
    duration_days = (trough_date - peak_date).days

    return {
        'max_drawdown_pct': max_dd,
        'peak_date': peak_date,
        'trough_date': trough_date,
        'peak_price': peak_price,
        'trough_price': prices.iloc[trough_idx],
        'duration_days': duration_days
    }


def compute_annualized_volatility(prices):
    """年化波动率（基于日对数收益率）"""
    log_returns = np.log(prices / prices.shift(1)).dropna()
    daily_vol = log_returns.std()
    annualized_vol = daily_vol * np.sqrt(252)
    return annualized_vol


def compute_sharpe_ratio(prices, risk_free_rate=0.02):
    """夏普比率"""
    total_days = len(prices) - 1
    total_years = total_days / 252
    total_return = (prices.iloc[-1] / prices.iloc[0]) ** (1 / total_years) - 1
    ann_vol = compute_annualized_volatility(prices)
    sharpe = (total_return - risk_free_rate) / ann_vol
    return sharpe


def compute_consecutive_years(yearly_returns):
    """最长连涨/连跌年数"""
    streaks = {'up': [], 'down': []}
    current_type = None
    start_year = None
    count = 0

    for _, row in yearly_returns.iterrows():
        year = int(row['year'])
        ret = row['return_pct']

        if ret > 0:
            streak_type = 'up'
        else:
            streak_type = 'down'

        if streak_type == current_type:
            count += 1
        else:
            if current_type is not None:
                streaks[current_type].append({
                    'start': start_year,
                    'end': year - 1,
                    'count': count
                })
            current_type = streak_type
            start_year = year
            count = 1

    # 保存最后一段
    if current_type is not None:
        streaks[current_type].append({
            'start': start_year,
            'end': int(yearly_returns.iloc[-1]['year']),
            'count': count
        })

    max_up = max(streaks['up'], key=lambda x: x['count']) if streaks['up'] else None
    max_down = max(streaks['down'], key=lambda x: x['count']) if streaks['down'] else None

    return {'max_up_streak': max_up, 'max_down_streak': max_down}


def compute_bear_markets(prices, dates, threshold=-20.0):
    """识别所有回撤超过阈值的熊市区间"""
    drawdown = compute_drawdown_series(prices)
    bears = []
    in_bear = False
    bear_start = None
    bear_peak = None
    bear_peak_date = None
    max_dd = 0
    max_dd_date = None

    for i in range(len(prices)):
        dd = drawdown.iloc[i]
        date = dates.iloc[i]
        price = prices.iloc[i]

        if dd <= threshold and not in_bear:
            in_bear = True
            bear_peak = prices.iloc[i] / (1 + dd / 100)
            bear_peak_date = dates.iloc[i]
            bear_start = i
            max_dd = dd
            max_dd_date = date
        elif in_bear:
            if dd < max_dd:
                max_dd = dd
                max_dd_date = date
            if dd >= 0:
                bears.append({
                    'peak_date': bear_peak_date,
                    'trough_date': max_dd_date,
                    'recovery_date': date,
                    'peak_price': bear_peak,
                    'trough_dd': max_dd,
                    'duration_days': (date - bear_peak_date).days,
                    'recovery_days': (date - max_dd_date).days
                })
                in_bear = False

    # 当前仍在熊市
    if in_bear:
        bears.append({
            'peak_date': bear_peak_date,
            'trough_date': max_dd_date,
            'recovery_date': None,
            'peak_price': bear_peak,
            'trough_dd': max_dd,
            'duration_days': (dates.iloc[-1] - bear_peak_date).days,
            'recovery_days': None
        })

    return pd.DataFrame(bears)


def print_report(df, yearly):
    """打印风险指标报告"""
    prices = df['close'].values
    prices_s = pd.Series(prices)
    dates = df['date']

    print("=" * 60)
    print("NASDAQ 综合指数风险指标分析")
    print("=" * 60)

    # 最大回撤
    dd_info = compute_max_drawdown(prices_s, dates)
    print(f"\n历史最大回撤:")
    print(f"  回撤幅度: {dd_info['max_drawdown_pct']:.1f}%")
    print(f"  高点日期: {dd_info['peak_date'].strftime('%Y-%m-%d')} (价格: {dd_info['peak_price']:.2f})")
    print(f"  低点日期: {dd_info['trough_date'].strftime('%Y-%m-%d')} (价格: {dd_info['trough_price']:.2f})")
    print(f"  持续天数: {dd_info['duration_days']}天")

    # 波动率
    vol = compute_annualized_volatility(prices_s)
    print(f"\n年化波动率: {vol * 100:.1f}%")

    # 夏普比率
    sharpe = compute_sharpe_ratio(prices_s)
    print(f"夏普比率: {sharpe:.2f} (无风险利率 2%)")

    # 连涨连跌
    consec = compute_consecutive_years(yearly)
    if consec['max_up_streak']:
        s = consec['max_up_streak']
        print(f"\n最长连涨: {s['start']}-{s['end']} ({s['count']}年)")
    if consec['max_down_streak']:
        s = consec['max_down_streak']
        print(f"最长连跌: {s['start']}-{s['end']} ({s['count']}年)")

    # 熊市统计
    bears = compute_bear_markets(prices_s, dates)
    print(f"\n熊市次数 (回撤 > 20%): {len(bears)}")
    for i, b in bears.iterrows():
        rec = f"恢复: {b['recovery_date'].strftime('%Y-%m-%d')} ({b['recovery_days']}天)" if pd.notna(b['recovery_date']) else "尚未恢复"
        print(f"  {b['peak_date'].strftime('%Y-%m-%d')} -> {b['trough_date'].strftime('%Y-%m-%d')}  "
              f"回撤: {b['trough_dd']:.1f}%  {rec}")


def main():
    df = load_data()
    yearly = df.groupby('year')['close'].last().reset_index()
    yearly.columns = ['year', 'close']
    yearly['prev_close'] = yearly['close'].shift(1)
    yearly['return_pct'] = ((yearly['close'] - yearly['prev_close']) / yearly['prev_close']) * 100
    yearly = yearly.dropna(subset=['return_pct']).reset_index(drop=True)
    print_report(df, yearly)


if __name__ == "__main__":
    main()
