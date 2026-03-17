"""
In-memory game store. Games are keyed by UUID and live for the process lifetime.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone

from schemas import GameStatus, GuessResult


@dataclass
class Game:
    id: str
    secret_word: str  # never sent to the client except on loss
    word_length: int
    max_turns: int
    status: GameStatus
    guesses: list[GuessResult] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))

    @property
    def remaining_turns(self) -> int:
        return self.max_turns - len(self.guesses)


_store: dict[str, Game] = {}


def create_game(secret_word: str, word_length: int) -> Game:
    game = Game(
        id=str(uuid.uuid4()),
        secret_word=secret_word,
        word_length=word_length,
        max_turns=word_length + 1,
        status="in_progress",
    )
    _store[game.id] = game
    return game


def get_game(game_id: str) -> Game | None:
    return _store.get(game_id)


def append_guess(game: Game, guess_result: GuessResult, new_status: GameStatus) -> None:
    game.guesses.append(guess_result)
    game.status = new_status
