import { useState } from "react";
import { createGame } from "./api";
import GameSetup from "./components/GameSetup";
import GameBoard from "./components/GameBoard";
import GameStatus from "./components/GameStatus";
import "./App.css";

export default function App() {
  const [game, setGame] = useState(null);
  const [error, setError] = useState(null);

  // Derive UI phase from game state — no separate phase variable needed.
  const isSetup = game === null;
  const isDone = game !== null && game.status !== "in_progress";

  async function handleStart(wordLength) {
    try {
      const newGame = await createGame(wordLength);
      setGame(newGame);
      setError(null);
    } catch (err) {
      setError(err.message ?? "Failed to start game. Is the backend running?");
    }
  }

  function handlePlayAgain() {
    setGame(null);
    setError(null);
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>WORDLE</h1>
      </header>

      {error && <div className="error-banner">{error}</div>}

      {isSetup && <GameSetup onStart={handleStart} />}

      {!isSetup && (
        <>
          <GameBoard
            game={game}
            onGuessResult={setGame}
            disabled={isDone}
          />
          {isDone && (
            <GameStatus game={game} onPlayAgain={handlePlayAgain} />
          )}
        </>
      )}
    </div>
  );
}
