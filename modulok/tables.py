import swisseph as swe


varga_factors = {
    "D1 (Rashi)": 1,
    "D2 (Hora)": 15,
    "D3 (Drekkana)": 10,
    "D4 (Chaturthamsa)": 7.5,
    "D5 (Panchamsa)": 6,
    "D6 (Shashthamsa)": 5,
    "D7 (Saptamsa)": 4.28,
    "D8 (Ashtamsa)": 3.75,
    "D9 (Navamsha)": 3.3333,
    "D10 (Dasamsa)": 3,
    "D11 (Rudramsa)": 2.8,
    "D12 (Dwadasamsa)": 2.5,
    "D16 (Shodasamsa)": 1.875,
    "D20 (Vimsamsa)": 1.5,
    "D24 (Chaturvimsamsa)": 1.25,
    "D27 (Nakshatramsa)": 1.1,
    "D30 (Trimsamsa)": 1,
    "D40 (Khavedamsa)": 0.75,
    "D45 (Akshavedamsa)": 0.6,
    "D60 (Shashtyamsa)": 0.5,
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
house_positions = {
    1: (1, 3),  # Kos
    2: (2, 3),  # Bika
    3: (3, 3),  # Ikrek
    4: (3, 2),  # Rák
    5: (3, 1),  # Oroszlán
    6: (3, 0),  # Szűz
    7: (2, 0),  # Mérleg
    8: (1, 0),  # Skorpió
    9: (0, 0),  # Nyilas
    10: (0, 1),  # Bak
    11: (0, 2),  # Vízöntő
    12: (0, 3),  # Halak
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
