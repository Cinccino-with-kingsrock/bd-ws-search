from playwright.sync_api import sync_playwright
import json
import os
import time
import urllib.request

OUTPUT_FILE = "data/cards_bottleneko.json"
API_URL = "https://bottleneko.app/api/card/78"
SERIES_URL = "https://bottleneko.app/series/78"


def map_card(card):
    # Map fields to requested format
    # schema: id, name, text, cost, level, trigger, power, soul, traits, type, color
    return {
        "id": card.get("id"),
        "name": card.get("title"),  # user asked for 'name', API has 'title'
        "text": card.get("effect"),  # user asked for 'text', API has 'effect'
        "level": card.get("level"),
        "cost": card.get("cost"),
        "power": card.get("attack"),  # user implied standard fields
        "soul": card.get("soul"),
        "trigger": card.get("trigger"),
        "traits": card.get("feature"),
        "type": card.get("type"),
        "color": card.get("color"),
        "rarity": card.get("rare"),
        "side": card.get("side"),
        "product": card.get("productName"),
    }


def fetch_api_direct():
    print(f"Fetching API directly: {API_URL}")
    req = urllib.request.Request(
        API_URL,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    print(f"Successfully captured {len(data)} items.")
    return data


def fetch_api_via_playwright():
    print("Launching Playwright...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        api_url_fragment = "api/card/78"
        print(f"Navigating to BottleNeko and waiting for API '{api_url_fragment}'...")

        api_data = None

        def handle_response(response):
            nonlocal api_data
            if api_url_fragment in response.url and "filter" not in response.url:
                print(f"Intercepted API response: {response.url}")
                try:
                    api_data = response.json()
                    print(f"Successfully captured {len(api_data)} items.")
                except Exception as e:
                    print(f"Failed to parse JSON: {e}")

        page.on("response", handle_response)
        page.goto(SERIES_URL)

        start_time = time.time()
        while api_data is None:
            if time.time() - start_time > 30:
                print("Timeout waiting for API response.")
                break
            page.wait_for_timeout(500)

        browser.close()
        return api_data


def save_cards(api_data):
    print("Processing data...")
    processed_cards = [map_card(card) for card in api_data]

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(processed_cards, f, indent=4, ensure_ascii=False)

    print(f"Saved {len(processed_cards)} cards to {OUTPUT_FILE}")


def run_scraper():
    api_data = None
    try:
        api_data = fetch_api_direct()
    except Exception as e:
        print(f"Direct API fetch failed: {e}")
        print("Falling back to Playwright intercept...")
        api_data = fetch_api_via_playwright()

    if api_data:
        save_cards(api_data)
    else:
        print("Failed to capture card data.")


if __name__ == "__main__":
    run_scraper()
