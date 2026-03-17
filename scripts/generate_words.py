"""
One-time script to generate word list files for the Wordle backend.

Produces two sets of files per word length:
  words_{n}.txt    — broad valid-guess dictionary (dwyl/english-words, ~15k-50k words)
  answers_{n}.txt  — curated answer pool (google-20k-english, common everyday words)

Proper-noun filtering
---------------------
The google-20k frequency list includes proper nouns (names, cities, etc.).
Intersecting with the Collins Scrabble Words list (SOWPODS) removes them:
Scrabble rules prohibit proper nouns by definition, so words like AARON,
ADAMS, EMILY, SCOTT are absent from SOWPODS while common English words that
happen to also be names (GRACE, AMBER, SANDY, TERRY) are correctly kept.

Usage:
    python scripts/generate_words.py
"""

import re
import pathlib
import urllib.request

# Full alphabetic word corpus — used as the valid-guess dictionary.
WORDS_URL = "https://raw.githubusercontent.com/dwyl/english-words/master/words_alpha.txt"

# Top 20k most common US English words (no profanity) — used as the answer pool.
# Cross-referencing with WORDS_URL ensures answers are also valid guesses.
ANSWERS_URL = "https://raw.githubusercontent.com/first20hours/google-10000-english/master/20k.txt"

# Collins Scrabble Words (SOWPODS) — used to filter proper nouns from the answer pool.
# Scrabble rules prohibit proper nouns, so this list is free of names and place names.
SOWPODS_URL = "https://raw.githubusercontent.com/jesstess/Scrabble/master/scrabble/sowpods.txt"


def fetch_lines(url: str) -> list[str]:
    return urllib.request.urlopen(url).read().decode().splitlines()


def alpha_words_of_length(lines: list[str], length: int) -> set[str]:
    return {w.upper() for w in lines if re.fullmatch(r"[a-zA-Z]+", w) and len(w) == length}


def main():
    output_dir = pathlib.Path(__file__).parent.parent / "backend" / "words"
    output_dir.mkdir(exist_ok=True)

    print("Fetching full word list…")
    full_lines = fetch_lines(WORDS_URL)
    print(f"  {len(full_lines)} lines")

    print("Fetching common word list…")
    common_lines = fetch_lines(ANSWERS_URL)
    print(f"  {len(common_lines)} lines")

    print("Fetching Scrabble word list (SOWPODS) for proper-noun filtering…")
    sowpods = set(fetch_lines(SOWPODS_URL))
    print(f"  {len(sowpods)} words")

    for n in [5, 6, 7, 8]:
        full_set = alpha_words_of_length(full_lines, n)
        full_sorted = sorted(full_set)
        (output_dir / f"words_{n}.txt").write_text("\n".join(full_sorted) + "\n")
        print(f"  words_{n}.txt: {len(full_sorted)}")

        # Answers must be:
        #   1. In the full valid-guess set (so the answer is always a guessable word)
        #   2. In SOWPODS (filters out proper nouns, abbreviations, and non-English words)
        common_set = alpha_words_of_length(common_lines, n) & full_set & sowpods
        answer_sorted = sorted(common_set)
        (output_dir / f"answers_{n}.txt").write_text("\n".join(answer_sorted) + "\n")
        print(f"  answers_{n}.txt: {len(answer_sorted)}")

    print("Done.")


if __name__ == "__main__":
    main()
