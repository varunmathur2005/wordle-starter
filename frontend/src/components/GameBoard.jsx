import { useState, useEffect, useCallback } from "react";
import { submitGuess } from "../api";
import GuessRow from "./GuessRow";
import Keyboard from "./Keyboard";

export default function GameBoard({ game, onGuessResult, disabled }) {
  const [currentInput, setCurrentInput] = useState("");
  const [inputError, setInputError] = useState(null);

  const { id, word_length, max_turns, guesses } = game;
  const completedCount = guesses.length;

  // Cell size scales down for longer words to avoid overflow on narrow screens.
  const cellSize = word_length <= 6 ? "62px" : "50px";

  const handleKey = useCallback(
    async (key) => {
      if (disabled) return;
      setInputError(null);

      if (key === "ENTER") {
        if (currentInput.length !== word_length) {
          setInputError(`Word must be ${word_length} letters`);
          return;
        }
        try {
          const updatedGame = await submitGuess(id, currentInput);
          setCurrentInput("");
          onGuessResult(updatedGame);
        } catch (err) {
          setInputError(err.message ?? "Something went wrong");
        }
        return;
      }

      if (key === "BACKSPACE") {
        setCurrentInput((prev) => prev.slice(0, -1));
        return;
      }

      if (/^[A-Z]$/.test(key) && currentInput.length < word_length) {
        setCurrentInput((prev) => prev + key);
      }
    },
    [disabled, currentInput, word_length, id, onGuessResult]
  );

  // Physical keyboard listener — cleanup is required to avoid duplicate listeners
  // in React StrictMode (which mounts/unmounts effects twice in development).
  useEffect(() => {
    function onKeyDown(e) {
      const k = e.key.toUpperCase();
      if (k === "ENTER" || k === "BACKSPACE" || /^[A-Z]$/.test(k)) {
        e.preventDefault();
        handleKey(k);
      }
    }
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [handleKey]);

  // Build rows: submitted rows, then the active draft row, then empty future rows.
  const rows = Array.from({ length: max_turns }, (_, i) => {
    if (i < completedCount) {
      return (
        <GuessRow
          key={i}
          guess={guesses[i].guess}
          feedback={guesses[i].feedback}
          wordLength={word_length}
        />
      );
    }
    if (i === completedCount && !disabled) {
      return (
        <GuessRow
          key={i}
          guess={currentInput}
          feedback={null}
          wordLength={word_length}
        />
      );
    }
    return <GuessRow key={i} guess="" feedback={null} wordLength={word_length} />;
  });

  return (
    <div className="game-board">
      <div className="grid" style={{ "--cell-size": cellSize }}>
        {rows}
      </div>
      {inputError && <p className="input-error">{inputError}</p>}
      <Keyboard guesses={game.guesses} onKey={handleKey} disabled={disabled} />
    </div>
  );
}
