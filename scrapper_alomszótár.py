import requests
from bs4 import BeautifulSoup
import json
import time
import os

BASE_URL = "https://almoskonyv.com"
INDEX_URL = BASE_URL + "/alomszotar"

# -------------------------------------------------------
# 1) BETŰOLDALAK INTELLIGENS LEKÉRÉSE
# -------------------------------------------------------
def get_letter_pages():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    r = requests.get(INDEX_URL, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")

    letter_pages = {}
    
    for a in soup.select("a"):
        href = a.get("href", "")
        
        # Ha a link tartalmazza ezt a specifikus szöveget, akkor ez egy betűgyűjtő oldal!
        if "-betuvel-kezdodo-almok" in href:
            # Kitaláljuk a betűt az URL-ből (pl. "a-a-betuvel..." -> "A")
            clean_url = href.strip()
            # Biztosítjuk, hogy teljes URL legyen
            if not clean_url.startswith("http"):
                clean_url = BASE_URL + clean_url
                
            # Kulcsként az URL végét használjuk, hogy egyedi legyen
            letter_key = clean_url.split("/")[-2].replace("-betuvel-kezdodo-almok-jelentese-es-ertelmezese", "").upper()
            letter_pages[letter_key] = clean_url

    print(f"🎯 Sikeresen megtaláltam {len(letter_pages)} betűcsoport oldalát!")
    for k, v in letter_pages.items():
        print(f"   • [{k}] -> {v}")
        
    return letter_pages


# -------------------------------------------------------
# 2) EGY BETŰ ALATTI ÖSSZES ÁLOMLINK KINYERÉSE
# -------------------------------------------------------
def scrape_letter_page(url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")

    dream_links = []
    for a in soup.select("a"):
        href = a.get("href", "")
        # Az oldalon az álmok linkjei úgy végződnek, hogy "-mit-jelent..." vagy "-almodni..."
        if "mit-jelent" in href or "almodni" in href:
            if not href.startswith("http"):
                href = BASE_URL + href
            # Kiszűrjük a főoldalt vagy szerzői linkeket, ha lennének
            if href != BASE_URL + "/" and "author" not in href:
                dream_links.append(href)

    return list(set(dream_links))


# -------------------------------------------------------
# 3) EGY SPECIFIKUS ÁLOM JELENTÉSÉNEK CIKK-KIVONÁSA
# -------------------------------------------------------
def scrape_dream(url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")

        # Cím kinyerése (pl. "Mit jelent kutyával álmodni?")
        title = soup.find("h1").text.strip() if soup.find("h1") else "ismeretlen"
        
        # Megtisztítjuk a címet a sallangtól, hogy tiszta kulcsszó legyen
        kulcsszo = title.replace("Mit jelent", "").replace("almodni", "").replace("álmodni", "").replace("?", "").strip().lower()

        # Megkeressük a leírást. A WordPress oldalakon ez általában az 'entry-content' div-ben van
        content = soup.find("div", class_="entry-content") or soup.find("article")
        
        if content:
            # Kiszedjük a bekezdéseket szövegként
            paragraphs = [p.text.strip() for p in content.find_all("p") if p.text.strip()]
            meaning = "\n".join(paragraphs)
        else:
            meaning = "Nem sikerült kinyerni a szöveget."

        return {
            "kulcsszo": kulcsszo,
            "jelentesek": [meaning] if meaning else ["Nincs részletes leírás."],
            "forras": url
        }
    except Exception as e:
        print(f"❌ Hiba a cikk letöltésekor ({url}): {e}")
        return None


# -------------------------------------------------------
# 4) FŐ FOLYAMAT
# -------------------------------------------------------
def scrape_all():
    letters = get_letter_pages()
    all_dreams = []

    for letter, url in letters.items():
        print(f"\n🔤 Betűcsoport feldolgozása: {letter}")
        dream_pages = scrape_letter_page(url)
        print(f"   Found {len(dream_pages)} darab álom szócikket ennél a betűnél.")

        # Hogy ne tartson órákig a tesztelés, betűnként az első 3-at szedjük le tesztnek, 
        # vagy vedd ki a [:3] részt, ha az összeset akarod egyszerre (az sok percig tarthat!)
        for dp in dream_pages[:3]: 
            print(f"    ➜ Letöltés: {dp}")
            dream_data = scrape_dream(dp)
            if dream_data:
                all_dreams.append(dream_data)
            time.sleep(0.5)  # Rövid szünet a szerver védelmében

    return all_dreams


def merge_with_existing(new_data, existing_path="alomszotar.json"):
    if not os.path.exists(existing_path):
        print("⚠ Nincs meglévő alomszotar.json — új fájlt hozok létre.")
        return new_data

    try:
        with open(existing_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            existing = data.get("alomszotar", [])
    except Exception as e:
        print(f"Hiba a meglévő fájl beolvasásakor, üresről indulunk: {e}")
        existing = []

    merged = {item["kulcsszo"]: item for item in existing if "kulcsszo" in item}

    for item in new_data:
        key = item["kulcsszo"]
        if key in merged:
            for jel in item["jelentesek"]:
                if jel not in merged[key]["jelentesek"]:
                    merged[key]["jelentesek"].append(jel)
        else:
            merged[key] = item

    return list(merged.values())


if __name__ == "__main__":
    print("⏳ Adatok letöltése az almoskonyv.com oldalról...")
    scraped = scrape_all()

    print(f"\n🔄 Összesen letöltve: {len(scraped)} új szócikk.")
    print("🔄 Összefűzés a meglévő alomszotar.json-nal...")
    merged = merge_with_existing(scraped)

    output = {"alomszotar": merged}

    with open("alomszotar.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

    print("🎉 Kész! A frissített adatbázis sikeresen mentve: alomszotar.json")