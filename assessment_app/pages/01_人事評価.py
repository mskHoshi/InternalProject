import streamlit as st
import extra_streamlit_components as stx
import pandas as pd
import numpy as np
import sqlite3
import dataclasses
from common_python.assessment import Assessment
from common_python.common import check_login, connect_db, close_db,select_year,select_month,searchName
from decimal import Decimal, ROUND_HALF_UP, ROUND_HALF_EVEN

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

st.subheader('人事評価')

# データベースに接続する
conn, c = connect_db('.\data\personnelAssessment.db')

def calcAsses(assessment: Assessment):
    formList = [getattr(assessment, attr) for attr in vars(assessment) if attr.startswith('ases_')]

    # 評価値をカウントする
    aCnt = formList.count('A')  # A評価のカウンター
    bCnt = formList.count('B')  # B評価のカウンター
    cCnt = formList.count('C')  # C評価のカウンター
    noneCnt = formList.count(None)  # 評価なしのカウンター

    # 評価値を計算する
    # 初期化
    pointSum = 0
    pointA = 0
    pointB = 0

    # 計算（件数 * ポイント / 100）
    if assessment.lv == 1:
        pointA = aCnt * 20 / 100
        pointB = bCnt * 10 / 100
    elif assessment.lv == 2:
        pointA = aCnt * 30 / 100
        pointB = bCnt * 20 / 100
    elif assessment.lv == 3:
        pointA = aCnt * 40 / 100
        pointB = bCnt * 30 / 100
    elif assessment.lv == 4:
        pointA = aCnt * 50 / 100
        pointB = bCnt * 40 / 100

    pointSum = pointA + pointB
    return Decimal(str(pointSum)).quantize(Decimal('0.1'), ROUND_HALF_UP)

