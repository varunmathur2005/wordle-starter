"""Pydantic models for all API request and response shapes."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

FeedbackValue = Literal["green", "yellow", "gray"]
GameStatus = Literal["in_progress", "won", "lost"]


# --- Requests ---

class CreateGameRequest(BaseModel):
    word_length: int = Field(..., ge=5, le=8)


class SubmitGuessRequest(BaseModel):
    guess: str


# --- Shared ---

class GuessResult(BaseModel):
    guess: str
    feedback: list[FeedbackValue]


class GameState(BaseModel):
    id: str
    word_length: int
    max_turns: int
    status: GameStatus
    guesses: list[GuessResult]
    remaining_turns: int
    created_at: datetime
    # Only populated when the game is lost, so the player can see the answer.
    answer: str | None = None
