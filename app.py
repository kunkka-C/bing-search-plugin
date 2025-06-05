from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

@app.route("/")
def index():
    return "Bing Search Plugin is running!"

@app.route("/bing_search", methods=["POST"])
def bing_search():
    try:
        data = request.get_json()
        query = data.get("query", "")
        access_key = data.get("key", "")

        print("🔍 Received query:", query)
        print("🔐 Provided key:", access_key)

        # ✅ 校验访问 key
        expected_key = os.environ.get("ALLOWED_PLUGIN_KEY", "your-secret-key")
        if access_key != expected_key:
            return jsonify({
                "error": "Access denied: invalid key.",
                "results": []
            }), 403

        # ✅ 读取 Bing API 密钥
        subscription_key = os.environ.get("BING_SEARCH_V7_SUBSCRIPTION_KEY")
        if not subscription_key:
            raise Exception("Missing BING_SEARCH_V7_SUBSCRIPTION_KEY")

        endpoint = "https://api.bing.microsoft.com/v7.0/search"

        headers = {
            "Ocp-Apim-Subscription-Key": subscription_key,
            "User-Agent": "Coze-Agent/1.0"
        }

        # ✅ 增强地域/语言/内容偏向：中文 + 中国境内
        params = {
            "q": query,
            "mkt": "zh-CN",        # 市场：简体中文 + 中国
            "setLang": "zh-Hans",  # 语言偏好：简体中文
            "cc": "CN",            # 国家代码：China
            "count": 5             # 返回 5 条
        }

        response = requests.get(endpoint, headers=headers, params=params)
        print("📥 Bing API status:", response.status_code)

        if response.status_code == 429:
            return jsonify({
                "error": "请求过于频繁，请稍后再试（Bing API 限流）",
                "results": []
            }), 429

        response.raise_for_status()
        data = response.json()

        items = data.get("webPages", {}).get("value", [])
        results = [
            {
                "title": item.get("name"),
                "url": item.get("url"),
                "snippet": item.get("snippet")
            } for item in items
        ]

        return jsonify({"results": results})

    except Exception as e:
        print("❌ Internal error:", str(e))
        return jsonify({
            "error": str(e),
            "results": []
        }), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