# 入力されたデータをSQLiteにUPSERTする
def registAses(submitted, Assessment):
    if submitted:
        # 評価年度、評価月、社員IDは入力必須とする
        if Assessment.ases_year and Assessment.ases_month and Assessment.id and Assessment.lv:
            param = (Assessment.ases_year, Assessment.ases_month, Assessment.id ,Assessment.lv)
            sql = '''select count(1) from assessment where 評価年度 = ? and 評価月 = ? and 社員ID = ? and 評価LV = ?'''
            c.execute(sql, param)
            result = c.fetchone()

            asesPoint = calcAsses(Assessment)

            if result[0] == 0:
                conn.execute(f'''
                INSERT INTO assessment 
                    (評価年度 , 
                    評価月 , 
                    社員ID , 
                    評価LV , 
                    評価点 , 
                    コメント , 
                    ases_a1 , 
                    ases_a2 , 
                    ases_a3 , 
                    ases_a4 , 
                    ases_a5 , 
                    ases_a6 , 
                    ases_a7 , 
                    ases_a8 , 
                    ases_b1 , 
                    ases_b2 , 
                    ases_b3 , 
                    ases_b4 , 
                    ases_b5 , 
                    ases_b6 , 
                    ases_b7 , 
                    ases_b8 , 
                    ases_c1 , 
                    ases_c2 , 
                    ases_c3 , 
                    ases_c4 , 
                    ases_c5 , 
                    ases_c6 , 
                    ases_c7 , 
                    ases_c8 , 
                    ases_d1 , 
                    ases_d2 , 
                    ases_d3 , 
                    ases_d4 , 
                    ases_d5 , 
                    ases_d6 , 
                    ases_d7 , 
                    ases_d8 , 
                    ases_e1 , 
                    ases_e2 , 
                    ases_e3 , 
                    ases_e4 , 
                    ases_e5 , 
                    ases_e6 , 
                    ases_e7 , 
                    ases_e8)
                VALUES (
                    '{Assessment.ases_year}',
                    '{Assessment.ases_month}',
                    '{Assessment.id}',
                    '{Assessment.lv}',
                    '{asesPoint}',
                    '{Assessment.comment}',
                    '{Assessment.ases_a1}',
                    '{Assessment.ases_a2}',
                    '{Assessment.ases_a3}',
                    '{Assessment.ases_a4}',
                    '{Assessment.ases_a5}',
                    '{Assessment.ases_a6}',
                    '{Assessment.ases_a7}',
                    '{Assessment.ases_a8}',
                    '{Assessment.ases_b1}',
                    '{Assessment.ases_b2}',
                    '{Assessment.ases_b3}',
                    '{Assessment.ases_b4}',
                    '{Assessment.ases_b5}',
                    '{Assessment.ases_b6}',
                    '{Assessment.ases_b7}',
                    '{Assessment.ases_b8}',
                    '{Assessment.ases_c1}',
                    '{Assessment.ases_c2}',
                    '{Assessment.ases_c3}',
                    '{Assessment.ases_c4}',
                    '{Assessment.ases_c5}',
                    '{Assessment.ases_c6}',
                    '{Assessment.ases_c7}',
                    '{Assessment.ases_c8}',
                    '{Assessment.ases_d1}',
                    '{Assessment.ases_d2}',
                    '{Assessment.ases_d3}',
                    '{Assessment.ases_d4}',
                    '{Assessment.ases_d5}',
                    '{Assessment.ases_d6}',
                    '{Assessment.ases_d7}',
                    '{Assessment.ases_d8}',
                    '{Assessment.ases_e1}',
                    '{Assessment.ases_e2}',
                    '{Assessment.ases_e3}',
                    '{Assessment.ases_e4}',
                    '{Assessment.ases_e5}',
                    '{Assessment.ases_e6}',
                    '{Assessment.ases_e7}',
                    '{Assessment.ases_e8}')
                    ''')
            else:
                conn.execute(f'''
                UPDATE assessment SET 
                    評価点='{asesPoint}', 
                    コメント='{Assessment.comment}', 
                    ases_a1='{Assessment.ases_a1}', 
                    ases_a2='{Assessment.ases_a2}', 
                    ases_a3='{Assessment.ases_a3}', 
                    ases_a4='{Assessment.ases_a4}', 
                    ases_a5='{Assessment.ases_a5}', 
                    ases_a6='{Assessment.ases_a6}', 
                    ases_a7='{Assessment.ases_a7}', 
                    ases_a8='{Assessment.ases_a8}', 
                    ases_b1='{Assessment.ases_b1}', 
                    ases_b2='{Assessment.ases_b2}', 
                    ases_b3='{Assessment.ases_b3}', 
                    ases_b4='{Assessment.ases_b4}', 
                    ases_b5='{Assessment.ases_b5}', 
                    ases_b6='{Assessment.ases_b6}', 
                    ases_b7='{Assessment.ases_b7}', 
                    ases_b8='{Assessment.ases_b8}', 
                    ases_c1='{Assessment.ases_c1}', 
                    ases_c2='{Assessment.ases_c2}', 
                    ases_c3='{Assessment.ases_c3}', 
                    ases_c4='{Assessment.ases_c4}', 
                    ases_c5='{Assessment.ases_c5}', 
                    ases_c6='{Assessment.ases_c6}', 
                    ases_c7='{Assessment.ases_c7}', 
                    ases_c8='{Assessment.ases_c8}', 
                    ases_d1='{Assessment.ases_d1}', 
                    ases_d2='{Assessment.ases_d2}', 
                    ases_d3='{Assessment.ases_d3}', 
                    ases_d4='{Assessment.ases_d4}', 
                    ases_d5='{Assessment.ases_d5}', 
                    ases_d6='{Assessment.ases_d6}', 
                    ases_d7='{Assessment.ases_d7}', 
                    ases_d8='{Assessment.ases_d8}', 
                    ases_e1='{Assessment.ases_e1}', 
                    ases_e2='{Assessment.ases_e2}', 
                    ases_e3='{Assessment.ases_e3}', 
                    ases_e4='{Assessment.ases_e4}', 
                    ases_e5='{Assessment.ases_e5}', 
                    ases_e6='{Assessment.ases_e6}', 
                    ases_e7='{Assessment.ases_e7}', 
                    ases_e8='{Assessment.ases_e8}'
                WHERE
                    評価年度='{Assessment.ases_year}' and
                    評価月='{Assessment.ases_month}' and
                    社員ID='{Assessment.id}' and
                    評価LV='{Assessment.lv}'
                    ''')
            conn.commit()
            st.success('登録/更新しました')
        else:
            st.error('IDを入力し、登録してください')

