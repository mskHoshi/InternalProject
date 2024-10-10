import streamlit as st
import extra_streamlit_components as stx
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests
from PIL import Image
import os
import sqlite3
import datetime
from enum import Enum
from datetime import datetime as dt
from common_python.common import check_login, connect_db, close_db


IMG_PATH = 'imgs\pic'
CLR_RED = '#ff0000'
CLR_YELLOW = '#ffff00'
CLR_BLUE = '#0000ff'
CLR_PINK = '#ffc0cb'
CLR_PURPLE = '#800080'
CLR_GRAY = '#808080'

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

st.subheader('人材データ')
st.write("社員の特性について照会および登録/更新・削除をおこないます")

# データベースに接続する
conn, c = connect_db('.\data\personnelAssessment.db')

# レコードを社員IDの昇順で取得する
with st.expander("人材データ表示"):
    with st.form("view_form", clear_on_submit=False):
        id = st.text_input('社員番号')
        submitted = st.form_submit_button("表示")

        # レコードを社員IDの昇順で取得する
        if submitted:
            if id:
                st.subheader('基本情報')

                # レイアウト調整（画像：左、カラー：右）
                column1, column2, column3 = st.columns(3)

                # 保存した画像を表示
                with column1:
                    img_path = 'imgs\pic\\' + id + '.jpg'
                    try:
                        img = Image.open(img_path)
                        st.image(img, width=150)
                    except FileNotFoundError:
                        img_path = 'imgs\pic\\no_image.jpg'
                        img = Image.open(img_path)
                        st.image(img, width=150)


                    # 色の定義
                    color_map = {
                        1: '#808080',  # CLR_GRAY
                        2: '#FFFF00',  # CLR_YELLOW
                        3: '#0000FF',  # CLR_BLUE
                        4: '#FFC0CB',  # CLR_PINK
                        5: '#800080',  # CLR_PURPLE
                        6: '#FF0000'   # CLR_RED
                    }

                    # データベース接続
                    query = f"SELECT * FROM assessment_color WHERE 社員ID == '{id}'"
                    df = pd.read_sql_query(query, conn)

                    # データの準備
                    categories = ['']
                    val1 = df['Entrance'].values
                    val2 = df['2ndColor'].values
                    val3 = df['3rdColor'].values
                    val4 = df['4thColor'].values
                    val5 = df['5thColor'].values
                    val6 = df['6thColor'].values

                with column2:
                   if df.empty:
                    st.error('該当IDの人材情報を登録してください')
                   else:
                    # グラフの作成
                    fig, ax = plt.subplots()
                    ax.barh(categories, [1], label='Entrance', color=color_map[val1[0]])
                    ax.barh(categories, [1], label='2ndColor', color=color_map[val2[0]], left=1)
                    ax.barh(categories, [1], label='3rdColor', color=color_map[val3[0]], left=2)
                    ax.barh(categories, [1], label='4thColor', color=color_map[val4[0]], left=3)
                    ax.barh(categories, [1], label='5thColor', color=color_map[val5[0]], left=4)
                    ax.barh(categories, [1], label='6thColor', color=color_map[val6[0]], left=5)

                    # ラベルと凡例の追加
                    ax.set_xlabel('')
                    ax.set_ylabel('')
                    ax.set_title('▶▶▶ Human Colors ▷▷▷')
                    ax.legend()

                    st.pyplot(fig)

                df = pd.read_sql_query(f'''
                SELECT 
                    社員ID, 氏名, 性別, 生年月日, 
                    ((strftime('%Y%m%d',date(CURRENT_TIMESTAMP)) - strftime('%Y%m%d',生年月日)) / 10000) AS 年齢,
                    所属, 入社年月日, 
                    CASE
                        WHEN (strftime('%m',date(CURRENT_TIMESTAMP)) - strftime('%m',入社年月日)) + 前職経験月数 < 0
                        THEN
                            (((strftime('%Y',date(CURRENT_TIMESTAMP)) - strftime('%Y',入社年月日)) + 前職経験年数) * 12 + (strftime('%m',date(CURRENT_TIMESTAMP)) - strftime('%m',入社年月日)) + 前職経験月数) / 12
                        ELSE
                            (strftime('%Y',date(CURRENT_TIMESTAMP)) - strftime('%Y',入社年月日)) + 前職経験年数
                    END AS '勤続年数',
                    CASE
                        WHEN 中途入社 =='〇' THEN '中途'
                        ELSE '新卒入社'
                    END AS '採用区分'
                FROM employee 
                WHERE 社員ID == '{id}'
                ORDER BY 社員ID aSC
                ''', conn)
                if df.empty:
                   st.error('このIDはありません。該当IDの社員情報を登録してください')
                else:
                   st.write(df.set_index('社員ID'))

                df2 = pd.read_sql_query(f'''
                           SELECT e.社員ID,
                                  ab.向上心,
                                  ab.チームワーク,
                                  ab.適応力,
                                  ab.コミュニケーション,
                                  ab.計画・企画力,
                                  ab.実行力,
                                  ab.観察・分析力,
                                  ab.専門知識・スキル,
                                  ab.マネジメント力,
                                  ab.プレゼン・プロモーション力,
                                  ab.リーダーシップ,
                                  ab.問題解決力
                           FROM assessment_ab ab
                           INNER JOIN employee e 
                           ON ab.社員ID = e.社員ID 
                           WHERE ab.社員ID == '{id}';
                ''', conn)

                # データを表示
                if df2.empty:
                   st.error('該当IDの人材情報を登録してください')
                else:
                   # レーダーチャート表示
                   st.subheader('レーダーチャート')
                   # カテゴリと値を設定
                   categories = ['向上心', 'チームワーク', '適応力','コミュニケーション', '計画・企画力', '実行力', '観察・分析力', '専門知識・スキル', 'マネジメント力', 'プレゼン/プロモーション力','リーダーシップ','問題解決力']
                   values = df2.iloc[0, 1:].values.tolist()  # データベースから取得した値を使用
                   # データを1から5の範囲に正規化
                   values = [max(1, min(5, value)) for value in values]
                   # カテゴリ数に合わせてデータポイントを調整
                   values += values[:1]  # 最初の値を最後に追加して閉じる
                   # レーダーチャートをプロット
                   fig, ax = plt.subplots(figsize=(10,10 ), subplot_kw=dict(polar=True))
                   angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
                   angles += angles[:1]  # 最初の角度を最後に追加して閉じる

                   ax.fill(angles, values, 'blue', alpha=0.25)
                   ax.plot(angles, values, 'blue', linewidth=2)

                   # 軸ラベルを設定
                   ax.set_thetagrids(np.degrees(angles[:-1]), labels=categories, fontname="Meiryo")
                   ax.set_yticklabels([])
                   # 軸の目盛りを5段階に設定
                   ax.set_rgrids([1, 2, 3, 4, 5], labels=['1', '2', '3', '4',''], angle=0, fontsize=10)
                   ax.set_ylim(0, 5)  # 軸の範囲を0から5に設定

                   st.pyplot(fig)
            else:
                st.error('社員IDを指定してください')

