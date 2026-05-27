import swisseph as swe


tithi_info = {
    1:  {"nev": "Shukla Pratipada",   "jelentes": "Új kezdet, indulás", 
         "ajanlas": "Fogalmazd meg a napi szándékod"},
    2:  {"nev": "Shukla Dwitiy",      "jelentes": "Stabilitás, párosítás", 
         "ajanlas": "Találd meg a belső egyensúlyt"},
    3:  {"nev": "Shukla Tritiya",     "jelentes": "Cselekvés, kezdeményezés", 
         "ajanlas": "Tedd meg az első lépést"},
    4:  {"nev": "Shukla Chaturthi",   "jelentes": "Kitartás, akadályok leküzdése", 
         "ajanlas": "Fókuszálj egy kihívásra"},
    5:  {"nev": "Shukla Panchami",    "jelentes": "Növekedés, bátorság", 
         "ajanlas": "Erősítsd a bizalmad és hangod"},
    6:  {"nev": "Shukla Shashti",     "jelentes": "Érzelmi tisztulás, gyógyulás", 
         "ajanlas": "Írj ki magadból valamit"},
    7:  {"nev": "Shukla Saptami",     "jelentes": "Napenergia, aktivitás", 
         "ajanlas": "Mozgasd át a tested"},
    8:  {"nev": "Shukla Ashtami",     "jelentes": "Harcos energia, fókuszáltság", 
         "ajanlas": "Cselekedj tudatosan"},
    9:  {"nev": "Shukla Navami",      "jelentes": "Intuíció, belső látás", 
         "ajanlas": "Meditálj 10 percet"},
    10: {"nev": "Shukla Dashami",     "jelentes": "Megértés, tanítás", 
         "ajanlas": "Oszd meg a tudásod"},
    11: {"nev": "Shukla Ekadashi",    "jelentes": "Tisztulás, könnyedség", 
         "ajanlas": "Kerüld a túlzást"},
    12: {"nev": "Shukla Dwadashi",    "jelentes": "Kiegyenlítődés, terjeszkedés", 
         "ajanlas": "Vizualizáld a céljaid"},
    13: {"nev": "Shukla Trayodashi",  "jelentes": "Spirituális integráció", 
         "ajanlas": "Olvass valami bölcset"},
    14: {"nev": "Shukla Chaturdashi", "jelentes": "Energia-maximum, szertartás", 
         "ajanlas": "Gyújts mécsest"},
    15: {"nev": "Purnima",            "jelentes": "Beteljesedés, teljesség", 
         "ajanlas": "Írd le, miért vagy hálás"},

    16: {"nev": "Krishna Pratipada",  "jelentes": "Visszalépés, befelé fordulás", 
         "ajanlas": "Pihenj, engedd el az elvárásokat"},
    17: {"nev": "Krishna Dwitiy",     "jelentes": "Elengedés, lassulás", 
         "ajanlas": "Engedd el a múlt egy darabját"},
    18: {"nev": "Krishna Tritiya",    "jelentes": "Feloldás, megbocsátás", 
         "ajanlas": "Írd le: 'megbocsátok…'"},
    19: {"nev": "Krishna Chaturthi",  "jelentes": "Feszültség és tudatosság", 
         "ajanlas": "Lélegezz 5 mélyet"},
    20: {"nev": "Krishna Panchami",   "jelentes": "Figyelem és tisztulás", 
         "ajanlas": "Figyeld meg a reakcióid"},
    21: {"nev": "Krishna Shashti",    "jelentes": "Önvizsgálat, csendeség", 
         "ajanlas": "Legyél egyedül kicsit"},
    22: {"nev": "Krishna Saptami",    "jelentes": "Átalakulás, újrakezdés", 
         "ajanlas": "Tegyél rendet egy kis területen"},
    23: {"nev": "Krishna Ashtami",    "jelentes": "Mély spirituális energia", 
         "ajanlas": "Hallgass mantrát"},
    24: {"nev": "Krishna Navami",     "jelentes": "Harc a belső démonokkal", 
         "ajanlas": "Ne ítélkezz magad fölött"},
    25: {"nev": "Krishna Dashami",    "jelentes": "Egyensúly keresése", 
         "ajanlas": "Írj egy levelet, amit nem küldesz el"},
    26: {"nev": "Krishna Ekadashi",   "jelentes": "Tisztulás, önuralom", 
         "ajanlas": "Tölts időt a természetben"},
    27: {"nev": "Krishna Dwadashi",   "jelentes": "Befejezés, reflexió", 
         "ajanlas": "Nézd vissza a heted"},
    28: {"nev": "Krishna Trayodashi", "jelentes": "Újjászületés, tisztítás", 
         "ajanlas": "Készülj új hold-szertartásra"},
    29: {"nev": "Krishna Chaturdashi","jelentes": "Belső csend", 
         "ajanlas": ""},
    30: {"nev": "Amavasya",           "jelentes": "Teljes sötétség, elengedés", 
         "ajanlas": ""},
}

