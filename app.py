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

        # ✅ 验证调用方传入的 key 是否和环境变量匹配
        expected_key = os.environ.get("ALLOWED_PLUGIN_KEY", "your-secret-key")
        if access_key != expected_key:
            print("❌ Invalid key access attempt.")
            return jsonify({
                "error": "Access denied: invalid key.",
                "results": []
            }), 403

        # ✅ 读取 Bing API 的 key 和 endpoint
        subscription_key = os.environ.get("BING_SEARCH_V7_SUBSCRIPTION_KEY")
        if not subscription_key:
            raise Exception("Missing BING_SEARCH_V7_SUBSCRIPTION_KEY")

        endpoint = "https://api.bing.microsoft.com/v7.0/search"

        headers = {
            "Ocp-Apim-Subscription-Key": subscription_key,
            "User-Agent": "Coze-Agent/1.0"
        }

        params = {
            "q": query,
            "mkt": "zh-CN",
            "count": 5
        }

        response = requests.get(endpoint, headers=headers, params=params)
        print("📥 Bing API status:", response.status_code)

        # 如果被限流，明确提示
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
