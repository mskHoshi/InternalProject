import streamlit as st
import streamlit_authenticator as stauth
import yaml
import pandas as pd
#import numpy as np
#import sqlite3
from common_python.common import connect_db, close_db, select_year,select_month
#from decimal import Decimal, ROUND_HALF_UP, ROUND_HALF_EVEN
from common_python.assessment_query import get_assessment_data,get_assessment_sp_data,runk_assessment_data, get_assessment_month_lv_data,cntdata_query

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

with open('./config.yaml') as file:
    config = yaml.load(file, Loader=yaml.SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
#    config['preauthorized'], verアップでAuthenticateクラスからパラメータ削除された
)

#name, authentication_status, username = authenticator.login('Login', 'main')　古い呼び出し方
#name, authentication_status, username = authenticator.login(fields= 'main')　古い呼び出し方
authenticator.login()
if 'authentication_status' not in st.session_state:
    st.session_state['authentication_status'] = None

if st.session_state["authentication_status"]:
    authenticator.logout('Logout', 'main')
    #st.write(f'ログインに成功しました')
	# ここにログイン後の処理を書く。
    # データベースに接続する
    conn, c = connect_db('.\data\personnelAssessment.db')

# 評価結果一覧を表示
    st.subheader('評価結果Ⅰ')
    st.write("現在到達LVにおける純粋な評価結果となります。")
    #月別のLV推移を表示
    with st.expander("月別LV推移表示"):
        with st.form("view_form", clear_on_submit=False):
            extraction_year = select_year()
            submitted = st.form_submit_button("表示")

            if submitted:
                if extraction_year:
                    df = get_assessment_month_lv_data(conn, extraction_year)
                    st.write(df.set_index('社員ID'))

                    # 各LV毎の人数をグラフ表示
                    st.markdown("###### LV毎の人数")
                    # グラフ表示用のデータ取得
                    cntdata = cntdata_query(conn, extraction_year)

                    # 各LVの人数初期化
                    Cnt1 = 0
                    Cnt2 = 0
                    Cnt3 = 0
                    Cnt4 = 0
                    for idx, row in cntdata.iterrows():
                        if row['LV'] == 1:
                            Cnt1 = row['人数']
                        elif row['LV'] == 2:
                            Cnt2 = row['人数']
                        elif row['LV'] == 3:
                            Cnt3 = row['人数']
                        elif row['LV'] == 4:
                            Cnt4 = row['人数']

                    data = pd.DataFrame({
                        'LV': ['LV1', 'LV2', 'LV3', 'LV4'],
                        '人数': [Cnt1, Cnt2, Cnt3, Cnt4]
                    })

                    # グラフの描画
                    st.bar_chart(data.set_index('LV'))
                else:
                    st.write("評価年度を指定してください")

    with st.expander("評価結果サマリ表示"):
        with st.form("view_form1", clear_on_submit=False):
            extraction_year = select_year()
            extraction_month = select_month()
            submitted = st.form_submit_button("表示")

        # 表とチャートの表示
        if submitted:
            if extraction_year:
                df = get_assessment_data(conn, extraction_year, extraction_month)
                st.write(df.set_index('社員ID'))
            else:
                st.write("評価年度を指定してください")

# すべての評価補正をおこなった評価結果一覧を表示
    st.subheader('評価結果Ⅱ')
    st.write("すべての評価補正をおこなった評価結果の参照ができます")
    with st.expander("補正評価一覧表示"):
        st.markdown("""
            - 経験年数に応じ、会社が期待するLVと現在のLVの対比評価をおこないます
            - 特別評価による再評価をおこないます
            - 上記を踏まえ、ランクの再設定をおこないます。
        """)
        with st.form("view_form2", clear_on_submit=False):
         extraction_year = select_year()
         extraction_month = select_month()
         submitted = st.form_submit_button("表示")

        # 表とチャートの表示
        if submitted:
            if extraction_year:
                df2 = get_assessment_sp_data(conn, extraction_year, extraction_month)
                st.write(df2.set_index('社員ID'))
            else:
                st.write("評価年度を指定してください")

# 経験年数と現在到達LVによる補正評価点の一覧を表示
    st.subheader('評価結果Ⅲ（経営層向け）')
    st.write("会社の基準との評価結果の参照ができます")
    with st.expander("補正評価一覧表示"):
        st.markdown("""
            - 経験年数に応じ、会社が期待するLVと現在のLVの対比評価をおこないます
        """)

        with st.form("view_form3", clear_on_submit=False):
            extraction_year = select_year()
            extraction_month = select_month()
            extraction_group = st.selectbox('所属グループ', ('','1G', '2G', '3G'))
            extraction_level = st.selectbox('現在LV', ('',1,2,3,4))
            submitted = st.form_submit_button("表示")

        def generate_query(conn, extraction_year, extraction_month, extraction_group='', extraction_level=''):
            base_query = runk_assessment_data(conn, extraction_year, extraction_month, extraction_group, extraction_level)
            if extraction_group:
                base_query = base_query[base_query['所属'] == extraction_group]
            if extraction_level:
                base_query = base_query[base_query['現在LV'] == extraction_level]
            return base_query

        # 表とチャートの表示
        if submitted:
            if extraction_year:
                df = generate_query(conn, extraction_year, extraction_month, extraction_group, extraction_level)
                st.write(df.set_index('社員ID'))
            else:
                st.write("評価年度を指定してください")

    # データベースへのアクセスが終わったら close する
    close_db(conn)
elif st.session_state["authentication_status"] is False:
    st.error('ユーザ名またはパスワードが間違っています')
elif st.session_state["authentication_status"] is None:
    st.warning('ユーザ名とパスワードを入力してください')