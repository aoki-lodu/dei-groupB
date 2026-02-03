import streamlit as st
import pandas as pd

# ==========================================
# 0. 設定 & データ定義
# ==========================================
st.set_page_config(page_title="LODU Game Mobile", layout="wide", initial_sidebar_state="collapsed")

# --- カスタムCSS（スマホ最適化） ---
st.markdown("""
<style>
    html, body, [class*="css"] {
        font-family: 'Helvetica Neue', 'Hiragino Kaku Gothic ProN', 'ヒラギノ角ゴ ProN W3', sans-serif;
    }
    /* スコアボード */
    .score-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(80px, 1fr));
        gap: 8px;
        background: #ffffff;
        padding: 10px;
        border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        text-align: center;
    }
    .score-item {
        display: flex; flex-direction: column; justify-content: center; align-items: center;
    }
    .score-label { font-size: 11px; color: #666; white-space: nowrap; }
    .score-value { font-size: 16px; font-weight: bold; color: #333; }
    
    /* 施策カード */
    .policy-card {
        background: white; border: 1px solid #ddd; padding: 10px; 
        border-radius: 6px; margin-bottom: 8px; 
        display: flex; justify-content: space-between; align-items: center;
    }
    .tag {
        font-size: 0.75em; padding: 2px 5px; border-radius: 4px; margin-left: 3px;
    }
    /* データフレームのヘッダーを隠すための調整 */
    thead tr th:first-child { display: none }
    tbody th { display: none }
</style>
""", unsafe_allow_html=True)

# --- 定数定義 ---
RISK_MAP_DISPLAY = {
    "1": "🎉 セーフ", "2": "💚 くらし", "3": "📖 キャリア", 
    "4": "🌏 グローバル", "5": "🌈 アイデンティティ", "6": "⚖️ フェア"
}
SORT_ORDER = ['💚', '📖', '🌏', '🌈', '⚖️']

