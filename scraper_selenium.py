from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
import time

print("🚀 Lancement du scraper LeBonCoin avec undetected_chromedriver")

options = uc.ChromeOptions()
# options.headless = True  # TEST SANS headless pour le moment
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36")

driver = uc.Chrome(options=options)

url = "https://www.leboncoin.fr/recherche?category=9&locations=Louverné_53950__48.12273_-0.72003_5000,L'Huisserie_53970__48.02281_-0.77001_5000,Saint-Berthevin_53940__48.06967_-0.83152_5000,Chang%C3%A9_53810__48.09901_-0.78975_5000,Laval_53000__48.07268_-0.77307_5000&price=min-320000&square=85-max&real_estate_type=1,3"

print(f"🔎 URL : {url}")
driver.get(url)

time.sleep(5)  # ⏱ important pour charger les annonces JS

print(f"✅ Titre de la page : {driver.title}")
print(driver.page_source[:1000])  # pour vérifier si la page contient bien les annonces

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
