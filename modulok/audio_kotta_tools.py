import os  # noqa: F401
import json  # noqa: F401
from pathlib import Path  # noqa: F401
import numpy as np
import librosa  # noqa: F401
import sounddevice as sd
import soundfile as sf
import pyttsx3  # noqa: F401
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages  # noqa: F401
from music21 import stream, note, metadata
import swisseph as swe
import pendulum  # ⏳ datetime helyett

from modulok import varshaphala_tools
from modulok.astro_core import (  # noqa: F401
    sanitize_longitude,
    sanitize_number,
    get_planet_position,
    calculate_nakshatra,
    get_ayanamsa,
)
from modulok.config import (  # noqa: F401
    aktualis_vezeteknev,
    aktualis_keresztnev,
    BASE_DIR,
)
from modulok.tables import (  # noqa: F401
    mantra_map,
    jegy_uralkodok,
    bolygo_nakshatra_map,
    nakshatras,
    full_pada_table,
)

# 📂 Mappák
MENTES_DIR = BASE_DIR / "static"
mantra_dir = BASE_DIR / "static" / "mantrák"
ambiance_path = BASE_DIR / "static" / "hangok" / "ambiance.wav"
harang_path = BASE_DIR / "static" / "hangok" / "templom harang.wav"
galboro_path = BASE_DIR / "static" / "hangok" / "galboro.wav"
zaj_path = BASE_DIR / "static" / "hangok" / "zaj.wav"

# 🎼 Kotta adatok
kotta_adatok = {
    "Mantra": [],
    "Jegyura": [],
    "Nakshatra": [],
    "Nakshatra ura": [],
    "Pada": [],
    "Tithi": [],  # ← ez hiányzott
}

savsorrend = ["Mantra", "Jegyura", "Nakshatra", "Nakshatra ura", "Pada", "Tithi"]


# 💾 PDF mentés
def save_kotta_pdf(kotta_adatok, vezetek_nev, kereszt_nev):
    pdf_filename = f"{vezetek_nev.lower()}_{kereszt_nev.lower()}_kotta_output.pdf"
    pdf_path = os.path.join("static", "kottak", pdf_filename)
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)

    with PdfPages(pdf_path) as pdf:
        fig, ax = plt.subplots(figsize=(11.69, 8.27))
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 5)

        for i, sav in enumerate(savsorrend):
            y = 5 - i - 0.5
            for line in range(5):
                ax.hlines(y - 0.2 + line * 0.1, 0, 10, colors="black", linewidth=0.5)
            ax.text(-0.3, y, sav, fontsize=12, fontweight="bold", va="center")

            for x, freq, nev in kotta_adatok.get(sav, []):
                ax.plot(x, y + 0.05, "ko")
                ax.text(x, y + 0.2, f"{nev}\n{freq}Hz", ha="center", fontsize=8)

        ax.set_xticks(range(11))
        ax.set_xticklabels([f"{i}s" for i in range(11)])
        ax.set_yticks([])
        ax.set_title(
            "Szonifikált horoszkóp - Zenei kottázat",
            fontsize=14,
            fontweight="bold",
        )
        ax.axis("off")

        pdf.savefig(fig)
        plt.close()

    print(f"PDF kotta mentve: {pdf_path}")
    print(json.dumps(kotta_adatok, indent=2))


# 💾 MusicXML mentés
def save_kotta_musicxml(kotta_adatok, vezetek_nev, kereszt_nev, freq_to_pitch):
    score = stream.Score()
    score.metadata = metadata.Metadata()
    score.metadata.title = "Szonifikált horoszkóp"
    score.metadata.composer = f"{vezetek_nev} {kereszt_nev}"

    for sav in kotta_adatok:
        part = stream.Part()
        part.id = sav
        part.partName = sav

        for _, freq, nev in kotta_adatok[sav]:
            n = freq_to_pitch(freq)
            n.quarterLength = 1
            n.lyric = nev
            part.append(n)

        score.append(part)

    filename = f"{vezetek_nev.lower()}_{kereszt_nev.lower()}_kotta_output.musicxml"
    save_dir = os.path.join("static", "kottak")
    os.makedirs(save_dir, exist_ok=True)
    score.write("musicxml", fp=os.path.join(save_dir, filename))
    print(f"MusicXML kotta mentve: {filename}")

