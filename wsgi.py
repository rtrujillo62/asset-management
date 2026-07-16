import os
from dotenv import load_dotenv

load_dotenv()

# Importar directamente de run.py
from run import app

if __name__ == "__main__":
    app.run()
