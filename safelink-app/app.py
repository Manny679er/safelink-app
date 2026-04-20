from flask import Flask, request, render_template
import requests
import time

app = Flask(__name__)

def analyze_website(url):
    score = 0
    result = {}

    if not url.startswith("http"):
        url = "http://" + url

    start = time.time()

    try:
        response = requests.get(url, timeout=5)
        load_time = time.time() - start

        # STATUS CHECK
        result["status"] = f"Website reachable ✅ ({response.status_code})"

        # SPEED SCORE
        if load_time < 1:
            score += 30
            result["speed"] = "⚡ Fast response"
        else:
            score += 10
            result["speed"] = "🐢 Slow response"

        # SERVER INFO (advanced signal)
        server = response.headers.get("Server", "Unknown")
        result["server"] = f"Server: {server}"

        if "cloudflare" in server.lower():
            score += 20
        elif server != "Unknown":
            score += 10

    except:
        result["status"] = "Website NOT reachable ❌"
        result["speed"] = "No response"
        result["server"] = "Unknown"
        score -= 30

    # SSL CHECK
    if url.startswith("https://"):
        score += 40
        result["ssl"] = "🔐 HTTPS enabled"
    else:
        score += 10
        result["ssl"] = "⚠️ HTTP only"

    # FINAL SCORE
    score = max(0, min(score, 100))
    result["score"] = score

    # RISK LABEL
    if score >= 80:
        result["label"] = "🟢 SAFE"
    elif score >= 50:
        result["label"] = "🟡 MEDIUM RISK"
    else:
        result["label"] = "🔴 HIGH RISK"

    return result


@app.route("/", methods=["GET", "POST"])
def home():
    result = None

    if request.method == "POST":
        url = request.form.get("url")
        result = analyze_website(url)

    return render_template("index.html", result=result)


if __name__ == "__main__":
    import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
