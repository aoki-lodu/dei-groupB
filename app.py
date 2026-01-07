import streamlit as st
import pandas as pd
import random
import time

# ==========================================
# 0. 設定
# ==========================================
st.set_page_config(page_title="LODU Game", layout="wide", initial_sidebar_state="expanded")

# カスタムCSS
st.markdown("""
<style>
    .big-font { font-size:20px !important; font-weight: bold; }
    .card { background-color: #f0f2f6; padding: 15px; border-radius: 10px; margin-bottom: 10px; border-left: 5px solid #ff4b4b; }
    .card-safe { border-left: 5px solid #00c853; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 1. ゲームデータ定義
# ==========================================
ICONS = {"くらし(💚)": "💚", "キャリア(📖)": "📖", "グローバル(🌏)": "🌏", "アイデンティティ(🌈)": "🌈", "フェア(⚖️)": "⚖️"}
RISK_MAP = {2: "💚", 3: "📖", 4: "🌏", 5: "🌈", 6: "⚖️"}

CHARACTERS_DB = [
    {"name": "白石 凛子", "base": 3, "icons": ["🌏", "🌈"], "role": "Manager"},
    {"name": "山本 大翔", "base": 2, "icons": ["🌈"], "role": "Staff"},
    {"name": "川瀬 美羽", "base": 1, "icons": ["💚", "📖", "🌈"], "role": "Newbie"},
    {"name": "Hanna Schmidt", "base": 2, "icons": ["💚", "🌏", "⚖️"], "role": "Specialist"},
    {"name": "宮下 慧", "base": 3, "icons": ["📖", "🌈"], "role": "Expert"},
    {"name": "川口 由衣", "base": 3, "icons": ["📖"], "role": "Leader"},
]

POLICIES_DB = [
    {"name": "ペアワーク＆コードレビュー", "target": ["📖", "🌈"], "power": 2, "type": ["promote"]},
    {"name": "時短・コア短縮", "target": ["💚"], "power": 2, "type": ["shield", "recruit"]},
    {"name": "二言語テンプレ＆用語集", "target": ["🌏"], "power": 1, "type": ["recruit"]},
    {"name": "ERG経営提言", "target": ["⚖️"], "power": 1, "type": ["promote"]},
    {"name": "透明な評価会(校正)", "target": ["🌈", "⚖️"], "power": 0, "type": ["shield", "promote"]},
    {"name": "アクセシブルツール支給", "target": ["💚"], "power": 2, "type": ["shield"]},
    {"name": "リターンシップ", "target": ["📖", "💚"], "power": 0, "type": ["recruit", "promote"]},
    {"name": "ATSバイアスアラート", "target": ["📖", "🌈"], "power": 0, "type": ["recruit"]},
]

# ==========================================
# 2. サイドバー（ここを変えました！）
# ==========================================
with st.sidebar:
    st.header("🎮 ゲーム操作盤")
    
    # セッション状態（記憶領域）にメンバーリストがない場合、初期化する
    if "selected_members" not in st.session_state:
        st.session_state.selected_members = [c["name"] for c in CHARACTERS_DB[:3]]

    # key="selected_members" を指定することで、プログラムからこのリストを操作できるようにする
    selected_char_names = st.multiselect(
        "👤 参加メンバー",
        [c["name"] for c in
