import os
from dotenv import load_dotenv

load_dotenv()

from app import create_app

if __name__ == '__main__':
    config_name = os.getenv('FLASK_ENV', 'development')
    app = create_app(config_name)
    
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=(config_name == 'development'))
