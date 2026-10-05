一个基于 Python + MySQL 的慢查询自动分析工具。从 performance_schema 自动采集慢查询，执行 EXPLAIN 分析执行计划，生成含索引建议的 Markdown 报告。

## 项目背景

MySQL 慢查询是后端性能问题的主要来源。手动分析需要：

1. 找到慢查询
2. 执行 EXPLAIN
3. 判断问题（全表扫描？临时表？文件排序？）
4. 给出索引建议

这个过程重复、繁琐。本项目把它自动化。

## 功能

- 从 performance_schema.events_statements_summary_by_digest 自动采集慢查询
- 对每条 SQL 执行 EXPLAIN，解析 type/key/rows/Extra 字段
- 识别常见问题：全表扫描、未命中索引、临时表、文件排序、JOIN 未走索引
- 自动生成索引建议（基于 WHERE 子句提取列）
- 输出 Markdown 格式报告

## 项目结构

config.py # 配置模板
collector.py # 采集模块
analyzer.py # 分析模块
reporter.py # 报告模块
main.py # 入口
requirements.txt # 依赖清单
experiments.md # 实验数据与结论


## 快速开始

### 1. 环境要求

- Python 3.8+
- MySQL 8.0+

### 2. 安装依赖
pip install -r requirements.txt

### 3. 配置

复制配置模板并填入你的 MySQL 密码：
cp config.example.py config.py

然后编辑 config.py，填入 MySQL 密码和数据库名。

### 4. 运行
python main.py

生成的报告在 report.md。

## 实验数据

在 Olist 巴西电商数据集（10 万+ 行）上验证效果。

### 实验1：三表 JOIN（小结果集）

查询：找出某州客户的订单并汇总金额。

| 指标 | 优化前 | 优化后 |
|---|---|---|
| type | ALL, ALL, ALL | ref, ref, ref |
| key | NULL | idx_* |
| 扫描行数 | 30 万 | 83 |
| 耗时 | 0.18 秒 | 0.015 秒 |

优化方法：给 JOIN 关联列分别加索引。

### 实验2：范围查询（大范围 vs 小范围）

查询：
SELECT * FROM orders
WHERE order_purchase_timestamp BETWEEN ... AND order_status='delivered'

大范围（2017年全年，返回 4.3 万行，占全表 44%）：

| 指标 | 走索引 | 强制全扫 |
|---|---|---|
| type | ALL | ALL |
| key | idx_purchase_time_status | NULL |
| 耗时 | 0.38 秒 | 0.43 秒 |

发现：加了索引但 MySQL 主动放弃使用。

小范围（2017年1月，返回 686 行，占全表 0.7%）：

| 指标 | 走索引 | 强制全扫 |
|---|---|---|
| type | range | ALL |
| key | idx_purchase_time_status | NULL |
| 扫描行数 | 730 | 98271 |
| 耗时 | 0.011 秒 | 0.12 秒 |

结论：索引是否被使用取决于返回行数占全表的比例。返回行数占比高时，MySQL 优化器判断回表成本大于全表扫描，主动放弃索引。

## 技术要点

- performance_schema：MySQL 自带监控库，按 SQL 模板（digest）聚合统计
- EXPLAIN：查看 MySQL 的执行计划，关键字段 type/key/rows/Extra
- B+树索引：MySQL 索引的底层结构，支持快速等值查找和范围查找
- 联合索引：范围列在前、等值列在后，符合最左前缀原则
- 覆盖索引：查询列全在索引里，不需要回表
- 优化器成本计算：MySQL 根据返回行数占比决定是否使用索引

## 已知限制

- 索引建议只处理等值查询，不支持范围查询和 IN
- 参数替换用 1 可能类型不匹配
- 只支持单表分析，多表 JOIN 的索引建议较简单

## 后续计划

- [ ] 支持范围查询的索引建议
- [ ] 从慢查询日志补充原始参数
- [ ] 加入 HTML 报告输出

## License

MIT