# レコードを社員IDの昇順で取得する
with st.expander("評価データ表示"):
    with st.form("view_form", clear_on_submit=False):
        extraction_year = select_year()
        extraction_id = st.text_input('社員IDで抽出')
        extraction_month = st.text_input('評価月で抽出')
        submitted = st.form_submit_button("表示")

    def generate_query(extraction_id=None, extraction_year=None, extraction_month=None):
        base_query = '''
        SELECT b.氏名,a.* FROM assessment As a inner join employee As b on a.社員ID = b.社員ID
        '''
        conditions = []
        if extraction_id:
            conditions.append(f"a.社員ID = '{extraction_id}'")
        if extraction_year:
            conditions.append(f"a.評価年度 = '{extraction_year}'")
        if extraction_month:
            conditions.append(f"a.評価月 = '{extraction_month}'")
        if conditions:
            base_query += ' WHERE ' + ' AND '.join(conditions)
        base_query += ' ORDER BY 社員ID, 評価月 aSC'
        return base_query

if submitted:
    query = generate_query(extraction_id, extraction_year, extraction_month)
    df = pd.read_sql_query(query, conn)
    st.write(df.set_index('社員ID'))

# 選択した評価LVをセッションに保持する
selected = st.radio("評価LVフォーマット選択", ("LV1", "LV2", "LV3", "LV4"), horizontal=True)
if selected:
    st.session_state['rdo_lv'] = selected 