tithi_dynamics = {
    1:  {"amp": 0.70, "attack": 0.10},
    2:  {"amp": 0.75, "attack": 0.09},
    3:  {"amp": 0.80, "attack": 0.08},
    4:  {"amp": 0.85, "attack": 0.07},
    5:  {"amp": 0.90, "attack": 0.06},
    6:  {"amp": 0.95, "attack": 0.06},
    7:  {"amp": 1.00, "attack": 0.05},
    8:  {"amp": 1.05, "attack": 0.05},
    9:  {"amp": 1.10, "attack": 0.04},
    10: {"amp": 1.15, "attack": 0.04},
    11: {"amp": 1.10, "attack": 0.05},
    12: {"amp": 1.05, "attack": 0.05},
    13: {"amp": 1.10, "attack": 0.04},
    14: {"amp": 1.15, "attack": 0.03},
    15: {"amp": 1.20, "attack": 0.03},  # Purnima – csúcs

    16: {"amp": 1.00, "attack": 0.05},
    17: {"amp": 0.95, "attack": 0.06},
    18: {"amp": 0.90, "attack": 0.07},
    19: {"amp": 0.85, "attack": 0.08},
    20: {"amp": 0.80, "attack": 0.09},
    21: {"amp": 0.75, "attack": 0.10},
    22: {"amp": 0.80, "attack": 0.09},
    23: {"amp": 0.85, "attack": 0.08},
    24: {"amp": 0.90, "attack": 0.07},
    25: {"amp": 0.95, "attack": 0.06},
    26: {"amp": 0.90, "attack": 0.07},
    27: {"amp": 0.85, "attack": 0.08},
    28: {"amp": 0.80, "attack": 0.09},
    29: {"amp": 0.70, "attack": 0.11},
    30: {"amp": 0.60, "attack": 0.12},  # Amavasya – lágy, halk
}

# Elem szótár (jegy → elem)
ELEMENTS = {
    "Kos": "Tűz",
    "Bika": "Föld",
    "Ikrek": "Levegő",
    "Rák": "Víz",
    "Oroszlán": "Tűz",
    "Szűz": "Föld",
    "Mérleg": "Levegő",
    "Skorpió": "Víz",
    "Nyilas": "Tűz",
    "Bak": "Föld",
    "Vízöntő": "Levegő",
    "Halak": "Víz"
}

