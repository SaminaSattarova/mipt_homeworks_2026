import os
import re

MAX_FILE_SIZE = 5 * 1024 * 1024


def _replace_file(match: re.Match[str]) -> str:
    filepath = match.group(1).strip()
    try:
        if os.path.getsize(filepath) > MAX_FILE_SIZE:
            print(f'Предупреждение: файл {filepath} превышает 5 МБ, пропускаю.')
            return ''
        with open(filepath, encoding='utf-8', errors='replace') as f:
            return '\n' + f.read()
    except FileNotFoundError:
        print(f'Предупреждение: файл {filepath} не найден.')
        return ''
    except OSError as exc:
        print(f'Предупреждение: ошибка чтения {filepath}: {exc}')
        return ''


def process_attachments(text: str) -> str:
    return re.sub(r'@::([^:]+)::', _replace_file, text)