# LV評価登録
with st.expander("評価登録"):
    st.subheader(f"{st.session_state['rdo_lv']}評価項目")

    with st.form("ases1_form", clear_on_submit=False):
        st.write('　※評価年度、評価月、IDが同じデータが存在する場合、上書き更新します')
        Assessment.ases_year = select_year()
        Assessment.ases_month = select_month()
        Assessment.id = st.text_input('社員ID')
        submitted = st.form_submit_button("氏名検索")
        strName = searchName(submitted, Assessment.id,c)
        if strName == 0:
            st.info('社員IDを指定してください')
        elif strName == 1:
            st.info('該当する情報が見つかりませんでした')
        else:
            st.write(strName)
        Assessment.name = strName

        if st.session_state['rdo_lv'] == 'LV1':
            Assessment.lv = 1
            st.subheader('ビジネスマナー')
            Assessment.ases_a1 = st.selectbox('社会人として適切な言葉遣いや、挨拶をする',('-','A','B','C','D'))
            Assessment.ases_a2 = st.selectbox('時間を守る',('-','A','B','C','D'))
            Assessment.ases_a3 = st.selectbox('誠実な姿勢で業務を行う（サポートしてもらった時のお礼、ミスや注意を受けた際の謝罪、反省、改善）',('-','A','B','C','D'))
            Assessment.ases_a4 = ''
            Assessment.ases_a5 = ''
            Assessment.ases_a6 = ''
            Assessment.ases_a7 = ''
            Assessment.ases_a8 = ''
            st.subheader('モチベーション')
            Assessment.ases_b1 = st.selectbox('同じまたは類似したミス、質問をくりかえさない',('-','A','B','C','D'))
            Assessment.ases_b2 = st.selectbox('分からない事は直ぐに質問する',('-','A','B','C','D'))
            Assessment.ases_b3 = st.selectbox('知識・技術を意欲的に身に付ける',('-','A','B','C','D'))
            Assessment.ases_b4 = ''
            Assessment.ases_b5 = ''
            Assessment.ases_b6 = ''
            Assessment.ases_b7 = ''
            Assessment.ases_b8 = ''
            st.subheader('協調性・コミュニケーション')
            Assessment.ases_c1 = st.selectbox('報連相をする',('-','A','B','C','D'))
            Assessment.ases_c2 = st.selectbox('周囲に困っている人を見つけたときに積極的にサポートする',('-','A','B','C','D'))
            Assessment.ases_c3 = st.selectbox('チームにおける自分の役割を理解し、責任を果たす',('-','A','B','C','D'))
            Assessment.ases_c4 = ''
            Assessment.ases_c5 = ''
            Assessment.ases_c6 = ''
            Assessment.ases_c7 = ''
            Assessment.ases_c8 = ''
            st.subheader('ビジネススキル')
            Assessment.ases_d1 = st.selectbox('質問の内容を明確にする',('-','A','B','C','D'))
            Assessment.ases_d2 = st.selectbox('仕事の目的を明確にする（担当している作業が何のための作業なのか考える）',('-','A','B','C','D'))
            Assessment.ases_d3 = st.selectbox('作業後はセルフチェックをおこなう',('-','A','B','C','D'))
            Assessment.ases_d4 = ''
            Assessment.ases_d5 = ''
            Assessment.ases_d6 = ''
            Assessment.ases_d7 = ''
            Assessment.ases_d8 = ''
            st.subheader('その他')
            Assessment.ases_e1 = st.selectbox('健康管理をおこない、体調不良で業務に支障をきたさないようにする',('-','A','B','C','D'))
            Assessment.ases_e2 = st.selectbox('ストレスに負けず、常に前向きな行動をとる（非加点項目）',('-'), disabled=True)
            Assessment.ases_e3 = st.selectbox('自分なりのストレス解消法を考え実行する（非加点項目）',('-'), disabled=True)
            Assessment.ases_e4 = st.selectbox('ストレスを成長のチャンスとして捉える（非加点項目）',('-'), disabled=True)
            Assessment.ases_e5 = st.selectbox('社内ルール、規律を厳守する',('-','A','B','C','D'))
            Assessment.ases_e6 = ''
            Assessment.ases_e7 = ''
            Assessment.ases_e8 = ''
        elif st.session_state['rdo_lv'] == 'LV2':
            Assessment.lv = 2
            #st.subheader('ビジネスマナー')
            Assessment.ases_a1 = ''
            Assessment.ases_a2 = ''
            Assessment.ases_a3 = ''
            Assessment.ases_a4 = ''
            Assessment.ases_a5 = ''
            Assessment.ases_a6 = ''
            Assessment.ases_a7 = ''
            Assessment.ases_a8 = ''
            #st.subheader('モチベーション')
            Assessment.ases_b1 = ''
            Assessment.ases_b2 = ''
            Assessment.ases_b3 = ''
            Assessment.ases_b4 = ''
            Assessment.ases_b5 = ''
            Assessment.ases_b6 = ''
            Assessment.ases_b7 = ''
            Assessment.ases_b8 = ''
            st.subheader('協調性・コミュニケーション')
            Assessment.ases_c1 = st.selectbox('要点を押えて理路整然と話しをする',('-','A','B','C','D'))
            Assessment.ases_c2 = st.selectbox('相手の話を前向きに聞く態度を取る',('-','A','B','C','D'))
            Assessment.ases_c3 = st.selectbox('適切なタイミングで質問をする',('-','A','B','C','D'))
            Assessment.ases_c4 = ''
            Assessment.ases_c5 = ''
            Assessment.ases_c6 = ''
            Assessment.ases_c7 = ''
            Assessment.ases_c8 = ''
            st.subheader('ビジネススキル')
            Assessment.ases_d1 = st.selectbox('覚えた仕事を活かし応用する（1~10まで説明を聞かなくとも対応できる）',('-','A','B','C','D'))
            Assessment.ases_d2 = st.selectbox('仕事を洗い出し、優先順位をつけて対応する',('-','A','B','C','D'))
            Assessment.ases_d3 = st.selectbox('個人タスクの計画を立てる',('-','A','B','C','D'))
            Assessment.ases_d4 = st.selectbox('作業の効率化を考える',('-','A','B','C','D'))
            Assessment.ases_d5 = st.selectbox('取組むべき課題を明確にする',('-','A','B','C','D'))
            Assessment.ases_d6 = st.selectbox('課題解決のための手順、方法を考える',('-','A','B','C','D'))
            Assessment.ases_d7 = ''
            Assessment.ases_d8 = ''
            st.subheader('その他')
            Assessment.ases_e1 = st.selectbox('ストレスに負けず、常に前向きな行動をとる（非加点項目）',('-'), disabled=True)
            Assessment.ases_e2 = st.selectbox('自分なりのストレス解消法を考え実行する（非加点項目）',('-'), disabled=True)
            Assessment.ases_e3 = st.selectbox('ストレスを成長のチャンスとして捉える（非加点項目）',('-'), disabled=True)
            Assessment.ases_e4 = ''
            Assessment.ases_e5 = ''
            Assessment.ases_e6 = ''
            Assessment.ases_e7 = ''
            Assessment.ases_e8 = ''
        elif st.session_state['rdo_lv'] == 'LV3':
            Assessment.lv = 3
            #st.subheader('ビジネスマナー')
            Assessment.ases_a1 = ''
            Assessment.ases_a2 = ''
            Assessment.ases_a3 = ''
            Assessment.ases_a4 = ''
            Assessment.ases_a5 = ''
            Assessment.ases_a6 = ''
            Assessment.ases_a7 = ''
            Assessment.ases_a8 = ''
            #st.subheader('モチベーション')
            Assessment.ases_b1 = ''
            Assessment.ases_b2 = ''
            Assessment.ases_b3 = ''
            Assessment.ases_b4 = ''
            Assessment.ases_b5 = ''
            Assessment.ases_b6 = ''
            Assessment.ases_b7 = ''
            Assessment.ases_b8 = ''
            st.subheader('協調性・コミュニケーション')
            Assessment.ases_c1 = st.selectbox('能動的に動く（指示待ちしない）',('-','A','B','C','D'))
            Assessment.ases_c2 = st.selectbox('他人が嫌がることも対応する',('-','A','B','C','D'))
            Assessment.ases_c3 = ''
            Assessment.ases_c4 = ''
            Assessment.ases_c5 = ''
            Assessment.ases_c6 = ''
            Assessment.ases_c7 = ''
            Assessment.ases_c8 = ''
            st.subheader('ビジネススキル')
            Assessment.ases_d1 = st.selectbox('品質の高い成果物を生み出す',('-','A','B','C','D'))
            Assessment.ases_d2 = st.selectbox('課題解決のための手順、方法の案を常に複数用意し、最適案を選択する',('-','A','B','C','D'))
            Assessment.ases_d3 = st.selectbox('相手が話しやすい雰囲気をつくる',('-','A','B','C','D'))
            Assessment.ases_d4 = st.selectbox('自分の考え方ややり方にこだわらず、臨機応変に対応する',('-','A','B','C','D'))
            Assessment.ases_d5 = st.selectbox('相手の意見や立場を尊重する',('-','A','B','C','D'))
            Assessment.ases_d6 = st.selectbox('他人の意見、やり方を受け入れ、自己向上に活かす',('-','A','B','C','D'))
            Assessment.ases_d7 = st.selectbox('取引先と良い関係を構築する',('-','A','B','C','D'))
            Assessment.ases_d8 = ''
            st.subheader('その他')
            Assessment.ases_e1 = st.selectbox('自分なりのストレス解消法を考え実行する（非加点項目）',('-'), disabled=True)
            Assessment.ases_e2 = st.selectbox('ストレスを成長のチャンスとして捉える（非加点項目）',('-'), disabled=True)
            Assessment.ases_e3 = ''
            Assessment.ases_e4 = ''
            Assessment.ases_e5 = ''
            Assessment.ases_e6 = ''
            Assessment.ases_e7 = ''
            Assessment.ases_e8 = ''
        elif st.session_state['rdo_lv'] == 'LV4':
            Assessment.lv = 4
            #st.subheader('ビジネスマナー')
            Assessment.ases_a1 = ''
            Assessment.ases_a2 = ''
            Assessment.ases_a3 = ''
            Assessment.ases_a4 = ''
            Assessment.ases_a5 = ''
            Assessment.ases_a6 = ''
            Assessment.ases_a7 = ''
            Assessment.ases_a8 = ''
            #st.subheader('モチベーション')
            Assessment.ases_b1 = ''
            Assessment.ases_b2 = ''
            Assessment.ases_b3 = ''
            Assessment.ases_b4 = ''
            Assessment.ases_b5 = ''
            Assessment.ases_b6 = ''
            Assessment.ases_b7 = ''
            Assessment.ases_b8 = ''
            st.subheader('協調性・コミュニケーション')
            Assessment.ases_c1 = st.selectbox('周囲の人々を巻き込み、目的を達成する',('-','A','B','C','D'))
            Assessment.ases_c2 = ''
            Assessment.ases_c3 = ''
            Assessment.ases_c4 = ''
            Assessment.ases_c5 = ''
            Assessment.ases_c6 = ''
            Assessment.ases_c7 = ''
            Assessment.ases_c8 = ''
            st.subheader('ビジネススキル')
            Assessment.ases_d1 = st.selectbox('自ら目標を設定し、その達成に取り組む',('-','A','B','C','D'))
            Assessment.ases_d2 = st.selectbox('目標達成の手順、方法を考え、確実に進める',('-','A','B','C','D'))
            Assessment.ases_d3 = st.selectbox('困難に遭遇しても、粘り強く行動する',('-','A','B','C','D'))
            Assessment.ases_d4 = st.selectbox('常に新しい発想、考えを身につけるような行動をとる（過去の手法に捉われず、よい結果を生み出すための思考を習慣化する）',('-','A','B','C','D'))
            Assessment.ases_d5 = st.selectbox('配下メンバーに対してリーダーシップを発揮し、部門運営を行う',('-','A','B','C','D'))
            Assessment.ases_d6 = st.selectbox('メンバーへの指揮を積極的に行い、能力アップを実現する',('-','A','B','C','D'))
            Assessment.ases_d7 = st.selectbox('常にコスト・効率を意識した行動をする',('-','A','B','C','D'))
            Assessment.ases_d8 = ''
            st.subheader('メンバー管理')
            Assessment.ases_e1 = st.selectbox('進捗管理ができる',('-','A','B','C','D'))
            Assessment.ases_e2 = st.selectbox('メンバー教育ができる',('-','A','B','C','D'))
            Assessment.ases_e3 = st.selectbox('信頼関係の構築をしている',('-','A','B','C','D'))
            Assessment.ases_e4 = ''
            Assessment.ases_e5 = ''
            Assessment.ases_e6 = ''
            Assessment.ases_e7 = ''
            Assessment.ases_e8 = ''
        else:
            st.write("評価LVを選択してください")

        Assessment.comment = st.text_area('コメント（任意）')
        submitted = st.form_submit_button("登録")

        registAses(submitted, Assessment)

