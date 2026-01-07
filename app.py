import streamlit as st
import pandas as pd
import random

# ==========================================
# 1. ゲームデータ定義
# ==========================================

# アイコン定義
ICONS = {
    "くらし(💚)": "💚",
    "キャリア(📖)": "📖",
    "グローバル(🌏)": "🌏",
    "アイデンティティ(🌈)": "🌈",
    "フェア(⚖️)": "⚖️"
}

# リスクの出目定義 (1はセーフ)
RISK_MAP = {
    2: "💚",
    3: "📖",
    4: "🌏",
    5: "🌈",
    6: "⚖️"
}

# 人財カードデータ
CHARACTERS_DB = [
    {"name": "白石 凛子", "base": 3, "icons": ["🌏", "🌈"]},
    {"name": "山本 大翔", "base": 2, "icons": ["🌈"]},
    {"name": "川瀬 美羽", "base": 1, "icons": ["💚", "📖", "🌈"]},
    {"name": "Hanna Schmidt", "base": 2, "icons": ["💚", "🌏", "⚖️"]},
    {"name": "宮下 慧", "base": 3, "icons": ["📖", "🌈"]}, 
    {"name": "川口 由衣", "base": 3, "icons": ["📖"]},     
]

# 施策カードデータ
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
# 2. アプリのレイアウト設定
# ==========================================
st.set_page_config(page_title="LODU Game Calculator", layout="wide")

st.title("🎲 DE&I ゲーム計算機")
st.markdown("施策を選択して、組織の状態をチェックしよう！")

# サイドバー：カードの選択
st.sidebar.header("🎴 場の状況を入力")

# 参加しているメンバーを選択
selected_char_names = st.sidebar.multiselect(
    "参加メンバーを選んでください",
    [c["name"] for c in CHARACTERS_DB],
    default=[c["name"] for c in CHARACTERS_DB[:4]] # 初期値は4人
)

# 実行した施策を選択
selected_policy_names = st.sidebar.multiselect(
    "実行した施策を選んでください",
    [p["name"] for p in POLICIES_DB],
    default=[]
)

# データの抽出
active_chars = [c for c in CHARACTERS_DB if c["name"] in selected_char_names]
active_policies = [p for p in POLICIES_DB if p["name"] in selected_policy_names]

# ==========================================
# 3. 計算ロジック
# ==========================================

total_power = 0
results = []

# 現在の場の「守り(盾)」状況を確認
active_shields = set() 
for pol in active_policies:
    if "shield" in pol["type"]:
        for t in pol["target"]:
            active_shields.add(t)

for char in active_chars:
    current_power = char["base"]
    status_text = []
    risk_icons = []
    
    # 施策効果の適用
    for pol in active_policies:
        if set(char["icons"]) & set(pol["target"]):
            current_power += pol["power"]
            if "promote" in pol["type"] and "🟢昇進" not in status_text:
                status_text.append("🟢昇進")
            if "recruit" in pol["type"] and "🔵採用" not in status_text:
                status_text.append("🔵採用")

    # リスク判定
    for icon in char["icons"]:
        if icon not in active_shields:
            risk_icons.append(icon)

    total_power += current_power
    
    results.append({
        "名前": char["name"],
        "アイコン": "".join(char["icons"]),
        "仕事力": current_power,
        "状態": " ".join(status_text) if status_text else "ー",
        "危険な出目": risk_icons
    })

# ==========================================
# 4. 結果表示
# ==========================================

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="🏆 チーム合計仕事力", value=total_power)
with col2:
    st.metric(label="🛡️ 離職防止(盾)", value=f"{len(active_shields)} 属性ガード中")
with col3:
    st.metric(label="👥 メンバー数", value=f"{len(active_chars)} 名")

st.divider()

st.subheader("🎲 運命のダイスロール")
if st.button("サイコロを振る！"):
    dice = random.randint(1, 6)
    st.success(f"出目は... **【 {dice} 】** です！")
    
    if dice == 1:
        st.balloons()
        st.markdown("### 🎉 セーフ！誰も辞めません！")
    else:
        risk_attr = RISK_MAP.get(dice)
        if risk_attr:
            st.markdown(f"### 対象属性: {risk_attr} (出目{dice})")
            dropouts = []
            for res in results:
                if risk_attr in res["危険な出目"]:
                    dropouts.append(res["名前"])
            
            if dropouts:
                st.error(f"😱 離職発生！: **{', '.join(dropouts)}** さんが退職します...")
            else:
                if risk_attr in active_shields:
                    st.info(f"🛡️ 施策の効果でガードしました！離職者はゼロです！")
                else:
                    st.info("該当するメンバーはいませんでした。セーフ！")

st.divider()

st.subheader("📊 メンバー詳細")
if results:
    df = pd.DataFrame(results)
    df["危険な出目"] = df["危険な出目"].apply(lambda x: "⚠️" + "".join(x) if x else "✅安全")
    st.dataframe(df, use_container_width=True)
