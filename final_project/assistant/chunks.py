import os
from typing import cast

from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam

from assistant.config import Config


def split_chunks(text: str, mode: str, n: int) -> list[str]:
    if mode == 'len':
        return [text[i : i + n] for i in range(0, len(text), n) if text[i : i + n].strip()]
    paragraphs = [p for p in text.split('\n') if p.strip()]
    if n == 1:
        return paragraphs
    return [
        '\n'.join(paragraphs[i : i + n])
        for i in range(0, len(paragraphs), n)
        if '\n'.join(paragraphs[i : i + n]).strip()
    ]


def parse_chunk_args(cmd: str) -> tuple[str, int, bool]:
    mode, n, auto = 'paragraph', 1, False
    for part in cmd.strip().split()[1:]:
        if part == '-y':
            auto = True
        elif part.startswith('paragraph='):
            mode, n = 'paragraph', int(part.split('=')[1])
        elif part.startswith('len='):
            mode, n = 'len', int(part.split('=')[1])
    return mode, n, auto


def run_file_chunk(client: OpenAI, config: Config, mode: str, n: int, auto: bool) -> None:
    print('>>> Введите путь до файла')
    try:
        filepath = input('>>> ').strip()
    except EOFError:
        return
    if filepath == r'\q':
        return

    if not os.path.exists(filepath):
        print(f'Ошибка: файл {filepath} не найден.')
        return

    try:
        with open(filepath, encoding='utf-8', errors='replace') as f:
            text = f.read()
    except OSError as exc:
        print(f'Ошибка при чтении файла: {exc}')
        return

    print('>>> Принято. Что нужно сделать для каждого фрагмента (User Prompt)?')
    try:
        user_prompt = input('>>> ').strip()
    except EOFError:
        return
    if user_prompt == r'\q':
        return

    print('>>> Принято. Начинаю обработку:')

    for idx, chunk in enumerate(split_chunks(text, mode, n)):
        if not auto and idx > 0:
            try:
                entry = input('>>> ').strip()
            except EOFError:
                break
            if entry == r'\q':
                break

        messages = cast(
            list[ChatCompletionMessageParam],
            [{'role': 'user', 'content': f'{user_prompt}\n\n{chunk}'}],
        )
        try:
            response = client.chat.completions.create(
                model=config.model,
                messages=messages,
                temperature=config.temperature,
            )
            content = response.choices[0].message.content or ''
            print(f'>>> {content}')
        except KeyboardInterrupt:
            print('\nЗапрос прерван. Продолжаю...')
        except Exception as exc:
            print(f'Ошибка API: {exc}')

    print('>>> Обработка файла завершена.')
