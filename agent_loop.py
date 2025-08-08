import os
import time
import json
import random
from datetime import datetime
from ai_dashboard.create_design import create_design_json
from generate_ui import generate_ui_from_design
from ai_core.feedback_manager import get_feedback_history

DESIGN_FILE = "data/design.json"

def analyze_feedback():
    """
    Geri bildirimleri analiz eder.
    Olumsuz geri bildirimlerde, UI'de daha büyük değişiklikler yapılır.
    """
    history = get_feedback_history()
    if not history:
        return {}

    last = history[-1]
    print(f"🔍 Son geri bildirim: {last}")

    if not last.get("approved"):
        # Olumsuz geri bildirimde radikal değişiklik
        return {
            "force_new_palette": True,
            "force_new_layout": True,
            "more_cards": True
        }
    else:
        # Olumluysa küçük iyileştirme
        return {
            "refresh_ui": True
        }

def smart_modify_design():
    """
    design.json'u okur, geri bildirimlere göre değiştirir ve kaydeder.
    """
    if not os.path.exists(DESIGN_FILE):
        print("❌ design.json bulunamadı, sıfırdan oluşturuluyor...")
        create_design_json()
        return

    with open(DESIGN_FILE, "r", encoding="utf-8") as f:
        design = json.load(f)

    feedback = analyze_feedback()

    if feedback.get("force_new_palette"):
        palettes = [
            {"background": "#f4f4f4", "color": "#333"},
            {"background": "#101010", "color": "#f0f0f0"},
            {"background": "#ffffff", "color": "#111"},
            {"background": "#ececec", "color": "#222"}
        ]
        new_palette = random.choice(palettes)
        design["background"] = new_palette["background"]
        design["color"] = new_palette["color"]
        design["title"] = random.choice(["Yeni Nesil Panel", "Modern Dashboard", "AI Yeniden Tasarımı"])
        design["header"] = random.choice(["Merhaba! Yeniden Başladık", "Yeni Tasarım Hazır", "Kullanıcı Geri Bildirimiyle Geliştirildi"])
        print("🎨 Yeni renk paleti ve başlık seçildi.")

    if feedback.get("more_cards"):
        # Kart sayısını artırıyoruz
        extra_cards = [
            {"title": "Yeni Öneri", "content": "Bu yeni kart AI tarafından önerildi."},
            {"title": "İpucu", "content": "Daha açık renklerle tasarımı deniyoruz."}
        ]
        design["cards"].extend(random.sample(extra_cards, k=min(2, len(extra_cards))))
        print("🃏 Ekstra kartlar eklendi.")

    # Layout rastgele değiştirilebilir
    if feedback.get("force_new_layout"):
        layouts = ["grid", "list", "masonry"]
        design["layout"] = random.choice(layouts)
        print(f"📐 Layout tipi değiştirildi: {design['layout']}")

    # Dosyayı kaydet
    with open(DESIGN_FILE, "w", encoding="utf-8") as f:
        json.dump(design, f, indent=2, ensure_ascii=False)

    print(f"💾 Yeni design.json kaydedildi ({datetime.now().strftime('%H:%M:%S')})")

def update_design_based_on_feedback():
    """
    Geri bildirimleri değerlendirip UI'yi günceller.
    """
    print("🕵️  Geri bildirim analizi başlatıldı...")
    feedback = analyze_feedback()

    if feedback.get("force_new_palette") or feedback.get("force_new_layout"):
        smart_modify_design()
    else:
        # sadece refresh
        if os.path.exists(DESIGN_FILE):
            generate_ui_from_design(DESIGN_FILE)
            print("🔄 Mevcut tasarımdan UI yeniden üretildi.")

def agent_loop():
    """
    3 dakikada bir geri bildirim kontrolü ve UI güncelleme
    """
    print("🤖 Adaptif Agent Loop başlatıldı (3 dakikada bir). Ctrl+C ile çık.")
    while True:
        try:
            update_design_based_on_feedback()
            time.sleep(180)
        except KeyboardInterrupt:
            print("⏹ Agent loop durduruldu.")
            break
        except Exception as e:
            print(f"❌ Agent loop hatası: {e}")
            time.sleep(60)

if __name__ == "__main__":
    agent_loop()
