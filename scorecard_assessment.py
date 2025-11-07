from playwright.sync_api import sync_playwright
import time

def fetch_and_save_scorecard():
    with sync_playwright() as playwright:

        browser_instance = playwright.chromium.launch(
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--window-size=1200,800"
            ]
        )
        browser_context = browser_instance.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/119.0.6045.105 Safari/537.36"
            ),
            viewport={"width": 1200, "height": 800}
        )
        page = browser_context.new_page()

        # Navigate to goodle
        page.goto("https://www.google.com/")
        time.sleep(3)

        # Handle Cookies
        try:
            page.locator("button:has-text('Accept all')").click(timeout=2500)
        except Exception:
            pass

        # Search Query
        request = "SA vs India womens final scorecard"
        page.locator('textarea[name="q"]').click()
        for char in request:
            page.keyboard.insert_text(char)
            time.sleep(0.04)
        page.keyboard.press("Enter")
        time.sleep(4)

        # Look for result page
        possible_phrases = [
            "South Africa Women vs India Women, Final",
            "India Women vs South Africa Women, Final",
            "Scorecard",
            "Live Score",
            "Cricbuzz",
            "ESPNcricinfo"
        ]
        clicked = False
        for phrase in possible_phrases:
            try:
                page.locator(f"text={phrase}").first.click(timeout=4000)
                clicked = True
                break
            except Exception:
                continue

        if not clicked:
            # Click the top relevant link
            try:
                page.locator("a:has-text('Cricket')").first.click(timeout=4000)
                clicked = True
            except Exception:
                print("Couldn't find expected match link. Exiting.")
                browser_instance.close()
                return

        time.sleep(5)

        # Take screen shot
        outfile = "scorecard.png"
        page.screenshot(path=outfile, full_page=True)
        print(f"✅ Score card Captured {outfile}")

        browser_instance.close()

fetch_and_save_scorecard()