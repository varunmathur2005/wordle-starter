"""
One-time script to generate word list files for the Wordle backend.
Fetches the dwyl/english-words public domain word list and filters by length.

Usage:
    python scripts/generate_words.py
"""

import re
import pathlib
import urllib.request

URL = "https://raw.githubusercontent.com/dwyl/english-words/master/words_alpha.txt"

def main():
    print(f"Fetching word list from {URL}...")
    raw = urllib.request.urlopen(URL).read().decode()
    all_words = raw.splitlines()
    print(f"  Total words fetched: {len(all_words)}")

    output_dir = pathlib.Path(__file__).parent.parent / "backend" / "words"
    output_dir.mkdir(exist_ok=True)

    for n in [5, 6, 7, 8]:
        words = sorted(
            {w.upper() for w in all_words if re.fullmatch(r"[a-zA-Z]+", w) and len(w) == n}
        )
        path = output_dir / f"words_{n}.txt"
        path.write_text("\n".join(words) + "\n")
        print(f"  words_{n}.txt: {len(words)} words")

    print("Done.")

if __name__ == "__main__":
    main()