# --- ✅ 人財データ ---
CHARACTERS_DB = [
    {"name": "井上 菜々", "icons": ["💚"], "base": 1},
    {"name": "木村 拓海", "icons": ["💚"], "base": 1},
    {"name": "林 佳奈", "icons": ["💚"], "base": 1},
    {"name": "清水 友香", "icons": ["💚"], "base": 1},
    {"name": "池田 悠真", "icons": ["💚"], "base": 1},
    {"name": "橋本 紗季", "icons": ["💚"], "base": 2},
    {"name": "山崎 優斗", "icons": ["💚"], "base": 2},
    {"name": "阿部 千尋", "icons": ["💚"], "base": 2},
    {"name": "森 真由", "icons": ["💚"], "base": 2},
    {"name": "池上 直樹", "icons": ["💚"], "base": 3},
    {"name": "大野 未来", "icons": ["💚"], "base": 3},
    {"name": "石井 直人", "icons": ["💚"], "base": 3},
    {"name": "原田 怜", "icons": ["💚"], "base": 4},
    {"name": "田村 結菜", "icons": ["💚"], "base": 4},
    {"name": "竹内 智也", "icons": ["💚"], "base": 5},
    {"name": "長谷川 凛", "icons": ["📖"], "base": 1},
    {"name": "近藤 海斗", "icons": ["📖"], "base": 1},
    {"name": "石田 紅葉", "icons": ["📖"], "base": 1},
    {"name": "岡本 さとみ", "icons": ["📖"], "base": 1},
    {"name": "藤田 陽", "icons": ["📖"], "base": 1},
    {"name": "遠藤 大地", "icons": ["📖"], "base": 2},
    {"name": "青木 里奈", "icons": ["📖"], "base": 2},
    {"name": "宮本 蒼真", "icons": ["📖"], "base": 2},
    {"name": "三浦 真琴", "icons": ["📖"], "base": 2},
    {"name": "松本 直哉", "icons": ["📖"], "base": 3},
    {"name": "川口 由衣", "icons": ["📖"], "base": 3},
    {"name": "内田 隼", "icons": ["📖"], "base": 3},
    {"name": "杉本 麻衣", "icons": ["📖"], "base": 4},
    {"name": "中島 慎也", "icons": ["📖"], "base": 4},
    {"name": "金子 拓真", "icons": ["📖"], "base": 5},
    {"name": "Ava Chen", "icons": ["🌏"], "base": 1},
    {"name": "Daniel Kim", "icons": ["🌏"], "base": 1},
    {"name": "Priya Singh", "icons": ["🌏"], "base": 1},
    {"name": "An Nguyen", "icons": ["🌏"], "base": 1},
    {"name": "Juan Martínez", "icons": ["🌏"], "base": 2},
    {"name": "Hyejin Park", "icons": ["🌏"], "base": 2},
    {"name": "Ethan Wang", "icons": ["🌏"], "base": 2},
    {"name": "Olga Petrov", "icons": ["🌏"], "base": 2},
    {"name": "Liam O'Connor", "icons": ["🌏"], "base": 3},
    {"name": "Sofia García", "icons": ["🌏"], "base": 3},
    {"name": "Minh Tran", "icons": ["🌏"], "base": 3},
    {"name": "Amira Hassan", "icons": ["🌏"], "base": 4},
    {"name": "Carlos Souza", "icons": ["🌏"], "base": 4},
    {"name": "Zoe Müller", "icons": ["🌏"], "base": 5},
    {"name": "佐藤 陽菜", "icons": ["🌈"], "base": 1},
    {"name": "鈴木 翔太", "icons": ["🌈"], "base": 1},
    {"name": "高橋 美咲", "icons": ["🌈"], "base": 1},
    {"name": "伊藤 葵", "icons": ["🌈"], "base": 1},
    {"name": "田中 蓮", "icons": ["🌈"], "base": 1},
    {"name": "中村 さくら", "icons": ["🌈"], "base": 2},
    {"name": "山本 大翔", "icons": ["🌈"], "base": 2},
    {"name": "渡辺 結衣", "icons": ["🌈"], "base": 2},
    {"name": "加藤 ひかる", "icons": ["🌈"], "base": 3},
    {"name": "吉田 玲奈", "icons": ["🌈"], "base": 3},
    {"name": "山田 隼人", "icons": ["🌈"], "base": 3},
    {"name": "佐々木 真央", "icons": ["🌈"], "base": 4},
    {"name": "山口 咲良", "icons": ["🌈"], "base": 4},
    {"name": "斎藤 陽介", "icons": ["🌈"], "base": 5},
    {"name": "村上 拓人", "icons": ["⚖️"], "base": 1},
    {"name": "新井 美月", "icons": ["⚖️"], "base": 1},
    {"name": "大西 悠", "icons": ["⚖️"], "base": 1},
    {"name": "谷口 実央", "icons": ["⚖️"], "base": 1},
    {"name": "本田 琴音", "icons": ["⚖️"], "base": 1},
    {"name": "平野 健太", "icons": ["⚖️"], "base": 2},
    {"name": "工藤 彩花", "icons": ["⚖️"], "base": 2},
    {"name": "上田 翔", "icons": ["⚖️"], "base": 2},
    {"name": "原 真子", "icons": ["⚖️"], "base": 2},
    {"name": "神田 亮", "icons": ["⚖️"], "base": 3},
    {"name": "安藤 望", "icons": ["⚖️"], "base": 3},
    {"name": "野村 智", "icons": ["⚖️"], "base": 3},
    {"name": "浜田 佑香", "icons": ["⚖️"], "base": 4},
    {"name": "片山 駿", "icons": ["⚖️"], "base": 4},
    {"name": "柴田 悠斗", "icons": ["⚖️"], "base": 5},
    {"name": "花田 里緒", "icons": ["💚", "📖"], "base": 1},
    {"name": "Julia Novak", "icons": ["💚", "🌏"], "base": 4},
    {"name": "杉浦 颯太", "icons": ["💚", "🌏"], "base": 4},
    {"name": "田辺 海斗", "icons": ["💚", "🌈"], "base": 1},
    {"name": "長井 智哉", "icons": ["💚", "🌈"], "base": 3},
    {"name": "山根 悠", "icons": ["💚", "⚖️"], "base": 2},
    {"name": "町田 柚希", "icons": ["📖", "🌏"], "base": 2},
    {"name": "佐伯 啓", "icons": ["📖", "🌈"], "base": 1},
    {"name": "宮下 慧", "icons": ["📖", "🌈"], "base": 3},
    {"name": "島田 こはる", "icons": ["📖", "⚖️"], "base": 2},
    {"name": "望月 さや", "icons": ["🌏", "🌈"], "base": 1},
    {"name": "白石 凛子", "icons": ["🌏", "🌈"], "base": 3},
    {"name": "中原 玲央", "icons": ["🌏", "⚖️"], "base": 2},
    {"name": "磯部 瞳", "icons": ["🌈", "⚖️"], "base": 1},
    {"name": "Alec Tan", "icons": ["🌈", "⚖️"], "base": 5},
    {"name": "Lucas Pereira", "icons": ["💚", "📖", "🌏"], "base": 2},
    {"name": "川瀬 美羽", "icons": ["💚", "📖", "🌈"], "base": 1},
    {"name": "Noor Rahman", "icons": ["💚", "📖", "⚖️"], "base": 3},
    {"name": "藤川 佑", "icons": ["💚", "🌏", "🌈"], "base": 1},
    {"name": "Hanna Schmidt", "icons": ["💚", "🌏", "⚖️"], "base": 2},
    {"name": "茅野 すみれ", "icons": ["📖", "🌏", "🌈"], "base": 5},
    {"name": "Sergey Ivanov", "icons": ["📖", "🌏", "⚖️"], "base": 3},
    {"name": "Mei Tanaka", "icons": ["📖", "🌈", "⚖️"], "base": 2},
]

