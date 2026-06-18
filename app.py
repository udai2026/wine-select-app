"""ワインセレクト Web アプリ（Streamlit 本体: UI と表示）"""
import html
import urllib.parse

import streamlit as st

from gemini_client import recommend_wine


def fetch_recommendation() -> None:
    """保存済みの入力条件で Gemini に推薦を依頼し、結果を session_state に格納する"""
    inputs = st.session_state["inputs"]
    try:
        with st.spinner("ソムリエが選んでいます… 🍷"):
            st.session_state["result"] = recommend_wine(
                budget=inputs["budget"],
                scenes=inputs["scenes"],
                wine_type=inputs["wine_type"],
                body=inputs["body"],
                dish=inputs["dish"],
            )
    except Exception as e:
        # API キー未設定・通信エラーなどもアプリを落とさず画面に表示する
        st.session_state["result"] = {"ok": False, "raw": "", "error": str(e)}

# ---- ページ設定 ----
st.set_page_config(page_title="ワインセレクト", page_icon="🍷", layout="centered")

# ---- カスタム CSS（カード風デザイン・装飾） ----
st.markdown(
    """
<style>
/* 手書き風フォント（見出し用） */
@import url('https://fonts.googleapis.com/css2?family=Klee+One:wght@400;600&display=swap');
.wine-hero h1, .wine-name, .alt-name, .section-title {
    font-family: 'Klee One', 'Yu Gothic', sans-serif;
}

/* オーニング（ビストロの赤白ストライプの日よけ） */
.awning {
    height: 14px;
    border-radius: 12px 12px 0 0;
    background: repeating-linear-gradient(90deg, #B5342D 0 26px, #FAF6EC 26px 52px);
    border-bottom: 3px solid #22354F;
}

/* ヒーローヘッダー（ネイビーの看板風） */
.wine-hero {
    background: #22354F;
    border-radius: 0 0 16px 16px;
    padding: 2rem 2rem 1.8rem;
    margin-bottom: 1.5rem;
    color: #FFF;
    box-shadow: 0 8px 20px rgba(34, 53, 79, 0.25);
}
.wine-hero h1 {
    color: #FAF6EC;
    font-size: 2rem;
    margin: 0 0 0.4rem 0;
    padding: 0;
}
.wine-hero p {
    color: #D8E0EC;
    margin: 0;
    font-size: 0.95rem;
}

/* メインのおすすめカード（メニュー表風の枠） */
.wine-card {
    background: #FFFDF6;
    border: 2px solid #22354F;
    border-radius: 14px;
    padding: 1.8rem 1.8rem 1.4rem;
    box-shadow: 6px 6px 0 rgba(34, 53, 79, 0.15);
    margin-bottom: 1rem;
}
.wine-card .wine-name {
    font-size: 1.5rem;
    font-weight: 700;
    color: #22354F;
    margin-bottom: 0.5rem;
}
.wine-badges { margin-bottom: 1rem; }
.wine-badge {
    display: inline-block;
    background: #E9EEF5;
    color: #22354F;
    border-radius: 999px;
    padding: 0.2rem 0.85rem;
    font-size: 0.82rem;
    font-weight: 600;
    margin-right: 0.4rem;
}
.wine-reason {
    background: #F6F1E3;
    border-left: 4px solid #B5342D;
    border-radius: 0 10px 10px 0;
    padding: 0.9rem 1.1rem;
    margin-bottom: 1rem;
    line-height: 1.8;
}
.wine-meta {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
}
.wine-meta-item {
    flex: 1;
    min-width: 220px;
    background: #F3EEE0;
    border-radius: 10px;
    padding: 0.7rem 1rem;
    font-size: 0.9rem;
    line-height: 1.7;
}
.wine-meta-item .label {
    font-weight: 700;
    color: #B5342D;
    display: block;
    font-size: 0.8rem;
}

/* 代替ワインのカード */
.alt-card {
    background: #FFFDF6;
    border: 1.5px dashed #22354F;
    border-radius: 12px;
    padding: 1rem 1.2rem;
    height: 100%;
}
.alt-card .alt-name {
    font-weight: 700;
    color: #22354F;
    margin-bottom: 0.3rem;
}
.alt-card .alt-reason {
    font-size: 0.85rem;
    color: #5A5648;
    line-height: 1.6;
}

/* 検索リンクボタン */
.wine-links { margin-top: 1rem; }
.wine-links a {
    display: inline-block;
    background: #FFF;
    border: 1.5px solid #22354F;
    color: #22354F !important;
    border-radius: 999px;
    padding: 0.35rem 1rem;
    font-size: 0.85rem;
    font-weight: 600;
    text-decoration: none !important;
    margin: 0 0.4rem 0.4rem 0;
    transition: background 0.15s, color 0.15s;
}
.wine-links a:hover {
    background: #22354F;
    color: #FAF6EC !important;
}
.alt-card .wine-links a {
    font-size: 0.78rem;
    padding: 0.25rem 0.8rem;
}

/* 入力フォームの枠付きコンテナ（セクション区切り） */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #FFFDF6;
    border: 1.5px solid #C9BCA3;
    border-radius: 12px;
}

/* セクション見出し */
.section-title {
    font-size: 1.15rem;
    font-weight: 700;
    color: #22354F;
    margin: 1.2rem 0 0.8rem;
}

/* ボタンを丸く・大きく */
div.stButton > button, div.stFormSubmitButton > button {
    border-radius: 999px;
    font-weight: 700;
    padding: 0.6rem 1rem;
}
</style>
""",
    unsafe_allow_html=True,
)

