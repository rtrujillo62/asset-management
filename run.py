"""
Servidor de desarrollo local.
En producción Railway usa application.py con gunicorn (ver Procfile).
"""
import os
from dotenv import load_dotenv

load_dotenv()

from app import create_app

config_name = os.getenv('FLASK_ENV', 'development')
app = create_app(config_name)

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=(config_name == 'development'))
