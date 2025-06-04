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
        print("🔍 Query received:", query)

        # ✅ 直接使用你已验证可用的 key 和 endpoint
        subscription_key = os.environ.get("BING_SEARCH_V7_SUBSCRIPTION_KEY")
        endpoint = "https://api.bing.microsoft.com/v7.0/search"

        if not subscription_key:
            raise Exception("Missing BING_SEARCH_V7_SUBSCRIPTION_KEY")

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
        print("Status Code:", response.status_code)
        print("Raw Response:", response.text)

        response.raise_for_status()
        json_data = response.json()
        items = json_data.get("webPages", {}).get("value", [])

        results = [
            {
                "title": item["name"],
                "url": item["url"],
                "snippet": item["snippet"]
            } for item in items
        ]

        return jsonify({"results": results})

    except Exception as e:
        print("❌ ERROR:", str(e))
        return jsonify({"error": str(e), "results": []}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