# --- ✅ 施策データ ---
POLICIES_DB = [
    {"name": "短時間勤務", "target": ["💚"], "cost": 2, "power": 2, "type": ["recruit", "shield", "power"]},
    {"name": "ケア支援（保育/介護補助）", "target": ["💚"], "cost": 2, "power": 2, "type": ["recruit", "shield", "power"]},
    {"name": "ユニーバーサルデザインサポート", "target": ["💚"], "cost": 3, "power": 2, "type": ["shield", "power"]},
    {"name": "各種申請ガイド＆相談窓口", "target": ["💚"], "cost": 1, "power": 0, "type": ["recruit", "shield"]},
    {"name": "ウェルビーイング表彰", "target": ["💚"], "cost": 2, "power": 2, "type": ["recruit", "shield", "power"]},
    {"name": "転勤支援", "target": ["🌏"], "cost": 1, "power": 0, "type": ["recruit", "shield"]},
    {"name": "就労在留支援", "target": ["🌏"], "cost": 1, "power": 0, "type": ["recruit", "shield"]},
    {"name": "メンター制度", "target": ["💚", "📖"], "cost": 2, "power": 1, "type": ["promote", "shield"]},
    {"name": "リターンシップ(復職支援)", "target": ["💚", "📖"], "cost": 2, "power": 0, "type": ["recruit", "promote"]},
    {"name": "復帰ブリッジ（育休/介護）", "target": ["💚", "📖"], "cost": 1, "power": 1, "type": ["promote", "shield", "power"]},
    {"name": "テレワーク・ワーケーション制度", "target": ["🌏", "💚"], "cost": 1, "power": 1, "type": ["recruit", "shield", "power"]},
    {"name": "多言語対応", "target": ["🌏", "💚"], "cost": 2, "power": 2, "type": ["recruit", "power"]},
    {"name": "サテライト/在宅手当", "target": ["🌏", "💚"], "cost": 1, "power": 1, "type": ["recruit", "shield", "power"]},
    {"name": "障がい者インクルージョンコミュニティ", "target": ["💚", "🌈"], "cost": 2, "power": 0, "type": ["promote", "shield"]},
    {"name": "通勤交通費支給", "target": ["💚", "⚖️"], "cost": 1, "power": 0, "type": ["recruit"]},
    {"name": "1on1", "target": ["📖", "🌏"], "cost": 2, "power": 3, "type": ["shield", "power"]},
    {"name": "アルムナイ/ブーメラン採用", "target": ["📖", "🌏"], "cost": 1, "power": 0, "type": ["recruit", "promote", "shield"]},
    {"name": "グローバルタレントマネジメント", "target": ["📖", "🌏"], "cost": 3, "power": 3, "type": ["recruit", "promote", "shield", "power"]},
    {"name": "社内公募・FA制度", "target": ["📖", "🌈"], "cost": 2, "power": 1, "type": ["promote", "shield", "power"]},
    {"name": "指導員制度", "target": ["📖", "🌈"], "cost": 2, "power": 2, "type": ["promote", "power"]},
    {"name": "アンコンシャス・バイアス研修", "target": ["📖", "🌈"], "cost": 2, "power": 0, "type": ["recruit", "shield"]},
    {"name": "DVO(DNP価値目標制度)制度と評価制度", "target": ["📖", "⚖️"], "cost": 1, "power": 0, "type": ["recruit", "promote"]},
    {"name": "キャリア自律支援金の支給", "target": ["📖", "⚖️"], "cost": 3, "power": 3, "type": ["promote", "power"]},
    {"name": "職群別キャリア・スキルマップの可視化", "target": ["📖", "⚖️"], "cost": 1, "power": 1, "type": ["promote", "power"]},
    {"name": "社内複業制度", "target": ["📖", "⚖️"], "cost": 3, "power": 3, "type": ["recruit", "promote", "shield", "power"]},
    {"name": "同性パートナーシップ制度", "target": ["⚖️", "🌈"], "cost": 1, "power": 0, "type": ["recruit", "promote", "shield"]},
    {"name": "スポンサーシッププログラム", "target": ["🌈", "⚖️"], "cost": 1, "power": 0, "type": ["promote"]},
    {"name": "面接官トレーニング", "target": ["🌈", "⚖️"], "cost": 1, "power": 0, "type": ["recruit", "promote"]},
    {"name": "インクルージョンループ", "target": ["🌈", "⚖️"], "cost": 2, "power": 3, "type": ["promote", "shield", "power"]},
    {"name": "キャリアサポート休暇・ライフサポート休暇", "target": ["🌈", "⚖️"], "cost": 2, "power": 1, "type": ["shield", "power"]},
    {"name": "施設（社員食堂、診療所、契約保養施設等）の充実", "target": ["🌈", "⚖️"], "cost": 2, "power": 0, "type": ["recruit", "shield"]},
    {"name": "マネジメントフィードバック（360度評価）", "target": ["🌈", "⚖️"], "cost": 1, "power": 0, "type": ["promote", "shield"]},
    {"name": "ミドル・シニア向けキャリア自律支援", "target": ["📖", "💚", "⚖️"], "cost": 2, "power": 1, "type": ["recruit", "power"]},
    {"name": "オープン・ドア・ルーム（内部通報制度）", "target": ["🌈", "📖", "⚖️"], "cost": 1, "power": 0, "type": ["shield"]},
    {"name": "タレントマネジメントシステムの活用", "target": ["🌈", "📖", "⚖️"], "cost": 2, "power": 0, "type": ["recruit"]},
]