# データ削除
with st.expander("評価削除"):
    with st.form("del_form", clear_on_submit=True):
        del_ases_year = st.text_input('対象評価年度')
        del_ases_month = st.text_input('対象評価月')
        del_id = st.text_input('社員ID')
        submitted = st.form_submit_button("削除")
        if submitted:
            if del_ases_year or del_ases_month or del_id:
                conn.execute(f'''
                             DELETE FROM assessment 
                             WHERE 評価年度='{del_ases_year}'
                             and 評価月='{del_ases_month}' 
                             and 社員ID='{del_id}';
                            ''')
                conn.commit()
                st.success('削除しました')

            else:
                st.write("削除条件をすべて指定してください")

st.subheader('特別評価・補正評価')

# レコードを社員IDの昇順で取得する
with st.expander("特別評価データ表示"):
    with st.form("sp_view_form", clear_on_submit=False):
        extraction_year = select_year()
        extraction_id = st.text_input('社員IDで抽出')
        submitted = st.form_submit_button("表示")

    def generate_query(table_name, extraction_id=None, extraction_year=None):
        base_query = f'''
        SELECT b.氏名,a.* FROM {table_name} As a inner join employee As b on a.社員ID = b.社員ID
        '''
        conditions = []
        if extraction_id:
            conditions.append(f"a.社員ID = '{extraction_id}'")
        if extraction_year:
            conditions.append(f"a.評価年度 = '{extraction_year}'")
        if conditions:
            base_query += ' WHERE ' + ' AND '.join(conditions)
        base_query += ' ORDER BY 社員ID aSC'
        return base_query

    if submitted:
        query = generate_query('assessment_sp', extraction_id, extraction_year)
        df = pd.read_sql_query(query, conn)
        st.write(df.set_index('社員ID'))