# Elem → ritmus (egyszerű példa)
RHYTHMS = {
    "Tűz": 0.25,   # gyors ütem (negyed másodperc)
    "Víz": 1.0,    # lassú ütem (1 mp)
    "Föld": 0.5,   # stabil ütem (fél mp)
    "Levegő": 0.75 # közepes ütem
}
# 💲 Globális tábla (uralkodó → nakshatra → 4 frekvencia)
nakshatra_data = {
    "Ashwini": {
        "ura": "ketu",
        "hangnem": "C-dúr",
        "scale": [0, 2, 4, 7, 9],
        "pada_freqs": [43.5, 87, 130.5, 174]
    },
    "Bharani": {
        "ura": "vénusz",
        "hangnem": "D-moll",
        "scale": [0, 2, 3, 5, 7, 10],
        "pada_freqs": [159.75, 319.5, 479.25, 639]
    },
    "Krittika": {
        "ura": "nap",
        "hangnem": "E-dúr",
        "scale": [0, 1, 4, 6, 7, 11],
        "pada_freqs": [240.75, 481.5, 722.25, 963]
    },
    "Rohini": {
        "ura": "hold",
        "hangnem": "A-dúr",
        "scale": [0, 2, 5, 7, 9],
        "pada_freqs": [104.25, 208.5, 312.75, 417]
    },
    "Mrigashira": {
        "ura": "mars",
        "hangnem": "G-dúr",
        "scale": [0, 2, 3, 5, 7, 9],
        "pada_freqs": [132, 264, 396, 528]
    },
    "Ardra": {
        "ura": "rahu",
        "hangnem": "F-moll",
        "scale": [0, 3, 5, 6, 10],
        "pada_freqs": [71.25, 142.5, 213.75, 285]
    },
    "Punarvasu": {
        "ura": "jupiter",
        "hangnem": "G-moll",
        "scale": [0, 2, 4, 5, 9],
        "pada_freqs": [213, 426, 639, 852]
    },
    "Pushya": {
        "ura": "szaturnusz",
        "hangnem": "B-dúr",
        "scale": [0, 2, 4, 7, 11],
        "pada_freqs": [92.25, 184.5, 276.75, 369]
    },
    "Ashlesha": {
        "ura": "merkúr",
        "hangnem": "D♯-moll",
        "scale": [0, 1, 4, 8, 10],
        "pada_freqs": [185.25, 370.5, 555.75, 741]
    },
    "Magha": {
        "ura": "ketu",
        "hangnem": "C♯-dúr",
        "scale": [0, 2, 5, 7, 10],
        "pada_freqs": [43.5, 87, 130.5, 174]
    },
    "Purva Phalguni": {
        "ura": "vénusz",
        "hangnem": "A♭-dúr",
        "scale": [0, 4, 5, 7, 9],
        "pada_freqs": [159.75, 319.5, 479.25, 639]
    },
    "Uttara Phalguni": {
        "ura": "nap",
        "hangnem": "B♭-dúr",
        "scale": [0, 2, 4, 7, 9, 11],
        "pada_freqs": [240.75, 481.5, 722.25, 963]
    },
    "Hasta": {
        "ura": "hold",
        "hangnem": "F-dúr",
        "scale": [0, 2, 3, 7, 9],
        "pada_freqs": [104.25, 208.5, 312.75, 417]
    },
    "Chitra": {
        "ura": "mars",
        "hangnem": "E♭-dúr",
        "scale": [0, 4, 6, 7, 11],
        "pada_freqs": [132, 264, 396, 528]
    },
    "Swati": {
        "ura": "rahu",
        "hangnem": "D-dúr",
        "scale": [0, 2, 5, 7, 9, 10],
        "pada_freqs": [71.25, 142.5, 213.75, 285]
    },
    "Vishakha": {
        "ura": "jupiter",
        "hangnem": "G♯-moll",
        "scale": [0, 1, 5, 7, 8],
        "pada_freqs": [213, 426, 639, 852]
    },
    "Anuradha": {
        "ura": "szaturnusz",
        "hangnem": "A-moll",
        "scale": [0, 3, 5, 7, 10],
        "pada_freqs": [92.25, 184.5, 276.75, 369]
    },
    "Jyeshtha": {
        "ura": "merkúr",
        "hangnem": "C-moll",
        "scale": [0, 1, 4, 6, 8, 11],
        "pada_freqs": [185.25, 370.5, 555.75, 741]
    },
    "Mula": {
        "ura": "ketu",
        "hangnem": "F♯-moll",
        "scale": [0, 3, 5, 6, 10],
        "pada_freqs": [43.5, 87, 130.5, 174]
    },
    "Purva Ashadha": {
        "ura": "vénusz",
        "hangnem": "E-moll",
        "scale": [0, 2, 5, 7, 9],
        "pada_freqs": [159.75, 319.5, 479.25, 639]
    },
    "Uttara Ashadha": {
        "ura": "nap",
        "hangnem": "G♭-dúr",
        "scale": [0, 2, 4, 7, 9, 11],
        "pada_freqs": [240.75, 481.5, 722.25, 963]
    },
    "Shravana": {
        "ura": "hold",
        "hangnem": "A♯-dúr",
        "scale": [0, 2, 5, 7, 9],
        "pada_freqs": [104.25, 208.5, 312.75, 417]
    },
    "Dhanishta": {
        "ura": "mars",
        "hangnem": "B♭-moll",
        "scale": [0, 2, 4, 7, 9, 10],
        "pada_freqs": [132, 264, 396, 528]
    },
    "Shatabhisha": {
        "ura": "rahu",
        "hangnem": "C♯-moll",
        "scale": [0, 1, 5, 7, 8],
        "pada_freqs": [71.25, 142.5, 213.75, 285]
    },
    "Purva Bhadrapada": {
        "ura": "jupiter",
        "hangnem": "F♯-dúr",
        "scale": [0, 3, 6, 7, 10],
        "pada_freqs": [213, 426, 639, 852]
    },
    "Uttara Bhadrapada": {
        "ura": "szaturnusz",
        "hangnem": "G-moll",
        "scale": [0, 2, 3, 7, 9],
        "pada_freqs": [92.25, 184.5, 276.75, 369]
    },
    "Revati": {
        "ura": "merkúr",
        "hangnem": "D-dúr",
        "scale": [0, 2, 4, 7, 9],
        "pada_freqs": [185.25, 370.5, 555.75, 741]
    }
}

