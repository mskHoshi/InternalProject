import pandas as pd

#評価結果Ⅰ
#月別LV推移表示
def get_assessment_month_lv_data(conn, extraction_year):
    query = f'''
    SELECT 
    a.社員ID,
    b.所属,
    b.氏名,
    b.リーダー,
    b.入社年月日,
    b.中途入社,
    max(CASE a.評価月 WHEN 4 THEN a.評価LV ELSE NULL END) AS '4月',
    max(CASE a.評価月 WHEN 5 THEN a.評価LV ELSE NULL END) AS '5月',
    max(CASE a.評価月 WHEN 6 THEN a.評価LV ELSE NULL END) AS '6月',
    max(CASE a.評価月 WHEN 7 THEN a.評価LV ELSE NULL END) AS '7月',
    max(CASE a.評価月 WHEN 8 THEN a.評価LV ELSE NULL END) AS '8月',
    max(CASE a.評価月 WHEN 9 THEN a.評価LV ELSE NULL END) AS '9月',
    max(CASE a.評価月 WHEN 10 THEN a.評価LV ELSE NULL END) AS '10月',
    max(CASE a.評価月 WHEN 11 THEN a.評価LV ELSE NULL END) AS '11月',
    max(CASE a.評価月 WHEN 12 THEN a.評価LV ELSE NULL END) AS '12月',
    max(CASE a.評価月 WHEN 1 THEN a.評価LV ELSE NULL END) AS '1月',
    max(CASE a.評価月 WHEN 2 THEN a.評価LV ELSE NULL END) AS '2月',
    max(CASE a.評価月 WHEN 3 THEN a.評価LV ELSE NULL END) AS '3月'
    FROM assessment AS a 
    inner join employee AS b 
    on a.社員ID = b.社員ID 
    WHERE a.評価年度 = '{extraction_year}'
    GROUP BY a.社員ID
    ORDER BY a.社員ID aSC;
    '''
    return pd.read_sql_query(query, conn)

def cntdata_query(conn, extraction_year):
    query = f'''
    SELECT count(a.LV) AS 人数, a.LV
    FROM
        (SELECT max(評価LV) AS LV
        FROM assessment 
        WHERE 評価年度 = '{extraction_year}'
        GROUP BY 社員ID) AS a 
    GROUP BY a.LV
    '''
    return pd.read_sql_query(query, conn)

#評価結果サマリ表示
def get_assessment_data(conn, extraction_year, extraction_month):
    query = f'''
    WITH RankedAssessments AS (
    SELECT 
        社員ID,
        評価LV,
        評価点,
        評価月,
        評価年度,
        ROW_NUMBER() OVER (PARTITION BY 社員ID ORDER BY 評価LV DESC) AS rn
    FROM 
        assessment
    WHERE  評価年度 = '{extraction_year}'
    AND    評価月 = '{extraction_month}'
    )
    , AggregatedAssessments AS (
    SELECT 
        社員ID,
        評価月,
        評価年度,
        MAX(CASE WHEN rn = 1 THEN 評価LV END) AS 現在LV,
        MAX(CASE WHEN rn = 1 THEN 評価点 END) AS 現在評価点,
        MAX(CASE WHEN rn = 2 THEN 評価LV END) AS 累積LV①,
        MAX(CASE WHEN rn = 2 THEN 評価点 END) AS 累積評価点①,
        MAX(CASE WHEN rn = 3 THEN 評価LV END) AS 累積LV②,
        MAX(CASE WHEN rn = 3 THEN 評価点 END) AS 累積評価点②,
        MAX(CASE WHEN rn = 4 THEN 評価LV END) AS 累積LV③,
        MAX(CASE WHEN rn = 4 THEN 評価点 END) AS 累積評価点③,
        COALESCE(MAX(CASE WHEN rn = 1 THEN 評価点 END), 0) +
        COALESCE(MAX(CASE WHEN rn = 2 THEN 評価点 END), 0) +
        COALESCE(MAX(CASE WHEN rn = 3 THEN 評価点 END), 0) +
        COALESCE(MAX(CASE WHEN rn = 4 THEN 評価点 END), 0) AS 評点合計
    FROM 
        RankedAssessments
    GROUP BY 
        社員ID, 評価月, 評価年度
    )
    SELECT
    aa.評価月,
    aa.評価年度,
    e.社員ID,
    e.氏名,
    aa.現在LV,
    aa.現在評価点,
    aa.累積LV①,
    aa.累積評価点①,
    aa.累積LV②,
    aa.累積評価点②,
    aa.累積LV③,
    aa.累積評価点③,
    aa.評点合計,
    ab.ランク AS 現在評価
    FROM 
    employee e
    LEFT JOIN 
    AggregatedAssessments aa ON e.社員ID = aa.社員ID
    LEFT JOIN 
    assessment_basis ab ON ab.LV = aa.現在LV
    AND 
    aa.評点合計 BETWEEN ab.下限 AND ab.上限
    WHERE aa.評価年度 = '{extraction_year}'
    AND    aa.評価月 = '{extraction_month}';
    '''
    return pd.read_sql_query(query, conn)

