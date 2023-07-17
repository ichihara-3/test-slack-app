from dotenv import load_dotenv
from pathlib import Path


def load_env():
    if Path('.env').is_file():
        load_dotenv()
