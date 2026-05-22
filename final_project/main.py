#!/usr/bin/env python3
from assistant.bot import run
from assistant.config import load_config


def main() -> None:
    config = load_config()
    run(config)


if __name__ == '__main__':
    main()
