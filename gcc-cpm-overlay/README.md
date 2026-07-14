# Keeta O2O CPM × GCC 营销节点对照（2025）

把 TikTok for Business《2024 Node Marketing Insights - GCC》时间轴，叠加到 Keeta O2O CPM（Pangle/TikTok × Android/iOS）趋势上，观察节日与大促节点对应的 CPM 波动。

## 产出物

| 文件 | 说明 |
|------|------|
| `keeta_cpm_gcc_nodes_overlay.png` | 四象限叠加总图 |
| `node_cpm_analysis_table.png` | 节点对照结论表 |
| `index.html` + `data.json` | 可交互叠加页（悬停看节点） |
| `generate_overlay.py` | 复现图表的脚本 |

## 关键发现

1. **宰牲节 + 旅游季（6–7 月）**：年中共性抬升；**Pangle iOS** 6 月尖峰最猛。
2. **White Friday / UAE 国庆 / DSF（11 月底–12 月）**：**TikTok Android** 年末极端尖峰最突出。
3. **斋月 → 开斋节（约 2/28–4/1）**：3–4 月起量；iOS 侧更敏感。
4. **返校季 + 沙特国庆（8–9 月）**：TikTok iOS 9 月前后波动抬升。
5. **iOS vs Android**：iOS 全年波动更高；Android 更稳，但年末可爆量。

## 日期说明

原洞察图是 **2024** 节点；CPM 图是 **2025**。叠加时伊斯兰节日已按 2025 实际日期平移：

- 斋月：约 2025-02-28 → 2025-03-29
- 开斋节：约 2025-03-30
- 宰牲节：约 2025-06-06

CPM 曲线为截图形态复刻的**相对指数**，用于时间对齐，不代表真实出价金额。

## 本地预览交互页

```bash
cd gcc-cpm-overlay
python3 -m http.server 8080
# 打开 http://localhost:8080
```