# 特別評価・補正評価登録
with st.expander("特別評価・補正評価登録"):
    with st.form("sp_ases1_form", clear_on_submit=False):
        ases_year = select_year()
        id = st.text_input('社員ID')
        submitted = st.form_submit_button("氏名検索")
        strName = searchName(submitted, id, c)
        if strName == 0:
            st.info('社員IDを指定してください')
        elif strName == 1:
            st.info('該当する情報が見つかりませんでした')
        else:
            st.write(strName)
        name = strName

        ases_item = st.text_input('評価項目')
        ases_content = st.text_input('評価内容')
        ases_point = st.text_input('評価点')
        comment = st.text_area('コメント（任意）')
        ases_mngid = st.text_input('【更新のみ指定】評価管理ID')
        submitted = st.form_submit_button("登録")

        # 入力されたデータをSQLiteにINSERTする
        if submitted:
            # 更新処理
            if ases_mngid:
                try:
                    conn.execute(f'''
                    UPDATE assessment_sp SET
                    評価年度='{ases_year}', 評価項目='{ases_item}', 評価内容='{ases_content}', 評価点='{ases_point}', コメント='{comment}'
                    WHERE 評価管理ID='{ases_mngid}'
                    ''')
                    conn.commit()
                    st.success('登録/更新しました')
                except sqlite3.OperationalError as e:
                    st.error('更新対象が見つかりませんでした')
                except sqlite3.DatabaseError as e2:
                    st.error('DB接続に失敗しました')
            else:
                # 登録処理
                if id:
                    conn.execute(f'''
                    INSERT INTO assessment_sp 
                                 (評価年度, 
                                 社員ID, 
                                 評価項目, 
                                 評価内容, 
                                 評価点, 
                                 コメント)
                    VALUES ('{ases_year}', 
                            '{id}', 
                            '{ases_item}', 
                            '{ases_content}', 
                            '{ases_point}', 
                            '{comment}')
                    ''')
                    conn.commit()
                    st.success('登録/更新しました')
                else:
                    st.error('IDを入力し、登録してください')

# データ削除
with st.expander("特別評価・補正評価削除"):
    with st.form("sp_del_form_unique", clear_on_submit=True):
        del_id = st.text_input('評価管理ID')
        submitted = st.form_submit_button("削除")
        if submitted:
            if del_id:
                conn.execute(f'''DELETE FROM assessment_sp WHERE 評価管理ID='{del_id}';''')
                conn.commit()
                st.success('削除しました')
            else:
                st.write("削除条件を指定してください")
close_db(conn)


