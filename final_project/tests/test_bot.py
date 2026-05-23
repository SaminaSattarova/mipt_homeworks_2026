from unittest.mock import MagicMock, patch

import pytest  # type: ignore[import-not-found]

from assistant.bot import _stream_reply, run
from assistant.config import Config


def _make_config(
    api_key: str = 'test',
    api_host: str = 'http://localhost/',
    model: str = 'test-model',
    temperature: float = 0.7,
    limit_message: int | None = None,
    limit_chars: int | None = None,
    system_prompt: str | None = None,
) -> Config:
    return Config(
        api_key=api_key,
        api_host=api_host,
        model=model,
        temperature=temperature,
        limit_message=limit_message,
        limit_chars=limit_chars,
        system_prompt=system_prompt,
    )


def _make_stream_mock(tokens: list[str]) -> MagicMock:
    chunks = []
    for token in tokens:
        chunk = MagicMock()
        chunk.choices[0].delta.content = token
        chunks.append(chunk)
    stream = MagicMock()
    stream.__iter__ = MagicMock(return_value=iter(chunks))
    return stream


def test_stream_reply_assembles_tokens(capsys: pytest.CaptureFixture[str]) -> None:
    client = MagicMock()
    client.chat.completions.create.return_value = _make_stream_mock(['Привет', ', ', 'мир!'])
    config = _make_config()
    history: list[dict[str, str]] = [{'role': 'user', 'content': 'hi'}]

    result = _stream_reply(client, config, history)

    assert result == 'Привет, мир!'


def test_run_quit_command(capsys: pytest.CaptureFixture[str]) -> None:
    config = _make_config()
    with patch('assistant.bot.OpenAI'), patch('builtins.input', side_effect=[r'\q']):
        run(config)
    assert 'До свидания' in capsys.readouterr().out


def test_run_sends_message(capsys: pytest.CaptureFixture[str]) -> None:
    config = _make_config()
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = _make_stream_mock(['Ответ'])

    with (
        patch('assistant.bot.OpenAI', return_value=mock_client),
        patch('builtins.input', side_effect=['Привет!', r'\q']),
    ):
        run(config)

    assert mock_client.chat.completions.create.called


def test_run_api_error_handled(capsys: pytest.CaptureFixture[str]) -> None:
    config = _make_config()
    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = RuntimeError('API сломан')

    with (
        patch('assistant.bot.OpenAI', return_value=mock_client),
        patch('builtins.input', side_effect=['Вопрос', r'\q']),
    ):
        run(config)

    assert 'API сломан' in capsys.readouterr().err
