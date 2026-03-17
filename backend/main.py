from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

import store
import word_repository as words
from game_logic import score_guess, is_win
from schemas import (
    CreateGameRequest,
    GameState,
    GuessResult,
    SubmitGuessRequest,
)

app = FastAPI(title="Wordle API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Structured business-logic errors
# ---------------------------------------------------------------------------

class AppError(Exception):
    def __init__(self, status_code: int, code: str, message: str):
        self.status_code = status_code
        self.code = code
        self.message = message


@app.exception_handler(AppError)
async def app_error_handler(_request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": exc.code, "message": exc.message},
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _to_game_state(game: store.Game) -> GameState:
    """Convert internal Game to the API response shape.
    The answer is only revealed when the game is lost."""
    return GameState(
        id=game.id,
        word_length=game.word_length,
        max_turns=game.max_turns,
        status=game.status,
        guesses=game.guesses,
        remaining_turns=game.remaining_turns,
        created_at=game.created_at,
        answer=game.secret_word if game.status == "lost" else None,
    )


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/games", response_model=GameState, status_code=201)
def create_game(body: CreateGameRequest):
    secret = words.get_random_word(body.word_length)
    game = store.create_game(secret, body.word_length)
    return _to_game_state(game)


@app.get("/games/{game_id}", response_model=GameState)
def get_game(game_id: str):
    game = store.get_game(game_id)
    if game is None:
        raise AppError(404, "GAME_NOT_FOUND", "Game not found")
    return _to_game_state(game)


@app.post("/games/{game_id}/guesses", response_model=GameState)
def submit_guess(game_id: str, body: SubmitGuessRequest):
    game = store.get_game(game_id)
    if game is None:
        raise AppError(404, "GAME_NOT_FOUND", "Game not found")
    if game.status != "in_progress":
        raise AppError(400, "GAME_COMPLETED", "Game is already completed")

    guess = body.guess.strip().upper()

    if len(guess) != game.word_length:
        raise AppError(
            400,
            "INVALID_GUESS_LENGTH",
            f"Guess must be exactly {game.word_length} letters",
        )
    if not words.is_valid_word(guess, game.word_length):
        raise AppError(400, "INVALID_WORD", "Not a valid word")

    feedback = score_guess(guess, game.secret_word)
    guess_result = GuessResult(guess=guess, feedback=feedback)

    # Determine new status before appending (remaining_turns is computed from current guess count)
    if is_win(feedback):
        new_status = "won"
    elif game.remaining_turns - 1 == 0:
        new_status = "lost"
    else:
        new_status = "in_progress"

    store.append_guess(game, guess_result, new_status)

    return _to_game_state(game)
