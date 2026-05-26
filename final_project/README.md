# Итоговый проект "GigaVibeMiptCode"

## Архитектура

```
main.py                  — точка входа, запускает load_config() и run()
assistant/
├── config.py            — читает config.yaml и переменные окружения, возвращает датакласс Config
├── bot.py               — главный цикл чата, стриминг ответов, обработка команд
├── context.py           — обрезает историю по лимиту сообщений или символов
├── attachments.py       — заменяет @::путь:: в сообщении на содержимое файла
└── chunks.py            — разбивает файл на части и отправляет по очереди
```

Поток данных при каждом сообщении:
1. `attachments.py` подставляет файлы если есть тег `@::...::`
2. сообщение добавляется в историю
3. `context.py` обрезает историю если она вышла за лимит
4. `bot.py` отправляет всю историю в API и стримит ответ токен за токеном
5. ответ модели добавляется в историю

## Установка

```bash
pip install -r requirements.txt
```

## Настройка

### Вариант 1 — через `.env`

Скопировать `.env.example` в `.env` и заполни:
```
API_KEY=ollama
API_HOST=http://localhost:11434/v1/
MODEL=llama3.2
```

### Вариант 2 — через `config.yaml`

Создать `config.yaml` в корне проекта:
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
