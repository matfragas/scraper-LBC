import requests
from bs4 import BeautifulSoup
from notion_client import Client
import hashlib

NOTION_SECRET = "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"
DATABASE_ID = "222e43cf42f5809e969a000cebc28997"

notion = Client(auth=NOTION_SECRET)

def ad_exists(url)
    results = notion.databases.query(
        {
            database_id DATABASE_ID,
            filter {
                property URL,
                url {
                    equals url
                }
            }
        }
    )
    return len(results.get(results, []))  0

def parse_annonce(url)
    res = requests.get(url, headers={User-Agent Mozilla5.0})
    soup = BeautifulSoup(res.text, html.parser)

    def get_text(selector)
        el = soup.select_one(selector)
        return el.text.strip() if el else 

    title = get_text(h1)
    price = get_text('[data-qa-id=adview_price]').replace("€", "").replace("\u202f", "").strip()
    desc = get_text('[data-qa-id=adview_description_container]')
    location = get_text('[data-qa-id=adview_location_informations]')

    details = {el.select_one(span).text.lower() el.select(span)[1].text
               for el in soup.select('[data-qa-id=criteria_item]') if len(el.select(span)) = 2}

    return {
        title title,
        price int(price) if price.isdigit() else 0,
        description desc,
        location location,
        surface details.get(surface, ),
        pièces details.get(pièces, ),
        type details.get(type de bien, ),
        étage details.get(étage, ),
        meublé details.get(meublé, ),
        énergie details.get(classe énergie, ),
        url url
    }

def insert_into_notion(data)
    notion.pages.create(parent={database_id DATABASE_ID}, properties={
        Titre {title [{text {content data[title]}}]},
        Prix {number data[price]},
        Localisation {rich_text [{text {content data[location]}}]},
        Surface {rich_text [{text {content data[surface]}}]},
        Pièces {rich_text [{text {content data[pièces]}}]},
        Type de bien {rich_text [{text {content data[type]}}]},
        Étage {rich_text [{text {content data[étage]}}]},
        Meublé {rich_text [{text {content data[meublé]}}]},
        Classe énergie {rich_text [{text {content data[énergie]}}]},
        URL {url data[url]}
    })

# Exemple d’URL à scrapper (peut être amélioré pour scrapper un listing)
urls = [
    httpswww.leboncoin.frventes_immobilieresxxxxxxx.htm
]

for url in urls
    if not ad_exists(url)
        data = parse_annonce(url)
        insert_into_notion(data)