# ソート用関数（キャッシュ化して高速化）
@st.cache_data
def get_sorted_data():
    def get_sort_priority_icons(icons_list):
        if len(icons_list) > 1: return 99
        icon = icons_list[0]
        return SORT_ORDER.index(icon) if icon in SORT_ORDER else 50
    
    sorted_chars = sorted(CHARACTERS_DB, key=lambda x: get_sort_priority_icons(x['icons']))
    sorted_policies = POLICIES_DB
    return sorted_chars, sorted_policies

sorted_chars, sorted_policies = get_sorted_data()

# ==========================================
# 1. スマホ対応入力エリア (st.dataframe版)
# ==========================================
st.title("🎲 DE&I 組織シミュレーター")

# セッション状態の初期化
if "selected_char_rows" not in st.session_state:
    st.session_state.selected_char_rows = []
if "selected_policy_rows" not in st.session_state:
    st.session_state.selected_policy_rows = []

with st.expander("⚙️ メンバーと施策を選ぶ (ここをタップ)", expanded=True):
    tab1, tab2 = st.tabs(["👥 メンバー選択", "🃏 施策実行"])
    
    # --- メンバー選択 (DataFrame) ---
    with tab1:
        st.caption("👇 リストをタップして選択してください（複数選択可）")
        
        # DataFrame作成
        df_chars = pd.DataFrame(sorted_chars)
        # 表示用の列を作成
        df_chars["選択用リスト"] = df_chars.apply(lambda x: f"{''.join(x['icons'])} {x['name']}", axis=1)
        
        # 選択用DataFrameの表示
        selection_event_chars = st.dataframe(
            df_chars[["選択用リスト"]], # 表示する列
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="multi-row",
            height=300, # スクロールしやすい高さ
            key="df_chars_selection" # ★重要：keyを指定して状態を保持する
        )
        
        # 選択された行のインデックスを取得
        selected_indices = selection_event_chars.selection.rows
        selected_chars = [sorted_chars[i] for i in selected_indices]
        
        if len(selected_chars) > 0:
            st.caption(f"現在 {len(selected_chars)} 名を選択中")

    # --- 施策選択 (DataFrame) ---
    with tab2:
        st.caption("👇 実施する施策をタップしてください（複数選択可）")
        
        # DataFrame作成
        df_pols = pd.DataFrame(sorted_policies)
        # 表示用の列を作成
        df_pols["施策リスト"] = df_pols.apply(lambda x: f"{''.join(x['target'])} {x['name']}", axis=1)
        
        # 選択用DataFrameの表示
        selection_event_pols = st.dataframe(
            df_pols[["施策リスト"]],
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="multi-row",
            height=300,
            key="df_pols_selection" # ★重要：keyを指定して状態を保持する
        )
        
        # 選択された行のインデックスを取得
        selected_pol_indices = selection_event_pols.selection.rows
        selected_policies = [sorted_policies[i] for i in selected_pol_indices]

