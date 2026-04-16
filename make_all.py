import re
import sys
import math
from pathlib import Path

PATTERN_COUNT = 243

def load_words(path: str):
    text = Path(path).read_text(encoding="utf-8", errors="ignore").lower()
    words = []
    for line in text.splitlines():
        w = line.strip()
        if len(w) == 5 and re.fullmatch(r"[a-z]{5}", w):
            words.append(w)
    return words

def word_to_ints(w: str):
    return [ord(c) - 97 for c in w]

def pattern_code(g, a):
    # g, a are lists of 5 ints 0..25
    res = [0]*5
    freq = [0]*26

    for i in range(5):
        if g[i] == a[i]:
            res[i] = 2
        else:
            freq[a[i]] += 1

    for i in range(5):
        if res[i] == 0:
            gi = g[i]
            if freq[gi] > 0:
                res[i] = 1
                freq[gi] -= 1

    code = 0
    pow3 = 1
    for i in range(5):
        code += res[i] * pow3
        pow3 *= 3
    return code  # 0..242

def main():
    if len(sys.argv) != 4:
        print("Usage: python3 make_all.py answers.txt allowed.txt OUT_DIR")
        sys.exit(1)

    answers_path, allowed_path, out_dir = sys.argv[1], sys.argv[2], Path(sys.argv[3])
    out_dir.mkdir(parents=True, exist_ok=True)

    answers = load_words(answers_path)
    allowed_only = load_words(allowed_path)

    # Keep answers order as given, but clean it
    answers_clean = answers

    # Allowed is combined + sorted (must match app)
    allowed_combined_sorted = sorted(set(allowed_only + answers_clean))

    A, G = len(answers_clean), len(allowed_combined_sorted)
    total = A * G
    print(f"answers={A}, allowed={G}, patterns bytes={total} (~{total/1_000_000:.1f} MB)")

    answers_i = [word_to_ints(w) for w in answers_clean]
    allowed_i = [word_to_ints(w) for w in allowed_combined_sorted]

    table = bytearray(total)
    for gi in range(G):
        base = gi * A
        g = allowed_i[gi]
        for ai in range(A):
            table[base + ai] = pattern_code(g, answers_i[ai])
        if gi % 800 == 0:
            print(f"... {gi}/{G}")

    (out_dir / "patterns.bin").write_bytes(table)
    (out_dir / "answers_clean.txt").write_text("\n".join(answers_clean) + "\n", encoding="utf-8")
    (out_dir / "allowed_combined_sorted.txt").write_text("\n".join(allowed_combined_sorted) + "\n", encoding="utf-8")

    print("Wrote:")
    print(" - patterns.bin")
    print(" - answers_clean.txt")
    print(" - allowed_combined_sorted.txt")

if __name__ == "__main__":
    main()
