import requests
from bs4 import BeautifulSoup
import csv
import json
import time
from pathlib import Path

# =========================
# CONFIG
# =========================
BASE_URL = "https://www.scrapethissite.com/pages/forms/"
TIMEOUT = 10
DELAY = 1
SEARCH_TERM = None  # set to "Boston" later if needed

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)


# =========================
# SCRAPER
# =========================
def scrape_hockey_teams(search_query=None):
    session = requests.Session()
    session.headers.update(HEADERS)

    results = []
    page = 1

    while True:
        params = {"page_num": page}
        if search_query:
            params["team"] = search_query

        response = session.get(BASE_URL, params=params, timeout=TIMEOUT)
        response.raise_for_status()

        print(f"Fetching page {page}")

        soup = BeautifulSoup(response.text, "html.parser")

        table = soup.find("table", class_="table")
        if not table:
            print("No table found — stopping")
            break

        # ✅ FIX: do NOT use tbody
        rows = table.find_all("tr")[1:]  # skip header row

        if not rows:
            print("No rows found — stopping")
            break

        for row in rows:
            cols = [td.get_text(strip=True) for td in row.find_all("td")]

            if len(cols) < 9:
                continue

            results.append({
                "Team Name": cols[0],
                "Year": cols[1],
                "Wins": cols[2],
                "Losses": cols[3],
                "OT Losses": cols[4],
                "Win %": cols[5],
                "Goals For (GF)": cols[6],
                "Goals Against (GA)": cols[7],
                "+ / -": cols[8],
            })

        print(f"Scraped {len(rows)} rows")
        page += 1
        time.sleep(DELAY)

    return results


# =========================
# SAVE
# =========================
def save_csv(data, path):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)


def save_json(data, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


# =========================
# MAIN
# =========================
def main():
    data = scrape_hockey_teams(SEARCH_TERM)

    if not data:
        print("❌ No data scraped")
        return

    save_csv(data, OUTPUT_DIR / "hockey_teams.csv")
    save_json(data, OUTPUT_DIR / "hockey_teams.json")

    print(f"\n✅ DONE — {len(data)} records saved")


if __name__ == "__main__":
    main()

