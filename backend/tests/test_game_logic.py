import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi.testclient import TestClient
from main import app
import game_logic

client = TestClient(app)


# ---------------------------------------------------------------------------
# Unit tests: scoring
# ---------------------------------------------------------------------------

def test_score_all_green():
    assert game_logic.score_guess("SPELL", "SPELL") == ["green"] * 5


def test_score_all_gray():
    assert game_logic.score_guess("ABCDE", "FGHIJ") == ["gray"] * 5


def test_score_basic_yellow():
    result = game_logic.score_guess("SABCD", "ASFGH")
    assert result[0] == "yellow"  # S present but wrong position
    assert result[1] == "yellow"  # A present but wrong position


def test_score_duplicate_guess_one_in_answer():
    # Guess SPEED vs answer SPELL: S, P, E are green.
    # The second E in SPEED has no remaining unmatched E in SPELL → gray.
    result = game_logic.score_guess("SPEED", "SPELL")
    assert result == ["green", "green", "green", "gray", "gray"]


def test_score_duplicate_answer_letter_one_in_guess():
    # Guess CANES vs answer LLAMA: A at pos1 finds a match in LLAMA → yellow.
    result = game_logic.score_guess("CANES", "LLAMA")
    assert result == ["gray", "yellow", "gray", "gray", "gray"]


def test_score_duplicate_answer_two_in_guess_one_in_answer():
    # FLASK has one S (pos 3). FLOSS has S at pos 3 (green) and pos 4.
    # The second S has no remaining unmatched S in the answer → gray.
    result = game_logic.score_guess("FLOSS", "FLASK")
    assert result == ["green", "green", "gray", "green", "gray"]


def test_score_yellow_not_double_counted():
    # ABBEY (two B's). Guess BOBBY: B at pos2 is green, B at pos0 is yellow
    # (matches the remaining B at pos1 in ABBEY). Second guess-B at pos3 → gray.
    result = game_logic.score_guess("BOBBY", "ABBEY")
    assert result == ["yellow", "gray", "green", "gray", "green"]


def test_is_win():
    assert game_logic.is_win(["green", "green", "green", "green", "green"])


def test_is_not_win():
    assert not game_logic.is_win(["green", "green", "green", "green", "yellow"])
    assert not game_logic.is_win(["gray"] * 5)


# ---------------------------------------------------------------------------
# Integration tests: game creation
# ---------------------------------------------------------------------------

def test_create_game_valid():
    r = client.post("/games", json={"word_length": 5})
    assert r.status_code == 201
    data = r.json()
    assert data["word_length"] == 5
    assert data["max_turns"] == 6
    assert data["status"] == "in_progress"
    assert data["guesses"] == []
    assert data["remaining_turns"] == 6
    assert "id" in data
    assert data.get("answer") is None


def test_create_game_valid_length_8():
    r = client.post("/games", json={"word_length": 8})
    assert r.status_code == 201
    assert r.json()["max_turns"] == 9


def test_create_game_invalid_length_low():
    r = client.post("/games", json={"word_length": 4})
    assert r.status_code == 422


def test_create_game_invalid_length_high():
    r = client.post("/games", json={"word_length": 9})
    assert r.status_code == 422


# ---------------------------------------------------------------------------
# Integration tests: game retrieval
# ---------------------------------------------------------------------------

def test_get_game_not_found():
    r = client.get("/games/nonexistent-id-12345")
    assert r.status_code == 404
    data = r.json()
    assert data["code"] == "GAME_NOT_FOUND"
    assert "message" in data


def test_get_game_valid():
    r = client.post("/games", json={"word_length": 5})
    game_id = r.json()["id"]
    r2 = client.get(f"/games/{game_id}")
    assert r2.status_code == 200
    assert r2.json()["id"] == game_id


# ---------------------------------------------------------------------------
# Integration tests: guess validation
# ---------------------------------------------------------------------------

def test_invalid_guess_wrong_length():
    r = client.post("/games", json={"word_length": 5})
    game_id = r.json()["id"]
    r2 = client.post(f"/games/{game_id}/guesses", json={"guess": "ABC"})
    assert r2.status_code == 400
    data = r2.json()
    assert data["code"] == "INVALID_GUESS_LENGTH"
    assert "message" in data


