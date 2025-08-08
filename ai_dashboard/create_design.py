import json
import os
import random
from datetime import datetime
from generate_ui import generate_ui_from_design

# Sadece açık renk paletleri
COLOR_PALETTES = [
    {"background": "#ffffff", "color": "#222222"},
    {"background": "#f5f5f5", "color": "#222222"},
    {"background": "#fafafa", "color": "#111111"},
]

TITLES = [
    "Otomatik Tasarım",
    "Modern Panel",
    "Yaratıcı Dashboard"
]

HEADERS = [
    "Hoş Geldiniz!",
    "Yeni Arayüz Hazır",
    "AI Tarafından Üretildi"
]

DESCRIPTIONS = [
    "Bu panel yapay zeka tarafından oluşturuldu.",
    "Her çalıştırmada farklı bir tema önerisi gelir.",
    "Tamamen otomatik bir panel deneyimi!"
]

CARDS = [
    ("Motivasyon", "Bugün öğrenmek için iyi bir gün!"),
    ("Rastgele Not", "Kodlama bir sanattır."),
    ("Bugünün İpucu", "Kreatif düşün ve farklı şeyler dene."),
    ("Yeni Özellik", "Bu kart AI tarafından oluşturuldu.")
]

BUTTONS = [
    {"text": "Raporları Gör", "action": "#"},
    {"text": "Kaydet", "action": "#"}
]

COUNTER_FILE = "data/design_counter.txt"

def get_next_design_name():
    os.makedirs("data", exist_ok=True)
    count = 1
    if os.path.exists(COUNTER_FILE):
        with open(COUNTER_FILE, "r", encoding="utf-8") as f:
            try:
                count = int(f.read().strip()) + 1
            except:
                count = 1
    with open(COUNTER_FILE, "w", encoding="utf-8") as f:
        f.write(str(count))
    return f"tasarim-{count}.json"

def create_design_json():
    """Yeni tasarımı oluştur ve JSON+HTML kaydet."""
    palette = random.choice(COLOR_PALETTES)
    selected_cards = random.sample(CARDS, 3)
    selected_buttons = random.sample(BUTTONS, 2)

    design = {
        "title": random.choice(TITLES),
        "header": random.choice(HEADERS),
        "description": f"{random.choice(DESCRIPTIONS)} ({datetime.now().strftime('%H:%M:%S')})",
        "background": palette["background"],
        "color": palette["color"],
        "cards": [{"title": t, "content": c} for t, c in selected_cards],
        "buttons": selected_buttons
    }

    # Dosya ismi
    file_name = get_next_design_name()
    file_path = os.path.join("data", file_name)

    # JSON kaydet
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(design, f, indent=2, ensure_ascii=False)

    # latest.txt güncelle
    with open("data/latest.txt", "w", encoding="utf-8") as f:
        f.write(file_name)

    print(f"Yeni tasarım dosyası: {file_path}")

    # HTML/CSS üret
    generate_ui_from_design(file_path)

if __name__ == "__main__":
    create_design_json()