def collect_first_layer(planet_positions):
    segments = []
    kotta_adatok["Mantra"] = []
    current_time = 0.0
    for planet, data in planet_positions.items():
        deg = data["longitude"] % 360
        sign = int(deg // 30) + 1
        if sign not in jegy_uralkodok:
            continue
        _, freq, mantra_name = mantra_map[sign]
        mantra_path = os.path.join(mantra_dir, f"{mantra_name}.wav")
        if not os.path.exists(mantra_path):
            continue
        y, sr = librosa.load(mantra_path, sr=None)
        duration = 3.0
        shifted = pitch_shift_to_hz(y, sr, freq)
        target_duration = 3.0  # másodperc
        current_duration = len(shifted) / sr
        if current_duration < target_duration:
            rate = current_duration / target_duration
            shifted = librosa.effects.time_stretch(shifted, rate)

        segments.append(shifted)
        kotta_adatok["Mantra"].append((current_time, freq, mantra_name))
        current_time += duration
    return segments, sr

def collect_second_layer(planet_positions):
    segments = []
    kotta_adatok["Jegyura"] = []
    current_time = 0.0
    for jegy in range(1, 13):
        uralkodo, freq = jegy_uralkodok[jegy]
        bolygo_deg = planet_positions.get(uralkodo, {}).get("longitude", None)
        if bolygo_deg is None:
            continue
        scaled = scale_pitch(y, orig_freq=440, target_freq=freq, sr=sr)
        duration = len(scaled) / sr
        segments.append(scaled)
        kotta_adatok["Jegyura"].append((current_time, freq, uralkodo))
        current_time += duration
    return segments, sr

def collect_third_layer(planet_positions, ayanamsa):
    segments = []
    kotta_adatok["Nakshatra"] = []
    current_time = 0.0
    for bolygo in bolygo_nakshatra_map:
        if bolygo not in planet_positions:
            continue
        longitude = planet_positions[bolygo]['longitude']
        nakshatra, _ = calculate_nakshatra(longitude, ayanamsa, nakshatras)
        if nakshatra in bolygo_nakshatra_map[bolygo]:
            scaled = scale_pitch(harang_y, orig_freq=440, target_freq=528, sr=harang_sr)
            duration = len(scaled) / harang_sr
            segments.append(scaled)
            kotta_adatok["Nakshatra"].append((current_time, 528, bolygo))
            current_time += duration
    return segments, harang_sr

def collect_fourth_layer(planet_positions, ayanamsa):
    segments = []
    kotta_adatok["Tithi"] = []
    current_time = 0.0
    for planet, data in planet_positions.items():
        lon = data['longitude']
        nakshatra, pada = calculate_nakshatra(lon, ayanamsa, nakshatras)
        freq = full_pada_table.get(pada, 440)
        scaled = scale_pitch(y, orig_freq=440, target_freq=freq, sr=sr)
        duration = len(scaled) / sr
        segments.append(scaled)
        kotta_adatok["Tithi"].append((current_time, freq, f"{planet}-{nakshatra}-p{pada}"))
        current_time += duration
    return segments, sr

def collect_fifth_layer(planet_positions):
    segments = []
    kotta_adatok["Pada"] = []
    current_time = 0.0
    asc_deg = planet_positions['ASC']['longitude'] % 360
    asc_sign = int(asc_deg // 30) + 1
    for jegy in range(1, 13):
        uralkodo, freq = jegy_uralkodok[jegy]
        if uralkodo not in planet_positions:
            continue
        bolygo_deg = planet_positions[uralkodo]['longitude'] % 360
        bolygo_sign = int(bolygo_deg // 30) + 1
        haz_pozicio = (bolygo_sign - asc_sign + 12) % 12 + 1
        scaled = scale_pitch(y, orig_freq=440, target_freq=freq, sr=sr)
        duration = len(scaled) / sr
        segments.append(scaled)
        kotta_adatok["Pada"].append((current_time, freq, f"{uralkodo}-H{haz_pozicio}"))
        current_time += duration
    return segments, sr

# 🔊 Rétegek keverése
def mix_layers(layers):
    all_segments = []
    for seg_list in layers:
        all_segments.extend(seg_list)

    max_len = max(len(seg) for seg in all_segments)
    padded_segments = [
        np.pad(seg, (0, max_len - len(seg)), mode="constant") for seg in all_segments
    ]
    mix = np.sum(padded_segments, axis=0)

    max_val = np.max(np.abs(mix))
    if max_val > 0:
        mix = mix / max_val

    return mix


def mix_layers_with_timing(kotta_adatok, sr):
    all_tracks = []
    max_len = 0

    for sav in kotta_adatok:
        for start_time, freq, _ in kotta_adatok[sav]:
            y, sr_sample = get_base_sample_for_sav(sav)
            shifted = pitch_shift_to_hz(y, sr_sample, freq)

            start_index = int(start_time * sr)
            padded = np.pad(shifted, (start_index, 0), mode="constant")
            all_tracks.append(padded)
            if len(padded) > max_len:
                max_len = len(padded)

    padded_tracks = [
        np.pad(track, (0, max_len - len(track)), mode="constant")
        for track in all_tracks
    ]
    mix = np.sum(padded_tracks, axis=0)

    max_val = np.max(np.abs(mix))
    if max_val > 0:
        mix = mix / max_val

    return mix


# 🎵 Alapminták
def get_base_sample_for_sav(sav):
    if sav == "Mantra":
        y, sr = librosa.load(mantra_dir / "om.wav", sr=None)
    elif sav == "Jegyura":
        y, sr = librosa.load(ambiance_path, sr=None)
    elif sav == "Nakshatra":
        y, sr = librosa.load(harang_path, sr=None)
    elif sav == "Nakshatra ura":
        y, sr = librosa.load(galboro_path, sr=None)
    elif sav == "Pada":
        y, sr = librosa.load(zaj_path, sr=None)
    else:
        raise ValueError(f"Ismeretlen sáv: {sav}")
    return y, sr


def play_all_layers(planet_data):
    global is_playing
    is_playing = True

    # ⏳ Pendulum idő UTC-ben
    now = pendulum.now("UTC")
    jd_ut = swe.julday(
        now.year,
        now.month,
        now.day,
        now.hour + now.minute / 60.0 + now.second / 3600.0,
    )
    aya_val = get_ayanamsa(jd_ut)

    # 1. rész: 1 + 2
    s1, sr1 = collect_first_layer(planet_data)
    s2, _ = collect_second_layer(planet_data)
    sd.play(np.concatenate(s1 + s2), samplerate=sr1)
    sd.wait()
    if not is_playing:
        return

    # 2. rész: 1 + 3 + 4
    s1, sr1 = collect_first_layer(planet_data)
    s3, _ = collect_third_layer(planet_data, aya_val)
    s4, _ = collect_fourth_layer(planet_data, aya_val)
    sd.play(np.concatenate(s1 + s3 + s4), samplerate=sr1)
    sd.wait()
    if not is_playing:
        return

    # 3. rész: 1 + 5
    s1, sr1 = collect_first_layer(planet_data)
    s5, _ = collect_fifth_layer(planet_data)
    sd.play(np.concatenate(s1 + s5), samplerate=sr1)
    sd.wait()


# 💾 Egységesített save_combined_wave()
def save_combined_wave(planet_data, selected_varga):
    global aktualis_vezeteknev, aktualis_keresztnev

    # ⏳ Pendulum idő UTC-ben
    utc_dt = pendulum.now("UTC")
    jd_ut = swe.julday(
        utc_dt.year,
        utc_dt.month,
        utc_dt.day,
        utc_dt.hour + utc_dt.minute / 60.0 + utc_dt.second / 3600.0,
    )
    ayanamsa = swe.get_ayanamsa_ut(jd_ut)

    # 🎶 Rétegek gyűjtése
    s1, sr1 = collect_first_layer(planet_data)
    s2, _ = collect_second_layer(planet_data)
    s3, _ = collect_third_layer(planet_data, ayanamsa)
    s4, _ = collect_fourth_layer(planet_data, ayanamsa)
    s5, _ = collect_fifth_layer(planet_data)

    full_wave = np.concatenate(s1 + s2 + s1 + s3 + s4 + s1 + s5)
    filename = os.path.join(
        MENTES_DIR,
        f"{aktualis_vezeteknev.lower()}_{aktualis_keresztnev.lower()}_{selected_varga.lower()}.wav",
    )
    sf.write(filename, full_wave, sr1)
    print(f"Mentve: {filename}")


# 🎼 Hangmagasság konverzió
def freq_to_pitch(freq):
    A4 = 440
    semitone_offset = 12 * np.log2(freq / A4)
    midi_number = int(round(69 + semitone_offset))
    return note.Note(midi_number)
def freq_to_pitch(freq):
    p = note.Note()
    p.pitch.frequency = freq
    return p


# 🎚 Hangmagasság váltás
def pitch_shift_to_hz(y, sr, target_freq, base_freq=440):
    """Eltolja a hangmintát úgy, hogy a target_freq-hez igazodjon."""
    n_steps = 12 * np.log2(target_freq / base_freq)
    return librosa.effects.pitch_shift(y, sr=sr, n_steps=n_steps)


def scale_pitch(y, sr, orig_freq, target_freq):
    """Wrapper a pitch shift-hez, orig_freq → target_freq"""
    n_steps = 12 * np.log2(target_freq / orig_freq)
    return librosa.effects.pitch_shift(y, sr=sr, n_steps=n_steps)


# ... (collect_xxx rétegek, változatlanok) ...


# 📦 Összes réteg gyűjtése
def collect_all_layers(planet_data, ayanamsa):
    layers = []
    s1, sr = collect_first_layer(planet_data)
    layers.append(s1)
    s2, _ = collect_second_layer(planet_data)
    layers.append(s2)
    s3, _ = collect_third_layer(planet_data, ayanamsa)
    layers.append(s3)
    s4, _ = collect_fourth_layer(planet_data, ayanamsa)
    layers.append(s4)
    s5, _ = collect_fifth_layer(planet_data)
    layers.append(s5)
    return layers, sr

import numpy as np

def synthesize_frequencies(freqs, duration=2.0, sr=44100):
    """
    Egyszerű szinusz alapú hanggenerálás több frekvenciára.
    - freqs: lista Hz értékekkel
    - duration: hossz másodpercben
    - sr: mintavételi frekvencia
    """
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    mix = np.zeros_like(t)

    for f in freqs:
        wave = np.sin(2 * np.pi * f * t)
        mix += wave

    # Normalizálás
    mix /= len(freqs)
    return mix.astype(np.float32), sr
def generate_music(chart_data, export_audio, keres_frekvencia_excelbol):
    planet_data = chart_data["planet_data"]
    varga_nev = chart_data.get("varga_nev", "D1")
    name = chart_data.get("keresztnev", "ismeretlen")

    freqs = []
    for planet, data in planet_data.items():
        jegy = int(data["longitude"] // 30) + 1
        haz = data.get("house", 1)
        nakshatra = data.get("nakshatra", "")
        ura = data.get("nakshatra_ura", "")
        pada = data.get("pada", 1)

        freq = keres_frekvencia_excelbol(planet, jegy, haz, nakshatra, ura, pada)
        if freq:
            freqs.append(freq)

    if not freqs:
        print("⚠️ Nincs elegendő frekvenciaadat a zenéhez.")
        return

    # 🎼 Hangminták generálása
    mix, sr = synthesize_frequencies(freqs)

    # 💾 Mentés
    export_audio(mix, sr, varga_nev, name, varga_nev)
    print(f"🎵 Zene generálva: {name}_{varga_nev}_combined.wav")
    n = freq_to_pitch(440)
    print(n.nameWithOctave)  # A4
    print(n.pitch.frequency)  # 440.0

if __name__ == "__main__":
    print("Audio kotta modul elindult.")
