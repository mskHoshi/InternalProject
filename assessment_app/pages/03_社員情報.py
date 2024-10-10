import streamlit as st
import extra_streamlit_components as stx
import pandas as pd
import numpy as np
import sqlite3
import datetime
from datetime import datetime as dt
from common_python.common import check_login, connect_db, close_db

button_css = f"""
<style>
  div.stButton > button:first-child  {{
    font-weight  : bold                ;/* 文字：太字                   */
    border       : 2px solid #b0c4de   ;/* 枠線：lightsteelblueで2ピクセルの実線 */
    border-radius: 10px 10px 10px 10px ;/* 枠線：半径10ピクセルの角丸     */
    background   : #f0ffff             ;/* 背景色：azure            */
  }}
</style>
"""
st.markdown(button_css, unsafe_allow_html=True)

# ログインの確認
check_login('some_cookie_name')

st.subheader('社員情報')
st.write("社員情報の照会および登録/更新・削除をおこないます")

# データベースに接続する
conn, c = connect_db('.\data\personnelAssessment.db')

# レコードを社員IDの昇順で取得する
with st.expander("社員情報表示"):
    with st.form("view_form", clear_on_submit=False):
        affiliation = st.selectbox('所属',('-','1G','2G','3G'))
        submitted = st.form_submit_button("表示")

def get_employee_data(affiliation, conn):
    base_query = '''
    SELECT 
        社員ID, 氏名, 性別, 入社年月日, 所属, リーダー, 中途入社, 前職経験年数, 前職経験月数,
        CASE
            WHEN (strftime('%m',date(CURRENT_TIMESTAMP)) - strftime('%m',入社年月日)) + 前職経験月数 < 0
            THEN
                (((strftime('%Y',date(CURRENT_TIMESTAMP)) - strftime('%Y',入社年月日)) + 前職経験年数) * 12 + (strftime('%m',date(CURRENT_TIMESTAMP)) - strftime('%m',入社年月日)) + 前職経験月数) / 12
            ELSE
                (strftime('%Y',date(CURRENT_TIMESTAMP)) - strftime('%Y',入社年月日)) + 前職経験年数
        END AS '経験年数',
        CASE
            WHEN (strftime('%m',date(CURRENT_TIMESTAMP)) - strftime('%m',入社年月日)) + 前職経験月数 < 0
            THEN
                (strftime('%m',date(CURRENT_TIMESTAMP)) - strftime('%m',入社年月日)) + 前職経験月数 + 12
            ELSE
                (strftime('%m',date(CURRENT_TIMESTAMP)) - strftime('%m',入社年月日)) + 前職経験月数
        END AS '経験月数',
        生年月日,
        ((strftime('%Y%m%d',date(CURRENT_TIMESTAMP)) - strftime('%Y%m%d',生年月日)) / 10000) AS 年齢
    FROM employee 
    '''
    
    if affiliation == '-':
        query = base_query + 'ORDER BY 社員ID ASC'
    else:
        query = base_query + f'WHERE 所属 == "{affiliation}" ORDER BY 社員ID ASC'
    
    return pd.read_sql_query(query, conn)

def get_experience_data(affiliation, conn):
    base_query = '''
    SELECT 
        (strftime('%Y',date(CURRENT_TIMESTAMP)) - strftime('%Y',入社年月日)) + 前職経験年数 + 1 as "年目",
        count(1) AS 人数
    FROM employee 
    '''
    
    if affiliation == '-':
        query = base_query + 'GROUP BY 年目'
    else:
        query = base_query + f'WHERE 所属 == "{affiliation}" GROUP BY 年目'
    
    return pd.read_sql_query(query, conn)

def get_age_gender_data(affiliation, conn, c):
    if affiliation == '-':
        # 平均年齢
        sql = ''' SELECT SUM((strftime('%Y%m%d',date(CURRENT_TIMESTAMP)) - strftime('%Y%m%d',生年月日)) / 10000) / count(1) as "平均年齢" FROM employee '''
        c.execute(sql)
        avg_age = c.fetchone()
        # 男女割合
        sql2 = '''SELECT 性別, count(性別) 件数, count(*) * 100 / SUM(count(*)) over() AS 割合 FROM employee GROUP BY 性別'''
        c.execute(sql2)
        gender_ratio = c.fetchone()
    else:
        # 平均年齢
        sql = ''' SELECT SUM((strftime('%Y%m%d',date(CURRENT_TIMESTAMP)) - strftime('%Y%m%d',生年月日)) / 10000) / count(1) as "平均年齢" FROM employee WHERE 所属 =?'''
        c.execute(sql, (affiliation,))
        avg_age = c.fetchone()
        # 男女割合
        sql2 = '''SELECT 性別, count(性別) 件数, count(*) * 100 / SUM(count(*)) over() AS 割合 FROM employee WHERE 所属 =? GROUP BY 性別'''
        c.execute(sql2, (affiliation,))
        gender_ratio = c.fetchone()
    
    return avg_age, gender_ratio

