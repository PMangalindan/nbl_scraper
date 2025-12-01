import os
from flask import Flask, request, render_template_string
from playwright.sync_api import sync_playwright

app = Flask(__name__)

TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>NBL Play By Play Extractor</title>
    <style>
        body { font-family: Arial; max-width: 900px; margin: 40px auto; }
        textarea { width: 100%; height: 400px; white-space: pre-wrap; }
        input { width: 90%; padding: 8px; }
        button { padding: 10px 20px; }
    </style>
</head>
<body>

<h2>NBL Play By Play Extractor</h2>

<form method="POST">
    <label>Enter NBL Game URL:</label><br>
    <input type="text" name="url" value="{{ default_url }}"><br><br>
    <button type="submit">Extract Play By Play</button>
</form>

{% if output %}
    <h3>Output</h3>
    <textarea readonly>{{ output }}</textarea>
{% endif %}

</body>
</html>
"""


def extract_pbp(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=60000)

        # Click Play By Play tab
        page.click('button:has-text("Play By Play")')

        # Wait for events to load
        page.wait_for_selector(".sw-fixture-pbp-event", timeout=20000)

        pbp_text = page.eval_on_selector(
            ".sw-fixture-pbp-periods-list",
            "el => el.innerText"
        )

        browser.close()

    # Save output
    with open("pbp_text.txt", "w", encoding="utf-8") as f:
        f.write(pbp_text)

    return pbp_text


@app.route("/", methods=["GET", "POST"])
def index():
    output = ""
    default_url = "https://www.nbl.com.au/matches/tasmania-jackjumpers-v-south-east-melbourne-phoenix-06-11-2025"

    if request.method == "POST":
        url = request.form.get("url", "").strip()
        if not url:
            output = "❌ Please enter a URL"
        else:
            try:
                output = extract_pbp(url)
                output = "✔️ Saved to pbp_text.txt\n\n" + output
            except Exception as e:
                output = f"❌ Error: {str(e)}"

    return render_template_string(TEMPLATE, output=output, default_url=default_url)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
