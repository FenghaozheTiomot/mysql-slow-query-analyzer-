import pymysql


def get_connection(cfg):
    """ Set up mysql conncetion"""
    return pymysql.connect(
        host=cfg.DB_HOST,
        user=cfg.DB_USER,
        password=cfg.DB_PASSWORD,
        database=cfg.DB_NAME,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )


def collect_slow_queries(conn, threshold_seconds, top_n):
    """
    From performance_schema find 平均耗时超过阈值的 SQL 模板。
    返回一个列表，每个元素是一条慢查询的统计信息。
    """
    sql = """
        SELECT
            DIGEST_TEXT,
            COUNT_STAR,
            ROUND(SUM_TIMER_WAIT / 1000000000000, 3) AS total_seconds,
            ROUND(AVG_TIMER_WAIT / 1000000000000, 6) AS avg_seconds,
            SUM_NO_INDEX_USED,
            SUM_ROWS_EXAMINED,
            SUM_ROWS_SENT
        FROM performance_schema.events_statements_summary_by_digest
        WHERE AVG_TIMER_WAIT / 1000000000000 > %s
          AND DIGEST_TEXT IS NOT NULL
          AND DIGEST_TEXT LIKE 'SELECT%%'
          AND DIGEST_TEXT NOT LIKE '%%performance_schema%%'
          AND DIGEST_TEXT NOT LIKE '%%information_schema%%'
          AND DIGEST_TEXT NOT LIKE '%%SLEEP%%'
          AND DIGEST_TEXT NOT LIKE '%%COUNT%%'
          AND DIGEST_TEXT NOT LIKE '%%SUM%%'
          AND DIGEST_TEXT NOT LIKE '%%AVG%%'
          AND DIGEST_TEXT NOT LIKE '%%MAX%%'
          AND DIGEST_TEXT NOT LIKE '%%MIN%%'
        ORDER BY AVG_TIMER_WAIT DESC
        LIMIT %s
    """
    with conn.cursor() as cur:
        cur.execute(sql, (threshold_seconds, top_n))
        return cur.fetchall()