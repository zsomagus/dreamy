import numpy as np
import sounddevice as sd
from mido import Message, MidiFile, MidiTrack
from modulok import astro_core, audio_kotta_tools
from modulok.config import BASE_DIR  # noqa: F401
from music21 import note  # noqa: F401
import os
from dotenv import load_dotenv
import soundfile as sf  # a fájl elején

def write(filename, samplerate, data):
    sf.write(filename, data, samplerate)


hegedu_path = BASE_DIR / "static" / "hangok" / "hegedu.wav"
fuvola_path = BASE_DIR / "static" / "hangok" / "fuvola.wav"
bracsa_path = BASE_DIR / "static" / "hangok" / "bracsa.wav"
cseleszt_path = BASE_DIR / "static" / "hangok" / "cseleszt.wav"
csello_path = BASE_DIR / "static" / "hangok" / "csello.wav"


def save_midi_from_notes(notes, filename="output.mid", velocity=64, duration=480):
    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)

    for note in notes:
        track.append(Message("note_on", note=note, velocity=velocity, time=0))
        track.append(Message("note_off", note=note, velocity=velocity, time=duration))

    mid.save(filename)


# MIDI konverzió
def freq_to_midi(f):
    return int(round(69 + 12 * np.log2(f / 440)))


def midi_to_note_name(midi_num):

    n = note()
    return n.midi_to_note(midi_num)


def freqs_to_musicpy_notes(freq_list):
    return [midi_to_note_name(freq_to_midi(f)) for f in freq_list]


# Időalapú keverés kotta_adatok alapján
def mix_layers_with_timing(kotta_adatok, sr):
    all_tracks = []
    max_len = 0

    for sav, events in kotta_adatok.items():
        base_sample, base_sr = audio_kotta_tools.get_base_sample_for_sav(sav)
        for start_time, freq, nev in events:
            shifted = audio_kotta_tools.pitch_shift_to_hz(base_sample, base_sr, freq)
            start_index = int(start_time * sr)
            padded = np.pad(shifted, (start_index, 0), mode="constant")
            all_tracks.append(padded)
            if len(padded) > max_len:
                max_len = len(padded)

    # Azonos hosszra igazítás
    padded_tracks = [
        np.pad(track, (0, max_len - len(track)), mode="constant")
        for track in all_tracks
    ]

    # Összeadás és normalizálás
    mix = np.sum(padded_tracks, axis=0)
    max_val = np.max(np.abs(mix))
    if max_val > 0:
        mix = mix / max_val

    return mix


# Harmonizációs főfüggvény
def harmonize_two_people1(birth_data1, birth_data2):
    # 1. Pozíciók és frekvenciák
    pos1, aya1 = astro_core.compute_positions(birth_data1)
    pos2, aya2 = astro_core.compute_positions(birth_data2)

    freqs1 = astro_core.get_all_freqs(pos1, aya1)
    freqs2 = astro_core.get_all_freqs(pos2, aya2)

    # 2. Harmonizált frekvenciák
    harmonizalt_freqs = [(f1 + f2) / 2 for f1, f2 in zip(freqs1, freqs2)]

    # 3. MIDI mentés
    harmonia_notes = freqs_to_musicpy_notes(harmonizalt_freqs)
    # Ezt írd a harmonize_two_people1-ben:
    save_midi_from_notes(harmonia_notes, "harmonia_duett.mid")

    # 4. Rétegek legenerálása mindkét személyhez
    kotta_adatok = audio_kotta_tools.kotta_adatok.copy()
    audio_kotta_tools.collect_all_layers(pos1, aya1)
    audio_kotta_tools.collect_all_layers(pos2, aya2)

    # 5. Keverés időbélyegekkel
    sr = 44100
    zenekari_mix = mix_layers_with_timing(kotta_adatok, sr)

    # 6. Lejátszás és mentés
    sd.play(zenekari_mix, samplerate=sr)
    sd.wait()

    write("zenekari_duett.wav", sr, zenekari_mix)

    return harmonizalt_freqs, zenekari_mix, sr

    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)

    track.append(Message("note_on", note=60, velocity=64, time=0))
    track.append(Message("note_off", note=60, velocity=64, time=480))

    mid.save("output.mid")


load_dotenv()

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")


def compute_person_mix(birth_data):
    # 1) pozíciók
    positions, ayanamsa = astro_core.compute_positions(birth_data)
    # 2) 5 réteg audió
    layers, sr = audio_kotta_tools.collect_all_layers(positions, ayanamsa)
    # 3) keverés
    mix = audio_kotta_tools.mix_layers(layers, sr)
    send_usage_email(
        subject="Horoszkóp rajzolva", body=f"Horoszkóp generálva: {birth_data['name']}"
    )
    return mix, sr


def harmonize_two_people(bd1, bd2):
    # Két személy végső mixének „zenekari” összekeverése
    mix1, sr1 = compute_person_mix(bd1)
    mix2, sr2 = compute_person_mix(bd2)
    assert sr1 == sr2
    import numpy as np

    L = max(len(mix1), len(mix2))
    a = np.pad(mix1, (0, L - len(mix1)))
    b = np.pad(mix2, (0, L - len(mix2)))
    harmonized = 0.5 * (a + b)
    send_usage_email(
        subject="Harmonizáció használva",
        body=f"Két személy harmonizációja lefutott:\n- {bd1['name']}\n- {bd2['name']}",
    )
    return harmonized, sr1


