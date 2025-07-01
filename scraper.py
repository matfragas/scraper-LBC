import os
import sys
import traceback
import requests
from bs4 import BeautifulSoup
from notion_client import Client

def fetch_annonces(url):
    print("📥 Étape 1 - Téléchargement de la page :")
    print(f"🔗 URL cible : {url}")
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
        print("✅ Page téléchargée avec succès")
        return response.text
    except Exception as e:
        print("❌ Erreur pendant le téléchargement de la page :", e)
        traceback.print_exc()
        sys.exit(1)

def parse_annonces(html):
    print("🔎 Étape 2 - Parsing du HTML")
    try:
        soup = BeautifulSoup(html, "html.parser")
        annonces = []

        cards = soup.find_all("a", class_="clearfix trackable")
        print(f"📦 {len(cards)} annonces trouvées")

        for card in cards:
            title = card.find("span", class_="title").text.strip() if card.find("span", class_="title") else "Sans titre"
            price = card.find("h3", class_="item_price").text.strip() if card.find("h3", class_="item_price") else "Sans prix"
            location = card.find("span", class_="item_supp").text.strip() if card.find("span", class_="item_supp") else "Sans localisation"
            url = f"https://www.leboncoin.fr{card['href']}" if card.get('href') else "URL manquante"

            annonces.append({
                "title": title,
                "price": price,
                "location": location,
                "url": url
            })
        print("✅ Parsing terminé")
        return annonces
    except Exception as e:
        print("❌ Erreur pendant le parsing :", e)
        traceback.print_exc()
        sys.exit(1)

def send_to_notion(annonces):
    print("🧠 Étape 3 - Envoi des données à Notion")
    NOTION_SECRET = os.getenv("NOTION_SECRET")
    DATABASE_ID = os.getenv("DATABASE_ID")

    if not NOTION_SECRET or not DATABASE_ID:
        print("❌ Les variables d'environnement NOTION_SECRET ou DATABASE_ID sont manquantes")
        sys.exit(1)

    try:
        notion = Client(auth=NOTION_SECRET)
        print(f"🔐 Connexion à Notion OK — Base : {DATABASE_ID}")
        
        for annonce in annonces:
            print(f"📤 Envoi de l'annonce : {annonce['title']}")

            response = notion.pages.create(
                parent={"database_id": DATABASE_ID},
                properties={
                    "Titre": {"title": [{"text": {"content": annonce["title"]}}]},
                    "Prix": {"rich_text": [{"text": {"content": annonce["price"]}}]},
                    "Ville": {"rich_text": [{"text": {"content": annonce["location"]}}]},
                    "URL": {"url": annonce["url"]},
                }
            )
        print("✅ Toutes les annonces ont été envoyées à Notion")

    except Exception as e:
        print("❌ Erreur pendant l'envoi à Notion :", e)
        traceback.print_exc()
        sys.exit(1)

def main():
    try:
        print("🚀 Lancement du scraper LeBonCoin")
        url = os.getenv("LBC_URL")
        print("URL récupérée depuis LBC_URL :", url)
        if not url:
            print("❌ La variable d’environnement LBC_URL est manquante")
            print("❌ LBC_URL est vide ou non défini")
            print("Environnement complet :", dict(os.environ))
            sys.exit(1)

        print("✅ URL récupérée depuis LBC_URL :", url)
        html = fetch_annonces(url)
        annonces = parse_annonces(html)
        send_to_notion(annonces)
        print("🎉 Script terminé avec succès")

    except Exception as e:
        print("❌ Erreur générale du script :", e)
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
