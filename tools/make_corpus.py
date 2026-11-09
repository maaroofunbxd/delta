#!/usr/bin/env python3
"""
Generate the Delta practice corpus.

Every proof here is produced from a family with a principled choice of N --
no fudged constants.  tests/corpus.py then runs all of them through Delta,
so the corpus cannot silently rot: if a proof stops being valid, the runner
says so.

    python3 tools/make_corpus.py
"""

import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "examples", "corpus")

FAMILIES = []


def add(family, seq, limit, n_expr, note):
    FAMILIES.append({
        "family": family,
        "seq": seq,
        "limit": limit,
        "n": n_expr,
        "note": note,
    })


# --- constant -------------------------------------------------------------
# |c - c| is 0, so any N at all works.
for c in ["0", "1", "-1", "5", "42", "-7", "1/2", "-3/4"]:
    add("constant", c, c if not c.startswith("-") else "(%s)" % c, "0",
        "a constant sequence is already at its limit")

# --- c / n ----------------------------------------------------------------
for num, den in [(1, 1), (2, 1), (3, 1), (5, 1), (10, 1), (100, 1), (-1, 1),
                 (-2, 1), (1, 2), (3, 4), (-5, 1), (7, 1)]:
    if den == 1:
        seq, n_expr = "%d / n" % num, "ceil(%d / eps)" % abs(num)
    else:
        seq = "%d / (%d * n)" % (num, den)
        n_expr = "ceil(%d / (%d * eps))" % (abs(num), den)
    add("c / n", seq, "0", n_expr, "|c/n| = |c|/n, so N = |c|/eps")

# --- c / n^2 --------------------------------------------------------------
for num, den in [(1, 1), (2, 1), (3, 1), (5, 1), (10, 1), (-1, 1), (-4, 1),
                 (1, 2), (2, 3), (-7, 1), (20, 1), (50, 1)]:
    if den == 1:
        seq = "%d / (n * n)" % num
        n_expr = "ceil(%d / eps)" % abs(num)
    else:
        seq = "%d / (%d * n * n)" % (num, den)
        n_expr = "ceil(%d / (%d * eps))" % (abs(num), den)
    add("c / n^2", seq, "0", n_expr,
        "n > |c|/eps gives n^2 > |c|/eps as well")

# --- c / n^3 --------------------------------------------------------------
for num in [1, 2, 6, -1, 10, 24]:
    add("c / n^3", "%d / (n * n * n)" % num, "0",
        "ceil(%d / eps)" % abs(num),
        "same idea, one more factor of n")

# --- (a n + b) / n  ->  a -------------------------------------------------
for a, b in [(2, 1), (3, 2), (-1, 4), (5, -3), (1, 7), (4, 1), (-2, -5),
             (7, 10), (1, -1), (6, 2)]:
    add("(a n + b) / n",
        "(%d * n + (%d)) / n" % (a, b), a, "ceil(%d / eps)" % abs(b),
        "|(an+b)/n - a| = |b|/n")

# --- n / (n + k) -> 1 -----------------------------------------------------
for k in [1, 2, 3, 5, 10, 100, 7, 25]:
    add("n / (n + k)", "n / (n + %d)" % k, "1", "ceil(%d / eps)" % k,
        "|n/(n+k) - 1| = k/(n+k) < k/n")

# --- c/n + d/n^2 -> 0 -----------------------------------------------------
for c, d in [(1, 1), (2, 1), (1, 3), (3, 2), (-1, 1), (5, -1), (2, 7),
             (4, 4)]:
    total = abs(c) + abs(d)
    add("c/n + d/n^2",
        "(%d) / n + (%d) / (n * n)" % (c, d), "0",
        "ceil(%d / eps)" % total,
        "bounded by (|c| + |d|)/n")

# --- (a n + b) / (c n + d) -> a/c -----------------------------------------
for a, b, c, d in [(1, 1, 2, 3), (3, 1, 1, 2), (2, -1, 5, 1), (1, 4, 3, -2),
                   (5, 2, 2, 7), (-1, 3, 4, 1), (7, 1, 3, 5), (2, 5, 1, 6),
                   (4, -3, 2, 1), (9, 2, 3, 4), (1, -5, 6, 2), (8, 1, 4, 3)]:
    diff = abs(c * b - a * d)
    add("(a n + b) / (c n + d)",
        "(%d * n + (%d)) / (%d * n + (%d))" % (a, b, c, d),
        "%d / %d" % (a, c),
        "ceil(%d / (%d * eps))" % (diff, c * c),
        "|... - a/c| = |cb - ad| / |c(cn+d)|, bounded by |cb-ad|/(c^2 n)")

