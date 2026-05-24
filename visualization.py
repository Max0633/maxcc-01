"""
NASDAQ 综合指数可视化
生成历史走势、年度涨跌幅、Top涨跌幅、年代收益分布图表
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import os

# 设置中文字体（Windows）
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 数据路径
DATA_PATH = r"E:\cc\maxs 01\nasdaq_complete_1971_2026.csv"

# 输出目录
CHARTS_DIR = os.path.join(os.path.dirname(__file__), "charts")


def load_data():
    """加载并预处理数据"""
    df = pd.read_csv(DATA_PATH)
    df['date'] = pd.to_datetime(df['date'])
    df['year'] = df['date'].dt.year
    return df


def calculate_yearly_returns(df):
    """计算年度涨跌幅"""
    yearly = df.groupby('year')['close'].last().reset_index()
    yearly.columns = ['year', 'close']
    yearly['prev_close'] = yearly['close'].shift(1)
    yearly['return_pct'] = ((yearly['close'] - yearly['prev_close']) / yearly['prev_close']) * 100
    yearly = yearly.dropna(subset=['return_pct']).reset_index(drop=True)
    return yearly


def plot_trend(df):
    """图表1: 历史走势线图"""
    fig, ax = plt.subplots(figsize=(14, 6))
    ax.plot(df['date'], df['close'], color='#1f77b4', linewidth=0.8)
    ax.set_yscale('log')
    ax.set_title('NASDAQ 综合指数 (1971-2026)', fontsize=16, fontweight='bold')
    ax.set_xlabel('日期', fontsize=12)
    ax.set_ylabel('收盘价（对数坐标）', fontsize=12)
    ax.grid(True, alpha=0.3)

    # 标注历史低点和高点
    low_idx = df['close'].idxmin()
    high_idx = df['close'].idxmin()
    high_idx = df['close'].idxmax()
    ax.annotate(f'最低: {df.loc[low_idx, "close"]:.2f}\n({df.loc[low_idx, "date"].strftime("%Y-%m-%d")})',
                xy=(df.loc[low_idx, 'date'], df.loc[low_idx, 'close']),
                xytext=(50, 30), textcoords='offset points',
                arrowprops=dict(arrowstyle='->', color='red'),
                fontsize=9, color='red')
    ax.annotate(f'最高: {df.loc[high_idx, "close"]:.2f}\n({df.loc[high_idx, "date"].strftime("%Y-%m-%d")})',
                xy=(df.loc[high_idx, 'date'], df.loc[high_idx, 'close']),
                xytext=(-100, -40), textcoords='offset points',
                arrowprops=dict(arrowstyle='->', color='green'),
                fontsize=9, color='green')

    plt.tight_layout()
    path = os.path.join(CHARTS_DIR, 'nasdaq_trend.png')
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {path}")


def plot_yearly_returns(yearly):
    """图表2: 年度涨跌幅柱状图"""
    fig, ax = plt.subplots(figsize=(16, 6))

    colors = ['#2ecc71' if x >= 0 else '#e74c3c' for x in yearly['return_pct']]
    bars = ax.bar(yearly['year'], yearly['return_pct'], color=colors, width=0.8)

    ax.axhline(y=0, color='black', linewidth=0.5)
    ax.set_title('NASDAQ 年度涨跌幅 (1972-2026)', fontsize=16, fontweight='bold')
    ax.set_xlabel('年份', fontsize=12)
    ax.set_ylabel('涨跌幅 (%)', fontsize=12)
    ax.grid(True, axis='y', alpha=0.3)

    # 每5年显示一个标签
    ax.xaxis.set_major_locator(ticker.MultipleLocator(5))
    plt.xticks(rotation=45)

    plt.tight_layout()
    path = os.path.join(CHARTS_DIR, 'yearly_returns.png')
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {path}")


def plot_top_returns(yearly):
    """图表3: 涨跌幅 Top 5 条形图"""
    top_gainers = yearly.nlargest(5, 'return_pct')
    top_losers = yearly.nsmallest(5, 'return_pct')

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # 涨幅 Top 5
    y_labels = [f"{int(y)}" for y in top_gainers['year']]
    bars1 = ax1.barh(y_labels, top_gainers['return_pct'], color='#2ecc71')
    ax1.set_xlabel('涨跌幅 (%)', fontsize=12)
    ax1.set_title('年度涨幅 Top 5', fontsize=14, fontweight='bold')
    ax1.invert_yaxis()
    for bar, val in zip(bars1, top_gainers['return_pct']):
        ax1.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
                 f'{val:.1f}%', va='center', fontsize=10, fontweight='bold')

    # 跌幅 Top 5
    y_labels = [f"{int(y)}" for y in top_losers['year']]
    bars2 = ax2.barh(y_labels, top_losers['return_pct'], color='#e74c3c')
    ax2.set_xlabel('涨跌幅 (%)', fontsize=12)
    ax2.set_title('年度跌幅 Top 5', fontsize=14, fontweight='bold')
    ax2.invert_yaxis()
    for bar, val in zip(bars2, top_losers['return_pct']):
        ax2.text(bar.get_width() - 0.5, bar.get_y() + bar.get_height()/2,
                 f'{val:.1f}%', va='center', ha='right', fontsize=10, fontweight='bold')

    plt.tight_layout()
    path = os.path.join(CHARTS_DIR, 'top_returns.png')
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {path}")


def plot_decade_boxplot(yearly):
    """图表4: 各年代收益箱线图"""
    yearly = yearly.copy()
    yearly['decade'] = (yearly['year'] // 10) * 10
    yearly['decade_label'] = yearly['decade'].astype(str) + 's'

    decades = sorted(yearly['decade'].unique())
    data = [yearly[yearly['decade'] == d]['return_pct'].values for d in decades]
    labels = [f"{d}s" for d in decades]

    fig, ax = plt.subplots(figsize=(12, 6))
    bp = ax.boxplot(data, tick_labels=labels, patch_artist=True)

    colors = plt.cm.Set3(range(len(decades)))
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)

    ax.axhline(y=0, color='black', linewidth=0.5, linestyle='--')
    ax.set_title('NASDAQ 各年代收益分布', fontsize=16, fontweight='bold')
    ax.set_xlabel('年代', fontsize=12)
    ax.set_ylabel('年化收益率 (%)', fontsize=12)
    ax.grid(True, axis='y', alpha=0.3)

    plt.tight_layout()
    path = os.path.join(CHARTS_DIR, 'decade_boxplot.png')
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {path}")


def main():
    print("NASDAQ 综合指数可视化")
    print("=" * 50)

    # 创建输出目录
    os.makedirs(CHARTS_DIR, exist_ok=True)

    # 加载数据
    df = load_data()
    yearly = calculate_yearly_returns(df)

    # 生成图表
    print("\nGenerating charts...")
    plot_trend(df)
    plot_yearly_returns(yearly)
    plot_top_returns(yearly)
    plot_decade_boxplot(yearly)

    print(f"\nAll charts saved to: {CHARTS_DIR}")


if __name__ == "__main__":
    main()
