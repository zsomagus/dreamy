# modulok/music_prompt.py
from  modulok import prashna_core
# music_prompt.py

# modulok/music_prompt.py

def build_music_prompt(text, mood, keywords, symbols):
    prompt = (
        f"Create an instrumental ambient chillout track and a matching visual artwork inspired by this dream.\n\n"
        f"--- DREAM DETAILS ---\n"
        f"Dream description: {text}\n"
        f"Mood/Atmosphere: {mood}\n"
        f"Keywords: {keywords}\n"
    )
    if symbols:
        prompt += f"Identified Symbols: {', '.join(symbols)}\n"

    prompt += (
        "\n--- AI INSTRUCTIONS ---\n"
        "1. MUSIC GENERATION: The music should be atmospheric, soft, flowing, and meditative. Use warm ambient pads, "
        "airy textures, subtle organic rhythms, and emotional depth reflecting the mood.\n"
        "2. IMAGE GENERATION: Create a highly detailed, surreal, dreamlike digital art or painting that captures "
        "the essence, colors, and key symbols of this dream."
    )
    return prompt