# 📌 Jegy -> (Uralkodó bolygó, Frekvencia, Mantra)
mantra_map = {
    1: ("Mars", 528, "ram"),
    2: ("Venus", 639, "yam"),
    3: ("Mercury", 741, "ham"),
    4: ("Moon", 417, "vam"),
    5: ("Sun", 963, "ram"),
    6: ("Mercury", 690, "ham"),
    7: ("Venus", 583.5, "yam"),
    8: ("Mars", 472.5, "ram"),
    9: ("Jupiter", 852, "om"),
    10: ("Saturn", 369, "lam"),
    11: ("Saturn", 907.5, "aum"),
    12: ("Jupiter", 796.5, "om"),
}
# Jegy -> (Uralkodó bolygó, Frekvencia)
jegy_uralkodok = {
    1: ("Mars", 528),
    2: ("Venus", 639),
    3: ("Mercury", 741),
    4: ("Moon", 417),
    5: ("Sun", 963),
    6: ("Mercury", 690),
    7: ("Venus", 583.5),
    8: ("Mars", 472.5),
    9: ("Jupiter", 852),
    10: ("Saturn", 369),
    11: ("Saturn", 907.5),
    12: ("Jupiter", 796.5),
}


varga_factors = {
    "D1 (Rashi)": 1,                 # test, egyéniség, ego, alapvető sorsmintázat
    "D2 (Hora)": 15,                 # egészség, anyagi helyzet, egzisztencia, vitalitás
    "D3 (Drekkana)": 10,             # erő, bátorság, testvérek, kezdeményezés
    "D4 (Chaturthamsa)": 7.5,        # otthon, lélek, érzelmi alap, belső stabilitás
    "D5 (Panchamsa)": 6,             # gyerek, kreativitás, intuíció, önkifejezés
    "D6 (Shashthamsa)": 5,           # nehézségek, munka, betegségek, szolgálat
    "D7 (Saptamsa)": 4.28,           # társ, munkatárs, házastárs, kapcsolati dinamika
    "D8 (Ashtamsa)": 3.75,           # változás, spiritualitás, krízisek, transzformáció
    "D9 (Navamsha)": 3.3333,         # tudás, tudat, dharma, házasság magasabb szintje
    "D10 (Dasamsa)": 3,              # siker, hivatás, társadalmi szerep
    "D11 (Rudramsa)": 2.8,           # erőpróbák, karmikus akadályok, kitartás
    "D12 (Dwadasamsa)": 2.5,         # mélyebb spiritualitás, ősök, családi örökség
    "D16 (Shodasamsa)": 1.875,       # járművek, komfort, luxus, finom örömök
    "D20 (Vimsamsa)": 1.5,           # hit, mantra, spirituális gyakorlatok
    "D24 (Chaturvimsamsa)": 1.25,    # tanulás, tudomány, intelligencia, oktatás
    "D27 (Nakshatramsa)": 1.1,       # erősségek, gyengeségek, finom testi energiák
    "D30 (Trimsamsa)": 1,            # hibák, árnyékok, belső démonok, balsors
    "D40 (Khavedamsa)": 0.75,        # anyai ág, finom karmák, érzelmi lenyomatok
    "D45 (Akshavedamsa)": 0.6,       # apai ág, karakter mélyrétegei
    "D60 (Shashtyamsa)": 0.5,        # előző életek, gyökérkarma, sors esszenciája
}

