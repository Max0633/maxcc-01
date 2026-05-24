"""
NASDAQ 季节性分析
月度收益率、热力图数据、最佳/最差月份、季度分析
"""

import pandas as pd
import numpy as np

DATA_PATH = r"E:\cc\maxs 01\nasdaq_complete_1971_2026.csv"


def load_data():
    df = pd.read_csv(DATA_PATH)
    df['date'] = pd.to_datetime(df['date'])
    return df


def compute_monthly_returns(df):
    """计算月度收益率"""
    monthly = df.set_index('date')['close'].resample('ME').last()
    returns = monthly.pct_change() * 100
    result = pd.DataFrame({
        'year': returns.index.year,
        'month': returns.index.month,
        'return_pct': returns.values
    })
    return result.dropna()


def compute_heatmap_data(monthly_returns):
    """生成热力图数据（年份 x 月份矩阵）"""
    pivot = monthly_returns.pivot_table(
        index='year', columns='month',
        values='return_pct', aggfunc='first'
    )
    return pivot


def compute_best_worst_months(monthly_returns):
    """各月平均收益率、最佳/最差月份、月胜率"""
    month_stats = monthly_returns.groupby('month').agg(
        avg_return=('return_pct', 'mean'),
        win_rate=('return_pct', lambda x: (x > 0).sum() / len(x) * 100)
    )
    best_month = month_stats['avg_return'].idxmax()
    worst_month = month_stats['avg_return'].idxmin()

    return {
        'monthly_avg': month_stats['avg_return'].to_dict(),
        'monthly_win_rate': month_stats['win_rate'].to_dict(),
        'best_month': best_month,
        'worst_month': worst_month,
        'best_month_avg': month_stats.loc[best_month, 'avg_return'],
        'worst_month_avg': month_stats.loc[worst_month, 'avg_return']
    }


def compute_seasonal_patterns(df):
    """季度分析、一月效应"""
    monthly = compute_monthly_returns(df)
    monthly['quarter'] = (monthly['month'] - 1) // 3 + 1

    quarterly = monthly.groupby('quarter')['return_pct'].mean()

    jan_effect = monthly[monthly['month'] == 1]['return_pct'].mean()
    rest_year = monthly[monthly['month'] != 1]['return_pct'].mean()

    return {
        'quarterly_avg': quarterly.to_dict(),
        'jan_avg': jan_effect,
        'rest_avg': rest_year,
        'jan_effect': jan_effect - rest_year
    }


MONTH_NAMES = ['一月', '二月', '三月', '四月', '五月', '六月',
               '七月', '八月', '九月', '十月', '十一月', '十二月']


def print_report(df):
    """打印季节性分析报告"""
    monthly = compute_monthly_returns(df)
    heatmap = compute_heatmap_data(monthly)
    bw = compute_best_worst_months(monthly)
    patterns = compute_seasonal_patterns(df)

    print("=" * 60)
    print("NASDAQ 季节性分析")
    print("=" * 60)

    print(f"\n最佳月份: {MONTH_NAMES[bw['best_month'] - 1]} (平均 {bw['best_month_avg']:+.2f}%)")
    print(f"最差月份: {MONTH_NAMES[bw['worst_month'] - 1]} (平均 {bw['worst_month_avg']:+.2f}%)")

    print("\n各月平均收益率:")
    for m in range(1, 13):
        avg = bw['monthly_avg'][m]
        wr = bw['monthly_win_rate'][m]
        bar = "+" * int(max(0, avg)) + "-" * int(max(0, -avg))
        print(f"  {MONTH_NAMES[m-1]:>4} {avg:>+7.2f}%  胜率: {wr:.0f}%  {bar}")

    print(f"\n季度平均收益率:")
    q_names = ['Q1', 'Q2', 'Q3', 'Q4']
    for q in range(1, 5):
        print(f"  {q_names[q-1]}: {patterns['quarterly_avg'][q]:+.2f}%")

    print(f"\n一月效应: {patterns['jan_effect']:+.2f}%")
    print(f"  一月平均: {patterns['jan_avg']:+.2f}%")
    print(f"  其他月份: {patterns['rest_avg']:+.2f}%")


def main():
    df = load_data()
    print_report(df)


if __name__ == "__main__":
    main()
