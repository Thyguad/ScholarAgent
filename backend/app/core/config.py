import os
from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel


BACKEND_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = BACKEND_DIR / ".env"


class Settings(BaseModel):
    """项目运行配置。

    这里集中读取 API key，避免把密钥散落在业务代码里。
    """

    openalex_api_key: str | None = None
    openalex_mailto: str | None = None


@lru_cache
def get_settings() -> Settings:
    """读取后端配置。

    优先读取系统环境变量，同时支持本地 `backend/.env`，方便开发时填写 API key。
    """
    env_values = _load_env_file(ENV_FILE)
    return Settings(
        openalex_api_key=os.getenv("OPENALEX_API_KEY") or env_values.get("OPENALEX_API_KEY"),
        openalex_mailto=os.getenv("OPENALEX_MAILTO") or env_values.get("OPENALEX_MAILTO"),
    )


def _load_env_file(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}

    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue

        key, value = stripped.split("=", maxsplit=1)
        values[key.strip()] = value.strip().strip('"').strip("'")

    return values