nakshatras = [
    "Ashwini",
    "Bharani",
    "Krittika",
    "Rohini",
    "Mrigashira",
    "Ardra",
    "Punarvasu",
    "Pushya",
    "Ashlesha",
    "Magha",
    "Purva Phalguni",
    "Uttara Phalguni",
    "Hasta",
    "Chitra",
    "Swati",
    "Vishaka",
    "Anuradha",
    "Jyeshta",
    "Mula",
    "Purva Shada",
    "Uttara Shada",
    "Shravana",
    "Dhanishta",
    "Shatabishak",
    "Purva Bhadrapada",
    "Uttara Bhadrapada",
    "Revati",
]
bolygo_nakshatra_map = {
    "Mars": ["Mrigashira", "Chitra", "Dhanishta"],
    "Venus": ["Bharani", "Purva Phalguni", "Purva Shada"],
    "Mercury": ["Ashlesha", "Jyeshta", "Revati"],
    "Moon": ["Rohini", "Hasta", "Shravana"],
    "Sun": ["Krittika", "Uttara Phalguni", "Uttara Shada"],
    "Jupiter": ["Punarvasu", "Vishaka", "Purva Bhadrapada"],
    "Saturn": ["Pushya", "Anuradha", "Uttara Bhadrapada"],
    "Rahu": ["Ardra", "Swati", "Shatabishaka"],
    "Ketu": ["Ashwini", "Magha", "Mula"],
}
# Horoszkóp számítása
##ayanamsa = swe.get_ayanamsa_ut(best_jd)
planet_ids = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mars": swe.MARS,
    "Mercury": swe.MERCURY,
    "Jupiter": swe.JUPITER,
    "Venus": swe.VENUS,
    "Saturn": swe.SATURN,
    "Rahu": swe.MEAN_NODE,
    "Ketu": swe.TRUE_NODE,
}

# Rövidítések létrehozása
planet_abbreviations = {
    "Sun": "Su",
    "Moon": "Mo",
    "Mars": "Ma",
    "Mercury": "Me",
    "Jupiter": "Ju",
    "Venus": "Ve",
    "Saturn": "Sa",
    "Rahu": "Ra",
    "Ketu": "Ke",
    "ASC": "As",
}
# Házpozíciók (dél-indiai rendszer, 1-től 12-ig)
# 🎯 JAVÍTÁS: A dél-indiai óramutató járása szerinti fix elrendezés (Y=0 a felső sor, Y=3 az alsó sor)
house_positions = {
    1:  (1, 0),  # Kos (Felső sor, 2. cella)
    2:  (2, 0),  # Bika (Felső sor, 3. cella)
    3:  (3, 0),  # Ikrek (Jobb felső sarok)
    4:  (3, 1),  # Rák (Jobb oldal, 2. sor)
    5:  (3, 2),  # Oroszlán (Jobb oldal, 3. sor)
    6:  (3, 3),  # Szűz (Jobb alsó sarok)
    7:  (2, 3),  # Mérleg (Alsó sor, 3. cella)
    8:  (1, 3),  # Skorpió (Alsó sor, 2. cella)
    9:  (0, 3),  # Nyilas (Bal alsó sarok)
    10: (0, 2),  # Bak (Bal oldal, 3. sor)
    11: (0, 1),  # Vízöntő (Bal oldal, 2. sor)
    12: (0, 0),  # Halak (Bal felső sarok)
}
purushartha_map = {
    1: {
        1: ("Dharma", "Becsületes élet"),
        2: ("Artha", "Anyagi jólét világa"),
        3: ("Kama", "Vágyaink vezérlik az életünket"),
        4: ("Moksha", "Spirituális élet, megvilágosodás"),
    },
    2: {
        1: ("Dharma", "Becsületes élet"),
        2: ("Artha", "Anyagi jólét világa"),
        3: ("Kama", "Vágyaink vezérlik az életünket"),
        4: ("Moksha", "Spirituális élet, megvilágosodás"),
    },
    3: {
        1: ("Dharma", "Becsületes élet"),
        2: ("Artha", "Anyagi jólét világa"),
        3: ("Kama", "Vágyaink vezérlik az életünket"),
        4: ("Moksha", "Spirituális élet, megvilágosodás"),
    },
    4: {
        1: ("Dharma", "Becsületes élet"),
        2: ("Artha", "Anyagi jólét világa"),
        3: ("Kama", "Vágyaink vezérlik az életünket"),
        4: ("Moksha", "Spirituális élet, megvilágosodás"),
    },
    5: {
        1: ("Dharma", "Becsületes élet"),
        2: ("Artha", "Anyagi jólét világa"),
        3: ("Kama", "Vágyaink vezérlik az életünket"),
        4: ("Moksha", "Spirituális élet, megvilágosodás"),
    },
    6: {
        1: ("Dharma", "Becsületes élet"),
        2: ("Artha", "Anyagi jólét világa"),
        3: ("Kama", "Vágyaink vezérlik az életünket"),
        4: ("Moksha", "Spirituális élet, megvilágosodás"),
    },
    7: {
        1: ("Dharma", "Becsületes élet"),
        2: ("Artha", "Anyagi jólét világa"),
        3: ("Kama", "Vágyaink vezérlik az életünket"),
        4: ("Moksha", "Spirituális élet, megvilágosodás"),
    },
    8: {
        1: ("Dharma", "Becsületes élet"),
        2: ("Artha", "Anyagi jólét világa"),
        3: ("Kama", "Vágyaink vezérlik az életünket"),
        4: ("Moksha", "Spirituális élet, megvilágosodás"),
    },
    9: {
        1: ("Dharma", "Becsületes élet"),
        2: ("Artha", "Anyagi jólét világa"),
        3: ("Kama", "Vágyaink vezérlik az életünket"),
        4: ("Moksha", "Spirituális élet, megvilágosodás"),
    },
    10: {
        1: ("Dharma", "Becsületes élet"),
        2: ("Artha", "Anyagi jólét világa"),
        3: ("Kama", "Vágyaink vezérlik az életünket"),
        4: ("Moksha", "Spirituális élet, megvilágosodás"),
    },
    11: {
        1: ("Dharma", "Becsületes élet"),
        2: ("Artha", "Anyagi jólét világa"),
        3: ("Kama", "Vágyaink vezérlik az életünket"),
        4: ("Moksha", "Spirituális élet, megvilágosodás"),
    },
    12: {
        1: ("Dharma", "Becsületes élet"),
        2: ("Artha", "Anyagi jólét világa"),
        3: ("Kama", "Vágyaink vezérlik az életünket"),
        4: ("Moksha", "Spirituális élet, megvilágosodás"),
    },
}


