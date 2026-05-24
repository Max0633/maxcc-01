"""
NASDAQ 历史重大跌幅深度分析
自动识别崩盘事件，关联历史事件知识库，生成结构化分析报告
"""

import pandas as pd
import numpy as np

DATA_PATH = r"E:\cc\maxs 01\nasdaq_complete_1971_2026.csv"

# 历史事件知识库
CRASH_KNOWLEDGE = {
    "1973-1974_oil_crisis": {
        "period": ("1973-01-11", "1974-10-03"),
        "peak": 136.84, "trough": 54.87, "max_drawdown": -59.9,
        "recovery_date": "1978-09-07", "recovery_days": 2065,
        "category": "外部冲击",
        "trigger": "OPEC石油禁运 + 尼克松水门事件",
        "fundamentals": "油价从$3暴涨至$12（4倍），企业利润被严重压缩；战后首次出现滞胀（经济停滞+高通胀并存）；美联储无法同时应对通胀和衰退",
        "key_events": ["1973-10-17: OPEC宣布石油禁运", "1974-08-09: 尼克松因水门事件辞职", "1974-10-03: 纳斯达克触及历史最低54.87"],
        "lesson": "外部供给冲击可引发深度衰退，滞胀环境是股市最恶劣的宏观组合"
    },
    "1987_black_monday": {
        "period": ("1987-08-26", "1987-10-28"),
        "peak": 455.26, "trough": 291.79, "max_drawdown": -35.9,
        "recovery_date": "1989-08-03", "recovery_days": 708,
        "category": "技术面踩踏",
        "trigger": "组合保险策略触发程序化交易连锁抛售",
        "fundamentals": "估值偏高但不极端，经济未衰退；流动性瞬间枯竭，做市商退出；前8个月涨40%，获利盘丰厚",
        "key_events": ["1987-10-19: 黑色星期一，道琼斯单日暴跌22.6%", "1987-10-28: 纳斯达克触及低点291"],
        "lesson": "技术面/流动性驱动的崩盘通常恢复较快，因经济基本面未受损"
    },
    "2000-2002_dot_com_crash": {
        "period": ("2000-03-10", "2002-10-09"),
        "peak": 5048.62, "trough": 1004.95, "max_drawdown": -79.7,
        "recovery_date": "2015-04-23", "recovery_days": 5522,
        "category": "泡沫破裂",
        "trigger": "互联网公司盈利证伪，估值泡沫破灭",
        "fundamentals": "市盈率普遍100x-500x，大量公司利润为负；烧钱获客但无法变现；风险投资枯竭，IPO市场关闭；安然/世通会计丑闻引爆信任危机",
        "key_events": ["2000-03-10: 纳斯达克触及5048历史高点", "2000-11-09: Pets.com破产", "2001-12-02: 安然申请破产", "2002-06-25: 世通财务造假曝光", "2002-10-09: 纳斯达克触及1004低点", "2015-04-23: 纳斯达克终于回到5000点"],
        "lesson": "没有盈利支撑的估值终将回归基本面，泡沫破裂后的恢复可能需要十年以上"
    },
    "2008_financial_crisis": {
        "period": ("2007-10-31", "2009-03-09"),
        "peak": 2861.51, "trough": 1268.64, "max_drawdown": -55.7,
        "recovery_date": "2015-03-02", "recovery_days": 2951,
        "category": "金融危机",
        "trigger": "次级抵押贷款崩溃引发全球银行系统性风险",
        "fundamentals": "银行间市场冻结，LIBOR飙升；房地产崩盘（跌幅30%+），失业率从4.7%飙至10%；金融股巨额亏损，非金融企业盈利骤降40%+",
        "key_events": ["2008-03-16: 贝尔斯登被收购", "2008-09-07: 美国政府接管两房", "2008-09-15: 雷曼兄弟破产", "2008-10-03: TARP计划通过（7000亿美元）", "2009-03-09: 纳斯达克触及危机低点1268"],
        "lesson": "系统性金融风险可从局部扩散至全球，流动性枯竭时所有资产同时下跌"
    },
    "2020_covid_crash": {
        "period": ("2020-02-19", "2020-03-23"),
        "peak": 9817.18, "trough": 6860.67, "max_drawdown": -30.1,
        "recovery_date": "2020-06-08", "recovery_days": 110,
        "category": "外部冲击",
        "trigger": "新冠疫情全球蔓延，经济停摆",
        "fundamentals": "全球封锁，GDP断崖式下跌；流动性危机（美元荒），连黄金和国债都被抛售；航空/酒店/零售收入归零",
        "key_events": ["2020-03-09: 美股第一次熔断", "2020-03-12: 第二次熔断", "2020-03-16: 第三次熔断", "2020-03-18: 第四次熔断（史上首次）", "2020-03-23: 纳斯达克触及低点6860", "2020-06-08: 纳斯达克收复失地（仅110天）"],
        "lesson": "政策应对速度决定恢复速度，美联储史无前例的反应使恢复仅用5个月"
    },
    "2022_rate_hike": {
        "period": ("2021-11-19", "2022-12-28"),
        "peak": 16057.44, "trough": 10203.99, "max_drawdown": -36.4,
        "recovery_date": "2024-02-29", "recovery_days": 832,
        "category": "政策收紧",
        "trigger": "美联储激进加息对抗通胀",
        "fundamentals": "美联储从0%加到5.25%，一年加息425个基点；CPI一度达9.1%（40年最高）；加密货币崩盘（Luna、FTX），风险资产全面承压",
        "key_events": ["2022-03-16: 美联储开启加息周期", "2022-06-15: 单次加息75bp（1994年以来最大）", "2022-09-13: CPI超预期，纳斯达克单日暴跌5.2%", "2022-11-08: FTX交易所破产", "2022-12-28: 纳斯达克触及年度低点10466"],
        "lesson": "估值杀（利率上升压低估值）与盈利杀不同，基本面未崩但流动性急剧收紧"
    },
    "2025_tariff_shock": {
        "period": ("2024-12-16", "2025-04-08"),
        "peak": 20173.89, "trough": 15267.05, "max_drawdown": -24.3,
        "recovery_date": None, "recovery_days": None,
        "category": "政策冲击",
        "trigger": "特朗普政府宣布对等关税，全球贸易战升级",
        "fundamentals": "关税推高进口成本，通胀预期上升；企业供应链成本上升，盈利预警；全球贸易体系受冲击",
        "key_events": ["2025-02-01: 美国对中国商品加征10%关税", "2025-04-02: 特朗普宣布对等关税方案", "2025-04-04: 中国反制加征34%关税", "2025-04-08: 纳斯达克触及低点15267"],
        "lesson": "政策不确定性本身可引发市场大幅波动，贸易战对科技供应链冲击尤为显著"
    }
}


