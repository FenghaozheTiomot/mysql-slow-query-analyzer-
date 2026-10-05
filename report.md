# MySQL 慢查询分析报告

生成时间: 2026-10-04 15:56:26

共分析 1 条慢查询

---

## 慢查询 #1

### 原始 SQL

```sql
SELECT * FROM `orders` WHERE `customer_id` = 1 AND STATUS = 1
```

### 执行统计

- 执行次数: 10
- 平均耗时: 0.0060 秒
- 总耗时: 0.060 秒
- 总扫描行数: 250004
- 总返回行数: 8
- 未用索引次数: 5

### EXPLAIN 结果

| table | type | key | rows | Extra |
|---|---|---|---|---|
| orders | ref | idx_customer_status | 6 | Using index condition |

### 诊断

- 未发现明显问题

### 优化建议

暂无建议

---
