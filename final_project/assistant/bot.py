import os
import sys
from typing import cast

from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam

from assistant.attachments import process_attachments
from assistant.chunks import parse_chunk_args, run_file_chunk
from assistant.config import Config
from assistant.context import trim_context


def _stream_reply(client: OpenAI, config: Config, history: list[dict[str, str]]) -> str:
    reply = ''
    print('>>> ', end='', flush=True)
    stream = client.chat.completions.create(
        model=config.model,
        messages=cast(list[ChatCompletionMessageParam], history),
        temperature=config.temperature,
        stream=True,
    )
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            print(delta, end='', flush=True)
            reply += delta
    print()
    return reply


def run(config: Config) -> None:
    client = OpenAI(api_key=config.api_key, base_url=config.api_host)

    history: list[dict[str, str]] = []
    if config.system_prompt:
        history.append({'role': 'system', 'content': config.system_prompt})

    print('ИИ-ассистент готов к работе.')
    print(r'Команды: \q — выход, /reset — сбросить историю, /file_chunk — обработка файла частями.')

    while True:
        try:
            user_input = input('>>> ').strip()
        except EOFError:
            break
        except KeyboardInterrupt:
            print()
            continue

        if not user_input:
            continue

        if user_input == r'\q':
            print('До свидания!')
            break

        if user_input == '/reset':
            history.clear()
            if config.system_prompt:
                history.append({'role': 'system', 'content': config.system_prompt})
            os.system('clear' if os.name == 'posix' else 'cls')  # noqa: S605,S607
            print('История очищена. ИИ-ассистент готов к работе.')
            continue

        if user_input.startswith('/file_chunk') or user_input.startswith('/filechunk'):
            chunk_mode, chunk_n, chunk_auto = parse_chunk_args(user_input)
            run_file_chunk(client, config, chunk_mode, chunk_n, chunk_auto)
            continue

        processed = process_attachments(user_input)
        history.append({'role': 'user', 'content': processed})
        trim_context(history, config.limit_message, config.limit_chars)

        try:
            reply = _stream_reply(client, config, history)
            history.append({'role': 'assistant', 'content': reply})
        except KeyboardInterrupt:
            print('\nЗапрос прерван. Можно ввести следующее сообщение.')
            history.pop()
        except Exception as exc:
            print(f'Ошибка API: {exc}', file=sys.stderr)
            history.pop()
