import streamlit as st
import extra_streamlit_components as stx
import pandas as pd
import numpy as np
import sqlite3
from common_python.common import check_login, connect_db, close_db,select_year

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

st.subheader('評価基準（マスタ情報）')
st.write("評価基準情報の照会および登録/更新・削除をおこないます")

# データベースに接続する
conn, c = connect_db('.\data\personnelAssessment.db')


def get_query(extraction_year=None, extraction_lv=None):
    query = "SELECT * FROM assessment_basis"
    conditions = []
    if extraction_year:
        conditions.append(f"評価年度='{extraction_year}'")
    if extraction_lv:
        conditions.append(f"LV='{extraction_lv}'")
    if conditions:
        query += " WHERE " + " and ".join(conditions)
    query += " ORDER BY 評価年度, LV, ランク ASC"
    return query

with st.expander("評価基準データ表示"):
    with st.form("view_form", clear_on_submit=False):
        extraction_year = select_year()
        extraction_lv = st.text_input('LVで抽出')
        submitted = st.form_submit_button("表示")

        if submitted:
            query = get_query(extraction_year, extraction_lv)
            df = pd.read_sql_query(query, conn)
            st.write(df)

def upsert_assessment_basis(conn, ases_year, lv, lowerLimit, upperLimit, rank):
    query = '''
    INSERT INTO assessment_basis (評価年度, LV, 下限, 上限, ランク)
    VALUES (?, ?, ?, ?, ?)
    ON CONFLICT(評価年度, LV, ランク) 
    DO UPDATE SET 
    評価年度=excluded.評価年度, LV=excluded.LV, 下限=excluded.下限, 上限=excluded.上限, ランク=excluded.ランク
    '''
    conn.execute(query, (ases_year, lv, lowerLimit, upperLimit, rank))
    conn.commit()

with st.expander("評価基準情報登録"):
    with st.form("reg_form", clear_on_submit=False):
        st.write('※既存のデータを入力している場合は上書きします')
        ases_year = select_year()
        lv = st.radio('LV',('1','2','3','4'), horizontal=True)
        rank = st.radio("ランク", ("A", "B", "C", "D", "E"), horizontal=True)
        lowerLimit = st.text_input('下限')
        upperLimit = st.text_input('上限')
        submitted = st.form_submit_button("登録")

    if submitted:
        if all([ases_year, lv, lowerLimit, upperLimit, rank]):
            upsert_assessment_basis(conn, ases_year, lv, lowerLimit, upperLimit, rank)
        else:
            st.error('すべての項目を入力し、登録してください')

# データ削除
with st.expander("評価基準情報削除"):
    with st.form("del_form", clear_on_submit=True):
        del_year = st.text_input('削除対象年度')
        del_LV = st.text_input('削除対象LV')
        del_rank = st.text_input('削除対象ランク')
        submitted = st.form_submit_button("削除")
        if submitted:
            if del_year and del_LV:
                conn.execute(f'''
                             DELETE FROM assessment_basis 
                             WHERE 評価年度='{del_year}' 
                             and LV='{del_LV}' 
                             and ランク='{del_rank}';
                             ''')
                conn.commit()
            else:
                st.error('削除対象を指定してください')
# データベースへのアクセスが終わったら close する
close_db(conn)