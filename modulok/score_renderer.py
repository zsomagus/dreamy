# modulok/score_renderer.py
import os
import matplotlib.pyplot as plt

def export_score_to_pdf_and_png(prompt_text, folder, base_name):
    """
    Létrehoz egy valódi kottalap stílusú dokumentumot (PDF és PNG) 
    zenei ötvonallal, violinkulccsal és az AI prompt szövegével.
    """
    png_path = os.path.join(folder, base_name + ".png")
    pdf_path = os.path.join(folder, base_name + ".pdf")
    
    # 1. Kottalap arányú vászon (A4-es álló formátumhoz hasonló: 8x11 hüvelyk)
    fig, ax = plt.subplots(figsize=(8, 11))
    fig.patch.set_facecolor('#ffffff')  # Klasszikus fehér papír háttér
    ax.set_facecolor('#ffffff')
    
    ax.axis('off')  # Matematikai tengelyek kikapcsolása
    
    # 2. Cím és fejléc
    ax.text(0.5, 0.95, "DREAM SONIC SCORE", 
            transform=ax.transAxes, color='#111111', 
            fontsize=18, fontweight='bold', ha='center')
    
    ax.text(0.5, 0.92, "✨ AI Music & Visual Prompt Sheet ✨", 
            transform=ax.transAxes, color='#555555', 
            fontsize=11, style='italic', ha='center', fontname='Segoe UI Symbol') # <-- fontname hozzáadva
            
    # 3. ZENEI ÖTVONAL RAJZOLÁSA (Kotta alap)
    y_lines = [0.80, 0.81, 0.82, 0.83, 0.84]
    for y in y_lines:
        ax.plot([0.1, 0.9], [y, y], color='black', linewidth=1.5, transform=ax.transAxes)
    
    # Kottavonal lezárások (ütemvonalak a két szélén)
    ax.plot([0.1, 0.1], [0.80, 0.84], color='black', linewidth=2, transform=ax.transAxes)
    ax.plot([0.9, 0.9], [0.80, 0.84], color='black', linewidth=2, transform=ax.transAxes)
    
    # VIOLINKULCS (G-kulcs) szimbólum kirajzolása a vonal elejére
    ax.text(0.12, 0.815, "𝄞", transform=ax.transAxes, color='black', 
            fontsize=45, ha='left', va='center', fontname='Segoe UI Symbol') # <-- fontname hozzáadva    
    # Egy kis dekoratív kezdő hangjegy a kottán
    ax.text(0.25, 0.817, "♩ ♪ ♫ ♩", transform=ax.transAxes, color='black', 
            fontsize=24, ha='left', va='center', fontname='Segoe UI Symbol') # <-- fontname hozzáadva    
    # Elválasztó dekorációs vonal a kotta és a szöveg között
    ax.text(0.5, 0.72, "✦ ────────────────────────────── ✦", 
            transform=ax.transAxes, color='#aaaaaa', fontsize=12, ha='center')

    # 4. AZ AI PROMPT SZÖVEG KIÍRÁSA A KOTTA ALÁ
    ax.text(0.1, 0.68, "📋 GENERATED AI PROMPT FOR GEMINI:", 
    transform=ax.transAxes,             
    fontsize=45, ha='left', va='center', fontname='Segoe UI Symbol')
    # A prompt szöveg soronkénti tördelése és formázása
    lines = prompt_text.split('\n')
    y_pos = 0.63  # Szöveg kezdőmagassága a kotta alatt
    
    for line in lines:
        line_str = line.strip()
        if not line_str:
            y_pos -= 0.02
            continue
            
        # Betűstílusok beállítása a tartalom szerint
        text_color = '#333333'
        font_weight = 'normal'
        font_size = 10
        
        if line_str.startswith("---") or line_str.endswith("---"):
            text_color = '#bf616a'  # Elegáns sötétvörös a szakaszcímeknek
            font_weight = 'bold'
            font_size = 11
        elif line_str.startswith("Dream description:") or line_str.startswith("Dream:"):
            text_color = '#2e3440'
            font_weight = 'bold'
        elif "INSTRUCTIONS" in line_str:
            text_color = '#d08770'
            font_weight = 'bold'
            
        # Szöveg kiírása (az automatikus wrap=True tördeli a sorokat)
        ax.text(0.1, y_pos, line_str, 
                transform=ax.transAxes, color=text_color, 
                fontsize=font_size, fontweight=font_weight, 
                va='top', ha='left', wrap=True)
        
        # Sormagasság léptetése lefelé
        if len(line_str) > 75:
            y_pos -= 0.05
        else:
            y_pos -= 0.03
            
    # 5. MENTÉS (PDF és PNG formátumban is)
    plt.savefig(pdf_path, bbox_inches='tight', facecolor=fig.get_facecolor(), dpi=150)
    plt.close()
    
    return pdf_path, png_path