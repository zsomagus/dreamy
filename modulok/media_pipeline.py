import os, pendulum, subprocess, requests
from music21 import stream, note, metadata
import openai
import suno
from modulok.elemzes import generate_markdown_summary
# 🔮 Prompt generálás
import re

def extract_visual_keywords(summary_text):
    """
    Kinyeri a vizuálisan releváns kulcsszavakat az elemzés szövegéből.
    """
    keywords = set()

    # Jegyek, házak, bolygók, kulcsfogalmak
    jegyek = ["Kos", "Bika", "Ikrek", "Rák", "Oroszlán", "Szűz", "Mérleg", "Skorpió", "Nyilas", "Bak", "Vízöntő", "Halak"]
    bolygok = ["Nap", "Hold", "Merkúr", "Vénusz", "Mars", "Jupiter", "Szaturnusz", "Rahu", "Ketu"]
    purushartha = ["Dharma", "Artha", "Kama", "Moksha"]
    szimbolikus = ["álom", "hal", "fény", "templom", "csillag", "víz", "meditáció", "archetípus", "szentély", "yantra"]

    # Regex keresés
    for word in jegyek + bolygok + purushartha + szimbolikus:
        if re.search(rf"\b{word}\b", summary_text, re.IGNORECASE):
            keywords.add(word)

    return list(keywords)
def generate_image_prompts(keywords, bolygo="Nap", jegy="Halak", haz="12"):
    """
    Képgeneráló promptokat készít a kulcsszavak alapján.
    """
    prompts = []

    # Archetípus
    prompts.append(
        f"A symbolic image of {bolygo} in {jegy}, representing its archetypal energy in house {haz}."
    )

    # Spirituális tanítás
    prompts.append(
        f"A mystical scene showing the spiritual lesson of {bolygo} in {jegy}, in the 12th house – with symbols of {', '.join(keywords)}."
    )

    # Álomszimbólum
    prompts.append(
        f"A dreamlike image of {bolygo} in {jegy}, floating in cosmic waters, surrounded by {', '.join([k for k in keywords if k in ['hal', 'csillag', 'víz', 'álom']])}."
    )

    # Rituális jelenet
    prompts.append(
        f"A ritualistic setting with {bolygo} in {jegy}, in the 12th house – featuring yantras, meditation, and sacred light."
    )

    return prompts# 📁 Mappa létrehozása
def create_output_folder(prompt):
    timestamp = pendulum.now().format("YYYY-MM-DD_HH-mm")
    folder_name = f"{timestamp}_{prompt[:30].replace(' ', '_')}"
    folder_path = os.path.join("horoscope_outputs", folder_name)
    os.makedirs(folder_path, exist_ok=True)
    return folder_path

# 🎶 SunoAI MP3 generálás
def generate_mp3(prompt, folder_path):
    result = generate_music(prompt=prompt, style="Ambient")
    mp3_url = result["audio_url"]
    mp3_path = os.path.join(folder_path, "horoscopezene.mp3")
    with open(mp3_path, "wb") as f:
        f.write(requests.get(mp3_url).content)
    return mp3_path

# 🎼 MusicXML + MIDI generálás
def generate_musicxml(prompt, folder_path):
    s = stream.Score()
    s.metadata = metadata.Metadata()
    s.metadata.title = " Horoszkóp zene"
    s.metadata.comments = [prompt]

    p = stream.Part()
    p.append(note.Note("C4", quarterLength=1.0))
    p.append(note.Note("E4", quarterLength=1.0))
    p.append(note.Note("G4", quarterLength=2.0))
    s.append(p)

    xml_path = os.path.join(folder_path, "kepletzene.musicxml")
    midi_path = os.path.join(folder_path, "kepletzenezene.mid")
    s.write("musicxml", fp=xml_path)
    s.write("midi", fp=midi_path)
    return xml_path, midi_path

# 📄 MuseScore PDF export
def export_pdf(xml_path, folder_path):
    pdf_path = os.path.join(folder_path, "kepletzene.pdf")
    subprocess.run(["musescore3", xml_path, "-o", pdf_path])
    return pdf_path

# 🎨 DALL·E 3 kép generálás
def generate_image(prompt, folder_path):
    response = openai.Image.create(prompt=prompt, n=1, size="1024x1024")
    image_url = response['data'][0]['url']
    image_path = os.path.join(folder_path, "kepletzenekep.png")
    with open(image_path, "wb") as f:
        f.write(requests.get(image_url).content)
    return image_path

# 📝 Prompt mentése
def save_prompt(prompt, folder_path):
    with open(os.path.join(folder_path, "prompt.txt"), "w", encoding="utf-8") as f:
        f.write(prompt)
def generate_house_bundle(haz_szam, bolygo="Nap", jegy="Halak"):
    keywords = extract_visual_keywords(f"{bolygo} in {jegy} in house {haz_szam}")
    prompts = generate_image_prompts(keywords, bolygo, jegy, str(haz_szam))
    folder = create_output_folder(prompts[1])  # spirituális tanítás alapján

    # 🎨 Képek (mind a 4 promptból)
    image_paths = []
    for i, prompt in enumerate(prompts):
        image_path = generate_image(prompt, folder)
        image_paths.append(image_path)

    # 🎶 Zene és kotta (csak a 2. promptból)
    mp3_path = generate_mp3(prompts[1], folder)
    xml_path, midi_path = generate_musicxml(prompts[1], folder)
    pdf_path = export_pdf(xml_path, folder)

    # 📝 Prompt mentés
    save_prompt(prompts[1], folder)

    return {
        "folder": folder,
        "images": image_paths,
        "mp3": mp3_path,
        "xml": xml_path,
        "midi": midi_path,
        "pdf": pdf_path,
        "prompt": prompts[1]
    }
