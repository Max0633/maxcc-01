"""
NASDAQ 综合指数涨跌幅分析
分析 1971-2026 年的年度涨跌幅，找出涨跌幅最大的年份及原因
"""

import pandas as pd
import os

# 数据路径
DATA_PATH = r"E:\cc\maxs 01\nasdaq_complete_1971_2026.csv"


def load_data():
    """加载并预处理数据"""
    df = pd.read_csv(DATA_PATH)
    df['date'] = pd.to_datetime(df['date'])
    df['year'] = df['date'].dt.year
    return df


def calculate_yearly_returns(df):
    """计算年度涨跌幅"""
    # 取每年最后一个交易日的收盘价
    yearly = df.groupby('year')['close'].last().reset_index()
    yearly.columns = ['year', 'close']

    # 计算涨跌幅
    yearly['prev_close'] = yearly['close'].shift(1)
    yearly['return_pct'] = ((yearly['close'] - yearly['prev_close']) / yearly['prev_close']) * 100

    # 去掉第一年（没有上年数据）
    yearly = yearly.dropna(subset=['return_pct']).reset_index(drop=True)
    return yearly


def get_top_returns(yearly, n=5):
    """获取涨跌幅 Top N"""
    top_gainers = yearly.nlargest(n, 'return_pct')[['year', 'close', 'return_pct']]
    top_losers = yearly.nsmallest(n, 'return_pct')[['year', 'close', 'return_pct']]
    return top_gainers, top_losers


# 涨跌幅原因分析（基于历史知识）
REASONS = {
    # 跌幅年份
    2008: "全球金融危机：次贷危机引发雷曼兄弟破产，信贷市场冻结，全球经济陷入严重衰退",
    2000: "互联网泡沫破裂：科技股估值泡沫破灭，大量.com公司倒闭，投资者信心崩溃",
    2022: "美联储激进加息：为对抗通胀，美联储大幅加息，科技股估值承压",
    2001: "9·11恐怖袭击 + 互联网泡沫余波：恐怖袭击加剧经济不确定性，科技股持续下跌",
    2002: "世通公司丑闻 + 互联网泡沫延续：企业会计丑闻频发，市场信心持续低迷",
    1973: "石油危机：OPEC石油禁运导致油价暴涨，引发全球经济衰退",
    1974: "石油危机延续 + 水门事件：经济滞胀严重，政治不确定性加剧",
    2018: "中美贸易战：贸易摩擦升级，科技股承压，美联储加息",

    # 涨幅年份
    1999: "互联网泡沫顶峰：科技股狂热，投资者疯狂追捧互联网公司，纳斯达克突破5000点",
    2003: "经济复苏：伊拉克战争结束，低利率环境刺激经济回暖，科技股反弹",
    2009: "量化宽松政策：美联储实施QE，大量流动性注入市场，股市从金融危机低点反弹",
    2020: "疫情流动性泛滥：美联储零利率+无限QE，居家办公推动科技股暴涨",
    2023: "AI热潮：ChatGPT引爆人工智能投资热潮，科技巨头股价飙升",
    2021: "疫后复苏 + 超宽松货币政策：经济强劲复苏，科技股创历史新高",
    2019: "美联储转鸽：美联储暂停加息并降息，贸易摩擦缓和，科技股反弹",
    1995: "互联网兴起：Windows 95发布，互联网开始普及，科技股进入牛市",
    1998: "亚洲金融危机后的反弹：美联储降息，科技股加速上涨",
    2024: "AI持续驱动：人工智能投资持续升温，科技股表现强劲",
}


def analyze_reasons(top_gainers, top_losers):
    """分析涨跌幅原因"""
    print("\n" + "=" * 70)
    print("涨跌幅原因分析")
    print("=" * 70)

    print("\n【涨幅最大的年份】")
    print("-" * 70)
    for _, row in top_gainers.iterrows():
        year = int(row['year'])
        ret = row['return_pct']
        reason = REASONS.get(year, "暂无详细分析")
        print(f"\n{year}年 | 涨幅: {ret:+.2f}%")
        print(f"  原因: {reason}")

    print("\n\n【跌幅最大的年份】")
    print("-" * 70)
    for _, row in top_losers.iterrows():
        year = int(row['year'])
        ret = row['return_pct']
        reason = REASONS.get(year, "暂无详细分析")
        print(f"\n{year}年 | 跌幅: {ret:+.2f}%")
        print(f"  原因: {reason}")


def main():
    print("NASDAQ 综合指数年度涨跌幅分析")
    print("=" * 70)

    # 加载数据
    df = load_data()
    print(f"数据范围: {df['date'].min().date()} 至 {df['date'].max().date()}")
    print(f"总交易日: {len(df)}")

    # 计算年度涨跌幅
    yearly = calculate_yearly_returns(df)

    # 打印所有年度涨跌幅
    print("\n" + "=" * 70)
    print("年度涨跌幅一览")
    print("=" * 70)
    print(f"{'年份':<8} {'收盘价':>12} {'涨跌幅':>10}")
    print("-" * 35)
    for _, row in yearly.iterrows():
        year = int(row['year'])
        close = row['close']
        ret = row['return_pct']
        print(f"{year:<8} {close:>12.2f} {ret:>+9.2f}%")

    # Top 5 涨跌幅
    top_gainers, top_losers = get_top_returns(yearly, n=5)

    print("\n" + "=" * 70)
    print("涨幅 Top 5")
    print("=" * 70)
    print(f"{'排名':<6} {'年份':<8} {'收盘价':>12} {'涨幅':>10}")
    print("-" * 40)
    for i, (_, row) in enumerate(top_gainers.iterrows(), 1):
        print(f"{i:<6} {int(row['year']):<8} {row['close']:>12.2f} {row['return_pct']:>+9.2f}%")

    print("\n" + "=" * 70)
    print("跌幅 Top 5")
    print("=" * 70)
    print(f"{'排名':<6} {'年份':<8} {'收盘价':>12} {'跌幅':>10}")
    print("-" * 40)
    for i, (_, row) in enumerate(top_losers.iterrows(), 1):
        print(f"{i:<6} {int(row['year']):<8} {row['close']:>12.2f} {row['return_pct']:>+9.2f}%")

    # 原因分析
    analyze_reasons(top_gainers, top_losers)

    # 保存年度数据到 CSV
    output_path = os.path.join(os.path.dirname(__file__), "yearly_returns.csv")
    yearly.to_csv(output_path, index=False)
    print(f"\n\n年度涨跌幅数据已保存至: {output_path}")


if __name__ == "__main__":
    main()
