import os
import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
options.headless = False  # important pour GitHub Actions
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Pas de --user-data-dir ici
driver = uc.Chrome(options=options)

driver.get(LBC_URL)

print(f"✅ Titre de la page : {driver.title}")
print(driver.page_source[:1000])  # Affiche les 1000 premiers caractères du HTML

# Attente explicite jusqu'à ce qu'au moins une annonce apparaisse
try:
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "a[data-qa-id='aditem_container']"))
    )
except:
    print("❌ Les annonces ne se sont pas chargées.")
    driver.quit()
    exit()

# Récupération des annonces
annonces = driver.find_elements(By.CSS_SELECTOR, "a[data-qa-id='aditem_container']")
print(f"🔄 {len(annonces)} annonces récupérées.")

# Exemple : afficher les titres
for a in annonces:
    try:
        titre = a.find_element(By.CSS_SELECTOR, "[data-qa-id='aditem_title']").text
        prix = a.find_element(By.CSS_SELECTOR, "[data-qa-id='aditem_price']").text
        print(f"🏠 {titre} - {prix}")
    except:
        pass

driver.quit()