haz_aspektusok = {
    1: (
        "Kendra",
        "4 alappillér. Attól függ, honnan számoljuk, de nem árt, ha van benne bolygó.",
    ),
    2: (
        "Trikona",
        "Erősítő házak. Ha ezekben a házakban van bolygó, az erősíti a házat.",
    ),
    3: ("Upachaya", "Követő házak."),
    4: (
        "Kendra",
        "4 alappillér. Attól függ, honnan számoljuk, de nem árt, ha van benne bolygó.",
    ),
    5: (
        "Trikona",
        "Erősítő házak. Ha ezekben a házakban van bolygó, az erősíti a házat.",
    ),
    6: ("Dushtansa", "Negatív hatású házak."),
    7: (
        "Kendra",
        "4 alappillér. Attól függ, honnan számoljuk, de nem árt, ha van benne bolygó.",
    ),
    8: ("Dushtansa", "Negatív hatású házak."),
    9: (
        "Trikona",
        "Erősítő házak. Ha ezekben a házakban van bolygó, az erősíti a házat.",
    ),
    10: (
        "Kendra",
        "4 alappillér. Attól függ, honnan számoljuk, de nem árt, ha van benne bolygó.",
    ),
    11: ("Upachaya", "Követő házak."),
    12: ("Dushtansa", "Negatív hatású házak."),
}
haz_bolygo_aspektusok = {
    1: ("Saturn", "Bolygó hatásával erősíti vagy gyengíti a házat és a jegyet."),
    2: ("Mars", "Bolygó hatásával erősíti vagy gyengíti a házat és a jegyet."),
    3: ("Saturn", "Bolygó hatásával erősíti vagy gyengíti a házat és a jegyet."),
    4: ("Jupiter", "Bolygó hatásával erősíti vagy gyengíti a házat és a jegyet."),
    5: ("Mars", "Bolygó hatásával erősíti vagy gyengíti a házat és a jegyet."),
    6: (None, "Nincs megadott bolygóhatás."),
    7: ("Saturn", "Bolygó hatásával erősíti vagy gyengíti a házat és a jegyet."),
    8: ("Jupiter", "Bolygó hatásával erősíti vagy gyengíti a házat és a jegyet."),
    9: ("Mars", "Bolygó hatásával erősíti vagy gyengíti a házat és a jegyet."),
    10: ("Saturn", "Bolygó hatásával erősíti vagy gyengíti a házat és a jegyet."),
    11: (None, "Nincs megadott bolygóhatás."),
    12: ("Jupiter", "Bolygó hatásával erősíti vagy gyengíti a házat és a jegyet."),
}