class Choice(Enum):
    def __str__(cls):
        return cls.name

    灰 = 1
    黄 = 2
    青 = 3
    桃 = 4
    紫 = 5
    赤 = 6

# Main code
with st.expander("人材データ登録"):
    with st.form("reg2_form", clear_on_submit=False):
        st.markdown('画像を保存する')
        id = st.text_input('社員ID　※既存のIDの場合、上書き更新します')
        file = st.file_uploader('画像をアップロードしてください。 拡張子は.jpgにしてください', type=['jpg'])
        if file and id:
            # ファイル名を社員IDに書き換える
            file_extension = file.name.split('.')[-1]
            new_file_name = f"{id}.{file_extension}"
            img_path = os.path.join(IMG_PATH, new_file_name)

            st.markdown(f'{new_file_name} をアップロードしました.')

            # 画像を保存する
            with open(img_path, 'wb') as f:
                f.write(file.read())

            # 保存した画像を表示
            img = Image.open(img_path)
            st.image(img)
        elif file and not id:
            st.warning('社員IDを入力してください。')

        st.markdown('レーダチャート')
        improve = st.selectbox('向上心', (1, 2, 3, 4, 5))
        team = st.selectbox('チームワーク', (1, 2, 3, 4, 5))
        adapt = st.selectbox('適応力', (1, 2, 3, 4, 5))
        comm = st.selectbox('コミュニケーション', (1, 2, 3, 4, 5))
        plan = st.selectbox('計画・企画力', (1, 2, 3, 4, 5))
        action = st.selectbox('実行力', (1, 2, 3, 4, 5))
        obse = st.selectbox('観察・分析力', (1, 2, 3, 4, 5))
        skill = st.selectbox('専門知識・スキル', (1, 2, 3, 4, 5))
        mgmt = st.selectbox('マネジメント力', (1, 2, 3, 4, 5))
        prom = st.selectbox('プレゼン・プロモーション力', (1, 2, 3, 4, 5))
        leader = st.selectbox('リーダーシップ', (1, 2, 3, 4, 5))
        solve = st.selectbox('問題解決力', (1, 2, 3, 4, 5))

        st.markdown('''▶▶▶ Human Colors ▷▷▷　''', unsafe_allow_html=True)

        # Entrance color selection
        entrance = st.radio("Entrance", Choice, horizontal=True)
        st.write(f'選択：{entrance.value}')

        # Second color selection
        second_color = st.radio("2ndColor", Choice, horizontal=True)
        st.write(f'選択：{second_color.value}')

        # Third color selection
        third_color = st.radio("3rdColor", Choice, horizontal=True)
        st.write(f'選択：{third_color.value}')

        # Fourth color selection
        fourth_color = st.radio("4thColor", Choice, horizontal=True)
        st.write(f'選択：{fourth_color.value}')

        # Fifth color selection
        fifth_color = st.radio("5thColor", Choice, horizontal=True)
        st.write(f'選択：{fifth_color.value}')

        # Sixth color selection
        sixth_color = st.radio("6thColor", Choice, horizontal=True)
        st.write(f'選択：{sixth_color.value}')

        submitted = st.form_submit_button("登録")

    # 入力されたデータをSQLiteにUPSERTする
    if submitted:
        # 社員IDは入力必須とする
        if id:
            conn.execute(f'''
            INSERT INTO assessment_ab (
                    社員ID,
                    向上心,
                    チームワーク,
                    適応力,
                    コミュニケーション,
                    計画・企画力,
                    実行力,
                    観察・分析力,
                    専門知識・スキル,
                    マネジメント力,
                    プレゼン・プロモーション力,
                    リーダーシップ,
                    問題解決力
            )
            VALUES ('{id}',
                    '{improve}',
                    '{team}',
                    '{adapt}',
                    '{comm}',
                    '{plan}',
                    '{action}',
                    '{obse}',
                    '{skill}',
                    '{mgmt}',
                    '{prom}',
                    '{leader}',
                    '{solve}'
            )
            ON CONFLICT(社員ID) 
            DO UPDATE SET 
                   向上心 ='{improve}',
                   チームワーク ='{team}',
                   適応力 ='{adapt}', 
                   コミュニケーション ='{comm}',
                   計画・企画力 ='{plan}',
                   実行力 ='{action}',
                   観察・分析力 ='{obse}', 
                   専門知識・スキル ='{skill}',
                   マネジメント力 ='{mgmt}',
                   プレゼン・プロモーション力 ='{prom}', 
                   リーダーシップ ='{leader}',
                   問題解決力 ='{solve}'
            ''')

            conn.execute(f'''
            INSERT INTO assessment_color (
                    社員ID,
                    Entrance,
                    "2ndColor",
                    "3rdColor",
                    "4thColor",
                    "5thColor",
                    "6thColor"
            )
            VALUES ('{id}',
                    '{entrance.value}',
                    '{second_color.value}',
                    '{third_color.value}',
                    '{fourth_color.value}',
                    '{fifth_color.value}',
                    '{sixth_color.value}'
            )
            ON CONFLICT(社員ID) 
            DO UPDATE SET 
                   Entrance ='{entrance.value}',
                   "2ndColor" ='{second_color.value}',
                   "3rdColor" ='{third_color.value}',
                   "4thColor" ='{fourth_color.value}',
                   "5thColor" ='{fifth_color.value}',
                   "6thColor" ='{sixth_color.value}'
            ''')
            conn.commit()
            st.success('登録/更新しました')
        else:
            st.error('社員IDを指定してください')

# データ削除
with st.expander("人材データ削除"):
    with st.form("del_form", clear_on_submit=True):
        削除社員ID = st.text_input('削除社員ID')
        submitted = st.form_submit_button("削除")
        if submitted:
            conn.execute(f'''DELETE FROM assessment_ab WHERE 社員ID='{削除社員ID}';''')
            conn.execute(f'''DELETE FROM assessment_color WHERE 社員ID='{削除社員ID}';''')
            conn.commit()
            st.success('削除しました')
# データベースへのアクセスが終わったら close する
close_db(conn)