# --- (a n^2 + b) / (c n^2 + d) -> a/c -------------------------------------
for a, b, c, d in [(1, 1, 2, 3), (3, 2, 1, 5), (2, -1, 4, 1), (1, 7, 3, 2),
                   (5, 1, 2, 9), (-1, 2, 3, 1), (4, 3, 1, 8), (7, -2, 2, 1),
                   (1, 5, 5, 2), (6, 1, 3, 7)]:
    diff = abs(c * b - a * d)
    add("(a n^2 + b) / (c n^2 + d)",
        "(%d * n * n + (%d)) / (%d * n * n + (%d))" % (a, b, c, d),
        "%d / %d" % (a, c),
        "ceil(%d / (%d * eps))" % (diff, c * c),
        "bounded by |cb-ad|/(c^2 n^2)")

# --- alternating sign over n -> 0 -----------------------------------------
SIGN = "(2 * (n - 2 * floor(n / 2)) - 1)"
for _ in range(4):
    add("(+-1)^n / n", "%s / n" % SIGN, "0", "ceil(1 / eps)",
        "the sign does not matter; |a(n)| = 1/n")

# --- mixed, one step harder ----------------------------------------------
MIXED = [
    ("n / (n * n + 1)", "0", "ceil(1 / eps)", "less than n/n^2 = 1/n"),
    ("(n - 1) / (n + 1)", "1", "ceil(2 / eps)", "|... - 1| = 2/(n+1) < 2/n"),
    ("(n + 1) / (2 * n + 3)", "1 / 2", "ceil(1 / (4 * eps))",
     "|... - 1/2| = 1/(4n + 6) < 1/(4n)"),
    ("(3 * n * n + n) / (n * n + 1)", "3", "ceil(1 / eps)",
     "|... - 3| = |n - 3|/(n^2 + 1), and that is under 1/n"),
    ("(n * n - 1) / (n * n + n)", "1", "ceil(1 / eps)",
     "|... - 1| = (n+1)/(n(n+1)) = 1/n exactly"),
    ("(2 * n + 1) / n", "2", "ceil(1 / eps)", "|... - 2| = 1/n"),
    ("(n + 5) / (2 * n)", "1 / 2", "ceil(5 / (2 * eps))",
     "|... - 1/2| = 5/(2n)"),
    ("(4 * n + 1) / (2 * n + 1)", "2", "ceil(1 / (2 * eps))",
     "|... - 2| = 1/(2(2n+1)) < 1/(4n)"),
    ("(n * n + 3) / (2 * n * n + 1)", "1 / 2", "ceil(5 / (4 * eps))",
     "|... - 1/2| = 5/(2(2n^2+1)) < 5/(4n^2)"),
    ("(1) / (n + 1)", "0", "ceil(1 / eps)", "smaller than 1/n"),
]
for seq, limit, n_expr, note in MIXED:
    add("mixed", seq, limit, n_expr, note)


TEMPLATE = """# {family}
# {note}

sequence a(n) = {seq}
claim a(n) -> {limit}

proof:
    for every eps, where eps > 0
        there is N = {n}
            for every n, where n > N
                abs(a(n) - {limit}) < eps
end
"""


def slug(text):
    out = []
    for ch in text:
        if ch.isalnum():
            out.append(ch)
        elif ch in " /^+-*()":
            out.append("_")
    slugged = "".join(out)
    while "__" in slugged:
        slugged = slugged.replace("__", "_")
    return slugged.strip("_").lower()


def main():
    if not os.path.isdir(OUT):
        os.makedirs(OUT)

    index = ["# Delta practice corpus", "",
             "Every proof here is checked by `tests/corpus.py`. None of them",
             "is hand-verified: if one breaks, the runner says so.", "",
             "| # | file | sequence | limit | N | family |",
             "|---|---|---|---|---|---|"]

    for number, item in enumerate(FAMILIES, start=1):
        name = "%03d_%s.delta" % (number, slug(item["family"]))
        path = os.path.join(OUT, name)
        with open(path, "w") as handle:
            handle.write(TEMPLATE.format(
                family=item["family"], note=item["note"], seq=item["seq"],
                limit=item["limit"], n=item["n"]))
        index.append("| %d | `%s` | `%s` | `%s` | `%s` | %s |"
                     % (number, name, item["seq"], item["limit"], item["n"],
                        item["family"]))

    index.append("")
    index.append("%d proofs." % len(FAMILIES))
    with open(os.path.join(OUT, "INDEX.md"), "w") as handle:
        handle.write("\n".join(index) + "\n")

    print("wrote %d proofs to %s" % (len(FAMILIES), OUT))


if __name__ == "__main__":
    main()