if submitted:
    df = get_employee_data(affiliation, conn)
    st.write(df.set_index('社員ID'))

    # タイトル表示
    st.header("全体" if affiliation == '-' else affiliation)

    # 人数表示
    st.subheader('人数：' + str(len(df)))

    if len(df) > 0:
        # 各経験年数の人数をグラフ表示
        st.markdown("###### 年次における割合")
        cntdata = get_experience_data(affiliation, conn)

        # 各LVの人数初期化
        experience_counts = [0] * 10
        for idx, row in cntdata.iterrows():
            year = row['年目']
            if year <= 9:
                experience_counts[year - 1] = row['人数']
            else:
                experience_counts[9] += row['人数']

        data = pd.DataFrame({
            '経験年数': ['1年目', '2年目', '3年目', '4年目', '5年目', '6年目', '7年目', '8年目', '9年目', '以上'],
            '人数': experience_counts
        })

        # グラフの描画
        st.bar_chart(data.set_index('経験年数'))

        # 平均年齢、男女割合のデータ取得
        avg_age, gender_ratio = get_age_gender_data(affiliation, conn, c)

        # 平均年齢表示
        st.subheader('平均年齢：' + str(avg_age[0]))
        # 男女割合表示
        st.subheader('男性：' + str(100 - gender_ratio[2]) + '％')
        st.subheader('女性：' + str(gender_ratio[2]) + '％')

# ユーザーからの入力を受け付ける
with st.expander("社員情報登録"):
    with st.form("reg_form", clear_on_submit=False):
        # 年月日入力項目のレンジ定義
        min_date = datetime.date(1970, 1, 1)
        max_date = datetime.date(2100, 12, 31)

        id = st.text_input('社員ID　※既存のIDの場合、上書き更新します')
        name = st.text_input('氏名')
        gender = st.selectbox('性別',('男','女'))
        affiliation = st.selectbox('所属',('1G','2G','3G','-'))
        leader = st.selectbox('リーダー',('●','○','-'))
        entry_ymd = st.date_input('入社年月日')
        mid_career = st.selectbox('中途入社',('-','●'))
        bef_exp_y = st.text_input('前職経験年数', 0)
        bef_exp_m = st.text_input('前職経験月数', 0)
        birth_ymd = st.date_input('生年月日', min_value=min_date, max_value=max_date)
        submitted = st.form_submit_button("登録")

    # 入力されたデータをSQLiteにUPSERTする
    if submitted:
        # 社員IDと氏名は入力必須とする
        if id and name:
            conn.execute(f'''
            INSERT INTO employee (社員ID, 氏名, 性別, 所属, リーダー, 入社年月日, 中途入社, 前職経験年数, 前職経験月数, 生年月日)
            VALUES ('{id}', '{name}', '{gender}', '{affiliation}', '{leader}', '{entry_ymd}', '{mid_career}', '{bef_exp_y}', '{bef_exp_m}', '{birth_ymd}')
            ON CONFLICT(社員ID) 
            DO UPDATE SET 
            氏名='{name}', 性別='{gender}',  所属='{affiliation}', リーダー='{leader}', 入社年月日='{entry_ymd}', 中途入社='{mid_career}', 前職経験年数='{bef_exp_y}', 前職経験月数='{bef_exp_m}', 生年月日='{birth_ymd}'
            ''')
            conn.commit()
            st.success('登録/更新しました')
        else:
            st.error('IDと名前を入力し、登録してください')

# データ削除
with st.expander("社員情報削除"):
    with st.form("del_form", clear_on_submit=True):
        削除社員ID = st.text_input('削除社員ID')
        submitted = st.form_submit_button("削除")
        if submitted:
            conn.execute(f'''DELETE FROM employee WHERE 社員ID='{削除社員ID}';''')
            conn.commit()
            st.success('削除しました')

# データベースへのアクセスが終わったら close する
close_db(conn)