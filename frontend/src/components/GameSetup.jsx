import { useState } from "react";

const LENGTHS = [5, 6, 7, 8];

export default function GameSetup({ onStart }) {
  const [wordLength, setWordLength] = useState(5);

  return (
    <div className="setup">
      <p className="setup-label">Select word length</p>
      <div className="setup-controls">
        {LENGTHS.map((n) => (
          <button
            key={n}
            className={`length-btn${wordLength === n ? " active" : ""}`}
            onClick={() => setWordLength(n)}
          >
            {n}
          </button>
        ))}
      </div>
      <button className="start-btn" onClick={() => onStart(wordLength)}>
        New Game
      </button>
    </div>
  );
}
