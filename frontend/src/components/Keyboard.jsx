const ROWS = [
  ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
  ["A", "S", "D", "F", "G", "H", "J", "K", "L"],
  ["ENTER", "Z", "X", "C", "V", "B", "N", "M", "BACKSPACE"],
];

// Priority for letter state: a confirmed green should never be downgraded.
const PRIORITY = { green: 3, yellow: 2, gray: 1 };

export default function Keyboard({ guesses, onKey, disabled }) {
  // Build the best-known state for each letter from all submitted guesses.
  const letterState = {};
  for (const { guess, feedback } of guesses) {
    for (let i = 0; i < guess.length; i++) {
      const letter = guess[i];
      const fb = feedback[i];
      if ((PRIORITY[fb] ?? 0) > (PRIORITY[letterState[letter]] ?? 0)) {
        letterState[letter] = fb;
      }
    }
  }

  return (
    <div className="keyboard">
      {ROWS.map((row, ri) => (
        <div key={ri} className="keyboard-row">
          {row.map((key) => {
            const state = letterState[key];
            return (
              <button
                key={key}
                className={[
                  "key",
                  state ? `key--${state}` : "",
                  key.length > 1 ? "key--wide" : "",
                ]
                  .filter(Boolean)
                  .join(" ")}
                onClick={() => !disabled && onKey(key)}
                disabled={disabled}
              >
                {key === "BACKSPACE" ? "⌫" : key}
              </button>
            );
          })}
        </div>
      ))}
    </div>
  );
}
