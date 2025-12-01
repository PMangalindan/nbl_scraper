import os
from flask import Flask, request, render_template_string
from playwright.sync_api import sync_playwright

app = Flask(__name__)

# ---------------- UI TEMPLATE ----------------
TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>NBL Play By Play Extractor</title>
    <style>
        body { font-family: Arial; max-width: 900px; margin: 40px auto; }
        textarea { width: 100%; height: 450px; white-space: pre-wrap; }
        input { width: 90%; padding: 8px; }
        button { padding: 10px 20px; }
        #waitmsg { font-weight: bold; color: blue; margin-top: 10px; }
    </style>
</head>
<body>

<h2>NBL Play By Play Extractor</h2>

<form method="POST" onsubmit="showWaitMessage()">
    <label>Enter NBL Game URL:</label><br>
    <input type="text" name="url" value="{{ default_url }}"><br><br>
    <button type="submit">Extract Play By Play</button>
</form>

<div id="waitmsg"></div>

{% if output %}
    <h3>Output</h3>
    <textarea readonly>{{ output }}</textarea>
{% endif %}

<script>
function showWaitMessage() {
    document.getElementById("waitmsg").innerText = "⏳ Please wait… scraping in progress...";
}
</script>

</body>
</html>
"""

# ---------------- SCRAPER FUNCTION ----------------
def extract_pbp(url):
    logs = []

    try:
        logs.append("Launching browser…")
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)

            logs.append("Opening new page…")
            page = browser.new_page()

            logs.append(f"Visiting URL: {url}")
            page.goto(url, wait_until="domcontentloaded", timeout=60000)

            logs.append("Clicking 'Play By Play' tab…")
            page.click('button:has-text("Play By Play")')

            logs.append("Waiting for Play By Play events to load…")
            page.wait_for_selector(".sw-fixture-pbp-event", timeout=20000)

            logs.append("Extracting text…")
            pbp_text = page.eval_on_selector(
                ".sw-fixture-pbp-periods-list",
                "el => el.innerText"
            )

            logs.append("Closing browser…")
            browser.close()

        logs.append("Saving pbp_text.txt…")

        with open("pbp_text.txt", "w", encoding="utf-8") as f:
            f.write(pbp_text)

        logs.append("✔ Done!")
        return pbp_text, logs

    except Exception as e:
        logs.append(f"❌ ERROR: {str(e)}")
        return None, logs


# ---------------- ROUTE ----------------
@app.route("/", methods=["GET", "POST"])
def index():
    output = ""
    default_url = "https://www.nbl.com.au/matches/tasmania-jackjumpers-v-south-east-melbourne-phoenix-06-11-2025"

    if request.method == "POST":
        url = request.form.get("url", "").strip()

        if not url:
            output = "❌ Please enter a URL."
        else:
            pbp_text, logs = extract_pbp(url)

            if pbp_text:
                output = "\n".join(logs) + "\n\n---\n" + pbp_text
            else:
                output = "\n".join(logs)

    return render_template_string(TEMPLATE, output=output, default_url=default_url)


# ---------------- MAIN ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
