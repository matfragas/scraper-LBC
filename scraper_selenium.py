import os
import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
import time
from bs4 import BeautifulSoup
import requests

# Notion API setup
NOTION_SECRET = os.getenv("NOTION_SECRET")
DATABASE_ID = os.getenv("DATABASE_ID")

LBC_URL = os.getenv("LBC_URL")
if not LBC_URL:
    print("❌ La variable d’environnement LBC_URL est manquante")
    exit(1)

print(f"🚀 Lancement du scraper LeBonCoin avec Selenium")
print(f"🔎 URL : {LBC_URL}")

# Setup Selenium Chrome headless
options = uc.ChromeOptions()
options.headless = True  # important pour GitHub Actions
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Pas de --user-data-dir ici
driver = uc.Chrome(options=options)

try:
    driver.get(LBC_URL)
    time.sleep(5)  # attendre que la page charge (ajuste si besoin)
    print("✅ Titre de la page :", driver.title)
    html = driver.page_source

    soup = BeautifulSoup(html, "html.parser")

    # Extraction des annonces
    ads = soup.select("li[data-qa-id='aditem_container']")
    print(f"🔄 {len(ads)} annonces récupérées.")

    for ad in ads:
        title = ad.select_one("[data-qa-id='aditem_title']")
        price = ad.select_one("[data-qa-id='aditem_price']")
        location = ad.select_one("[data-qa-id='aditem_location']")
        date = ad.select_one("[data-qa-id='aditem_date']")
        url = ad.select_one("a")["href"] if ad.select_one("a") else None

        print("---")
        print("Titre:", title.text.strip() if title else "N/A")
        print("Prix:", price.text.strip() if price else "N/A")
        print("Localisation:", location.text.strip() if location else "N/A")
        print("Date:", date.text.strip() if date else "N/A")
        print("URL:", f"https://www.leboncoin.fr{url}" if url else "N/A")

        # TODO: Appeler fonction pour push dans Notion + gestion doublons

finally:
    driver.quit()