active_chars = selected_chars
active_policies = selected_policies

# ==========================================
# 2. 計算ロジック
# ==========================================
total_power = 0
active_shields = set()
active_recruits = set()
active_promotes = set()

for pol in active_policies:
    if "shield" in pol["type"]:
        for t in pol["target"]: active_shields.add(t)
    if "recruit" in pol["type"]:
        for t in pol["target"]: active_recruits.add(t)
    if "promote" in pol["type"]:
        for t in pol["target"]: active_promotes.add(t)

char_results = []
for char in active_chars:
    current_power = char["base"]
    status_tags = []
    
    for pol in active_policies:
        # 属性マッチでパワー加算
        if set(char["icons"]) & set(pol["target"]):
            current_power += pol["power"]
            
            # 効果タグの付与 (重複なし)
            if "promote" in pol["type"] and "🟢昇進" not in status_tags: 
                status_tags.append("🟢昇進")
            if "recruit" in pol["type"] and "🔵採用" not in status_tags: 
                status_tags.append("🔵採用")
            
    risks = [icon for icon in char["icons"] if icon not in active_shields]
    is_safe = len(risks) == 0 
    
    total_power += current_power
    char_results.append({
        "data": char, "power": current_power, "tags": status_tags, "risks": risks, "is_safe": is_safe
    })

president_data = {
    "data": {"name": "社長", "icons": ["👑"]},
    "power": 2, "tags": [], "risks": [], "is_safe": True
}
total_power += president_data["power"]
char_results.insert(0, president_data)

# ==========================================
# 3. メイン画面レイアウト（スマホ最適化）
# ==========================================

# --- スコアボード ---
shield_disp = "".join(sorted(list(active_shields))) if active_shields else "ー"
recruit_disp = "".join(sorted(list(active_recruits))) if active_recruits else "ー"
promote_disp = "".join(sorted(list(active_promotes))) if active_promotes else "ー"

