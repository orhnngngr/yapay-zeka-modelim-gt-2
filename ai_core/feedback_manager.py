# feedback_manager.py
import json
import os
from datetime import datetime

FEEDBACK_FILE = "data/feedback_loop.json"

def save_feedback(feedback: dict):
    """Kullanıcı geri bildirimi kaydeder."""
    os.makedirs("data", exist_ok=True)

    history = []
    if os.path.exists(FEEDBACK_FILE):
        try:
            with open(FEEDBACK_FILE, "r", encoding="utf-8") as f:
                history = json.load(f)
        except Exception:
            history = []

    feedback_record = {
        "timestamp": datetime.now().isoformat(),
        **feedback
    }

    history.append(feedback_record)

    with open(FEEDBACK_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

    print(f"💾 Geri bildirim kaydedildi: {feedback_record}")


def get_feedback_history():
    """Tüm geri bildirim geçmişini döndürür."""
    if os.path.exists(FEEDBACK_FILE):
        with open(FEEDBACK_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []
