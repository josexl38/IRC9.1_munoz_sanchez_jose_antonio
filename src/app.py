from flask import Flask, render_template
import os

# Variables de entorno
PORT = int(os.getenv("APP_PORT", 8080))
DEBUG = os.getenv("APP_DEBUG", "true").lower() == "true"

# Instancia de Flask
app = Flask(__name__)

# Ruta principal
@app.route('/')
def home():
    return render_template('index.html',
                         version=os.getenv('APP_VERSION', '1.0.0'))

# Ruta about
@app.route('/about')
def about():
    return "<h1>Acerca de esta aplicación</h1><p>Esta app está hecha con Flask y Docker.</p>"

# Ruta de salud
@app.route('/health')
def health():
    return {'status': 'healthy', 'version': os.getenv('APP_VERSION', '1.0.0')}

# Arranque
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=PORT, debug=DEBUG)

