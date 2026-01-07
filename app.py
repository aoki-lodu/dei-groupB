import streamlit as st
import pandas as pd
import random
import time

# ==========================================
# 0. 設定 & データ定義
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
# 1. メンバー削除ロジック（ここを最初に行う！）
# ==========================================
# 初期化
if "selected_members" not in st.session_state:
    st.session_state.selected_members = [c["name"] for c in CHARACTERS_DB[:3]]

# 「退職予約」がある場合、ここで実際にリストから削除して更新する
if "pending_removal" in st.session_state and st.session_state.pending_removal:
    remove_list = st.session_state.pending_removal
    # リストから削除
    new_members = [m for m in st.session_state.selected_members if m not in remove_list]
    # 更新（Widgetが作られる前なのでエラーにならない！）
    st.session_state.selected_members = new_members
    # 予約をクリア
    del st.session_state.pending_removal

# ==========================================
# 2. サイドバー
# ==========================================
with st.sidebar:
    st.header("🎮 ゲーム操作盤")
    
    # ウィジェットの作成
    selected_char_names = st.multiselect(
        "👤 参加メンバー",
        [c["name"] for c in CHARACTERS_DB],
        key="selected_members"
    )
    
    st.divider()
    
    selected_policy_names = st.multiselect(
        "🃏 実行した施策",
        [p["name"] for p in POLICIES_DB],
        default=[]
    )
    
    st.divider()
    if st.button("🔄 リセット", type="primary"):
        st.session_state.selected_members = [c["name"] for c in CHARACTERS_DB[:3]]
        if "pending_removal" in st.session_state:
            del st.session_state.pending_removal
        st.rerun()

# データの抽出
active_chars = [c for c in CHARACTERS_DB if c["name"] in selected_char_names]
active_policies = [p for p in POLICIES_DB if p["name"] in selected_policy_names]

# ==========================================
# 3. 計算ロジック
# ==========================================
total_power = 0
active_shields = set()
for pol in active_policies:
    if "shield" in pol["type"]:
        for t in pol["target"]:
            active_shields.add(t)

char_results = []
for char in active_chars:
    current_power = char["base"]
    status_tags = []
    
    for pol in active_policies:
        if set(char["icons"]) & set(pol["target"]):
            current_power += pol["power"]
            if "promote" in pol["type"] and "🟢昇進" not in status_tags: status_tags.append("🟢昇進")
            if "recruit" in pol["type"] and "🔵採用" not in status_tags: status_tags.append("🔵採用")
            
    risks = [icon for icon in char["icons"] if icon not in active_shields]
    is_safe = len(risks) == 0 
    
    total_power += current_power
    char_results.append({
        "data": char,
        "power": current_power,
        "tags": status_tags,
        "risks": risks,
        "is_safe": is_safe
    })

# ==========================================
# 4. メイン画面レイアウト
# ==========================================
st.title("🎲 DE&I 組織シミュレーター")

c1, c2, c3 = st.columns(3)
with c1:
    st.metric("🏆 チーム仕事力", f"{total_power} pt")
with c2:
    if active_shields:
        shield_text = " ".join(sorted(list(active_shields)))
    else:
        shield_text = "ー"
    st.metric("🛡️ ガード中の属性", shield_text)
with c3:
    st.metric("👥 メンバー数", f"{len(active_chars)} 名")

st.divider()

# ダイスロールセクション
st.subheader("🎲 運命のダイスロール")
col_dice_btn, col_dice_result = st.columns([1, 2])

with col_dice_btn:
    roll_btn = st.button("サイコロを振る！", type="primary", use_container_width=True)

with col_dice_result:
    if roll_btn:
        with st.spinner("コロコロ..."):
            time.sleep(1)
            dice = random.randint(1, 6)
        
        st.markdown(f"### 出目: **【 {dice} 】**")
        
        if dice == 1:
            st.balloons()
            st.success("🎉 **セーフ！** トラブルは起きませんでした！")
        else:
            risk_attr = RISK_MAP.get(dice)
            st.warning(f"⚠️ 対象: **{risk_attr}** の属性を持つメンバー")
            
            # 離職判定
            dropouts = [res["data"]["name"] for res in char_results if risk_attr in res["risks"]]
            
            if dropouts:
                st.error(f"😱 **離職発生！**: {', '.join(dropouts)} さんが退職します...")
                st.write("🔄 メンバーリストから削除しています...")
                
                time.sleep(3)
                
                # 【修正ポイント】ここで直接削除せず、「予約」だけして再起動する
                st.session_state.pending_removal = dropouts
                st.rerun()

            elif risk_attr in active_shields:
                st.info(f"🛡️ **ガード成功！** 施策のおかげで {risk_attr} のメンバーは守られました！")
            else:
                st.success("💨 該当するメンバーがいなかったのでセーフ！")

st.divider()

st.subheader("📊 組織メンバーの状態")

cols = st.columns(3)
if not char_results:
    st.info("メンバーがいません。サイドバーから追加してください。")
else:
    for i, res in enumerate(char_results):
        with cols[i % 3]:
            emoji_status = "🛡️鉄壁" if res["is_safe"] else "⚠️危険"
            with st.container():
                st.markdown(f"**{res['data']['name']}**")
                st.caption(f"属性: {''.join(res['data']['icons'])}")
                st.progress(min(res["power"] / 10, 1.0), text=f"仕事力: {res['power']}")
                if res["tags"]:
                    st.markdown(" ".join([f"`{t}`" for t in res["tags"]]))
                else:
                    st.caption("特殊効果なし")
                if res["is_safe"]:
                    st.success(f"{emoji_status}")
                else:
                    st.error(f"{emoji_status}: {''.join(res['risks'])}が出たらアウト")
