import Cell from "./Cell";

export default function GuessRow({ guess = "", feedback = null, wordLength }) {
  return (
    <div className="guess-row">
      {Array.from({ length: wordLength }, (_, i) => {
        const letter = guess[i] ?? "";
        let variant = "empty";
        if (feedback) {
          variant = feedback[i];
        } else if (letter) {
          variant = "filled";
        }
        return <Cell key={i} letter={letter} variant={variant} />;
      })}
    </div>
  );
}