st.markdown(f"""
<div class="score-grid">
    <div class="score-item">
        <div class="score-label">🏆 チーム仕事力</div>
        <div class="score-value" style="color:#d32f2f; font-size:24px;">{total_power}</div>
    </div>
    <div class="score-item">
        <div class="score-label">🛡️ 離職防止</div>
        <div class="score-value">{shield_disp}</div>
    </div>
    <div class="score-item">
        <div class="score-label">🔵 採用強化</div>
        <div class="score-value">{recruit_disp}</div>
    </div>
    <div class="score-item">
        <div class="score-label">🟢 昇進対象</div>
        <div class="score-value">{promote_disp}</div>
    </div>
    <div class="score-item">
        <div class="score-label">👥 メンバー</div>
        <div class="score-value">{len(char_results)}<span style="font-size:12px">名</span></div>
    </div>
</div>
""", unsafe_allow_html=True)

# サイコロ表
with st.expander("🎲 サイコロの出目を見る"):
    cols = st.columns(6)
    for i, (num, desc) in enumerate(RISK_MAP_DISPLAY.items()):
        with cols[i]:
            st.markdown(f"**{num}**<br>{desc.replace(' ', '<br>')}", unsafe_allow_html=True)

# --- メンバー表示 ---
st.subheader("📊 組織メンバー")

if char_results:
    cols = st.columns(3)
    for i, res in enumerate(char_results):
        with cols[i % 3]:
            if res["is_safe"]:
                border_color = "#00c853"
                bg_color = "#f1f8e9"
                status_icon = "🛡️SAFE"
                footer_text = "✅ 安泰"
                footer_color = "#2e7d32"
            else:
                border_color = "#ff5252"
                bg_color = "#fffbee"
                status_icon = "⚠️RISK"
                risk_icons = " ".join(res['risks'])
                footer_text = f"🎲 {risk_icons} でOUT" 
                footer_color = "#c62828"

            if res['data']['name'] == "社長":
                status_icon = "👑 社長"
                footer_text = "鉄壁"

            tags_str = "".join([f"<span style='font-size:10px; border:1px solid #ccc; border-radius:3px; padding:1px 3px; margin-right:3px; background:white;'>{t}</span>" for t in res["tags"]])
            
            html_card = (
                f'<div class="member-card" style="border-left: 5px solid {border_color}; background-color: {bg_color};">'
                f'<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:5px;">'
                f'  <div style="font-weight:bold; font-size:0.9em; color:{border_color}">{status_icon}</div>'
                f'  <div style="font-size:0.8em; font-weight:bold; color:#555">力: {res["power"]}</div>'
                f'</div>'
                f'<div style="font-weight:bold; font-size:1.1em; margin-bottom:2px;">{res["data"]["name"]}</div>'
                f'<div style="font-size:0.85em; color:#666; margin-bottom:5px;">{"".join(res["data"]["icons"])}</div>'
                f'<div style="margin-bottom:8px; min-height:16px;">{tags_str}</div>'
                f'<div style="border-top:1px dashed {border_color}; padding-top:4px; font-size:0.85em; color:{footer_color}; text-align:right; font-weight:bold;">'
                f'{footer_text}'
                f'</div>'
                f'</div>'
            )
            st.markdown(html_card, unsafe_allow_html=True)

# --- 施策表示 ---
if active_policies:
    st.divider()
    st.subheader("🛠️ 実行施策リスト")
    
    for pol in active_policies:
        # タグ生成
        ptags = []
        
        # パワーが0より大きい場合のみ表示
        if pol["power"] > 0: ptags.append(f"力+{pol['power']}")
        
        if "shield" in pol["type"]: ptags.append("離職防")
        if "recruit" in pol["type"]: ptags.append("採用")
        if "promote" in pol["type"]: ptags.append("昇進")
        
        ptags_html = " ".join([f"<span class='tag' style='background:#e8eaf6; color:#3949ab;'>{t}</span>" for t in ptags])
        
        st.markdown(
            f"""
            <div class="policy-card">
                <div>
                    <div style="font-weight:bold; color:#333; font-size:0.95em;">{pol['name']}</div>
                    <div style="font-size:0.8em; color:#777;">対象: {"".join(pol['target'])}</div>
                </div>
                <div style="text-align:right;">{ptags_html}</div>
            </div>
            """, unsafe_allow_html=True
        )
else:
    st.info("👆 上の「設定」パネルを開いて施策を選んでください")
