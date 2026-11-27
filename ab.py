import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="班級飲料團購統計", page_icon="🧋", layout="wide")

# ---------- 視覺美化：奶茶系漸層背景 ----------
st.markdown("""
  <style>
  @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;600;700;800&display=swap');
  html, body, [class*="css"] { font-family: 'Noto Sans TC', sans-serif; }
  .stApp {
    background:
      radial-gradient(ellipse at 8% 5%, rgba(255,220,190,.75), transparent 34%),
      radial-gradient(ellipse at 92% 12%, rgba(244,198,190,.55), transparent 30%),
      linear-gradient(145deg, #fff8ef 0%, #fff3eb 48%, #f9e8e3 100%);
    color: #493b35;
  }
  [data-testid="stHeader"] { background: rgba(255,248,240,.55); }
  [data-testid="stSidebar"] {
    background: linear-gradient(180deg, #f8e4d5 0%, #f5ddd7 100%);
    border-right: 1px solid rgba(160,112,91,.12);
  }
  .block-container { max-width: 1180px; padding-top: 2.2rem; padding-bottom: 3rem; }
  h1 { color: #68483c !important; font-weight: 800 !important; letter-spacing: .03em; }
  h2, h3 { color: #795748 !important; font-weight: 700 !important; }
  p, label, [data-testid="stCaptionContainer"] { color: #78665d; }
  [data-testid="stForm], [data-testid="stDataFrame"],
  [data-testid="stMetric"], [data-testid="stExpander"] {
    background: rgba(255,255,255,.72);
    border: 1px solid rgba(181,133,111,.18);
    border-radius: 18px;
    box-shadow: 0 8px 26px rgba(111,76,59,.07);
  }
  [data-testid="stMetric"] { padding: 16px 18px; }
  [data-testid="stMetricValue"] { color: #a76550; font-weight: 800; }
  .stButton > button, .stDownloadButton > button,
  [data-testid="stFormSubmitButton"] > button {
    border: 0; border-radius: 12px; color: white; font-weight: 700;
    background: linear-gradient(110deg, #c98268, #df9b83);
    box-shadow: 0 5px 14px rgba(174,105,81,.2); transition: .2s ease;
  }
  .stButton > button:hover, .stDownloadButton > button:hover,
  [data-testid="stFormSubmitButton"] > button:hover {
    color: white; border: 0; transform: translateY(-2px);
    background: linear-gradient(110deg, #b97059, #d58c75);
  }
  .stTextInput input, .stNumberInput input,
  .stSelectbox [data-baseweb="select"] > div {
    border-radius: 10px; background: rgba(255,255,255,.88);
  }
  hr { border-color: rgba(166,119,98,.18); }
  [data-testid="stAlert"] { border-radius: 12px; }
  footer { visibility: hidden; }
  </style>
  """, unsafe_allow_html=True)

st.title("🧋 班級飲料團購統計")
st.caption("快速登記同學訂單，並自動統計總杯數與總金額。")

if "orders" not in st.session_state:
    st.session_state.orders = []

with st.sidebar:
    st.header("團購資訊")
    class_name = st.text_input("班級", value="例如：二年三班")
    order_deadline = st.text_input("收單時間（選填）", placeholder="例如：今天 12:00")
    st.divider()
    st.caption("資料目前儲存在此 Streamlit 工作階段；重新啟動或清除工作階段後不會保留。")

st.subheader("新增訂單")
with st.form("order_form", clear_on_submit=True):
    c1, c2, c3 = st.columns(3)
    name = c1.text_input("訂購人姓名 *")
    drink = c2.text_input("飲料名稱 *", placeholder="例如：珍珠奶茶")
    quantity = c3.number_input("杯數", min_value=1, max_value=99, value=1, step=1)

    c4, c5, c6 = st.columns(3)
    sugar = c4.selectbox("甜度", ["正常糖", "少糖", "半糖", "微糖", "無糖", "固定甜度", "其他"])
    ice = c5.selectbox("冰塊", ["正常冰", "少冰", "微冰", "去冰", "完全去冰", "熱飲", "常溫"])
    unit_price = c6.number_input("單杯金額（元）", min_value=0, max_value=10000, value=60, step=5)

    note = st.text_input("備註（選填）", placeholder="例如：珍珠另外加料、不要吸管")
    submitted = st.form_submit_button("➕ 加入訂單", use_container_width=True)

    if submitted:
        if not name.strip() or not drink.strip():
            st.error("請填寫訂購人姓名與飲料名稱。")
        else:
            st.session_state.orders.append({
                "訂購時間": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "姓名": name.strip(),
                "飲料": drink.strip(),
                "甜度": sugar,
                "冰塊": ice,
                "杯數": int(quantity),
                "單杯金額": int(unit_price),
                "小計": int(quantity) * int(unit_price),
                "備註": note.strip(),
            })
            st.success(f"已加入 {name.strip()} 的訂單！")

st.divider()
orders = st.session_state.orders

st.subheader("📊 訂單統計")
total_cups = sum(o["杯數"] for o in orders)
total_amount = sum(o["小計"] for o in orders)
people_count = len(set(o["姓名"] for o in orders))

m1, m2, m3 = st.columns(3)
m1.metric("總杯數", f"{total_cups} 杯")
m2.metric("總金額", f"NT$ {total_amount:,}")
m3.metric("訂單筆數", f"{len(orders)} 筆")

if orders:
    st.subheader("📋 訂單明細")
    df = pd.DataFrame(orders)
    st.dataframe(
        df[["姓名", "飲料", "甜度", "冰塊", "杯數", "單杯金額", "小計", "備註"]],
        use_container_width=True,
        hide_index=True,
    )

    # 按姓名彙整，方便收款
    summary = df.groupby("姓名", as_index=False).agg(
        杯數=("杯數", "sum"),
        應付金額=("小計", "sum"),
    )
    st.subheader("💰 個人應付金額")
    st.dataframe(summary, use_container_width=True, hide_index=True)

    csv = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "⬇️ 下載訂單 CSV",
        data=csv,
        file_name="班級飲料團購訂單.csv",
        mime="text/csv",
        use_container_width=True,
    )

    with st.expander("管理訂單"):
        labels = [
            f'{i + 1}. {o["姓名"]}｜{o["飲料"]}｜{o["杯數"]} 杯｜NT$ {o["小計"]}'
            for i, o in enumerate(orders)
        ]
        selected = st.selectbox("選擇要刪除的訂單", range(len(labels)), format_func=lambda i: labels[i])
        if st.button("🗑️ 刪除選取訂單"):
            st.session_state.orders.pop(selected)
            st.rerun()
        if st.button("清空全部訂單", type="secondary"):
            st.session_state.orders = []
            st.rerun()
else:
    st.info("目前還沒有訂單，請從上方新增第一筆飲料訂單。")

st.caption("小提醒：每筆訂單可包含多杯相同飲料；金額會依「杯數 × 單杯金額」自動計算。")
