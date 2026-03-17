"""
Core Wordle game logic: scoring and win detection.

Scoring uses a two-pass approach to correctly handle duplicate letters:
  Pass 1: Exact position matches → "green". Mark those answer positions as consumed.
  Pass 2: For each non-green guess letter, find the leftmost unconsumed matching
          answer position → "yellow". Anything unmatched → "gray".
"""

from typing import Literal

Feedback = Literal["green", "yellow", "gray"]


def score_guess(guess: str, answer: str) -> list[Feedback]:
    """Return per-letter feedback for a guess against a known answer."""
    assert len(guess) == len(answer), "guess and answer must be the same length"

    n = len(answer)
    result: list[Feedback | None] = [None] * n
    # Tracks which answer positions are still available for yellow matching.
    # Using None (not deletion) to keep indices stable.
    answer_available: list[str | None] = list(answer)

    # Pass 1: greens
    for i in range(n):
        if guess[i] == answer[i]:
            result[i] = "green"
            answer_available[i] = None

    # Pass 2: yellows and grays
    for i in range(n):
        if result[i] is not None:
            continue
        letter = guess[i]
        if letter in answer_available:
            result[i] = "yellow"
            # Consume the leftmost unmatched occurrence
            answer_available[answer_available.index(letter)] = None
        else:
            result[i] = "gray"

    return result  # type: ignore[return-value]


def is_win(feedback: list[Feedback]) -> bool:
    return all(f == "green" for f in feedback)