# ---- ヒーローヘッダー ----
st.markdown(
    """
<div class="awning"></div>
<div class="wine-hero">
    <h1>🍷 ワインセレクト</h1>
    <p>シチュエーション・予算・好みから、あなたにぴったりの1本をご提案します。</p>
</div>
""",
    unsafe_allow_html=True,
)

# ---- 入力フォーム（セクションごとに枠で区切る） ----
with st.container(border=True):
    budget = st.slider("💰 予算（円）", min_value=500, max_value=10000, step=500, value=3000)

with st.container(border=True):
    # シーン：ボタン型（pills）で複数選択可
    scenes = st.pills(
        "🥂 シーン（複数選択可）",
        [
            "近所のスーパーでサッと",
            "平日の晩酌に",
            "日曜の昼にまったり",
            "誕生日・記念日",
            "ホームパーティ",
            "自分へのご褒美",
            "来客のおもてなし",
            "デート",
            "友人・知人へのギフト",
            "アウトドア・BBQ",
            "クリスマス・季節イベント",
            "お祝い・昇進祝い",
        ],
        selection_mode="multi",
    )

with st.container(border=True):
    wine_type = st.radio(
        "🍇 ワインタイプ",
        ["赤", "白", "ロゼ", "スパークリング", "おまかせ"],
        horizontal=True,
    )

with st.container(border=True):
    # 味わい：チェックを入れるとスライダーが操作できるようになる
    use_body = st.checkbox("味わいの好みを指定する")
    body = st.select_slider(
        "⚖️ 味わい（軽い ⇔ 重い）",
        options=[1, 2, 3, 4, 5],
        value=3,
        format_func=lambda v: {1: "とても軽め", 2: "やや軽め", 3: "中間", 4: "やや重め", 5: "とても重め"}[v],
        disabled=not use_body,
    )

with st.container(border=True):
    # 料理：ラジオボタン＋「その他」選択時のみ自由記述
    dish_choice = st.radio(
        "🍽️ 合わせる料理",
        ["指定なし", "肉料理", "魚介料理", "和食", "イタリアン", "中華", "チーズ・おつまみ", "スイーツ", "その他"],
        horizontal=True,
    )
    if dish_choice == "その他":
        dish = st.text_input("料理を入力してください", placeholder="例: BBQ、エスニック、鍋料理")
    elif dish_choice == "指定なし":
        dish = ""
    else:
        dish = dish_choice

