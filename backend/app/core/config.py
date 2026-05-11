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

    # LLM 配置：接入任一 OpenAI-compatible API（DeepSeek、OpenAI 等）。
    llm_provider: str = "deepseek"
    llm_api_key: str | None = None
    llm_base_url: str = "https://api.deepseek.com"
    llm_model: str = "deepseek-chat"
    llm_timeout_seconds: float = 30
    llm_max_claims_per_paper: int = 3


@lru_cache
def get_settings() -> Settings:
    """读取后端配置。

    优先读取系统环境变量，同时支持本地 `backend/.env`，方便开发时填写 API key。
    """
    env_values = _load_env_file(ENV_FILE)
    return Settings(
        openalex_api_key=os.getenv("OPENALEX_API_KEY") or env_values.get("OPENALEX_API_KEY"),
        openalex_mailto=os.getenv("OPENALEX_MAILTO") or env_values.get("OPENALEX_MAILTO"),
        llm_provider=os.getenv("LLM_PROVIDER") or env_values.get("LLM_PROVIDER", "deepseek"),
        llm_api_key=os.getenv("LLM_API_KEY") or env_values.get("LLM_API_KEY"),
        llm_base_url=os.getenv("LLM_BASE_URL") or env_values.get("LLM_BASE_URL", "https://api.deepseek.com"),
        llm_model=os.getenv("LLM_MODEL") or env_values.get("LLM_MODEL", "deepseek-chat"),
        llm_timeout_seconds=_parse_float(os.getenv("LLM_TIMEOUT_SECONDS") or env_values.get("LLM_TIMEOUT_SECONDS", "30")),
        llm_max_claims_per_paper=_parse_int(os.getenv("LLM_MAX_CLAIMS_PER_PAPER") or env_values.get("LLM_MAX_CLAIMS_PER_PAPER", "3")),
    )


def _parse_float(value: str) -> float:
    try:
        return float(value)
    except (ValueError, TypeError):
        return 30.0


def _parse_int(value: str) -> int:
    try:
        return int(value)
    except (ValueError, TypeError):
        return 3


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
