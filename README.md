# Wordle Full Stack Assessment

## Background

Wordle is a word-guessing game. You guess a hidden word one letter at a time, and after each guess you learn which letters are correct (green), present but misplaced (yellow), or absent (gray).

Play the original: [NYT Wordle](https://www.nytimes.com/games/wordle/index.html)

---

## Rules

1. Letters in the right position turn **green**.
2. Letters in the answer but wrong position turn **yellow**.
3. Letters not in the answer turn **gray**.
4. Each guess must be a real word in the dictionary.
5. Letters can appear more than once.
6. You do not have to reuse correct letters in subsequent guesses.

**This version adds two differences from the original:**
- **Multiple games**: create as many games as you want.
- **Configurable word length**: choose 5–8 letters; you always get N+1 turns (e.g. 7-letter word → 8 turns).

---

## Project Structure

```
wordle-starter/
├── backend/
│   ├── main.py               # FastAPI app + route handlers
│   ├── schemas.py            # Pydantic request/response models
│   ├── store.py              # In-memory game store
│   ├── game_logic.py         # Scoring + win/loss logic
│   ├── word_repository.py    # Word list loading + validation
│   ├── words/                # Bundled word lists (words_5.txt … words_8.txt)
│   ├── tests/
│   │   └── test_game_logic.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   └── src/
│       ├── App.jsx           # Top-level orchestration (phase state machine)
│       ├── api.js            # Fetch wrappers for all API calls
│       └── components/
│           ├── GameSetup.jsx   # Word-length picker + start button
│           ├── GameBoard.jsx   # Grid + keyboard input handler
│           ├── GuessRow.jsx    # One row of letter tiles
│           ├── Cell.jsx        # Single tile with color variant
│           ├── Keyboard.jsx    # On-screen QWERTY keyboard
│           └── GameStatus.jsx  # Win/loss message + Play Again
├── scripts/
│   └── generate_words.py     # One-time script used to produce the word lists
├── docker-compose.yml
└── README.md
```

---

## Setup & Running

### Prerequisites
- Docker & Docker Compose
- Node.js 18+

### Backend

```bash
docker compose up --build
```

The API starts at `http://localhost:8000`.
Interactive docs: `http://localhost:8000/docs`

To run in the background:
```bash
docker compose up -d --build
```

To stop:
```bash
docker compose down
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The UI is available at `http://localhost:5173`.

### Running Tests

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 -m pytest tests/ -v
```

---

## API Overview

### `POST /games`
Create a new game.

**Request**
```json
{ "word_length": 5 }
```
`word_length` must be 5–8.

**Response** `201`
```json
{
  "id": "uuid",
  "word_length": 5,
  "max_turns": 6,
  "status": "in_progress",
  "guesses": [],
  "remaining_turns": 6,
  "created_at": "2024-01-01T00:00:00Z",
  "secret_word": null
}
```

---

### `GET /games/{game_id}`
Retrieve the current state of a game.

**Response** `200` — same shape as above (with `guesses` populated).

**Errors**: `404` if the game doesn't exist.

---

### `POST /games/{game_id}/guesses`
Submit a guess.

**Request**
```json
{ "guess": "CRANE" }
```

**Response** `200`
```json
{
  "game": { "...full game state..." },
  "latest_guess": {
    "guess": "CRANE",
    "feedback": ["gray", "yellow", "gray", "green", "gray"]
  }
}
```

**Errors**:
- `400` — wrong length, not a dictionary word, or game already finished
- `404` — game not found

**Notes**:
- Input is case-insensitive (normalized to uppercase server-side).
- `secret_word` is only populated in `game` when `status == "lost"`, so the player can see what they missed.

---

## Design Decisions

### Backend

**Modular structure over a single `main.py`**
Route handlers are thin — they validate input, delegate to focused modules (`game_logic`, `store`, `word_repository`), and convert to response schemas. This keeps business logic testable in isolation.

**Two-pass scoring for duplicate letters**
Standard Wordle scoring can be tricky with repeated letters. The algorithm:
1. First pass: mark greens (exact position matches), mark those answer positions as consumed.
2. Second pass: for each non-green letter, find the leftmost unconsumed matching position in the answer → yellow; otherwise gray.

This is the same algorithm used in the original game and handles all edge cases correctly.

**In-memory store**
Games live in a module-level dict keyed by UUID. Simple, fast, no external dependencies. State is lost on restart, which is acceptable per the brief.

**Static word lists**
Word lists for lengths 5–8 are pre-generated from the [dwyl/english-words](https://github.com/dwyl/english-words) public-domain corpus and committed as `.txt` files. They're loaded once at startup into a `list` (for random selection) and a `set` (for O(1) validation). The same set serves as both answer pool and valid-guess dictionary — no curation needed for a take-home assessment.

**`secret_word` revealed on loss only**
The `GameState` response shape has `secret_word: null` during play and on win. It's only populated (by `_to_game_state`) when `status == "lost"`, so the frontend can show "The word was X" at the end of a lost game without requiring a separate endpoint.

### Frontend

**Phase state machine in `App.jsx`**
Three phases: `setup → playing → done`. The `GameBoard` component stays mounted during `done` so the completed grid remains visible while `GameStatus` appears below it.

**Server as single source of truth**
The frontend never computes game state locally. Every guess submission returns the full updated `GameState` from the server, which replaces React state atomically. This simplifies the frontend significantly.

**`useCallback` + `useEffect` for keyboard input**
`handleKey` is defined with `useCallback` (all relevant state in deps) to avoid stale closures. The `keydown` listener is attached/removed in a `useEffect` with cleanup — required to prevent duplicate listeners in React StrictMode development mode.

---

## Tradeoffs & Assumptions

| Area | Decision | Tradeoff |
|------|----------|----------|
| Word list curation | Use full filtered corpus for both answers and valid guesses | Some obscure words may appear as answers; acceptable for an assessment |
| In-memory store | Module-level dict, no locking | Not thread-safe under concurrent writes in production; sufficient for single-process dev use |
| Pydantic validation | `ge=5, le=8` on `word_length` returns 422 | Slightly different from the 400 used for business-logic errors; consistent with FastAPI idioms |
| No authentication | Games identified only by UUID | Intentional per brief; any client with the UUID can view/play a game |
| No persistence | State lost on restart | Acceptable per brief; would require a database for production |

---

## Future Improvements

- Persist games to a database (SQLite / PostgreSQL via SQLAlchemy)
- Add a smaller, curated answer word list separate from the valid-guess dictionary
- Animate tile reveals with CSS transitions
- Add a share-result feature (colored emoji grid)
- Track per-session stats (win rate, guess distribution)
- Improve word list quality: filter out proper nouns, abbreviations, and archaic words
