from flask import Flask, render_template, request, g, make_response, redirect, url_for
import os
import random

app = Flask(__name__)
app.config.from_pyfile('config.py')

# Tema yükleme fonksiyonu
def load_theme(theme_name='default'):
    theme_path = os.path.join('themes', theme_name)
    return {
        'static': f'static/themes/{theme_name}',
        'template': f'themes/{theme_name}'
    }


def get_recent_activities():
    """Return a list of recent activities for the dashboard."""
    return []

# Tema seçimi middleware'i
@app.before_request
def set_theme():
    themes = [
        d for d in os.listdir("static/themes")
        if os.path.isdir(os.path.join("static/themes", d))
    ]
    selected_theme = random.choice(themes)
    g.theme = selected_theme
    g.theme_config = load_theme(selected_theme)

# Dinamik template loader
@app.context_processor
def inject_theme():
    return dict(theme=g.theme_config)

@app.route("/")
def index():
    return redirect(url_for("dashboard"))

@app.route('/change_theme/<theme_name>')
def change_theme(theme_name):
    response = make_response(redirect(request.referrer or url_for('index')))
    response.set_cookie('theme', theme_name, max_age=30*24*60*60)
    return response

@app.route('/dashboard')
def dashboard():
    theme = g.theme
    if theme == 'admin':
        return render_template(f'themes/{theme}/dashboard.html', 
                           activities=get_recent_activities())
    else:
        return render_template(f'themes/{theme}/dashboard.html')
