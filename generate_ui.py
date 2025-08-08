import json
import os
import time

def get_latest_design_file():
    latest_file = "data/latest.txt"
    if os.path.exists(latest_file):
        with open(latest_file, "r", encoding="utf-8") as f:
            name = f.read().strip()
        path = os.path.join("data", name)
        if os.path.exists(path):
            return path
    if os.path.exists("data/design.json"):
        return "data/design.json"
    raise FileNotFoundError("Hiçbir tasarım dosyası bulunamadı.")

def generate_ui_from_design(design_file_path=None, output_html_path="templates/generated_ui.html", output_css_path="static/css/generated_ui.css"):
    design_file = design_file_path or get_latest_design_file()

    with open(design_file, "r", encoding="utf-8") as f:
        design = json.load(f)

    os.makedirs(os.path.dirname(output_html_path), exist_ok=True)
    os.makedirs(os.path.dirname(output_css_path), exist_ok=True)

    html_path = output_html_path
    css_path = output_css_path

    # HTML
    css_version = int(time.time())
    html = f"""
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>{design.get("title","AI Panel")}</title>
    <link rel="stylesheet" href="/static/css/generated_ui.css?v={css_version}">
</head>
<body>
    <header>
        <h1>{design.get("header")}</h1>
        <p>{design.get("description")}</p>
    </header>
    <main>
        <section class="cards">
            {''.join([f'<div class="card"><h3>{c["title"]}</h3><p>{c["content"]}</p></div>' for c in design.get("cards", [])])}
        </section>
        <section class="buttons">
            {''.join([f'<button onclick="window.location=\'{b["action"]}\'">{b["text"]}</button>' for b in design.get("buttons", [])])}
        </section>

        <section class="feedback">
            <button onclick="sendFeedback(true)">👍 Beğendim</button>
            <button onclick="sendFeedback(false)">👎 Beğenmedim</button>
        </section>

        <section class="buttons">
            <button onclick="regenerateUI()">Yeniden Oluştur</button>
            <button onclick="window.location='/generated_ui'">Raporları Gör</button>
        </section>
    </main>

<script>
function regenerateUI() {{
    fetch('/api/regenerate_ui', {{method: 'POST'}})
        .then(r => r.json())
        .then(data => {{
            if (data.status === "ok") {{
                document.open();
                document.write(data.html);
                document.close();
            }} else {{
                alert("Hata: " + data.message);
            }}
        }})
}}
function sendFeedback(approved) {{
    fetch('/feedback', {{
        method: 'POST',
        headers: {{'Content-Type': 'application/json'}},
        body: JSON.stringify({{
            approved: approved,
            comments: approved ? "Beğendim" : "Beğenmedim"
        }})
    }})
    .then(r => r.json())
    .then(data => alert("Geri bildiriminiz kaydedildi!"));
}}
</script>
</body>
</html>
"""

    # CSS
    css = f"""
body {{
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 0;
    background: {design.get("background","#f4f4f4")};
    color: {design.get("color","#333")};
}}
header {{
    text-align: center;
    padding: 20px;
    background: white;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}}
.cards {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 20px;
    padding: 20px;
}}
.card {{
    background: white;
    padding: 15px;
    border-radius: 10px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.1);
}}
.buttons {{
    text-align: center;
    padding: 20px;
}}
button {{
    margin: 10px;
    padding: 10px 20px;
    font-size: 16px;
    cursor: pointer;
}}
.feedback {{
    text-align: center;
    margin-top: 30px;
}}
"""

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    with open(css_path, "w", encoding="utf-8") as f:
        f.write(css)

    print(f"✅ Yeni UI üretildi -> {html_path}")
