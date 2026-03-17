export default function GameStatus({ game, onPlayAgain }) {
  const won = game.status === "won";
  const turnsUsed = game.guesses.length;

  return (
    <div className="game-status">
      <p className="status-message">
        {won
          ? `You got it in ${turnsUsed}!`
          : `The word was ${game.answer ?? "????"}`}
      </p>
      <button className="play-again-btn" onClick={onPlayAgain}>
        Play Again
      </button>
    </div>
  );
}
