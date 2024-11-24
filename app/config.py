import os


def load_secret(file_path):
    try:
        with open(file_path) as file:
            return file.read().strip()
    except FileNotFoundError:
        return None


MONGO_USERNAME = load_secret("/run/secrets/mongo_username") or os.getenv(
    "MONGO_USERNAME"
)
MONGO_PASSWORD = load_secret("/run/secrets/mongo_password") or os.getenv(
    "MONGO_PASSWORD"
)
MONGO_HOST = os.getenv("MONGO_HOST", "cluster0.afeh5pj.mongodb.net")
MONGO_DBNAME = os.getenv("MONGO_DBNAME", "satellites_db")

MONGO_URL = (
    f"mongodb+srv://{MONGO_USERNAME}:{MONGO_PASSWORD}@{MONGO_HOST}/"  # noqa: E231
    f"{MONGO_DBNAME}?retryWrites=true&w=majority&appName=Cluster0"
)

CELESTRAK_100_BRIGHTEST_URL = (
    "https://celestrak.org/NORAD/elements/gp.php?GROUP=visual&FORMAT=tle"
)
