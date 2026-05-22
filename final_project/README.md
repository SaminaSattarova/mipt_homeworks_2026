# Консольный ИИ-ассистент

Чат-бот в терминале с поддержкой стриминга, подстановки файлов и управления историей.
Работает через OpenAI-совместимый API — можно подключить Ollama, OpenAI или любой другой совместимый сервис.

## Установка

```bash
pip install -r requirements.txt
```

Если используешь Ollama — скачай модель:
```bash
ollama pull llama3.2
```

## Настройка

### Вариант 1 — через `.env`

Скопируй `.env.example` в `.env` и заполни:
```
API_KEY=ollama
API_HOST=http://localhost:11434/v1/
MODEL=llama3.2
```

### Вариант 2 — через `config.yaml`

Создай `config.yaml` в корне проекта:
```yaml
api_key: ollama
api_host: http://localhost:11434/v1/
model: llama3.2
temperature: 0.7
limit_message: 20
limit_chars: 8000
system_prompt: Ты полезный ассистент.
```

Параметры `temperature`, `limit_message`, `limit_chars`, `system_prompt` — необязательные.

## Запуск

```bash
python main.py
```

## Тесты

```bash
pytest
```

С отчётом о покрытии:
```bash
pytest --cov=assistant --cov-report=html
```

## Проверка кода

Форматирование:
```bash
ruff format .
```

Линтер:
```bash
ruff check .
```

Типы:
```bash
mypy .
```

Или всё сразу:
```bash
ruff format . && ruff check . && mypy . && pytest --cov=assistant
```