#評価結果 Ⅱ
def get_assessment_sp_data (conn, extraction_year, extraction_month):
    query = f'''
    WITH RankedAssessments AS (
        SELECT 
            社員ID,
            評価LV,
            評価点,
            評価月,
            評価年度,
            ROW_NUMBER() OVER (PARTITION BY 社員ID ORDER BY 評価LV DESC) AS rn
        FROM 
            assessment
        WHERE  評価年度 = '{extraction_year}'
        AND    評価月 = '{extraction_month}'
        ),
    AggregatedAssessments AS (
        SELECT 
            社員ID,
            評価月,
            評価年度,
            MAX(CASE WHEN rn = 1 THEN 評価LV END) AS 現在LV,
            COALESCE(MAX(CASE WHEN rn = 1 THEN 評価点 END), 0) +
            COALESCE(MAX(CASE WHEN rn = 2 THEN 評価点 END), 0) +
            COALESCE(MAX(CASE WHEN rn = 3 THEN 評価点 END), 0) +
            COALESCE(MAX(CASE WHEN rn = 4 THEN 評価点 END), 0) AS 評点合計
        FROM 
            RankedAssessments
        GROUP BY 
            社員ID, 評価月, 評価年度
        )
    SELECT
        aa.評価月,
        aa.評価年度,
        e.社員ID,
        e.氏名,
        aa.現在LV,
        aa.評点合計 AS 評点合計（補正前）,
        CASE WHEN as2.評価点 IS NULL
            THEN aa.評点合計
        ELSE
            aa.評点合計 + as2.評価点 
        END AS 評点合計（補正後）,
        ab.ランク AS ランク（補正前）,
        ab2.ランク AS ランク（補正後）
    FROM 
        employee e
    LEFT JOIN 
        AggregatedAssessments aa ON e.社員ID = aa.社員ID
    LEFT JOIN 
        assessment_sp as2 ON e.社員ID = as2.社員ID
    LEFT JOIN 
        assessment_basis ab ON ab.LV = aa.現在LV
        AND aa.評点合計 BETWEEN ab.下限 AND ab.上限
    LEFT JOIN 
        assessment_basis ab2 ON ab2.LV = aa.現在LV
        AND (CASE WHEN as2.評価点 IS NULL THEN aa.評点合計 ELSE aa.評点合計 + as2.評価点 END) BETWEEN ab2.下限 AND ab2.上限
    WHERE 
        aa.評価年度 = '{extraction_year}'
    AND 
        aa.評価月 = '{extraction_month}';
    '''
    return pd.read_sql_query(query, conn)

#評価結果　Ⅲ
def runk_assessment_data(conn, extraction_year, extraction_month, extraction_group, extraction_level):
    query = f'''
            WITH RankedAssessments AS (
                SELECT 
                    社員ID,
                    評価LV,
                    評価点,
                    評価月,
                    評価年度,
                    ROW_NUMBER() OVER (PARTITION BY 社員ID ORDER BY 評価LV DESC) AS rn
                FROM 
                    assessment
                WHERE 評価年度 = '{extraction_year}'
                AND   評価月 = '{extraction_month}'
            )
            , AggregatedAssessments AS (
                SELECT 
                    社員ID,
                    評価月,
                    評価年度,
                    MAX(CASE WHEN rn = 1 THEN 評価LV END) AS 現在LV
                FROM 
                    RankedAssessments
                GROUP BY 
                    社員ID, 評価月, 評価年度
            )
            , EmployeeYears AS (
                SELECT 
                    e.所属,
                    e.リーダー,
                    e.社員ID,
                    e.氏名,
                    CAST((julianday('now') - julianday(e.入社年月日)) / 365 AS INTEGER) + e.前職経験年数 + 1 AS 年目,
                    aa.現在LV
                FROM 
                    employee e
                LEFT JOIN 
                    AggregatedAssessments aa ON e.社員ID = aa.社員ID
                WHERE aa.評価年度 = '{extraction_year}'
                AND   aa.評価月 = '{extraction_month}'
            )
            SELECT DISTINCT
                ey.所属,
                ey.リーダー,
                ey.社員ID,
                ey.氏名,
                ey.年目,
                ey.現在LV,
                CASE 
                    WHEN ey.年目 = 1 THEN 1
                    WHEN ey.年目 = 2 THEN 2
                    WHEN ey.年目 = 3 THEN 2
                    WHEN ey.年目 = 4 THEN 3
                    WHEN ey.年目 = 5 THEN 3
                    WHEN ey.年目 >= 6 THEN 4
                END AS 要求LV,
                ar.ランク,
                ar.評点
            FROM 
                EmployeeYears ey
            LEFT JOIN 
                assessment_rk ar 
            ON 
                (CASE WHEN ey.年目 >= 6 THEN 6
                 ELSE ey.年目
                 END 
                ) = ar.年目 
            AND 
                ey.現在LV = ar.LV
            WHERE 
                ar.年目 IS NOT NULL
            AND 
                ar.LV IS NOT NULL;
            '''
    return pd.read_sql_query(query, conn)