import requests
from bs4 import BeautifulSoup
import json
import time
import string
import os

BASE_URL = "https://almoskonyv.com"
INDEX_URL = BASE_URL + "/alomszotar"

# -------------------------------------------------------
# 1) BETŰOLDALAK LEKÉRÉSE
# -------------------------------------------------------
def get_letter_pages():
    r = requests.get(INDEX_URL)
    soup = BeautifulSoup(r.text, "html.parser")

    letter_pages = {}
    for a in soup.select("a"):
        text = a.text.strip()
        href = a.get("href", "")

        if len(text) == 1 and text.upper() in string.ascii_uppercase:
            letter_pages[text.upper()] = BASE_URL + href

    return letter_pages


# -------------------------------------------------------
# 2) EGY BETŰ ALATTI ÁLOMLINKEK
# -------------------------------------------------------
def scrape_letter_page(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")

    dream_links = []
    for a in soup.select("a"):
        href = a.get("href", "")
        if "/alom/" in href:
            dream_links.append(BASE_URL + href)

    return list(set(dream_links))


# -------------------------------------------------------
# 3) EGY ÁLOM JELENTÉSÉNEK LEKÉRÉSE
# -------------------------------------------------------
def scrape_dream(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")

    title = soup.find("h1").text.strip() if soup.find("h1") else "ismeretlen"
    content = soup.find("div", class_="entry-content")

    meaning = content.get_text("\n").strip() if content else ""

    return {
        "kulcsszo": title.lower(),
        "jelentesek": [meaning],
        "forras": url
    }


# -------------------------------------------------------
# 4) TELJES SCRAPE A–Z
# -------------------------------------------------------
def scrape_all():
    letters = get_letter_pages()
    all_dreams = []

    for letter, url in letters.items():
        print(f"🔤 Betű: {letter}")
        dream_pages = scrape_letter_page(url)

        for dp in dream_pages:
            print(f"   ➜ Letöltés: {dp}")
            dream_data = scrape_dream(dp)
            all_dreams.append(dream_data)
            time.sleep(1)  # kíméletes lekérés

    return all_dreams


# -------------------------------------------------------
# 5) ÖSSZEFŰZÉS A MEGLÉVŐ alomszotar.json-NAL
# -------------------------------------------------------
def merge_with_existing(new_data, existing_path="alomszotar.json"):
    if not os.path.exists(existing_path):
        print("⚠ Nincs meglévő alomszotar.json — új fájlt hozok létre.")
        return new_data

    with open(existing_path, "r", encoding="utf-8") as f:
        existing = json.load(f).get("alomszotar", [])

    merged = {item["kulcsszo"]: item for item in existing}

    for item in new_data:
        key = item["kulcsszo"]
        if key in merged:
            # új jelentések hozzáfűzése, duplikáció nélkül
            for jel in item["jelentesek"]:
                if jel not in merged[key]["jelentesek"]:
                    merged[key]["jelentesek"].append(jel)
        else:
            merged[key] = item

    return list(merged.values())


# -------------------------------------------------------
# 6) FUTTATÁS
# -------------------------------------------------------
if __name__ == "__main__":
    print("⏳ Adatok letöltése...")
    scraped = scrape_all()

    print("🔄 Összefűzés a meglévő alomszotar.json-nal...")
    merged = merge_with_existing(scraped)

    output = {"alomszotar": merged}

    with open("alomszotar.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

    print("🎉 Kész! A frissített adatbázis mentve: alomszotar.json")
