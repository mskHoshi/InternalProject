# common.py
import sqlite3
import extra_streamlit_components as stx
import streamlit as st

def check_login(cookie_name):
    value = stx.CookieManager().get(cookie=cookie_name)
    if value is None:
        st.warning("**ログインしてください**")
        st.stop()

def connect_db(db_path):
    conn = sqlite3.connect(db_path)
    return conn, conn.cursor()

def close_db(conn):
    conn.close()

def select_year():
    extraction_year = st.selectbox('評価年度', ('2023', '2024', '2025', '2026', '2027', '2028', '2029', '2030'))
    return extraction_year

def select_month():
    extraction_month = st.selectbox('評価月', ('4', '5', '6', '7', '8', '9', '10', '11', '12', '1', '2', '3'))
    return extraction_month

def searchName(check, id, c):
    if check:
        if id:
            param = (id,)
            sql = '''select 氏名 from employee where 社員ID = ? '''
            c.execute(sql, param)
            result = c.fetchone()
            if result is not None:
                return result[0]
            else:
                return 1
        else:
            return 0