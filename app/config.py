from dotenv import load_dotenv
import os

load_dotenv()

class settings:
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./gotyolo.db")

def get_settings():
    return settings