import os
import json
import random
from transformers import pipeline

MODEL_PATH = "gpt2-soru-model/final_model"
OUTPUT_FILE = "data/design.json"

def generate_random_design():
    print("--- 🤖 Yapay Zeka Tasarımcı Başlatılıyor ---")
    try:
        generator = pipeline('text-generation', model=MODEL_PATH)
        print("✅ Model başarıyla yüklendi.")
    except Exception as e:
        print(f"❌ HATA: Model yüklenirken bir sorun oluştu: {e}")
        return

    prompts = [
        '{"title": "Uzay Keşfi Paneli", "header": "Galaksi Raporları", "style": {"background": "#0a192f", "color": "#ccd6f6"}, "components": [',
        '{"title": "Doğa Yürüyüşü Uygulaması", "header": "Patika Notları", "style": {"background": "#f0fff0", "color": "#2e8b57"}, "components": [',
        '{"title": "Müzik Festivali Sayfası", "header": "Sahne Programı", "style": {"background": "#121212", "color": "#1DB954"}, "components": [',
    ]
    selected_prompt = random.choice(prompts)
    print(f"Seçilen Prompt: {selected_prompt[:50]}...")

    try:
        generated_text = generator(selected_prompt, max_new_tokens=200)[0]['generated_text']
        print("\nÜretilen Ham Metin:", generated_text)
        
        # Üretilen metni geçerli bir JSON'a dönüştürmeye çalış
        # En basit yöntem, açılan son '[''den sonrasını alıp kapatmaktır.
        try:
            start_index = generated_text.rfind('[')
            json_body = generated_text[start_index:]
            # Açık kalan parantezleri kapatmaya çalış
            if json_body.count('[') > json_body.count(']'): json_body += ']'
            if json_body.count('{') > json_body.count('}'): json_body += '}'
            # Başlangıç prompt'unu alıp sonuna ekle
            final_json_str = selected_prompt + json_body.strip("[]") + ']}'
            design_data = json.loads(final_json_str)
            print("\n✅ Geçerli bir JSON tasarımı üretildi!")
        except (json.JSONDecodeError, IndexError):
            print("❌ UYARI: AI geçerli bir JSON üretemedi. Varsayılan tasarım kullanılıyor.")
            design_data = { "title": "Hata", "header": "Tasarım Üretilemedi", "components": [{"type": "card", "title": "Hata", "value": "Model geçerli bir JSON üretemedi."}] }

        os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(design_data, f, ensure_ascii=False, indent=4)
            
        print(f"🎯 Yeni tasarım '{OUTPUT_FILE}' dosyasına kaydedildi.")

    except Exception as e:
        print(f"❌ HATA: Tasarım üretimi sırasında bir sorun oluştu: {e}")

if __name__ == "__main__":
    generate_random_design()