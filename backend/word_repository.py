"""
Word lists loaded once at startup from bundled text files.

Two separate concerns:
  _ANSWER_LISTS  — curated common-word pool, used to pick random target words
  _WORD_SETS     — broad dictionary, used to validate player guesses

Keeping them separate ensures answers feel like everyday words while still
allowing players to guess less-common words that are in the dictionary.
"""

import random
from pathlib import Path

_ANSWER_LISTS: dict[int, list[str]] = {}
_WORD_SETS: dict[int, set[str]] = {}
_VALID_LENGTHS = [5, 6, 7, 8]


def _load() -> None:
    base = Path(__file__).parent / "words"
    for n in _VALID_LENGTHS:
        answers = [
            w.strip().upper()
            for w in (base / f"answers_{n}.txt").read_text().splitlines()
            if w.strip()
        ]
        _ANSWER_LISTS[n] = answers

        guesses = [
            w.strip().upper()
            for w in (base / f"words_{n}.txt").read_text().splitlines()
            if w.strip()
        ]
        _WORD_SETS[n] = set(guesses)


_load()


def get_random_word(length: int) -> str:
    return random.choice(_ANSWER_LISTS[length])


def is_valid_word(word: str, length: int) -> bool:
    return word.upper() in _WORD_SETS.get(length, set())


def valid_lengths() -> list[int]:
    return _VALID_LENGTHS
