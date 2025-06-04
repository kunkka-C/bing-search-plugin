from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# 替换成你自己的 Bing Search API Key
BING_API_KEY = "80cf34778f5b4a939219901af27e523f"
BING_SEARCH_URL = "https://api.bing.microsoft.com/v7.0/search"

@app.route("/bing_search", methods=["POST"])
def bing_search():
    data = request.get_json()
    query = data.get("query", "")

    headers = {
        "Ocp-Apim-Subscription-Key": BING_API_KEY,
        "User-Agent": "Mozilla/5.0"
    }

    params = {
        "q": query,
        "count": 5,
        "textDecorations": True,
        "textFormat": "Raw"
    }

    try:
        response = requests.get(BING_SEARCH_URL, headers=headers, params=params)
        response.raise_for_status()

        items = response.json().get("webPages", {}).get("value", [])

        results = []
        for item in items:
            results.append({
                "title": item.get("name"),
                "url": item.get("url"),
                "snippet": item.get("snippet")
            })

        return jsonify({"results": results})

    except Exception as e:
        return jsonify({"error": str(e)}), 500