def load_data():
    df = pd.read_csv(DATA_PATH)
    df['date'] = pd.to_datetime(df['date'])
    return df


def identify_crashes(prices, dates, min_drawdown=-20.0):
    """从数据中自动识别所有超过阈值的崩盘事件"""
    running_max = prices.expanding().max()
    drawdown = (prices - running_max) / running_max * 100

    crashes = []
    in_crash = False
    crash_peak_price = None
    crash_peak_date = None
    max_dd = 0
    max_dd_date = None
    max_dd_idx = 0

    for i in range(len(prices)):
        dd = drawdown.iloc[i]
        price = prices.iloc[i]
        date = dates.iloc[i]

        if dd <= min_drawdown and not in_crash:
            in_crash = True
            crash_peak_price = running_max.iloc[i]
            crash_peak_date = date
            max_dd = dd
            max_dd_date = date
            max_dd_idx = i
        elif in_crash:
            if dd < max_dd:
                max_dd = dd
                max_dd_date = date
                max_dd_idx = i
            if dd >= 0:
                crashes.append({
                    'peak_date': crash_peak_date,
                    'trough_date': max_dd_date,
                    'recovery_date': date,
                    'peak_price': crash_peak_price,
                    'trough_price': prices.iloc[max_dd_idx],
                    'recovery_price': price,
                    'max_drawdown': max_dd,
                    'crash_days': (max_dd_date - crash_peak_date).days,
                    'recovery_days': (date - max_dd_date).days,
                    'total_days': (date - crash_peak_date).days
                })
                in_crash = False

    if in_crash:
        crashes.append({
            'peak_date': crash_peak_date,
            'trough_date': max_dd_date,
            'recovery_date': None,
            'peak_price': crash_peak_price,
            'trough_price': prices.iloc[max_dd_idx],
            'recovery_price': None,
            'max_drawdown': max_dd,
            'crash_days': (max_dd_date - crash_peak_date).days,
            'recovery_days': None,
            'total_days': (dates.iloc[-1] - crash_peak_date).days
        })

    return pd.DataFrame(crashes)


