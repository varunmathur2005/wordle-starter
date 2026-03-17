// variant: "empty" | "filled" | "green" | "yellow" | "gray"
export default function Cell({ letter = "", variant = "empty" }) {
  return (
    <div className={`cell cell--${variant}`}>
      {letter}
    </div>
  );
}
