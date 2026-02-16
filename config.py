import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # =========================
    # Telegram Bot Credentials
    # =========================
    BOT_TOKEN = os.getenv("BOT_TOKEN")

    # =========================
    # Telegram API (User Session)
    # =========================
    API_ID = int(os.getenv("API_ID", 0))
    API_HASH = os.getenv("API_HASH")

    # =========================
    # MongoDB
    # =========================
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    DB_NAME = os.getenv("DB_NAME", "wordle_solver")

    # =========================
    # Solver Settings
    # =========================
    START_WORD = os.getenv("START_WORD", "stone")
    WORDLIST_FILE = os.getenv("WORDLIST_FILE", "data/commonWords.json")
    GUESS_DELAY = float(os.getenv("GUESS_DELAY", 1.9))
    AUTO_LOOP = os.getenv("AUTO_LOOP", "True") == "True"

    @staticmethod
    def validate():
        if not Config.BOT_TOKEN:
            raise ValueError("BOT_TOKEN is missing in .env")
        if not Config.API_ID:
            raise ValueError("API_ID is missing in .env")
        if not Config.API_HASH:
            raise ValueError("API_HASH is missing in .env")
