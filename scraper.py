import os
import sys

def main():
    print("🚀 Lancement du scraper LeBonCoin")

    # Récupération de la variable d'environnement LBC_URL
    lbc_url = os.getenv('LBC_URL')
    print(f"URL récupérée depuis LBC_URL : {lbc_url}")

    if not lbc_url:
        print("❌ La variable d’environnement LBC_URL est manquante ou vide")
        sys.exit(1)

    # Exemple basique : ici tu lances ton scraping avec lbc_url
    # TODO : ajoute ta logique de scraping ici

    print("✅ Scraping terminé avec succès")

if __name__ == "__main__":
    main()
