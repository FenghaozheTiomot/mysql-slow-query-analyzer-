# main.py
# 入口：把所有模块串起来

import config
from collector import get_connection, collect_slow_queries
from analyzer import analyze
from reporter import generate_report


def main():
    print("连接 MySQL...")
    conn = get_connection(config)

    print(f"采集慢查询（平均耗时 > {config.SLOW_THRESHOLD_SECONDS} 秒）...")
    queries = collect_slow_queries(
        conn,
        config.SLOW_THRESHOLD_SECONDS,
        config.TOP_N
    )
    print(f"共采集到 {len(queries)} 条慢查询\n")

    if not queries:
        print("没有采集到慢查询。")
        print("请先手动跑几条 SELECT 语句，让 performance_schema 记录。")
        conn.close()
        return

    analyses = []
    for i, q in enumerate(queries, 1):
        preview = q['DIGEST_TEXT'][:70]
        print(f"[{i}/{len(queries)}] 分析: {preview}...")
        a = analyze(conn, q['DIGEST_TEXT'])
        analyses.append({'query': q, 'analysis': a})
        if a['issues']:
            for issue in a['issues']:
                print(f"    - {issue}")

    generate_report(analyses, 'report.md')

    conn.close()
    print("\n完成！打开 report.md 查看结果。")


if __name__ == '__main__':
    main()