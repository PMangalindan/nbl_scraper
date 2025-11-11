import sys
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QTextEdit, QVBoxLayout
from PyQt6.QtCore import QThread, pyqtSignal
from playwright.sync_api import sync_playwright

class PBPThread(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, url):
        super().__init__()
        self.url = url

    def run(self):
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(self.url, wait_until="domcontentloaded", timeout=60000)

                # Click Play By Play tab
                page.click('button:has-text("Play By Play")')

                # Wait for events to load
                page.wait_for_selector(".sw-fixture-pbp-event", timeout=20000)

                # Extract visible text
                pbp_text = page.eval_on_selector(
                    ".sw-fixture-pbp-periods-list",
                    "el => el.innerText"
                )

                browser.close()

            # Save to file
            with open("pbp_text.txt", "w", encoding="utf-8") as f:
                f.write(pbp_text)

            self.finished.emit(pbp_text)

        except Exception as e:
            self.error.emit(str(e))


class PBPExtractor(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NBL Play By Play Extractor")
        self.setGeometry(100, 100, 600, 400)

        # Widgets
        self.label = QLabel("Enter NBL Game URL:")
        self.url_input = QLineEdit()
        self.url_input.setText("https://www.nbl.com.au/matches/tasmania-jackjumpers-v-south-east-melbourne-phoenix-06-11-2025")
        self.run_button = QPushButton("Extract Play By Play")
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.url_input)
        layout.addWidget(self.run_button)
        layout.addWidget(self.output_text)
        self.setLayout(layout)

        # Connect button
        self.run_button.clicked.connect(self.start_extraction)

    def start_extraction(self):
        url = self.url_input.text().strip()
        if not url:
            self.output_text.setPlainText("❌ Please enter a URL")
            return

        self.output_text.setPlainText("⏳ Running... Please wait.")

        # Run Playwright in a separate thread
        self.thread = PBPThread(url)
        self.thread.finished.connect(self.on_finished)
        self.thread.error.connect(self.on_error)
        self.thread.start()

    def on_finished(self, text):
        self.output_text.setPlainText(f"✅ Done! Play By Play text saved to 'pbp_text.txt'\n\n---\n\n{text}")

    def on_error(self, msg):
        self.output_text.setPlainText(f"❌ Error: {msg}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PBPExtractor()
    window.show()
    sys.exit(app.exec())