def test_invalid_guess_not_a_word():
    r = client.post("/games", json={"word_length": 5})
    game_id = r.json()["id"]
    r2 = client.post(f"/games/{game_id}/guesses", json={"guess": "ZZZZZ"})
    assert r2.status_code == 400
    data = r2.json()
    assert data["code"] == "INVALID_WORD"
    assert "message" in data


def test_guess_after_win_returns_400(monkeypatch):
    import word_repository
    monkeypatch.setattr(word_repository, "get_random_word", lambda length: "CRANE")
    monkeypatch.setattr(word_repository, "is_valid_word", lambda word, length: True)
    r = client.post("/games", json={"word_length": 5})
    game_id = r.json()["id"]
    client.post(f"/games/{game_id}/guesses", json={"guess": "CRANE"})
    r2 = client.post(f"/games/{game_id}/guesses", json={"guess": "CRANE"})
    assert r2.status_code == 400
    assert r2.json()["code"] == "GAME_COMPLETED"


# ---------------------------------------------------------------------------
# Integration tests: case normalization
# ---------------------------------------------------------------------------

def test_guess_lowercase_normalized(monkeypatch):
    import word_repository
    monkeypatch.setattr(word_repository, "get_random_word", lambda length: "CRANE")
    monkeypatch.setattr(word_repository, "is_valid_word", lambda word, length: True)
    r = client.post("/games", json={"word_length": 5})
    game_id = r.json()["id"]
    r2 = client.post(f"/games/{game_id}/guesses", json={"guess": "crane"})
    assert r2.status_code == 200
    assert r2.json()["guesses"][-1]["guess"] == "CRANE"


def test_guess_mixedcase_normalized(monkeypatch):
    import word_repository
    monkeypatch.setattr(word_repository, "get_random_word", lambda length: "CRANE")
    monkeypatch.setattr(word_repository, "is_valid_word", lambda word, length: True)
    r = client.post("/games", json={"word_length": 5})
    game_id = r.json()["id"]
    r2 = client.post(f"/games/{game_id}/guesses", json={"guess": "CrAnE"})
    assert r2.status_code == 200
    assert r2.json()["guesses"][-1]["guess"] == "CRANE"


# ---------------------------------------------------------------------------
# Integration tests: win / loss transitions
# ---------------------------------------------------------------------------

def test_win_transition(monkeypatch):
    import word_repository
    monkeypatch.setattr(word_repository, "get_random_word", lambda length: "CRANE")
    monkeypatch.setattr(word_repository, "is_valid_word", lambda word, length: True)
    r = client.post("/games", json={"word_length": 5})
    game_id = r.json()["id"]
    r2 = client.post(f"/games/{game_id}/guesses", json={"guess": "CRANE"})
    assert r2.status_code == 200
    body = r2.json()
    assert body["status"] == "won"
    assert body["guesses"][-1]["feedback"] == ["green"] * 5
    assert body.get("answer") is None


def test_loss_transition(monkeypatch):
    import word_repository
    monkeypatch.setattr(word_repository, "get_random_word", lambda length: "CRANE")
    monkeypatch.setattr(word_repository, "is_valid_word", lambda word, length: True)
    r = client.post("/games", json={"word_length": 5})
    game_id = r.json()["id"]
    for _ in range(6):  # max_turns = 5+1 = 6
        r2 = client.post(f"/games/{game_id}/guesses", json={"guess": "ABCDE"})
    assert r2.status_code == 200
    body = r2.json()
    assert body["status"] == "lost"
    assert body["answer"] == "CRANE"


def test_remaining_turns_decrements(monkeypatch):
    import word_repository
    monkeypatch.setattr(word_repository, "get_random_word", lambda length: "CRANE")
    monkeypatch.setattr(word_repository, "is_valid_word", lambda word, length: True)
    r = client.post("/games", json={"word_length": 5})
    game_id = r.json()["id"]
    assert r.json()["remaining_turns"] == 6
    r2 = client.post(f"/games/{game_id}/guesses", json={"guess": "ABCDE"})
    assert r2.json()["remaining_turns"] == 5
