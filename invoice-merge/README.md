# 发票项目合并到第一项

电子发票里多行「项目名称」（如代订机票 / 退改费用 / 代订附加产品）**合并到第一项**，不再分开展示。

## 合并规则

1. **保留第一项的项目名称**（不拼接、不改名）
2. **金额、税额求和**；数量沿用第一项；单价按「金额 ÷ 数量」重算
3. **税率、单位等其它字段**沿用第一项
4. 发票合计金额 / 合计税额 / 价税合计不变

## 样例（两张携程机票票）

| 发票号码 | 合并前 | 合并后项目名称 | 金额 | 税额 |
|---------|--------|----------------|------|------|
| 26317000002585360901 | 3 行 | `*生产生活服务*代订机票` | 9217.92 | 553.08 |
| 26317000002585360900 | 2 行 | `*生产生活服务*代订机票产品` | 7483.96 | 449.04 |

## 使用

```bash
cd invoice-merge
python3 merge_items.py
# 输出 merged_invoices.json

python3 -m unittest test_merge_items.py -v

python3 -m http.server 8080
# 打开 http://localhost:8080 看前后对照
```

也可指定输入输出：

```bash
python3 merge_items.py -i sample_invoices.json -o merged_invoices.json
```

## 文件

| 文件 | 说明 |
|------|------|
| `merge_items.py` | 合并逻辑 CLI |
| `sample_invoices.json` | 原始多行明细 |
| `merged_invoices.json` | 合并结果 |
| `index.html` | 合并前后预览页 |
| `test_merge_items.py` | 单元测试 |
