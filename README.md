# Wordle Full Stack Assessment

Wordle is a word-guessing game. You guess a hidden word one letter at a time; after each guess you learn which letters are correct (green), present but misplaced (yellow), or absent (gray).

**This version adds two differences from the original:**
- **Multiple games** — create and play as many games as you want.
- **Configurable word length** — choose 5–8 letters; you always get N+1 turns (e.g. a 7-letter word gives 8 turns).

---

## Project Structure

```
wordle-starter/
├── backend/
│   ├── main.py               # FastAPI app and route handlers
│   ├── schemas.py            # Pydantic request/response models
│   ├── store.py              # In-memory game store
│   ├── game_logic.py         # Scoring and win/loss logic
│   ├── word_repository.py    # Word list loading, answer selection, guess validation
│   ├── words/
│   │   ├── words_{5-8}.txt   # Broad valid-guess dictionaries (~15k–52k words each)
│   │   └── answers_{5-8}.txt # Curated answer pools (~2,300 common words each)
│   ├── tests/
│   │   └── test_game_logic.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   └── src/
│       ├── App.jsx           # Top-level component; game state and phase
│       ├── api.js            # Fetch wrappers for all API calls
│       └── components/
│           ├── GameSetup.jsx   # Word-length picker and start button
│           ├── GameBoard.jsx   # Grid and keyboard input handler
│           ├── GuessRow.jsx    # One row of letter tiles
│           ├── Cell.jsx        # Single tile with color variant
│           ├── Keyboard.jsx    # On-screen QWERTY keyboard
│           └── GameStatus.jsx  # Win/loss message and Play Again
├── scripts/
│   └── generate_words.py     # One-time script that produced the word list files
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

```bash
docker compose up -d --build   # run in background
docker compose down            # stop
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The UI is available at `http://localhost:5173`.

### Tests

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 -m pytest tests/ -v
```

---

## API

All endpoints return the same `GameState` shape.

### `POST /games`

Create a new game. `word_length` must be 5–8.

**Request**
```json
{ "word_length": 5 }
```

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
  "answer": null
}
```

### `GET /games/{game_id}`

Retrieve current game state. `404` if not found.

### `POST /games/{game_id}/guesses`

Submit a guess. Returns the updated `GameState`.

**Request**
```json
{ "guess": "CRANE" }
```

**Response** `200` — same `GameState` shape, with the new guess appended and feedback included.

**Errors** (all return `{ "code": "...", "message": "..." }`)

| Status | Code | Condition |
|--------|------|-----------|
| 404 | `GAME_NOT_FOUND` | Unknown game ID |
| 400 | `GAME_COMPLETED` | Game already won or lost |
| 400 | `INVALID_GUESS_LENGTH` | Guess length ≠ word_length |
| 400 | `INVALID_WORD` | Not in the valid-guess dictionary |

**Notes:**
- Guesses are case-insensitive; the server normalizes to uppercase.
- `answer` is `null` during play and on win. It is revealed only when `status == "lost"`.

---

## Design Decisions

### Two separate word lists

`word_repository.py` loads two distinct file sets at startup:

- **`answers_{n}.txt`** — ~2,000–2,300 common everyday words per length, sourced from a top-20k English frequency list and filtered against the Collins Scrabble Words list to exclude proper nouns. These are the randomly selected target words. The curated pool ensures answers feel recognizable rather than obscure.
- **`words_{n}.txt`** — a broad ~15k–52k word dictionary per length (full alphabetic corpus). Used only to validate player guesses, so players can submit any real word.

Keeping these separate is the same approach the original NYT Wordle uses: a smaller answer set, a larger valid-guess set.

### Modular backend

Route handlers in `main.py` are thin — they validate input, call into `game_logic`, `store`, or `word_repository`, then convert to the response schema. Business logic lives in focused, independently testable modules.

### Two-pass duplicate-letter scoring

Wordle scoring with repeated letters requires care:
1. **Pass 1** — mark exact-position matches as green; mark those answer positions as consumed.
2. **Pass 2** — for each non-green guess letter, find the leftmost unconsumed matching answer position → yellow; otherwise gray.

This matches the algorithm used by the original game and is covered by dedicated edge-case tests.

### In-memory store

Games live in a module-level `dict` keyed by UUID. This was chosen intentionally because the assessment explicitly allows in-memory state. It avoids introducing a database dependency while keeping the implementation simple and easy to review. Games are lost on restart, which is acceptable for this scope.

### Flat API responses

All three endpoints — `POST /games`, `GET /games/{id}`, and `POST /games/{id}/guesses` — return the same `GameState` shape. This keeps the API consistent and makes the frontend state management straightforward: every response is just the new game state.

### Frontend as thin view layer

The React frontend never computes game state locally. Every guess submission returns the full updated `GameState` from the server, which atomically replaces local state. Phase (setup / playing / done) is derived from `game === null` and `game.status`, not stored separately.

---

## Tradeoffs & Assumptions

| Area | Decision | Rationale |
|------|----------|-----------|
| In-memory storage | Module-level dict, no DB | Assessment explicitly permits this; avoids infrastructure complexity |
| Answer word curation | Frequency list × SOWPODS intersection | Eliminates obscure words and proper nouns; some uncommon-usage words may remain |
| No authentication | Games identified by UUID only | Out of scope per assessment brief |
| Pydantic field validation | `ge=5, le=8` on `word_length` returns 422 | Consistent with FastAPI idioms; business-logic errors return structured 400s |
| Single-process concurrency | No locking on the in-memory store | Sufficient for local dev; production use would need a real store |

---

## Future Improvements

- Persist games to a database (SQLite or PostgreSQL via SQLAlchemy)
- Animate tile reveals with a flip transition
- Add a share-result feature (colored emoji grid, à la NYT Wordle)
- Track per-session statistics (win rate, guess distribution)
