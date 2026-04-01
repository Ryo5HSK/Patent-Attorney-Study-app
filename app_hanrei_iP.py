import streamlit as st
import pandas as pd
import random

PASSWORD = "1203"

if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    pw = st.text_input("パスワードを入力", type="password")
    if st.button("ログイン"):
        if pw == PASSWORD:
            st.session_state.auth = True
        else:
            st.error("パスワードが違います")
    st.stop()

file_name = "復習用問題_判例_論点.xlsx"

@st.cache_data
def load_data():
    return pd.read_excel(file_name)

df = load_data()

# ===== 初期化 =====
if "data" not in st.session_state:
    filtered_df = df[(df.iloc[:, 0] >= 1) & (df.iloc[:, 0] <= 3)]

    df_A = filtered_df[filtered_df.iloc[:, 3] == 'A']
    df_B = filtered_df[filtered_df.iloc[:, 3] == 'B']
    df_C = filtered_df[filtered_df.iloc[:, 3] == 'C']

    st.session_state.data = pd.concat([
        df_A.sample(n=min(1, len(df_A))),
        df_B.sample(n=min(3, len(df_B))),
        df_C.sample(n=min(6, len(df_C)))
    ])


if "current" not in st.session_state:
    st.session_state.current = None

if "show_answer" not in st.session_state:
    st.session_state.show_answer = False

if "queue" not in st.session_state:
    st.session_state.queue = []

if "step" not in st.session_state:
    st.session_state.step = 0

st.title("弁理士試験 学習アプリ")

# ===== 問題出題 =====
if st.button("問題を出す"):
    st.session_state.step += 1

    due_questions = [q for q in st.session_state.queue if q["due"] <= st.session_state.step]

    if due_questions:
        q = random.choice(due_questions)
        st.session_state.current = None
        st.session_state.recall_row = q["row"]
        st.session_state.queue.remove(q)

    elif not st.session_state.data.empty:
        st.session_state.current = random.randrange(len(st.session_state.data))

    st.session_state.show_answer = False

# ===== 問題表示 =====
if st.session_state.current is not None:
    row = st.session_state.data.iloc[st.session_state.current]

    st.subheader("問題")
    st.markdown(row.iloc[1].replace("\n", "  \n"))

    if st.button("答えを見る"):
        st.session_state.show_answer = True

# ===== 解答表示 =====
if st.session_state.show_answer:
    row = st.session_state.data.iloc[st.session_state.current]

    st.subheader("解答")
    st.markdown(row.iloc[2].replace("\n", "  \n"))

    result = st.radio("正解しましたか？", ["y", "n"], key="result")

    if result == "y":
        new_rank = st.selectbox("新しいRank", ["A", "B", "C"], key="rank")

        if st.button("更新して次へ"):
            idx = row.name
            df.at[idx, df.columns[3]] = new_rank
            df.to_excel(file_name, index=False)

            st.session_state.data = st.session_state.data.drop(
    st.session_state.data.index[st.session_state.current]
).reset_index(drop=True)
            st.session_state.current = None
            st.session_state.show_answer = False

            st.rerun()

    elif result == "n":
        if st.button("次の問題へ"):

            remaining = len(st.session_state.data) + len(st.session_state.queue)

            if remaining <= 2:
                delay = 1
            else:
                delay = random.randint(2, 3)

            st.session_state.queue.append({
    "row": row,
    "due": st.session_state.step + delay
})

            st.session_state.current = None
            st.session_state.show_answer = False

            st.rerun()

# ===== 全問終了時の表示 =====
if st.session_state.data.empty and not st.session_state.queue:
    st.success("🎉 すべての問題が終了しました！")
    if st.button("もう一度やる"):
        del st.session_state.data
        del st.session_state.current
        del st.session_state.show_answer
        st.rerun()
    st.stop()