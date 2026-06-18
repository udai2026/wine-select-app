"""Gemini API 呼び出し・プロンプト組み立て・JSON パースを担当するモジュール"""
import json
import os
import re
import time

from dotenv import load_dotenv
from google import genai
from google.genai import errors

# .env から API キーを読み込む
load_dotenv()

# 使用モデル（変更しやすいよう定数化）
MODEL_NAME = "gemini-2.5-flash"

# システム指示（ソムリエとしての振る舞いと出力形式を固定）
SYSTEM_INSTRUCTION = """あなたは経験豊富なソムリエです。
日本で一般的に入手できるワインを前提に推薦してください。

ルール:
- 銘柄名は実在しそうなものを挙げ、availability には正直にコメントする（必ず買えると断言しない）。
- ユーザーの予算・シーン・タイプ・好み・料理を必ず踏まえる。
- 出力は次の JSON のみ。前置き・後書き・コードフェンスは一切付けない。

{
  "main": {
    "name": "銘柄名",
    "type": "赤/白/ロゼ/スパークリング",
    "grape": "主なブドウ品種",
    "price_range": "価格目安（例: 2,000〜3,000円）",
    "reason": "このシーン・予算・好みに合う理由（2〜3文）",
    "availability": "入手しやすさのコメント（例: スーパーでよく見かける / ネット通販向き）",
    "pairing": "合う料理"
  },
  "alternatives": [
    { "name": "", "type": "", "short_reason": "一言理由" },
    { "name": "", "type": "", "short_reason": "一言理由" }
  ]
}"""


def build_prompt(budget: int, scenes: list[str], wine_type: str, body: int | None, dish: str) -> str:
    """フォーム入力値から Gemini に送る日本語プロンプトを組み立てる"""
    lines = [
        "以下の条件に合うワインを1本（＋代替2本）推薦してください。",
        f"- 予算: {budget:,}円程度",
        f"- シーン: {'、'.join(scenes) if scenes else '特に指定なし'}",
        f"- ワインタイプ: {wine_type}",
    ]
    if body is not None:
        # スライダー値（1〜5）を言葉に変換
        body_labels = {1: "とても軽め", 2: "やや軽め", 3: "中間", 4: "やや重め", 5: "とても重め"}
        lines.append(f"- 味わいの好み: {body_labels[body]}")
    if dish.strip():
        lines.append(f"- 合わせる料理: {dish.strip()}")
    return "\n".join(lines)


def _parse_json(text: str) -> dict | None:
    """応答テキストから JSON を取り出してパースする。失敗したら None を返す"""
    # コードフェンスが付いていた場合は除去
    cleaned = re.sub(r"```(?:json)?", "", text).strip()
    # 最初の { から最後の } までを抜き出す
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start == -1 or end == -1:
        return None
    try:
        return json.loads(cleaned[start : end + 1])
    except json.JSONDecodeError:
        return None


def recommend_wine(budget: int, scenes: list[str], wine_type: str, body: int | None, dish: str) -> dict:
    """Gemini にワイン推薦を依頼する。

    戻り値:
        {"ok": True, "data": パース済み dict}              … 成功
        {"ok": False, "raw": 生テキスト, "error": 説明}    … JSON パース失敗（生テキストを表示用に返す）
    例外:
        API キー未設定・通信エラーなどは呼び出し側で捕捉する
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY が設定されていません。.env を確認してください。")

    client = genai.Client(api_key=api_key)

    # 混雑（503）・レート制限（429）のときは少し待って自動リトライ（最大3回）
    response = None
    for wait_sec in (0, 3, 6):
        if wait_sec:
            time.sleep(wait_sec)
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=build_prompt(budget, scenes, wine_type, body, dish),
                config={"system_instruction": SYSTEM_INSTRUCTION},
            )
            break
        except errors.APIError as e:
            if e.code in (429, 503):
                continue
            raise
    if response is None:
        raise RuntimeError(
            "Gemini のサーバーが混雑しています（3回試しました）。"
            "1〜2分待ってから「もう一度提案」を押してみてください。"
        )

    text = response.text or ""

    data = _parse_json(text)
    if data is None:
        return {"ok": False, "raw": text, "error": "応答を JSON として解釈できませんでした。"}
    return {"ok": True, "data": data}
