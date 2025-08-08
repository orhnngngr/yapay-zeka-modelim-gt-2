# ai_designer.py - OpenAI GPT ile Dinamik Arayüz Tasarımı Üreten Nihai Betik

import os
import sys
import json
import io
import argparse
from datetime import datetime
import openai

# ==============================================================================
# 1. ORTAM AYARLARI VE GÜVENLİK KONTROLÜ
# ==============================================================================

# Windows terminalinde Unicode karakter (örn: emoji) hatalarını önler
# Bu, betiğin farklı ortamlarda sorunsuz çalışmasını sağlar.
try:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
except (TypeError, ValueError):
    # Bu blok, betik etkileşimli olmayan bir ortamda çalıştırıldığında
    # oluşabilecek hataları engeller (örn: bir web sunucusu içinden).
    pass

# 'generate_ui' modülünün bulunabilmesi için projenin kök dizinini yola ekle
# Bu dosya "ai_dashboard" klasöründe yer aldığından, kök dizine erişmek için iki seviye yukarı çıkılır.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

try:
    from generate_ui import generate_ui_from_design
except ImportError:
    print("❌ HATA: 'generate_ui.py' dosyası bulunamadı.")
    print("Lütfen bu betiğin ve 'generate_ui.py'nin aynı ana klasörde olduğundan emin olun.")
    sys.exit(1)

# OpenAI API anahtarını ortam değişkeninden güvenli bir şekilde oku
if "OPENAI_API_KEY" not in os.environ:
    print("❌ KRİTİK HATA: OPENAI_API_KEY ortam değişkeni tanımlı değil!")
    print("Lütfen terminalde 'setx OPENAI_API_KEY \"sk-.....\"' komutu ile anahtarınızı ayarlayın.")
    print("Komutu uyguladıktan sonra terminali yeniden başlatmanız gerekebilir.")
    sys.exit(1)
openai.api_key = os.environ["OPENAI_API_KEY"]

# ==============================================================================
# 2. YARDIMCI FONKSİYONLAR
# ==============================================================================

def save_design_to_file(design_data: dict, base_dir: str = "data") -> str:
    """Verilen tasarım sözlüğünü sıralı bir JSON dosyasına kaydeder."""
    os.makedirs(base_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    file_name = f"tasarim-ai-{timestamp}.json"
    file_path = os.path.join(base_dir, file_name)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(design_data, f, indent=2, ensure_ascii=False)

    # En son üretilen dosyanın adını 'latest.txt'ye yaz
    latest_file_path = os.path.join(base_dir, "latest.txt")
    with open(latest_file_path, "w", encoding="utf-8") as f:
        f.write(file_name)

    print(f"🎨 Yeni AI tasarım dosyası kaydedildi: {file_path}")
    return file_path

def clean_ai_response(raw_response: str) -> dict:
    """AI'dan gelen ham metni temizleyip geçerli bir JSON sözlüğüne dönüştürür."""
    print("AI yanıtı temizleniyor ve doğrulanıyor...")
    try:
        # AI'nın sıkça kullandığı ```json ... ``` markdown bloğunu ara
        if "```json" in raw_response:
            json_str = raw_response.split("```json")[1].split("```")[0].strip()
        else: # Değilse, ilk ve son süslü parantezi bul
            start = raw_response.find("{")
            end = raw_response.rfind("}") + 1
            if start == -1 or end == 0:
                raise ValueError("Yanıt içinde JSON yapısı bulunamadı.")
            json_str = raw_response[start:end]
        
        return json.loads(json_str)
    except Exception as e:
        raise ValueError(f"AI yanıtı geçerli bir JSON formatında değil: {e}\n---\nHam Yanıt:\n{raw_response}\n---")

# ==============================================================================
# 3. ANA İŞ MANTIĞI
# ==============================================================================

def generate_and_build_design(prompt: str, model_name: str):
    """
    OpenAI API'sini kullanarak bir tasarım üretir, kaydeder ve bu tasarımdan
    HTML/CSS arayüzünü oluşturur.
    """
    print("🤖 OpenAI API'ye istek gönderiliyor...")
    try:
        client = openai.OpenAI() # En güncel API kullanımı için client oluştur
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800,
            temperature=0.7
        )
        raw_content = response.choices[0].message.content
        print("✅ Yanıt alındı.")
        
        design = clean_ai_response(raw_content)
        design_file_path = save_design_to_file(design)

        generate_ui_from_design(
            design_file_path=design_file_path,
            output_html_path="templates/generated_ui.html",
            output_css_path="static/css/generated_ui.css"
        )
        print("🚀 Yeni UI başarıyla oluşturuldu ve sunulmaya hazır.")

    except openai.APIError as e:
        print(f"❌ OpenAI API Hatası: {e}")
    except Exception as e:
        print(f"❌ Ana süreçte bir hata oluştu: {e}")

# ==============================================================================
# 4. BETİĞİN GİRİŞ NOKTASI VE KOMUT SATIRI ARGÜMANLARI
# ==============================================================================

def main():
    """Komut satırı argümanlarını yönetir ve ana işlevselliği başlatır."""
    
    # Varsayılan prompt metnini daha temiz bir şekilde tanımla
    default_prompt = (
        "Modern, minimalist ve profesyonel bir web dashboard arayüzü için JSON formatında bir tema üret. "
        "JSON formatı şu şekilde olmalı: "
        '{"title": "Sayfa Başlığı", "header": "Ana Başlık", "description": "Kısa bir açıklama", '
        '"style": {"background": "#rrggbb", "color": "#rrggbb"}, "components": ['
        '{"type": "card", "title": "Kart Başlığı 1", "value": "İçerik 1"}, '
        '{"type": "chart", "title": "Grafik Başlığı", "data": {"type": "bar", "label": "Veri", "labels": ["A", "B", "C"], "values": [10, 20, 15]}}, '
        '{"type": "button", "label": "Eylem Butonu"}'
        ']} '
        "Açık ve pastel tonlarda, okunabilir renkler kullan."
    )

    parser = argparse.ArgumentParser(description="OpenAI kullanarak dinamik web arayüz tasarımları üretir.")
    parser.add_argument("-p", "--prompt", type=str, default=default_prompt, help="Tasarım üretimi için AI'ya verilecek olan prompt metni.")
    parser.add_argument("-m", "--model", type=str, default="gpt-4o-mini", help="Kullanılacak OpenAI modelinin adı.")
    args = parser.parse_args()

    generate_and_build_design(prompt=args.prompt, model_name=args.model)

if __name__ == "__main__":
    main()