from pathlib import Path


DATABASE_PATH = Path(__file__).resolve().parent / "novelmind.sqlite3"
DATABASE_URL = f"sqlite:///{DATABASE_PATH.as_posix()}"


def get_database_url() -> str:
    return DATABASE_URL