def match_with_knowledge(crashes, knowledge_db):
    """将自动识别的崩盘事件与知识库匹配"""
    for idx, crash in crashes.iterrows():
        matched = False
        crash_year = crash['peak_date'].year
        trough_year = crash['trough_date'].year

        for key, info in knowledge_db.items():
            k_start = pd.Timestamp(info['period'][0])
            k_end = pd.Timestamp(info['period'][1])

            # 匹配条件：崩盘的高点或低点年份与知识库的高点或低点年份相同
            if (crash_year == k_start.year or crash_year == k_end.year or
                trough_year == k_start.year or trough_year == k_end.year):
                crashes.loc[idx, 'knowledge_key'] = key
                crashes.loc[idx, 'category'] = info['category']
                crashes.loc[idx, 'trigger'] = info['trigger']
                crashes.loc[idx, 'fundamentals'] = info['fundamentals']
                crashes.loc[idx, 'lesson'] = info['lesson']
                matched = True
                break

        if not matched:
            crashes.loc[idx, 'knowledge_key'] = None
            crashes.loc[idx, 'category'] = '其他'
            crashes.loc[idx, 'trigger'] = '暂无详细分析'
            crashes.loc[idx, 'fundamentals'] = '暂无'
            crashes.loc[idx, 'lesson'] = '暂无'
    return crashes


def get_category_stats(crashes):
    """按类别统计"""
    stats = crashes.groupby('category').agg(
        count=('max_drawdown', 'count'),
        avg_drawdown=('max_drawdown', 'mean'),
        avg_crash_days=('crash_days', 'mean'),
        avg_recovery_days=('recovery_days', 'mean')
    )
    return stats


def generate_crash_report(crashes, knowledge_db):
    """生成完整的文本报告"""
    crashes = match_with_knowledge(crashes, knowledge_db)

    lines = []
    lines.append("=" * 70)
    lines.append("NASDAQ 历史重大跌幅深度分析")
    lines.append("=" * 70)

    lines.append(f"\n共识别 {len(crashes)} 次重大崩盘事件（回撤超20%）\n")

    for idx, crash in crashes.iterrows():
        lines.append("-" * 70)
        key = crash.get('knowledge_key')
        if key and key in knowledge_db:
            info = knowledge_db[key]
            lines.append(f"【{info['category']}】{crash['peak_date'].strftime('%Y-%m-%d')} -> {crash['trough_date'].strftime('%Y-%m-%d')}")
        else:
            lines.append(f"【未知】{crash['peak_date'].strftime('%Y-%m-%d')} -> {crash['trough_date'].strftime('%Y-%m-%d')}")

        lines.append(f"  高点: {crash['peak_price']:.2f}  低点: {crash['trough_price']:.2f}")
        lines.append(f"  最大回撤: {crash['max_drawdown']:.1f}%")
        lines.append(f"  下跌持续: {crash['crash_days']}天")
        if pd.notna(crash.get('recovery_date')):
            lines.append(f"  恢复日期: {crash['recovery_date'].strftime('%Y-%m-%d')} (恢复用时 {crash['recovery_days']}天)")
        else:
            lines.append(f"  恢复日期: 尚未恢复")

        if pd.notna(crash.get('trigger')):
            lines.append(f"\n  触发因素: {crash['trigger']}")
        if pd.notna(crash.get('fundamentals')):
            lines.append(f"  基本面: {crash['fundamentals']}")
        if pd.notna(crash.get('lesson')):
            lines.append(f"  教训: {crash['lesson']}")

        if key and key in knowledge_db:
            lines.append(f"\n  关键事件:")
            for event in info['key_events']:
                lines.append(f"    - {event}")
        lines.append("")

    # 分类统计
    cat_stats = get_category_stats(crashes)
    lines.append("=" * 70)
    lines.append("按类别统计")
    lines.append("=" * 70)
    for cat, row in cat_stats.iterrows():
        lines.append(f"  {cat}: {int(row['count'])}次, 平均回撤 {row['avg_drawdown']:.1f}%, "
                     f"平均下跌 {row['avg_crash_days']:.0f}天, 平均恢复 {row['avg_recovery_days']:.0f}天")

    return "\n".join(lines)


def main():
    df = load_data()
    prices = df['close'].values
    prices_s = pd.Series(prices)
    dates = df['date']

    crashes = identify_crashes(prices_s, dates)
    report = generate_crash_report(crashes, CRASH_KNOWLEDGE)
    print(report)


if __name__ == "__main__":
    main()
