from flask import Flask, request, render_template
import requests
import time

app = Flask(__name__)

def analyze_website(url):
    score = 0
    result = {}

    if not url.startswith("http"):
        url = "http://" + url

    # 🚨 Suspicious keyword detection (NEW)
    suspicious_words = ["login", "verify", "secure", "update", "password", "account"]

    if any(word in url.lower() for word in suspicious_words):
        score -= 20
        result["threat"] = "⚠️ Suspicious URL pattern detected"
    else:
        result["threat"] = "No obvious threats detected"

    start = time.time()

    try:
        response = requests.get(url, timeout=5)
        load_time = time.time() - start

        result["status"] = f"Reachable ✅ ({response.status_code})"

        # Speed scoring
        if load_time < 1:
            score += 30
            result["speed"] = "⚡ Fast response"
        else:
            score += 10
            result["speed"] = "🐢 Slow response"

        # Server detection
        server = response.headers.get("Server", "Unknown")
        result["server"] = server

        if "cloudflare" in server.lower():
            score += 20
        elif server != "Unknown":
            score += 10

    except:
        result["status"] = "❌ Not reachable"
        result["speed"] = "No response"
        result["server"] = "Unknown"
        score -= 30

    # SSL check
    if url.startswith("https://"):
        score += 40
        result["ssl"] = "🔐 Secure HTTPS"
    else:
        score += 10
        result["ssl"] = "⚠️ HTTP only"

    # Final score
    score = max(0, min(score, 100))
    result["score"] = score

    # Risk label
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
    app.run(debug=True)
