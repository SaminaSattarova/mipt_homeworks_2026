import os
import sys
from dataclasses import dataclass

import yaml

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass


@dataclass
class Config:
    api_key: str
    api_host: str
    model: str = 'gpt-4o-mini'
    limit_message: int | None = None
    limit_chars: int | None = None
    temperature: float = 0.7
    system_prompt: str | None = None


def _read_yaml() -> dict[str, str]:
    if not os.path.exists('config.yaml'):
        return {}
    try:
        with open('config.yaml', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        if not isinstance(data, dict):
            return {}
        return {str(k): str(v) for k, v in data.items() if v is not None}
    except Exception as exc:
        print(f'Предупреждение: ошибка чтения config.yaml: {exc}')
        return {}


def load_config() -> Config:
    raw = _read_yaml()

    env_keys: dict[str, str] = {
        'API_KEY': 'api_key',
        'API_HOST': 'api_host',
        'LIMIT_CHARS': 'limit_chars',
        'LIMIT_MESSAGE': 'limit_message',
        'TEMPERATURE': 'temperature',
        'MODEL': 'model',
        'SYSTEM_PROMPT': 'system_prompt',
    }
    for env_key, cfg_key in env_keys.items():
        val = os.environ.get(env_key)
        if val is not None:
            raw[cfg_key] = val

    if not raw:
        print(
            'Ошибка: конфигурация не найдена.\n'
            'Укажите параметры через переменные окружения, .env или config.yaml.'
        )
        sys.exit(1)

    for required in ('api_key', 'api_host'):
        if not raw.get(required):
            print(f'Ошибка: не задан {required.upper()}.')
            sys.exit(1)

    return Config(
        api_key=raw['api_key'],
        api_host=raw['api_host'],
        model=raw.get('model', 'gpt-4o-mini'),
        limit_message=int(raw['limit_message']) if 'limit_message' in raw else None,
        limit_chars=int(raw['limit_chars']) if 'limit_chars' in raw else None,
        temperature=float(raw.get('temperature', '0.7')),
        system_prompt=raw.get('system_prompt'),
    )
