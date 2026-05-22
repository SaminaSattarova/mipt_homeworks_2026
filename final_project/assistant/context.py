def trim_context(
    history: list[dict[str, str]],
    limit_message: int | None,
    limit_chars: int | None,
) -> None:
    system_msgs = [m for m in history if m['role'] == 'system']
    chat_msgs = [m for m in history if m['role'] != 'system']

    if limit_message is not None:
        while len(chat_msgs) > limit_message:
            chat_msgs.pop(0)

    if limit_chars is not None:
        total = sum(len(m['content']) for m in chat_msgs)
        while total > limit_chars and len(chat_msgs) > 1:
            removed = chat_msgs.pop(0)
            total -= len(removed['content'])
        if chat_msgs:
            total = sum(len(m['content']) for m in chat_msgs)
            if total > limit_chars:
                excess = total - limit_chars
                chat_msgs[0]['content'] = chat_msgs[0]['content'][excess:]

    history.clear()
    history.extend(system_msgs + chat_msgs)
