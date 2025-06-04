from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route("/")
def home():
    return "Bing Search Plugin is running!"

@app.route("/bing_search", methods=["POST"])
def bing_search():
    data = request.get_json()
    query = data.get("query", "")

    headers = {
        "Ocp-Apim-Subscription-Key": "YOUR_BING_API_KEY",
        "User-Agent": "Mozilla/5.0"
    }
    params = {"q": query, "count": 5}
    res = requests.get("https://api.bing.microsoft.com/v7.0/search", headers=headers, params=params)
    items = res.json().get("webPages", {}).get("value", [])

    results = [{"title": i["name"], "url": i["url"], "snippet": i["snippet"]} for i in items]
    return jsonify({"results": results})

# ✅ 关键监听代码
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
