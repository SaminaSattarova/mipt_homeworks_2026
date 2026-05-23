import pytest  # type: ignore[import-not-found]

import assistant.attachments as att_module
from assistant.attachments import process_attachments


def test_replaces_file_with_content(tmp_path: pytest.TempPathFactory) -> None:
    f = tmp_path / 'hello.txt'
    f.write_text('file content')
    result = process_attachments(f'смотри @::{f}::')
    assert 'file content' in result


def test_missing_file_prints_warning(capsys: pytest.CaptureFixture[str]) -> None:
    result = process_attachments('@::/nonexistent/path/file.txt::')
    assert result == ''
    assert 'не найден' in capsys.readouterr().out


def test_no_pattern_unchanged() -> None:
    text = 'обычное сообщение без файлов'
    assert process_attachments(text) == text


def test_file_too_large_skipped(
    tmp_path: pytest.TempPathFactory, monkeypatch: pytest.MonkeyPatch
) -> None:
    f = tmp_path / 'big.txt'
    f.write_text('много данных')
    monkeypatch.setattr(att_module, 'MAX_FILE_SIZE', 1)
    result = process_attachments(f'@::{f}::')
    assert result == ''
