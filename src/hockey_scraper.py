import requests
from bs4 import BeautifulSoup
import csv
import json
import time
from pathlib import Path

BASE_URL = "https://www.scrapethissite.com/pages/forms/"
OUTPUT_DIR = Path("C:\Users\Seelan\HockeyTeamRepo\outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

TIMEOUT = 10
DELAY = 1  # polite scraping
SESSION_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; HockeyScraper/1.0)"
}


def scrape_hockey_teams(search_query=None):
    session = requests.Session()
    session.headers.update(SESSION_HEADERS)

    all_results = []
    page = 1

    while True:
        params = {"page_num": page}
        if search_query:
            params["team"] = search_query

        try:
            response = session.get(BASE_URL, params=params, timeout=TIMEOUT)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Request failed on page {page}: {e}")
            break

        soup = BeautifulSoup(response.text, "html.parser")
        rows = soup.select("table.table tbody tr")

        if not rows:
            break  # No more pages

        for row in rows:
            cols = [c.get_text(strip=True) for c in row.find_all("td")]

            team_data = {
                "Team Name": cols[0],
                "Year": cols[1],
                "Wins": cols[2],
                "Losses": cols[3],
                "OT Losses": cols[4],
                "Win %": cols[5],
                "Goals For (GF)": cols[6],
                "Goals Against (GA)": cols[7],
                "+ / -": cols[8],
            }

            all_results.append(team_data)

        print(f"Scraped page {page} ({len(rows)} rows)")
        page += 1
        time.sleep(DELAY)

    return all_results


def save_csv(data, filename):
    if not data:
        return

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)


def save_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def main():
    # 🔍 Search query (can be None or e.g. "Boston")
    SEARCH_TERM = "Boston"  # change or set to None

    results = scrape_hockey_teams(search_query=SEARCH_TERM)

    save_csv(results, OUTPUT_DIR / "hockey_teams.csv")
    save_json(results, OUTPUT_DIR / "hockey_teams.json")

    print(f"\nCompleted: {len(results)} records saved.")


if __name__ == "__main__":
    main()
