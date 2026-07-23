import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def load_secret(file_path):
    secret_path = Path(file_path)
    if secret_path.exists():
        return secret_path.read_text().strip()
    return None


MONGO_USERNAME = load_secret("/run/secrets/mongo_username") or os.getenv("MONGO_USERNAME")
MONGO_PASSWORD = load_secret("/run/secrets/mongo_password") or os.getenv("MONGO_PASSWORD")
MONGO_HOST = os.getenv("MONGO_HOST", "cluster0.afeh5pj.mongodb.net")
MONGO_DBNAME = os.getenv("MONGO_DBNAME", "satellites_db")

MONGO_URI = os.getenv("MONGO_URI") or (
    f"mongodb+srv://{MONGO_USERNAME}:{MONGO_PASSWORD}@{MONGO_HOST}/"  # noqa: E231
    f"{MONGO_DBNAME}?retryWrites=true&w=majority&appName=Cluster0"
)

CELESTRAK_100_BRIGHTEST_URL = "https://celestrak.org/NORAD/elements/gp.php?GROUP=visual&FORMAT=tle"
CELESTRAK_SATCAT_URL = "https://celestrak.org/satcat/records.php?GROUP=visual&FORMAT=JSON"
