import os
import json
import shutil
import time
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from generate_ui import generate_ui_from_design

# --- 1. Klasör yapısı tanımı ---
def get_folder_structure():
    return {
        "static": ["css", "js", "images"],
        "templates": [],
        "model": [],
        "data": [],
        "logs": [],
        "ai_dashboard": ["components", "assets"]
    }

# --- 2. Dosya türlerine göre yönlendirme ---
FILE_ROUTING = {
    ".html": "templates",
    ".css": "static/css",
    ".js": "static/js",
    ".png": "static/images",
    ".jpg": "static/images",
    ".jpeg": "static/images",
    ".json": "data",
    ".py": "ai_dashboard",
    ".pkl": "model"
}

# --- 3. Varsayılan dosyalar ---
def get_default_files():
    return {
        "templates/index.html": (
            "<!DOCTYPE html>\n<html lang='tr'><head><meta charset='UTF-8'>"
            "<title>AI Dashboard</title></head><body><h1>Hoş geldiniz</h1></body></html>"
        ),
        "static/css/style.css": "body { font-family: Arial, sans-serif; }",
        "static/js/app.js": "console.log('AI Dashboard başlatıldı');",
        "app.py": (
            "from flask import Flask, render_template\n"
            "app = Flask(__name__)\n\n"
            "@app.route('/')\n"
            "def home():\n"
            "    return render_template('index.html')\n\n"
            "if __name__ == '__main__':\n"
            "    app.run(debug=True)"
        )
    }

# --- 4. Klasörleri oluştur ---
def create_folders(base_path="."):
    created = []
    for folder, subfolders in get_folder_structure().items():
        full = os.path.join(base_path, folder)
        os.makedirs(full, exist_ok=True)
        created.append(full)
        for sub in subfolders:
            subpath = os.path.join(full, sub)
            os.makedirs(subpath, exist_ok=True)
            created.append(subpath)
    return created

# --- 5. Dosyaları oluştur ---
def create_files():
    files = get_default_files()
    created_files = []
    for path, content in files.items():
        folder = os.path.dirname(path)
        if folder and folder.strip():
            os.makedirs(folder, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        created_files.append(path)
    return created_files

# --- 6. Dosya taşıma ---
def auto_organize_file(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    target = FILE_ROUTING.get(ext)
    if not target:
        return None
    os.makedirs(target, exist_ok=True)
    filename = os.path.basename(file_path)
    new_path = os.path.join(target, filename)
    if os.path.abspath(file_path) != os.path.abspath(new_path):
        shutil.move(file_path, new_path)
    return new_path

# --- 7. Log tutma ---
def log_creation(paths, log_dir="logs"):
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "folder_structure.json")
    with open(log_file, "w", encoding="utf-8") as f:
        json.dump({"timestamp": datetime.now().isoformat(), "created": paths}, f, indent=2, ensure_ascii=False)

# --- 8. İzleme event handler ---
class NewFileHandler(FileSystemEventHandler):
    def process_design_file(self, file_path):
        """design.json dosyasını yakalayıp UI üretir"""
        if file_path.endswith("design.json"):
            print("🎨 Yeni tasarım dosyası algılandı, arayüz oluşturuluyor...")
            generate_ui_from_design(design_file_path=file_path)

    def on_created(self, event):
        if not event.is_directory:
            moved_path = auto_organize_file(event.src_path)
            if moved_path:
                print(f"📁 Yeni dosya taşındı: {event.src_path} ➜ {moved_path}")
                self.process_design_file(moved_path)
            else:
                self.process_design_file(event.src_path)

    def on_modified(self, event):
        if not event.is_directory:
            # Tasarım dosyası güncellenince de çalışsın
            self.process_design_file(event.src_path)


# --- 9. Çalıştır ---
if __name__ == "__main__":
    all_paths = create_folders() + create_files()
    log_creation(all_paths)
    print("📦 Klasörler ve dosyalar hazırlandı.")

    observer = Observer()
    observer.schedule(NewFileHandler(), path=".", recursive=True)
    observer.start()
    print("👁 İzleme başlatıldı...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("🛑 İzleme durdu.")
    observer.join()

