"""
NASDAQ 综合指数深度分析仪表盘
整合所有分析模块，生成自包含 HTML 交互式仪表盘
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio
import os

# 导入分析模块
import risk_metrics
import technical_analysis
import seasonal_analysis
import cycle_analysis
import crash_analysis

# 自定义 Plotly 极简模板
pio.templates['minimalist'] = pio.templates['plotly_white']
pio.templates['minimalist'].layout.update(
    font=dict(family='system-ui, -apple-system, Segoe UI, sans-serif', size=12, color='#374151'),
    paper_bgcolor='white',
    plot_bgcolor='white',
    xaxis=dict(gridcolor='#f3f4f6', zerolinecolor='#e5e7eb'),
    yaxis=dict(gridcolor='#f3f4f6', zerolinecolor='#e5e7eb'),
    margin=dict(l=60, r=20, t=40, b=40)
)

DATA_PATH = r"E:\cc\maxs 01\nasdaq_complete_1971_2026.csv"
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "dashboard_output.html")

# 月度名称
MONTH_NAMES = ['一月', '二月', '三月', '四月', '五月', '六月',
               '七月', '八月', '九月', '十月', '十一月', '十二月']

# 历史事件（复用 analysis.py 的知识库）
REASONS = {
    2008: "全球金融危机：次贷危机引发雷曼兄弟破产",
    2000: "互联网泡沫破裂：科技股估值泡沫破灭",
    2022: "美联储激进加息：为对抗通胀大幅加息",
    2001: "9·11恐怖袭击 + 互联网泡沫余波",
    2002: "世通公司丑闻 + 互联网泡沫延续",
    1973: "石油危机：OPEC石油禁运导致油价暴涨",
    1974: "石油危机延续 + 水门事件",
    1999: "互联网泡沫顶峰：科技股狂热",
    2003: "经济复苏：低利率环境刺激经济回暖",
    2009: "量化宽松政策：美联储实施QE",
    2020: "疫情流动性泛滥：美联储零利率+无限QE",
    2023: "AI热潮：ChatGPT引爆人工智能投资热潮",
    2021: "疫后复苏 + 超宽松货币政策",
    1995: "互联网兴起：Windows 95发布",
    1998: "亚洲金融危机后的反弹",
    2024: "AI持续驱动：人工智能投资持续升温",
    1987: "黑色星期一：程序化交易连锁抛售",
    1990: "海湾战争 + 储蓄信贷危机",
    1984: "利率高企 + 贸易赤字",
    1977: "能源危机余波",
    1978: "石油危机后续影响",
    1981: "美联储激进加息对抗通胀",
    1982: "经济衰退触底",
    1980: "第二次石油危机",
    1985: "广场协议 + 美元贬值",
    1986: "低利率环境",
    1988: "黑色星期一后恢复",
    1991: "海湾战争结束 + 经济复苏",
    1992: "经济复苏缓慢",
    1993: "经济温和增长",
    1994: "美联储加息周期",
    1996: "互联网商业化加速",
    1997: "亚洲金融危机",
    2004: "经济复苏 + 低利率",
    2005: "利率上升 + 房地产泡沫",
    2006: "房地产泡沫顶峰",
    2007: "次贷危机初现",
    2010: "QE1 + 经济复苏",
    2011: "欧债危机 + 美国评级下调",
    2012: "QE3 + 欧债危机缓解",
    2013: "QE持续 + 经济复苏",
    2014: "油价暴跌 + 经济增长",
    2015: "中国经济担忧 + 加息预期",
    2016: "英国脱欧 + 特朗普当选",
    2017: "税改预期 + 经济增长",
    2018: "中美贸易战 + 美联储加息",
    2019: "美联储转鸽 + 贸易摩擦缓和",
    2025: "关税冲击：特朗普宣布对等关税",
}

# 重大涨幅事件知识库（对齐 CRASH_KNOWLEDGE 结构）
GAIN_KNOWLEDGE = {
    "1999_dot_com_euphoria": {
        "period": ("1999-01-01", "1999-12-31"),
        "start_price": 2192.69, "end_price": 4069.31, "gain_pct": 85.6,
        "category": "投机狂热",
        "trigger": "互联网概念股全民狂热，散户蜂拥入市",
        "fundamentals": "Y2K恐慌后资金涌入科技股；纳斯达克IPO数量创纪录，首日涨幅动辄翻倍；思科、英特尔、微软市值冲击万亿美元；P/E普遍100x+，市场对未来收益极度乐观",
        "key_events": ["1999-01-01: Y2K恐慌消退，资金回流股市", "1999-04-07: 纳斯达克首次突破2500点", "1999-10-15: 纳斯达克突破3000点", "1999-12-31: 纳斯达克收于4069，年涨85.6%"],
        "lesson": "极端涨幅往往伴随极端估值，全民狂热是泡沫最可靠的信号"
    },
    "1991_gulf_war_recovery": {
        "period": ("1991-01-01", "1991-12-31"),
        "start_price": 490.46, "end_price": 769.05, "gain_pct": 56.8,
        "category": "战后复苏",
        "trigger": "海湾战争胜利 + 经济走出衰退",
        "fundamentals": "1990年储贷危机和海湾战争双重打击后经济触底；美联储降息至6%以下；伊拉克入侵科威特后油价先涨后跌，企业成本下降；科技股初露锋芒（Windows 3.0发布）",
        "key_events": ["1991-01-17: 海湾战争爆发，沙漠风暴行动开始", "1991-02-28: 海湾战争停火，市场大幅反弹", "1991-04-01: 美联储大幅降息", "1991-12-31: 纳斯达克年涨56.8%"],
        "lesson": "战争恐慌释放后的反弹往往迅猛，经济基本面韧性是关键"
    },
    "2003_post_bubble_recovery": {
        "period": ("2003-01-01", "2003-12-31"),
        "start_price": 1349.83, "end_price": 2017.97, "gain_pct": 49.5,
        "category": "泡沫后复苏",
        "trigger": "伊拉克战争不确定性消除 + 经济复苏确认",
        "fundamentals": "美联储维持1%超低利率；房地产市场繁荣带动财富效应；企业盈利在低基数上强劲反弹；伊拉克战争速战速决消除地缘不确定性",
        "key_events": ["2003-01-01: 纳斯达克处于泡沫破裂后低谷", "2003-03-20: 伊拉克战争爆发", "2003-05-01: 布什宣布主要战事结束", "2003-12-31: 纳斯达克年涨49.5%"],
        "lesson": "深度熊市后的复苏往往涨幅惊人，低利率环境是最大推手"
    },
    "2009_qe_rally": {
        "period": ("2009-01-01", "2009-12-31"),
        "start_price": 1577.03, "end_price": 2269.15, "gain_pct": 43.9,
        "category": "量化宽松",
        "trigger": "美联储QE1 + 金融危机后触底反弹",
        "fundamentals": "美联储2008年11月宣布QE1（购买1.25万亿MBS）；银行体系避免了全面崩溃；企业盈利在2009Q2触底后快速反弹；失业率虽高但市场定价'最坏已过'",
        "key_events": ["2009-03-09: 纳斯达克触及危机低点1268", "2009-03-18: 美联储宣布扩大QE规模", "2009-07-15: 财报季确认盈利反弹", "2009-12-31: 纳斯达克年涨43.9%"],
        "lesson": "央行无限火力是市场底部最可靠的信号，'别和美联储作对'再次验证"
    },
    "2020_covid_stimulus": {
        "period": ("2020-01-01", "2020-12-31"),
        "start_price": 9092.19, "end_price": 12888.28, "gain_pct": 43.6,
        "category": "流动性驱动",
        "trigger": "美联储零利率 + 无限QE + 财政刺激",
        "fundamentals": "美联储将利率降至0-0.25%，每月购买800亿美元国债+400亿MBS；国会通过 CARES 法案（2.2万亿美元）；居家办公推动科技股需求爆发；Zoom、特斯拉等成为新宠",
        "key_events": ["2020-03-23: 纳斯达克触及低点6860", "2020-03-27: CARES法案通过", "2020-04-30: 纳斯达克已收复年内失地", "2020-06-08: 纳斯达克创历史新高", "2020-12-31: 纳斯达克年涨43.6%"],
        "lesson": "央行+财政双重刺激的威力前所未有，流动性驱动的牛市可完全脱离基本面"
    },
    "2023_ai_revolution": {
        "period": ("2023-01-01", "2023-12-31"),
        "start_price": 10466.48, "end_price": 15011.35, "gain_pct": 43.4,
        "category": "AI革命",
        "trigger": "ChatGPT引爆人工智能投资热潮",
        "fundamentals": "OpenAI ChatGPT发布后用户破亿（史上最快）；英伟达GPU供不应求，股价年涨239%；微软、谷歌、Meta全面押注AI；AI概念股成为新主线，纳斯达克七巨头贡献大部分涨幅",
        "key_events": ["2023-01-01: ChatGPT发布两个月后全球关注", "2023-05-24: 英伟达财报超预期，单日涨24%", "2023-06-06: 英伟达市值破万亿美元", "2023-12-31: 纳斯达克年涨43.4%，七巨头主导"],
        "lesson": "技术革命可重塑市场格局，AI可能是继互联网后最大的科技浪潮"
    },
    "1995_internet_dawn": {
        "period": ("1995-01-01", "1995-12-31"),
        "start_price": 751.95, "end_price": 1052.14, "gain_pct": 39.9,
        "category": "科技黎明",
        "trigger": "互联网商业化元年 + Windows 95发布",
        "fundamentals": "Netscape 1995年8月IPO首日涨108%，点燃互联网投资热潮；Windows 95发布带动PC普及；美联储温和降息，经济软着陆；科技股从'小众'走向主流投资标的",
        "key_events": ["1995-01-01: 互联网商业化起步", "1995-08-09: Netscape IPO，首日翻倍", "1995-08-24: Windows 95发布，全球排队抢购", "1995-12-31: 纳斯达克年涨39.9%"],
        "lesson": "颠覆性技术的商业化初期往往孕育最大投资机会"
    },
}


def get_top_crashes(knowledge_db, n=7):
    """按 max_drawdown 排序取前 n 个最深崩盘"""
    sorted_crashes = sorted(knowledge_db.items(), key=lambda x: x[1]['max_drawdown'])
    return sorted_crashes[:n]


def get_top_gains(gain_knowledge, n=7):
    """按 gain_pct 排序取前 n 个最大涨幅"""
    sorted_gains = sorted(gain_knowledge.items(), key=lambda x: -x[1]['gain_pct'])
    return sorted_gains[:n]


def load_data():
    df = pd.read_csv(DATA_PATH)
    df['date'] = pd.to_datetime(df['date'])
    df['year'] = df['date'].dt.year
    return df


def calculate_yearly_returns(df):
    yearly = df.groupby('year')['close'].last().reset_index()
    yearly.columns = ['year', 'close']
    yearly['prev_close'] = yearly['close'].shift(1)
    yearly['return_pct'] = ((yearly['close'] - yearly['prev_close']) / yearly['prev_close']) * 100
    return yearly.dropna(subset=['return_pct']).reset_index(drop=True)


# ========== 图表构建函数 ==========

def build_price_chart(df, ohlcv_df, crosses_df):
    """图表1: 交互式价格走势图 + 成交量"""
    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.8, 0.2]
    )

    # 主图：收盘价
    fig.add_trace(go.Scatter(
        x=df['date'], y=df['close'],
        name='收盘价', line=dict(color='#1f77b4', width=1),
        hovertemplate='%{x|%Y-%m-%d}<br>价格: %{y:.2f}<extra></extra>'
    ), row=1, col=1)

    # SMA50（默认隐藏）
    if 'sma_50' in ohlcv_df.columns:
        fig.add_trace(go.Scatter(
            x=ohlcv_df.index, y=ohlcv_df['sma_50'],
            name='SMA50', line=dict(color='orange', width=1),
            visible='legendonly',
            hovertemplate='%{x|%Y-%m-%d}<br>SMA50: %{y:.2f}<extra></extra>'
        ), row=1, col=1)

    # SMA200（默认隐藏）
    if 'sma_200' in ohlcv_df.columns:
        fig.add_trace(go.Scatter(
            x=ohlcv_df.index, y=ohlcv_df['sma_200'],
            name='SMA200', line=dict(color='blue', width=1),
            visible='legendonly',
            hovertemplate='%{x|%Y-%m-%d}<br>SMA200: %{y:.2f}<extra></extra>'
        ), row=1, col=1)

    # 布林带（默认隐藏）
    if 'bb_upper' in ohlcv_df.columns:
        for col, name, color in [('bb_upper', '布林上轨', 'gray'), ('bb_middle', '布林中轨', 'gray'), ('bb_lower', '布林下轨', 'gray')]:
            dash = 'dash' if col != 'bb_middle' else 'solid'
            fig.add_trace(go.Scatter(
                x=ohlcv_df.index, y=ohlcv_df[col],
                name=name, line=dict(color=color, width=1, dash=dash),
                visible='legendonly',
                hovertemplate=f'%{{x|%Y-%m-%d}}<br>{name}: %{{y:.2f}}<extra></extra>'
            ), row=1, col=1)

    # 金叉标记
    if len(crosses_df) > 0:
        golden = crosses_df[crosses_df['type'] == 'golden']
        death = crosses_df[crosses_df['type'] == 'death']

        if len(golden) > 0:
            fig.add_trace(go.Scatter(
                x=golden['date'], y=golden['close'],
                name='金叉', mode='markers',
                marker=dict(symbol='triangle-up', size=10, color='green'),
                hovertemplate='%{x|%Y-%m-%d}<br>金叉<br>价格: %{y:.2f}<extra></extra>'
            ), row=1, col=1)

        if len(death) > 0:
            fig.add_trace(go.Scatter(
                x=death['date'], y=death['close'],
                name='死叉', mode='markers',
                marker=dict(symbol='triangle-down', size=10, color='red'),
                hovertemplate='%{x|%Y-%m-%d}<br>死叉<br>价格: %{y:.2f}<extra></extra>'
            ), row=1, col=1)

    # 成交量子图
    ohlcv_vol = ohlcv_df[ohlcv_df['volume'] > 0]
    colors = ['#2ecc71' if ohlcv_vol['close'].iloc[i] >= ohlcv_vol['close'].iloc[max(0, i-1)] else '#e74c3c'
              for i in range(len(ohlcv_vol))]
    fig.add_trace(go.Bar(
        x=ohlcv_vol.index, y=ohlcv_vol['volume'],
        name='成交量', marker_color=colors, opacity=0.6,
        hovertemplate='%{x|%Y-%m-%d}<br>成交量: %{y:,.0f}<extra></extra>'
    ), row=2, col=1)

    # 2004年分界线
    fig.add_shape(type="line", x0='2004-01-02', x1='2004-01-02',
                  y0=0, y1=1, yref='paper',
                  line=dict(color='gray', dash='dash', width=1))
    fig.add_annotation(x='2004-01-02', y=1, yref='paper',
                      text='OHLCV数据起始', showarrow=False,
                      font=dict(color='gray', size=10))

    fig.update_layout(
        title='NASDAQ 综合指数走势 (1971-2026)',
        height=700, template='minimalist',
        yaxis_type='log', yaxis_title='收盘价（对数坐标）',
        xaxis2_title='日期', yaxis2_title='成交量',
        legend=dict(x=0, y=1.02, orientation='h'),
        font=dict(family='system-ui, -apple-system, Segoe UI, sans-serif')
    )
    return fig


def build_drawdown_chart(drawdown_series, dates):
    """图表2: 历史回撤分析"""
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=dates, y=drawdown_series.values,
        fill='tozeroy', fillcolor='rgba(31, 119, 180, 0.3)',
        line=dict(color='#1f77b4', width=0.5),
        name='回撤幅度',
        hovertemplate='%{x|%Y-%m-%d}<br>回撤: %{y:.1f}%<extra></extra>'
    ))

    # 标注-20%线
    fig.add_hline(y=-20, line_dash='dash', line_color='red', opacity=0.5,
                  annotation_text='熊市阈值 (-20%)')

    fig.update_layout(
        title='历史回撤分析', height=400, template='minimalist',
        yaxis_title='回撤幅度 (%)', xaxis_title='日期',
        yaxis=dict(autorange='reversed'),
        font=dict(family='system-ui, -apple-system, Segoe UI, sans-serif')
    )
    return fig


def build_heatmap(heatmap_data):
    """图表3: 月度收益率热力图"""
    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data.values,
        x=[MONTH_NAMES[m - 1] for m in heatmap_data.columns],
        y=heatmap_data.index.astype(str),
        colorscale='RdYlGn',
        text=[[f'{v:.1f}%' if pd.notna(v) else '' for v in row] for row in heatmap_data.values],
        texttemplate='%{text}',
        textfont=dict(size=9),
        hovertemplate='年份: %{y}<br>月份: %{x}<br>收益率: %{z:.1f}%<extra></extra>',
        colorbar=dict(title='收益率(%)')
    ))

    fig.update_layout(
        title='月度收益率热力图 (年份 x 月份)',
        height=max(600, len(heatmap_data) * 12),
        template='minimalist',
        font=dict(family='system-ui, -apple-system, Segoe UI, sans-serif')
    )
    return fig


def build_cycle_timeline(cycles, current_regime):
    """图表4: 牛熊周期时间轴"""
    fig = go.Figure()

    for _, cycle in cycles.iterrows():
        color = '#2ecc71' if cycle['period_type'] == 'bull' else '#e74c3c'
        label = '牛市' if cycle['period_type'] == 'bull' else '熊市'
        ret_str = f"{cycle['return_pct']:+.1f}%" if pd.notna(cycle.get('return_pct')) else "进行中"
        dur_str = f"{cycle['duration_days']}天" if pd.notna(cycle.get('duration_days')) else "进行中"

        fig.add_trace(go.Bar(
            x=[cycle['duration_days'] or 1],
            y=[cycle['start_date'].strftime('%Y-%m')],
            base=[(cycle['start_date'] - pd.Timestamp('1971-01-01')).days],
            orientation='h',
            marker_color=color,
            name=f'{label} ({ret_str})',
            hovertemplate=f'{label}<br>起始: {cycle["start_date"].strftime("%Y-%m-%d")}<br>'
                         f'持续: {dur_str}<br>收益: {ret_str}<extra></extra>',
            showlegend=True,
            legendgroup=label
        ))

    fig.update_layout(
        title='市场牛熊周期', height=max(400, len(cycles) * 25),
        template='minimalist', barmode='stack',
        font=dict(family='system-ui, -apple-system, Segoe UI, sans-serif')
    )
    return fig


def build_crash_timeline(crashes_df, knowledge_db):
    """图表5a: 崩盘时间轴"""
    fig = go.Figure()

    category_colors = {
        '泡沫破裂': '#e74c3c', '金融危机': '#e67e22', '外部冲击': '#f1c40f',
        '政策收紧': '#3498db', '政策冲击': '#9b59b6', '技术面踩踏': '#1abc9c', '其他': '#95a5a6'
    }

    for _, crash in crashes_df.iterrows():
        cat = crash.get('category', '其他')
        color = category_colors.get(cat, '#95a5a6')
        trigger = crash.get('trigger', '暂无')

        fig.add_trace(go.Bar(
            x=[abs(crash['max_drawdown'])],
            y=[f"{crash['peak_date'].strftime('%Y-%m')} -> {crash['trough_date'].strftime('%Y-%m')}"],
            orientation='h',
            marker_color=color,
            name=f"{cat} ({crash['max_drawdown']:.1f}%)",
            hovertemplate=f"<b>{cat}</b><br>"
                         f"高点: {crash['peak_date'].strftime('%Y-%m-%d')}<br>"
                         f"低点: {crash['trough_date'].strftime('%Y-%m-%d')}<br>"
                         f"回撤: {crash['max_drawdown']:.1f}%<br>"
                         f"触发: {trigger}<extra></extra>",
            showlegend=True,
            legendgroup=cat
        ))

    fig.update_layout(
        title='历史崩盘深度分析', height=max(400, len(crashes_df) * 40),
        xaxis_title='最大回撤幅度 (%)', template='minimalist',
        font=dict(family='system-ui, -apple-system, Segoe UI, sans-serif')
    )
    return fig


def build_crash_comparison(crashes_df):
    """图表5b: 崩盘对比分析"""
    labels = [f"{c['peak_date'].strftime('%Y')}" for _, c in crashes_df.iterrows()]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=labels, y=[abs(c['max_drawdown']) for _, c in crashes_df.iterrows()],
        name='最大回撤 (%)', marker_color='#e74c3c',
        hovertemplate='%{x}年<br>回撤: %{y:.1f}%<extra></extra>'
    ))

    fig.add_trace(go.Bar(
        x=labels, y=[c['crash_days'] for _, c in crashes_df.iterrows()],
        name='下跌天数', marker_color='#e67e22',
        hovertemplate='%{x}年<br>下跌: %{y}天<extra></extra>'
    ))

    recovery_days = [c['recovery_days'] if pd.notna(c.get('recovery_days')) else 0 for _, c in crashes_df.iterrows()]
    fig.add_trace(go.Bar(
        x=labels, y=recovery_days,
        name='恢复天数', marker_color='#2ecc71',
        hovertemplate='%{x}年<br>恢复: %{y}天<extra></extra>'
    ))

    fig.update_layout(
        title='崩盘对比：回撤幅度 / 持续时间 / 恢复时间',
        height=400, template='minimalist', barmode='group',
        font=dict(family='system-ui, -apple-system, Segoe UI, sans-serif')
    )
    return fig


def build_rsi_chart(rsi_df):
    """图表6: RSI 相对强弱指标"""
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=rsi_df.index, y=rsi_df['rsi_14'],
        name='RSI(14)', line=dict(color='#1f77b4', width=1),
        hovertemplate='%{x|%Y-%m-%d}<br>RSI: %{y:.1f}<extra></extra>'
    ))

    fig.add_hline(y=70, line_dash='dash', line_color='red', opacity=0.5,
                  annotation_text='超买 (70)')
    fig.add_hline(y=30, line_dash='dash', line_color='green', opacity=0.5,
                  annotation_text='超卖 (30)')

    fig.update_layout(
        title='RSI 相对强弱指标 (14日)', height=300, template='minimalist',
        yaxis_title='RSI', xaxis_title='日期',
        yaxis=dict(range=[0, 100]),
        font=dict(family='system-ui, -apple-system, Segoe UI, sans-serif')
    )
    return fig


def build_macd_chart(macd_df):
    """图表7: MACD 指标"""
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=macd_df.index, y=macd_df['macd'],
        name='MACD', line=dict(color='#1f77b4', width=1),
        hovertemplate='%{x|%Y-%m-%d}<br>MACD: %{y:.2f}<extra></extra>'
    ))

    fig.add_trace(go.Scatter(
        x=macd_df.index, y=macd_df['macd_signal'],
        name='信号线', line=dict(color='orange', width=1),
        hovertemplate='%{x|%Y-%m-%d}<br>信号线: %{y:.2f}<extra></extra>'
    ))

    colors = ['#2ecc71' if v >= 0 else '#e74c3c' for v in macd_df['macd_histogram']]
    fig.add_trace(go.Bar(
        x=macd_df.index, y=macd_df['macd_histogram'],
        name='柱状图', marker_color=colors, opacity=0.6,
        hovertemplate='%{x|%Y-%m-%d}<br>柱状图: %{y:.2f}<extra></extra>'
    ))

    fig.update_layout(
        title='MACD 指标', height=300, template='minimalist',
        yaxis_title='MACD', xaxis_title='日期',
        font=dict(family='system-ui, -apple-system, Segoe UI, sans-serif')
    )
    return fig


def build_yearly_returns_chart(yearly_returns):
    """图表8: 年度涨跌幅"""
    colors = ['#2ecc71' if x >= 0 else '#e74c3c' for x in yearly_returns['return_pct']]

    hover_texts = []
    for _, row in yearly_returns.iterrows():
        year = int(row['year'])
        ret = row['return_pct']
        reason = REASONS.get(year, '')
        hover_texts.append(f"{year}年<br>收益率: {ret:+.1f}%<br>{reason}")

    fig = go.Figure(go.Bar(
        x=yearly_returns['year'],
        y=yearly_returns['return_pct'],
        marker_color=colors,
        text=[f"{v:+.1f}%" for v in yearly_returns['return_pct']],
        textposition='outside',
        hovertext=hover_texts,
        hoverinfo='text'
    ))

    fig.update_layout(
        title='NASDAQ 年度涨跌幅 (1972-2026)', height=400, template='minimalist',
        xaxis_title='年份', yaxis_title='涨跌幅 (%)',
        xaxis=dict(dtick=5),
        font=dict(family='system-ui, -apple-system, Segoe UI, sans-serif')
    )
    return fig


def build_risk_metrics_panel(metrics, bears, current_regime):
    """生成风险指标卡片 HTML"""
    cards = [
        ("Max Drawdown", f"{metrics['max_drawdown']:.1f}%"),
        ("Volatility", f"{metrics['volatility']*100:.1f}%"),
        ("Sharpe Ratio", f"{metrics['sharpe']:.2f}"),
        ("Bear Markets", f"{metrics['bear_count']}"),
    ]

    card_html = ''
    for label, value in cards:
        card_html += f'''
        <div class="metric-card">
            <div class="metric-value">{value}</div>
            <div class="metric-label">{label}</div>
        </div>'''

    # 当前状态
    regime_label = 'Bull Market' if current_regime['regime'] == 'bull' else 'Bear Market'
    regime_color = '#16a34a' if current_regime['regime'] == 'bull' else '#dc2626'
    if current_regime['regime'] == 'bull':
        regime_detail = f"{current_regime['duration_days']}d, {current_regime['current_gain']:+.1f}%"
    else:
        regime_detail = f"{current_regime['duration_days']}d, {current_regime['current_drawdown']:.1f}%"

    card_html += f'''
    <div class="metric-card">
        <div class="metric-value" style="color: {regime_color};">{regime_label}</div>
        <div class="metric-label">{regime_detail}</div>
    </div>'''

    return card_html


def build_events_section_html(top_crashes, top_gains):
    """生成重大涨跌事件板块 HTML（纯 HTML/CSS，非 Plotly）"""
    category_colors = {
        '泡沫破裂': '#e74c3c', '金融危机': '#e67e22', '外部冲击': '#f39c12',
        '政策收紧': '#3498db', '政策冲击': '#9b59b6', '技术面踩踏': '#1abc9c',
        '投机狂热': '#e74c3c', '战后复苏': '#27ae60', '泡沫后复苏': '#2ecc71',
        '量化宽松': '#3498db', '流动性驱动': '#2980b9', 'AI革命': '#8e44ad',
        '科技黎明': '#16a085', '其他': '#95a5a6'
    }

    def make_event_card(item, is_crash=True):
        key, data = item
        cat = data.get('category', '其他')
        color = category_colors.get(cat, '#95a5a6')

        if is_crash:
            period = data['period']
            change_str = f"{data['max_drawdown']:.1f}%"
            price_str = f"{data['peak']:.0f} → {data['trough']:.0f}"
            change_color = '#dc2626'
        else:
            period = data['period']
            change_str = f"+{data['gain_pct']:.1f}%"
            price_str = f"{data['start_price']:.0f} → {data['end_price']:.0f}"
            change_color = '#16a34a'

        events_li = ''.join(f'<li>{e}</li>' for e in data.get('key_events', []))

        return f'''
        <div class="event-card">
            <div class="event-header">
                <span class="event-tag" style="background: {color}20; color: {color}; border: 1px solid {color}40;">{cat}</span>
                <span class="event-date">{period[0]} — {period[1]}</span>
            </div>
            <div class="event-change" style="color: {change_color};">{change_str}</div>
            <div class="event-prices">{price_str}</div>
            <div class="event-field">
                <span class="event-label">Trigger</span>
                <span class="event-value">{data['trigger']}</span>
            </div>
            <div class="event-field">
                <span class="event-label">Fundamentals</span>
                <span class="event-value">{data['fundamentals']}</span>
            </div>
            <div class="event-field">
                <span class="event-label">Key Events</span>
                <ul class="event-timeline">{events_li}</ul>
            </div>
            <div class="event-field">
                <span class="event-label">Lesson</span>
                <span class="event-value event-lesson">{data['lesson']}</span>
            </div>
        </div>'''

    # 左栏：最大跌幅
    crash_cards = ''.join(make_event_card(item, is_crash=True) for item in top_crashes)
    # 右栏：最大涨幅
    gain_cards = ''.join(make_event_card(item, is_crash=False) for item in top_gains)

    return f'''
    <div class="events-grid">
        <div class="events-column">
            <h3 class="events-col-title">Largest Declines <span class="events-col-sub">最大跌幅</span></h3>
            {crash_cards}
        </div>
        <div class="events-column">
            <h3 class="events-col-title">Largest Gains <span class="events-col-sub">最大涨幅</span></h3>
            {gain_cards}
        </div>
    </div>'''


# ========== 主函数 ==========

def main():
    print("NASDAQ 综合指数深度分析仪表盘")
    print("=" * 50)

    # 加载数据
    df = load_data()
    yearly = calculate_yearly_returns(df)

    # 风险指标
    prices_s = pd.Series(df['close'].values)
    dates = df['date']
    dd_series = risk_metrics.compute_drawdown_series(prices_s)
    dd_info = risk_metrics.compute_max_drawdown(prices_s, dates)
    vol = risk_metrics.compute_annualized_volatility(prices_s)
    sharpe = risk_metrics.compute_sharpe_ratio(prices_s)
    bears = risk_metrics.compute_bear_markets(prices_s, dates)
    cycles = cycle_analysis.identify_bull_bear_markets(prices_s, dates)
    current_regime = cycle_analysis.identify_current_regime(prices_s, dates, cycles)

    metrics = {
        'max_drawdown': dd_info['max_drawdown_pct'],
        'volatility': vol,
        'sharpe': sharpe,
        'bear_count': len(bears)
    }

    # 技术分析（仅 2004+）
    ohlcv = technical_analysis.prepare_ohlcv(df)
    ohlcv_ind = technical_analysis.compute_sma(ohlcv, [50, 200])
    ohlcv_ind = technical_analysis.compute_rsi(ohlcv_ind)
    ohlcv_ind = technical_analysis.compute_macd(ohlcv_ind)
    ohlcv_ind = technical_analysis.compute_bollinger_bands(ohlcv_ind)
    crosses = technical_analysis.compute_golden_death_crosses(ohlcv)

    # 季节性分析
    monthly_returns = seasonal_analysis.compute_monthly_returns(df)
    heatmap_data = seasonal_analysis.compute_heatmap_data(monthly_returns)

    # 崩盘分析
    crashes = crash_analysis.identify_crashes(prices_s, dates)
    crashes = crash_analysis.match_with_knowledge(crashes, crash_analysis.CRASH_KNOWLEDGE)

    # 构建所有图表
    print("\n构建图表...")
    figs = []
    figs.append(build_price_chart(df, ohlcv_ind, crosses))
    figs.append(build_drawdown_chart(dd_series, dates))
    figs.append(build_heatmap(heatmap_data))
    figs.append(build_cycle_timeline(cycles, current_regime))
    figs.append(build_crash_timeline(crashes, crash_analysis.CRASH_KNOWLEDGE))
    figs.append(build_crash_comparison(crashes))
    figs.append(build_rsi_chart(ohlcv_ind))
    figs.append(build_macd_chart(ohlcv_ind))
    figs.append(build_yearly_returns_chart(yearly))

    # 风险指标面板
    metrics_html = build_risk_metrics_panel(metrics, bears, current_regime)

    # 重大事件板块
    top_crashes = get_top_crashes(crash_analysis.CRASH_KNOWLEDGE, n=7)
    top_gains = get_top_gains(GAIN_KNOWLEDGE, n=7)
    events_html = build_events_section_html(top_crashes, top_gains)

    # 生成 HTML
    print("生成 HTML...")
    divs = []
    for i, fig in enumerate(figs):
        include_js = (i == 0)
        div = pio.to_html(fig, full_html=False, include_plotlyjs=include_js)
        divs.append(div)

    # 图表标题 + id
    chart_sections = [
        ("price", "Price Trend & Volume", "价格走势 + 成交量"),
        ("drawdown", "Historical Drawdown", "历史回撤分析"),
        ("seasonal", "Monthly Returns Heatmap", "月度收益率热力图"),
        ("cycles", "Bull / Bear Cycles", "牛熊周期"),
        ("crash-depth", "Crash Depth Analysis", "崩盘深度分析"),
        ("crash-compare", "Crash Comparison", "崩盘对比"),
        ("rsi", "RSI Indicator", "RSI 指标"),
        ("macd", "MACD Indicator", "MACD 指标"),
        ("yearly", "Annual Returns", "年度涨跌幅"),
    ]

    sections = ""
    for (sec_id, en_title, cn_title), div in zip(chart_sections, divs):
        sections += f'<div class="section" id="{sec_id}"><h2>{en_title} <span class="section-sub">{cn_title}</span></h2>{div}</div>\n'

    date_range = f"{df['date'].min().strftime('%Y-%m-%d')} — {df['date'].max().strftime('%Y-%m-%d')}"

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NASDAQ Composite — Deep Analysis</title>
    <style>
        *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;
            background: #ffffff; color: #111827; line-height: 1.5;
            -webkit-font-smoothing: antialiased;
        }}
        .container {{ max-width: 1400px; margin: 0 auto; padding: 0 32px; }}

        /* ---- Navigation ---- */
        .nav-bar {{
            position: sticky; top: 0; z-index: 100;
            background: rgba(255,255,255,0.92); backdrop-filter: blur(12px);
            border-bottom: 1px solid #e5e7eb;
        }}
        .nav-inner {{
            max-width: 1400px; margin: 0 auto; padding: 0 32px;
            display: flex; align-items: center; gap: 24px;
            overflow-x: auto; white-space: nowrap;
            scrollbar-width: none;
        }}
        .nav-inner::-webkit-scrollbar {{ display: none; }}
        .nav-brand {{ font-weight: 700; font-size: 14px; color: #111827; flex-shrink: 0; padding: 12px 0; }}
        .nav-bar a {{
            font-size: 13px; color: #6b7280; text-decoration: none;
            padding: 12px 0; border-bottom: 2px solid transparent;
            transition: color 0.15s, border-color 0.15s; flex-shrink: 0;
        }}
        .nav-bar a:hover {{ color: #111827; border-bottom-color: #d1d5db; }}

        /* ---- Header ---- */
        .header {{ padding: 48px 0 32px; }}
        .header h1 {{
            font-size: 36px; font-weight: 700; color: #111827;
            letter-spacing: -0.02em; margin-bottom: 8px;
        }}
        .header .subtitle {{ font-size: 15px; color: #6b7280; }}

        /* ---- Metrics Panel ---- */
        .metrics-panel {{
            display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 0; border-top: 1px solid #e5e7eb; border-bottom: 1px solid #e5e7eb;
            margin: 0 0 48px;
        }}
        .metric-card {{
            padding: 24px 0; text-align: left;
            border-right: 1px solid #f3f4f6;
        }}
        .metric-card:last-child {{ border-right: none; }}
        .metric-value {{
            font-size: 32px; font-weight: 600; color: #111827;
            letter-spacing: -0.02em;
        }}
        .metric-label {{
            font-size: 11px; text-transform: uppercase; letter-spacing: 0.06em;
            color: #9ca3af; margin-top: 4px;
        }}

        /* ---- Sections ---- */
        .section {{ padding: 40px 0; border-bottom: 1px solid #f3f4f6; }}
        .section:last-child {{ border-bottom: none; }}
        .section h2 {{
            font-size: 20px; font-weight: 600; color: #111827;
            margin-bottom: 20px; letter-spacing: -0.01em;
        }}
        .section-sub {{ font-weight: 400; color: #9ca3af; font-size: 14px; margin-left: 8px; }}

        /* ---- Events Grid ---- */
        .events-grid {{
            display: grid; grid-template-columns: 1fr 1fr; gap: 48px;
        }}
        .events-col-title {{
            font-size: 18px; font-weight: 600; color: #111827;
            margin-bottom: 24px; padding-bottom: 12px;
            border-bottom: 1px solid #e5e7eb;
        }}
        .events-col-sub {{ font-weight: 400; color: #9ca3af; font-size: 13px; margin-left: 6px; }}
        .event-card {{
            padding: 20px 0; border-bottom: 1px solid #f3f4f6;
        }}
        .event-card:last-child {{ border-bottom: none; }}
        .event-header {{ display: flex; align-items: center; gap: 12px; margin-bottom: 8px; }}
        .event-tag {{
            display: inline-block; padding: 2px 8px; border-radius: 4px;
            font-size: 11px; font-weight: 500; text-transform: uppercase;
            letter-spacing: 0.04em;
        }}
        .event-date {{ font-size: 13px; color: #9ca3af; }}
        .event-change {{ font-size: 24px; font-weight: 700; letter-spacing: -0.02em; }}
        .event-prices {{ font-size: 13px; color: #6b7280; margin-bottom: 12px; }}
        .event-field {{ margin-bottom: 10px; }}
        .event-label {{
            display: block; font-size: 11px; text-transform: uppercase;
            letter-spacing: 0.06em; color: #9ca3af; margin-bottom: 2px;
            font-weight: 500;
        }}
        .event-value {{ font-size: 14px; color: #374151; line-height: 1.6; }}
        .event-lesson {{ font-style: italic; color: #6b7280; }}
        .event-timeline {{
            list-style: none; padding: 0; margin: 4px 0 0;
        }}
        .event-timeline li {{
            font-size: 13px; color: #374151; padding: 3px 0;
            padding-left: 16px; position: relative; line-height: 1.5;
        }}
        .event-timeline li::before {{
            content: ''; position: absolute; left: 0; top: 10px;
            width: 6px; height: 6px; border-radius: 50%;
            background: #d1d5db;
        }}

        /* ---- Footer ---- */
        .footer {{
            padding: 32px 0; text-align: center;
            font-size: 12px; color: #9ca3af;
            border-top: 1px solid #f3f4f6; margin-top: 24px;
        }}

        /* ---- Responsive ---- */
        @media (max-width: 768px) {{
            .container {{ padding: 0 16px; }}
            .header h1 {{ font-size: 24px; }}
            .events-grid {{ grid-template-columns: 1fr; gap: 32px; }}
            .metrics-panel {{ grid-template-columns: 1fr 1fr; }}
            .metric-card {{ border-right: none; border-bottom: 1px solid #f3f4f6; }}
        }}
    </style>
</head>
<body>
    <nav class="nav-bar">
        <div class="nav-inner">
            <span class="nav-brand">NASDAQ</span>
            <a href="#overview">Overview</a>
            <a href="#events">Major Events</a>
            <a href="#price">Price</a>
            <a href="#drawdown">Drawdown</a>
            <a href="#seasonal">Seasonal</a>
            <a href="#cycles">Cycles</a>
            <a href="#crash-depth">Crashes</a>
            <a href="#crash-compare">Compare</a>
            <a href="#rsi">RSI</a>
            <a href="#macd">MACD</a>
            <a href="#yearly">Annual</a>
        </div>
    </nav>

    <div class="container">
        <header class="header" id="overview">
            <h1>NASDAQ Composite Index</h1>
            <p class="subtitle">Deep Analysis Dashboard &middot; {date_range} &middot; {len(df):,} trading days</p>
        </header>

        <div class="metrics-panel">
            {metrics_html}
        </div>

        <div class="section" id="events">
            <h2>Major Events <span class="section-sub">重大涨跌事件</span></h2>
            {events_html}
        </div>

        {sections}

        <div class="footer">
            NASDAQ Composite Deep Analysis &middot; Data: {date_range} &middot; Generated {pd.Timestamp.now().strftime('%Y-%m-%d')}
        </div>
    </div>
</body>
</html>"""

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"\n仪表盘已生成: {OUTPUT_FILE}")
    print(f"文件大小: {os.path.getsize(OUTPUT_FILE) / 1024 / 1024:.1f} MB")


if __name__ == "__main__":
    main()
