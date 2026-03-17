"""
Loads static word lists at startup and exposes helpers for random word selection
and guess validation. Two structures per word length:
  - list: for O(1) random selection
  - set:  for O(1) membership checks
"""

import random
from pathlib import Path

_WORD_LISTS: dict[int, list[str]] = {}
_WORD_SETS: dict[int, set[str]] = {}
_VALID_LENGTHS = [5, 6, 7, 8]


def _load() -> None:
    base = Path(__file__).parent / "words"
    for n in _VALID_LENGTHS:
        words = [
            w.strip().upper()
            for w in (base / f"words_{n}.txt").read_text().splitlines()
            if w.strip()
        ]
        _WORD_LISTS[n] = words
        _WORD_SETS[n] = set(words)


_load()


def get_random_word(length: int) -> str:
    return random.choice(_WORD_LISTS[length])


def is_valid_word(word: str, length: int) -> bool:
    return word.upper() in _WORD_SETS.get(length, set())


def valid_lengths() -> list[int]:
    return _VALID_LENGTHS
