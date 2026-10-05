# analyzer.py
# 对每条慢查询执行 EXPLAIN，并诊断问题

import re


def analyze(conn, digest_text):
    """
    输入：一条 SQL 模板（带 ? 占位符）
    输出：{
        'sql': 替换占位符后的 SQL,
        'explain': EXPLAIN 结果,
        'issues': 诊断信息列表,
        'suggestions': 索引建议列表
    }
    """
    # performance_schema 里的 SQL 带 ?，EXPLAIN 需要具体值，这里简单替换成 1
    sql = digest_text.replace('?', '1')

    try:
        with conn.cursor() as cur:
            cur.execute("EXPLAIN " + sql)
            explain_result = cur.fetchall()
    except Exception as e:
        return {
            'sql': sql,
            'explain': [],
            'issues': [f"EXPLAIN 执行失败: {e}"],
            'suggestions': []
        }

    issues = diagnose(explain_result)
    suggestions = suggest_index(explain_result, digest_text)

    return {
        'sql': sql,
        'explain': explain_result,
        'issues': issues,
        'suggestions': suggestions
    }


def diagnose(explain_result):
    """根据 EXPLAIN 结果识别问题"""
    issues = []
    for row in explain_result:
        table = row.get('table')
        access_type = row.get('type')
        key = row.get('key')
        rows = row.get('rows')
        extra = row.get('Extra') or ''

        if access_type == 'ALL':
            issues.append(f"[{table}] 全表扫描 (type=ALL)，预估扫描 {rows} 行")
        if key is None and access_type not in ('ALL', 'index'):
            issues.append(f"[{table}] 未命中索引")
        if 'Using temporary' in extra:
            issues.append(f"[{table}] 使用了临时表")
        if 'Using filesort' in extra:
            issues.append(f"[{table}] 需要额外排序")
        if 'Using join buffer' in extra:
            issues.append(f"[{table}] JOIN 使用连接缓冲区（未命中索引）")

    return issues


def suggest_index(explain_result, digest_text):
    """简化版索引建议：从 WHERE 子句提取列，生成 CREATE INDEX"""
    suggestions = []

    for row in explain_result:
        if row.get('type') == 'ALL' or row.get('key') is None:
            where_match = re.search(
                r'WHERE (.+?)(?:GROUP|ORDER|LIMIT|$)',
                digest_text,
                re.IGNORECASE
            )
            if not where_match:
                continue

            where_clause = where_match.group(1)
            # 匹配 `col` = ? 或 col = ?
            cols = re.findall(r'`?(\w+)`?\s*=', where_clause)
            if not cols:
                continue

            table = row.get('table')
            idx_name = 'idx_' + '_'.join(cols)
            suggestion = f"CREATE INDEX {idx_name} ON {table}({', '.join(cols)});"
            if suggestion not in suggestions:
                suggestions.append(suggestion)

    return suggestions