from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

@app.route("/")
def home():
    return "Bing Search Plugin is running!"

@app.route("/bing_search", methods=["POST"])
def bing_search():
    data = request.get_json()
    query = data.get("query", "")

    subscription_key = os.environ.get("BING_SEARCH_V7_SUBSCRIPTION_KEY")
    endpoint = os.environ.get("BING_SEARCH_V7_ENDPOINT") + "/bing/v7.0/search"

    if not subscription_key or not endpoint:
        return jsonify({"error": "Bing API key or endpoint not configured."}), 500

    headers = {
        "Ocp-Apim-Subscription-Key": subscription_key,
        "User-Agent": "Coze-Agent/1.0"
    }
    params = {
        "q": query,
        "mkt": "zh-CN",
        "count": 5
    }

    try:
        res = requests.get(endpoint, headers=headers, params=params)
        res.raise_for_status()
        raw = res.json()

        items = raw.get("webPages", {}).get("value", [])
        results = [
            {
                "title": item["name"],
                "url": item["url"],
                "snippet": item["snippet"]
            } for item in items
        ]

        return jsonify({"results": results})
    except Exception as e:
        return jsonify({"error": str(e), "results": []}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
