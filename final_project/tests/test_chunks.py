from assistant.chunks import parse_chunk_args, split_chunks


def test_split_by_paragraph() -> None:
    chunks = split_chunks('a\nb\nc', mode='paragraph', n=1)
    assert chunks == ['a', 'b', 'c']


def test_split_by_len() -> None:
    chunks = split_chunks('abcdefghij', mode='len', n=3)
    assert chunks == ['abc', 'def', 'ghi', 'j']


def test_split_skips_blank_lines() -> None:
    chunks = split_chunks('a\n\n\nb\n\nc', mode='paragraph', n=1)
    assert '' not in chunks
    assert len(chunks) == 3


def test_parse_chunk_args_default() -> None:
    mode, n, auto = parse_chunk_args('/file_chunk')
    assert mode == 'paragraph'
    assert n == 1
    assert auto is False


def test_parse_chunk_args_with_options() -> None:
    mode, n, auto = parse_chunk_args('/file_chunk len=50 -y')
    assert mode == 'len'
    assert n == 50
    assert auto is True
