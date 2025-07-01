import os
import requests
from bs4 import BeautifulSoup
from notion_client import Client

# Variables d'environnement
LBC_URL = os.getenv("LBC_URL")
NOTION_SECRET = os.getenv("NOTION_SECRET")
DATABASE_ID = os.getenv("DATABASE_ID")

if not LBC_URL:
    print("❌ La variable d’environnement LBC_URL est manquante")
    exit(1)
if not NOTION_SECRET or not DATABASE_ID:
    print("❌ Variables Notion manquantes")
    exit(1)

print(f"🚀 Scraping LeBonCoin à partir de l'URL : {LBC_URL}")

notion = Client(auth=NOTION_SECRET)

def get_annonces(url):
    annonces = []
    page = 1

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/114.0.0.0 Safari/537.36"
    }

    while True:
        full_url = f"{url}&page={page}"
        print(f"🔎 Récupération page {page}: {full_url}")
        response = requests.get(full_url, headers=headers)
        if response.status_code == 403:
            print("🚫 Erreur 403: Accès refusé, le serveur bloque la requête.")
            break
        if response.status_code != 200:
            print(f"Erreur HTTP {response.status_code} à la page {page}")
            break

        soup = BeautifulSoup(response.text, 'html.parser')
        ads = soup.select("li[data-qa-id='aditem_container']")
        if not ads:
            print("🚫 Plus d'annonces trouvées, fin du scraping.")
            break

        for ad in ads:
            try:
                ad_id = ad.get("data-qa-ad-id")
                title = ad.select_one("[data-qa-id='aditem_title']").get_text(strip=True)
                price = ad.select_one("[data-qa-id='aditem_price']").get_text(strip=True).replace("\u202f", "").replace("€", "")
                location = ad.select_one("[data-qa-id='aditem_location']").get_text(strip=True)
                date = ad.select_one("[data-qa-id='aditem_date']").get_text(strip=True)
                url_detail = ad.select_one("a[data-qa-id='aditem_title']").get("href")

                annonces.append({
                    "id": ad_id,
                    "title": title,
                    "price": price,
                    "location": location,
                    "date": date,
                    "url": "https://www.leboncoin.fr" + url_detail
                })
            except Exception as e:
                print(f"⚠️ Problème lecture annonce: {e}")
        page += 1

    return annonces


def annonce_exists(ad_id):
    # Recherche dans Notion si l'annonce existe déjà via l'id stocké en propriété "Annonce ID"
    filter_params = {
        "property": "Annonce ID",
        "rich_text": {
            "equals": ad_id
        }
    }
    results = notion.databases.query(database_id=DATABASE_ID, filter=filter_params)
    return len(results.get("results", [])) > 0

def add_annonce_to_notion(ad):
    properties = {
        "Annonce ID": {
            "rich_text": [{"text": {"content": ad["id"]}}]
        },
        "Titre": {
            "title": [{"text": {"content": ad["title"]}}]
        },
        "Prix": {
            "number": int(ad["price"]) if ad["price"].isdigit() else None
        },
        "Localisation": {
            "rich_text": [{"text": {"content": ad["location"]}}]
        },
        "Date": {
            "rich_text": [{"text": {"content": ad["date"]}}]
        },
        "URL": {
            "url": ad["url"]
        }
    }
    notion.pages.create(parent={"database_id": DATABASE_ID}, properties=properties)
    print(f"✅ Annonce ajoutée: {ad['title']}")

def main():
    annonces = get_annonces(LBC_URL)
    print(f"Nombre d'annonces récupérées: {len(annonces)}")

    for ad in annonces:
        if annonce_exists(ad["id"]):
            print(f"⏭️ Annonce déjà présente : {ad['title']}")
            continue
        add_annonce_to_notion(ad)

if __name__ == "__main__":
    main()
