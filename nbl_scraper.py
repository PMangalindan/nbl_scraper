from playwright.sync_api import sync_playwright

url = "https://www.nbl.com.au/matches/tasmania-jackjumpers-v-south-east-melbourne-phoenix-06-11-2025"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)  # set True to hide the browser
    page = browser.new_page()
    page.goto(url, wait_until="domcontentloaded", timeout=60000)

    # Click the Play By Play tab
    page.click('button:has-text("Play By Play")')

    # Wait for the play-by-play events to appear
    page.wait_for_selector(".sw-fixture-pbp-event", timeout=20000)

    # Extract all visible text from the Play By Play container
    pbp_text = page.eval_on_selector(
        ".sw-fixture-pbp-periods-list",
        "el => el.innerText"
    )

    browser.close()

# Save the text to a file
with open("pbp_text.txt", "w", encoding="utf-8") as f:
    f.write(pbp_text)

print("✅ All visible Play By Play text saved to 'pbp_text.txt'")
