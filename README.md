# mysql-slow-query-analyzer-

# MySQL 慢查询分析与优化工具

一个基于 Python + MySQL 的慢查询自动分析工具。从 `performance_schema` 
自动采集慢查询，执行 `EXPLAIN` 分析执行计划，生成含索引建议的 Markdown 报告。

## 项目背景

MySQL 慢查询是后端性能问题的主要来源。手动分析需要：
1. 找到慢查询
2. 执行 EXPLAIN
3. 判断问题（全表扫描？临时表？文件排序？）
4. 给出索引建议

这个过程重复、繁琐。本项目把它自动化。

## 功能

- 从 `performance_schema.events_statements_summary_by_digest` 自动采集慢查询
- 对每条 SQL 执行 `EXPLAIN`，解析 type/key/rows/Extra 字段
- 识别常见问题：全表扫描、未命中索引、临时表、文件排序、JOIN 未走索引
- 自动生成索引建议（基于 WHERE 子句提取列）
- 输出 Markdown 格式报告

## 项目结构
├── config.example.py # 配置模板
├── collector.py # 采集模块
├── analyzer.py # 分析模块
├── reporter.py # 报告模块
├── main.py # 入口
├── scripts/ # 实验脚本
│ ├── import_olist.py
│ ├── exp1_join.py
│ └── exp2_range.py
└── docs/
└── experiments.md # 实验数据


## 快速开始

### 1. 环境要求

- Python 3.8+
- MySQL 8.0+

### 2. 安装依赖

```bash
pip install -r requirements.txt

### 3.快速开始

cp config.py
# 编辑 config.py，填入 MySQL 密码和数据库名

### 4.运行
python main.py
