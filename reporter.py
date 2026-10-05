# reporter.py
# 把分析结果写成 Markdown 报告

from datetime import datetime


def generate_report(analyses, output_path='report.md'):
    lines = []

    lines.append("# MySQL 慢查询分析报告\n")
    lines.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    lines.append(f"共分析 {len(analyses)} 条慢查询\n")
    lines.append("---\n")

    for i, item in enumerate(analyses, 1):
        q = item['query']
        a = item['analysis']

        lines.append(f"## 慢查询 #{i}\n")

        lines.append("### 原始 SQL\n")
        lines.append(f"```sql\n{a['sql']}\n```\n")

        lines.append("### 执行统计\n")
        lines.append(f"- 执行次数: {q['COUNT_STAR']}")
        lines.append(f"- 平均耗时: {q['avg_seconds']} 秒")
        lines.append(f"- 总耗时: {q['total_seconds']} 秒")
        lines.append(f"- 总扫描行数: {q['SUM_ROWS_EXAMINED']}")
        lines.append(f"- 总返回行数: {q['SUM_ROWS_SENT']}")
        lines.append(f"- 未用索引次数: {q['SUM_NO_INDEX_USED']}\n")

        lines.append("### EXPLAIN 结果\n")
        if a['explain']:
            lines.append("| table | type | key | rows | Extra |")
            lines.append("|---|---|---|---|---|")
            for r in a['explain']:
                lines.append(
                    f"| {r.get('table')} | {r.get('type')} | "
                    f"{r.get('key')} | {r.get('rows')} | {r.get('Extra')} |"
                )
        else:
            lines.append("(EXPLAIN 无结果)")
        lines.append("")

        lines.append("### 诊断\n")
        if a['issues']:
            for issue in a['issues']:
                lines.append(f"- {issue}")
        else:
            lines.append("- 未发现明显问题")
        lines.append("")

        lines.append("### 优化建议\n")
        if a['suggestions']:
            for s in a['suggestions']:
                lines.append(f"```sql\n{s}\n```")
        else:
            lines.append("暂无建议")
        lines.append("\n---\n")

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    print(f"\n报告已生成: {output_path}")