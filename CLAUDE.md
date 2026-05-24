# NASDAQ 综合指数深度分析项目

## 项目概述

基于 NASDAQ 1971-2026 年历史数据（13,941 条日线），构建交互式深度分析仪表盘。

## 数据

- **文件：** `E:\cc\maxs 01\nasdaq_complete_1971_2026.csv`
- **时间范围：** 1971-02-05 至 2026-05-22
- **字段：** date, open, high, low, close, volume, amount
- **数据质量：** 1971-2003 仅有收盘价（OHLC相同，volume=0）；2004+ 完整 OHLCV

## 文件结构

| 文件 | 状态 | 说明 |
|------|------|------|
| `analysis.py` | 已有 | 年度收益率控制台分析 |
| `visualization.py` | 已有 | 4张 matplotlib 静态图表 |
| `risk_metrics.py` | 已完成 | 最大回撤、波动率、夏普比率、熊市识别 |
| `technical_analysis.py` | 已完成 | SMA、金叉死叉、RSI、MACD、布林带（仅2004+） |
| `seasonal_analysis.py` | 已完成 | 月度收益率、热力图、季节性模式 |
| `cycle_analysis.py` | 已完成 | 牛熊周期识别、统计 |
| `crash_analysis.py` | 已完成 | 崩盘自动识别 + 历史事件知识库（7次重大崩盘） |
| `dashboard.py` | 已完成 | Plotly 交互式仪表盘主程序 |
| `dashboard_output.html` | 已生成 | 最终产出（8.3MB，10个图表，浏览器打开即用） |
| `DEVELOPMENT.md` | 已有 | 完整开发文档（含崩盘历史参考数据） |
| `requirements.txt` | 已有 | pandas, matplotlib, numpy, plotly |

## 开发进度

- [x] Phase 1: 安装 plotly
- [x] Phase 2: 5个分析模块
- [x] Phase 3: dashboard.py 仪表盘
- [ ] 用户查看效果后调优

## 下一步

用户查看 `dashboard_output.html` 后，根据反馈调整图表样式、内容或新增功能。

## 注意事项

- 技术指标（SMA/RSI/MACD/布林带）仅在 2004+ 数据上计算
- 全量分析（风险指标、季节性、周期）使用 close 列覆盖 1971-2026
- 中文字体使用 Microsoft YaHei（Windows 自带）
- Plotly.js 内联（8.3MB），完全离线可用