submitted = st.button("🔍 これで探す", type="primary", use_container_width=True)

# ---- 検索実行（Gemini に推薦を依頼） ----
if submitted:
    st.session_state["inputs"] = {
        "budget": budget,
        "scenes": scenes,
        "wine_type": wine_type,
        "body": body if use_body else None,
        "dish": dish,
    }
    fetch_recommendation()


def esc(value: str) -> str:
    """HTML 埋め込み用にエスケープする"""
    return html.escape(str(value or "－"))


def search_links_html(wine_name: str) -> str:
    """銘柄名から楽天・Amazon・Google の検索リンク（HTML）を組み立てる"""
    if not wine_name:
        return ""
    query = urllib.parse.quote(f"{wine_name} ワイン")
    links = [
        (f"https://search.rakuten.co.jp/search/mall/{query}/", "🛒 楽天で探す"),
        (f"https://www.amazon.co.jp/s?k={query}", "📦 Amazonで探す"),
        (f"https://www.google.com/search?q={query}", "🔍 Googleで検索"),
    ]
    tags = "".join(
        f'<a href="{url}" target="_blank" rel="noopener noreferrer">{label}</a>' for url, label in links
    )
    return f'<div class="wine-links">{tags}</div>'


# ---- 結果表示 ----
if "result" in st.session_state:
    result = st.session_state["result"]

    if result.get("ok"):
        data = result["data"]
        main = data.get("main", {})
        alts = data.get("alternatives", [])
    else:
        # 失敗時：エラー内容と生テキストを表示してアプリは落とさない
        main = {}
        alts = []
        st.error(f"うまく提案を取得できませんでした：{result.get('error', '不明なエラー')}")
        if result.get("raw"):
            st.caption("AI からの応答をそのまま表示します：")
            st.markdown(result["raw"])

    if main:
        st.markdown('<div class="section-title">🎯 おすすめの1本</div>', unsafe_allow_html=True)
        st.markdown(
            f"""
<div class="wine-card">
    <div class="wine-name">{esc(main.get("name"))}</div>
    <div class="wine-badges">
        <span class="wine-badge">{esc(main.get("type"))}</span>
        <span class="wine-badge">{esc(main.get("grape"))}</span>
        <span class="wine-badge">💰 {esc(main.get("price_range"))}</span>
    </div>
    <div class="wine-reason">{esc(main.get("reason"))}</div>
    <div class="wine-meta">
        <div class="wine-meta-item"><span class="label">🛒 入手しやすさ</span>{esc(main.get("availability"))}</div>
        <div class="wine-meta-item"><span class="label">🍽️ 合う料理</span>{esc(main.get("pairing"))}</div>
    </div>
    {search_links_html(main.get("name", ""))}
</div>
""",
            unsafe_allow_html=True,
        )

    if alts:
        st.markdown('<div class="section-title">🍷 こちらもおすすめ</div>', unsafe_allow_html=True)
        cols = st.columns(len(alts))
        for col, alt in zip(cols, alts):
            with col:
                st.markdown(
                    f"""
<div class="alt-card">
    <div class="alt-name">{esc(alt.get("name"))}<span style="font-weight:400;">（{esc(alt.get("type"))}）</span></div>
    <div class="alt-reason">{esc(alt.get("short_reason"))}</div>
    {search_links_html(alt.get("name", ""))}
</div>
""",
                    unsafe_allow_html=True,
                )

    st.write("")
    # 同じ条件で再生成（AI は毎回違う提案を返しうる）
    st.caption("提案がピンとこなかったら、同じ条件のままもう一度引き直せます。")
    if st.button("🔄 同じ条件で別のワインを提案してもらう", use_container_width=True):
        fetch_recommendation()
        st.rerun()
