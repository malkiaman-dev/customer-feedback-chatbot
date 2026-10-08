"""Optional local visual verification. Requires Playwright and Chrome or Edge."""
from pathlib import Path
import os
from playwright.sync_api import sync_playwright

root = Path(__file__).resolve().parents[1]
screenshots = root / ".tmp" / "screenshots"
screenshots.mkdir(parents=True, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(channel="msedge", headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 1000}, reduced_motion="reduce")
    page.goto(os.getenv("FAQ_APP_URL", "http://127.0.0.1:8501"))
    page.get_by_role("heading", name="FAQ Chatbot", exact=True).wait_for()
    page.get_by_text("FAQ preview", exact=True).click()
    page.get_by_role("button", name="Required technologies", exact=False).wait_for()
    page.get_by_test_id("stStatusWidget").wait_for(state="hidden")
    page.screenshot(path=str(screenshots / "desktop.png"), full_page=True)
    page.get_by_role("button", name="Required technologies", exact=False).click()
    page.get_by_text("FAQ preview", exact=True).wait_for()
    page.get_by_text("Sources (1)", exact=True).wait_for()
    page.screenshot(path=str(screenshots / "conversation.png"), full_page=True)
    page.get_by_role("button", name="New conversation", exact=False).click()
    page.locator(".welcome").wait_for()
    for width, height, name in [(375, 812, "mobile"), (768, 1024, "tablet"), (1024, 768, "landscape")]:
        page.set_viewport_size({"width": width, "height": height})
        page.screenshot(path=str(screenshots / f"{name}.png"), full_page=True)
        print(f"{name} horizontal overflow:", page.evaluate("document.documentElement.scrollWidth > window.innerWidth"))
    print("Visual screenshots saved to", screenshots)
    print("Horizontal overflow:", page.evaluate("document.documentElement.scrollWidth > window.innerWidth"))
    browser.close()
