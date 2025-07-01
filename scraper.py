import os
import time
import requests
from bs4 import BeautifulSoup
from notion_client import Client

NOTION_SECRET = os.getenv("NOTION_SECRET")
DATABASE_ID = os.getenv("DATABASE_ID")
LBC_URL = os.getenv("LBC_URL")

if not LBC_URL:
    print("❌ La variable d’environnement LBC_URL est manquante")
    exit(1)

notion = Client(auth=NOTION_SECRET)

HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) "
                   "Chrome/114.0.0.0 Safari/537.36"),
    "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Referer": "https://www.leboncoin.fr/",
    "Connection": "keep-alive",
}

def fetch_page(url):
    print(f"🔎 Récupération URL : {url}")
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print(f"Erreur HTTP {response.status_code} sur {url}")
        return None
    return BeautifulSoup(response.text, "html.parser")

def parse_annonce(ad):
    try:
        ad_id = ad.get("data-qa-ad-id")
        title = ad.select_one("[data-qa-id='aditem_title']").get_text(strip=True)
        price_raw = ad.select_one("[data-qa-id='aditem_price']").get_text(strip=True)
        price = price_raw.replace("\u202f", "").replace("€", "").strip()
        location = ad.select_one("[data-qa-id='aditem_location']").get_text(strip=True)
        date = ad.select_one("[data-qa-id='aditem_date']").get_text(strip=True)
        url_detail = ad.select_one("a[data-qa-id='aditem_title']").get("href")
        full_url = "https://www.leboncoin.fr" + url_detail

        # Pour récupérer plus de données, on va aller sur la page détail
        detail_soup = fetch_page(full_url)
        if not detail_soup:
            return None

        description = detail_soup.select_one("[data-qa-id='adview_description_container']")
        description_text = description.get_text(strip=True) if description else ""

        # Extraits supplémentaires (ex: surface, pièces, type)
        infos = {}
        details_rows = detail_soup.select("[data-qa-id='adview_description_properties'] li")
        for li in details_rows:
            label = li.select_one("span[data-qa-id='adview_description_property_label']")
            value = li.select_one("span[data-qa-id='adview_description_property_value']")
            if label and value:
                infos[label.get_text(strip=True)] = value.get_text(strip=True)

        surface = infos.get("Surface") or infos.get("surface")
        pieces = infos.get("Pièces") or infos.get("pièces") or infos.get("Nombre de pièces")

        # Photos
        photos = []
        photo_elements = detail_soup.select("[data-qa-id='adview_image_container'] img")
        for img in photo_elements:
            src = img.get("src")
            if src:
                photos.append(src)

        return {
            "id": ad_id,
            "title": title,
            "price": price,
            "location": location,
            "date": date,
            "url": full_url,
            "description": description_text,
            "surface": surface,
            "pieces": pieces,
            "photos": photos,
        }
    except Exception as e:
        print(f"⚠️ Erreur parsing annonce: {e}")
        return None

def get_annonces(url):
    annonces = []
    page = 1
    while True:
        page_url = f"{url}&page={page}"
        soup = fetch_page(page_url)
        if not soup:
            break

        ads = soup.select("li[data-qa-id='aditem_container']")
        if not ads:
            print("🚫 Plus d'annonces trouvées, arrêt.")
            break

        for ad in ads:
            annonce = parse_annonce(ad)
            if annonce:
                annonces.append(annonce)

        print(f"⏳ Pause 2s pour limiter le blocage...")
        time.sleep(2)
        page += 1

    return annonces

def notion_page_exists(ad_id):
    # Recherche si une annonce avec cet ID est déjà dans Notion
    query = {
        "filter": {
            "property": "AnnonceID",
            "rich_text": {
                "equals": ad_id
            }
        }
    }
    results = notion.databases.query(database_id=DATABASE_ID, **query)
    return len(results.get("results", [])) > 0

def insert_in_notion(annonce):
    if notion_page_exists(annonce["id"]):
        print(f"🛑 Annonce {annonce['id']} déjà présente, saut.")
        return
    properties = {
        "AnnonceID": {
            "rich_text": [{"text": {"content": annonce["id"]}}]
        },
        "Titre": {
            "title": [{"text": {"content": annonce["title"]}}]
        },
        "Prix": {
            "number": int(annonce["price"]) if annonce["price"].isdigit() else None
        },
        "Lieu": {
            "rich_text": [{"text": {"content": annonce["location"]}}]
        },
        "Date": {
            "rich_text": [{"text": {"content": annonce["date"]}}]
        },
        "Description": {
            "rich_text": [{"text": {"content": annonce["description"]}}]
        },
        "Surface": {
            "rich_text": [{"text": {"content": annonce.get("surface") or ""}}]
        },
        "Pièces": {
            "rich_text": [{"text": {"content": annonce.get("pieces") or ""}}]
        },
        "URL": {
            "url": annonce["url"]
        }
    }
    notion.pages.create(parent={"database_id": DATABASE_ID}, properties=properties)
    print(f"✅ Annonce {annonce['id']} ajoutée dans Notion.")

def main():
    print("🚀 Lancement du scraper LeBonCoin")
    annonces = get_annonces(LBC_URL)
    print(f"🔄 {len(annonces)} annonces récupérées.")
    for annonce in annonces:
        insert_in_notion(annonce)

if __name__ == "__main__":
    main()
