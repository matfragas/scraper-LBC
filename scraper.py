import os
import time
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
from notion_client import Client
import json

NOTION_API_KEY = os.getenv("NOTION_SECRET")
NOTION_DATABASE_ID = os.getenv("DATABASE_ID")
LEBONCOIN_URL = os.getenv("LBC_URL")


def extract_ads(html):
    soup = BeautifulSoup(html, "html.parser")
    ads = []
    for a in soup.select("a[href^='/ai']"):
        title = a.text.strip()
        link = "https://www.leboncoin.fr" + a.get("href")
        ads.append({"title": title, "url": link})
    return ads

def push_to_notion(ad):
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28",
    }
    data = {
        "parent": {"database_id": NOTION_DATABASE_ID},
        "properties": {
            "Name": {"title": [{"text": {"content": ad['title']}}]},
            "URL": {"url": ad['url']},
        }
    }
    response = requests.post("https://api.notion.com/v1/pages", headers=headers, data=json.dumps(data))
    return response.status_code == 200

def main():
    print("🚀 Lancement du scraper LeBonCoin")

    options = uc.ChromeOptions()
    options.headless = True
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")

    driver = uc.Chrome(options=options)
    driver.get(LEBONCOIN_URL)
    time.sleep(5)  # attendre le chargement complet

    html = driver.page_source
    ads = extract_ads(html)
    print(f"🔎 {len(ads)} annonces extraites")

    for ad in ads:
        success = push_to_notion(ad)
        print(f"{'✅' if success else '❌'} {ad['title']}")

    driver.quit()

if __name__ == "__main__":
    main()
