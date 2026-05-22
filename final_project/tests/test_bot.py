from unittest.mock import MagicMock, patch

import pytest

from assistant.bot import _stream_reply, run
from assistant.config import Config


def _make_config(**kwargs: object) -> Config:
    defaults: dict[str, object] = {
        'api_key': 'test',
        'api_host': 'http://localhost/',
        'model': 'test-model',
        'temperature': 0.7,
        'limit_message': None,
        'limit_chars': None,
        'system_prompt': None,
    }
    defaults.update(kwargs)
    return Config(**defaults)


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
