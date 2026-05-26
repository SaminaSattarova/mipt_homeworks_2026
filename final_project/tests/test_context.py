from assistant.context import trim_context


def _history(*pairs: tuple[str, str]) -> list[dict[str, str]]:
    return [{'role': r, 'content': c} for r, c in pairs]


def test_trim_by_message_limit_removes_oldest() -> None:
    history = _history(
        ('user', 'a'), ('assistant', 'b'), ('user', 'c'), ('assistant', 'd'), ('user', 'e')
    )
    trim_context(history, limit_message=3, limit_chars=None)
    assert len(history) == 3
    assert history[0]['content'] == 'c'


def test_trim_keeps_system_message() -> None:
    history = _history(
        ('system', 'sys'), ('user', 'a'), ('assistant', 'b'), ('user', 'c'), ('assistant', 'd')
    )
    trim_context(history, limit_message=2, limit_chars=None)
    assert history[0] == {'role': 'system', 'content': 'sys'}
    assert len(history) == 3


def test_trim_by_chars_removes_oldest() -> None:
    history = _history(('user', 'aaaa'), ('assistant', 'bbbb'), ('user', 'cccc'))
    trim_context(history, limit_message=None, limit_chars=10)
    total = sum(len(m['content']) for m in history)
    assert total <= 10


def test_trim_no_limits_unchanged() -> None:
    history = _history(('user', 'a'), ('user', 'b'), ('user', 'c'))
    trim_context(history, limit_message=None, limit_chars=None)
    assert len(history) == 3
