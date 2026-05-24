"""Local secret storage service - reads/writes to %APPDATA%/NovelMind/secrets.local.json.

Never saves into the repository directory.
Never returns full API key to the frontend.
"""

import json
import os
from pathlib import Path


def _secrets_dir() -> Path:
    appdata = os.environ.get("APPDATA", "")
    if appdata:
        d = Path(appdata) / "NovelMind"
    else:
        d = Path.home() / ".novelmind"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _secrets_file() -> Path:
    return _secrets_dir() / "secrets.local.json"


def _read_all() -> dict:
    f = _secrets_file()
    if not f.is_file():
        return {}
    try:
        return json.loads(f.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def _write_all(data: dict) -> None:
    f = _secrets_file()
    tmp = f.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(f)


def save_api_key(provider_id: int, api_key: str) -> None:
    d = _read_all()
    d[str(provider_id)] = api_key
    _write_all(d)


def get_api_key(provider_id: int) -> str | None:
    d = _read_all()
    return d.get(str(provider_id))


def delete_api_key(provider_id: int) -> bool:
    d = _read_all()
    key = str(provider_id)
    if key not in d:
        return False
    del d[key]
    _write_all(d)
    return True


def has_api_key(provider_id: int) -> bool:
    d = _read_all()
    return str(provider_id) in d


def mask_key(key: str | None) -> str:
    if not key:
        return ""
    if len(key) <= 8:
        return key[:2] + "****" + key[-2:]
    return key[:4] + "****" + key[-4:]


def get_status(provider_id: int) -> dict:
    has = has_api_key(provider_id)
    key = get_api_key(provider_id) if has else None
    return {
        "has_direct_api_key": has,
        "masked_api_key": mask_key(key) if has else "",
    }
