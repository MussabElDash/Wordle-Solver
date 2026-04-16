import math
from pathlib import Path

PATTERN_COUNT = 243

def load_words(path):
    return [line.strip().lower() for line in Path(path).read_text(encoding="utf-8").splitlines()
            if len(line.strip()) == 5 and line.strip().isalpha()]

def main():
    answers = load_words("answers_clean.txt")
    allowed = load_words("allowed_combined_sorted.txt")
    A, G = len(answers), len(allowed)

    data = Path("patterns.bin").read_bytes()
    if len(data) != A * G:
        raise SystemExit(f"patterns.bin size mismatch: expected {A*G}, got {len(data)}")

    # candidates = all answers at start: indices 0..A-1
    dn = float(A)

    scored = []
    for gi in range(G):
        base = gi * A
        counts = [0] * PATTERN_COUNT

        # bucket counts over ALL answers
        for ai in range(A):
            counts[data[base + ai]] += 1

        # metrics
        entropy = 0.0
        exp_rem = 0.0
        worst = 0
        for c in counts:
            if c:
                if c > worst: worst = c
                p = c / dn
                entropy -= p * math.log(p, 2)
                exp_rem += (c * c) / dn

        scored.append((-entropy, worst, exp_rem, allowed[gi]))  # hybrid default sort keys

        if gi % 800 == 0:
            print(f"... {gi}/{G}")

    # Hybrid default:
    # 1) (effectively) max entropy (since we put -entropy)
    # 2) min worst bucket
    # 3) min expected remaining
    # 4) alphabetical
    scored.sort()

    topN = 200
    openers = [w for _, _, _, w in scored[:topN]]
    Path("openers.txt").write_text("\n".join(openers) + "\n", encoding="utf-8")

    print("Wrote openers.txt (top", topN, ")")

if __name__ == "__main__":
    main()
