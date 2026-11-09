#!/usr/bin/env python3
"""
Tests for Delta.

    python3 tests/run_tests.py
"""

import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DELTA = os.path.join(ROOT, "delta.py")
EXAMPLES = os.path.join(ROOT, "examples")
PYTHON = sys.executable


# Proofs that should check out, with a phrase the report must contain.
ACCEPTED = [
    ("reciprocal.delta", "no counterexample"),
    ("affine.delta", "no counterexample"),
    # the original flat notation, parsed to the same proof object
    ("old_style.delta", "no counterexample"),
]

# Proofs that should be refused, with where the complaint lands.
REFUSED = [
    ("errors/wrong_order.delta", "stderr", "'n' does not exist yet"),
    ("errors/wrong_n.delta", "stdout", "A COUNTEREXAMPLE"),
]


def run(path, eps=None):
    command = [PYTHON, DELTA, "run"]
    if eps is not None:
        command += ["--eps", eps]
    command.append(path)
    return subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
    )


def main():
    passed = 0
    failed = 0

    for name, phrase in ACCEPTED:
        path = os.path.join(EXAMPLES, name)
        result = run(path)
        if result.returncode != 0:
            failed += 1
            print("FAIL %s: exit %d\n%s" % (name, result.returncode,
                                            result.stderr))
            continue
        if phrase not in result.stdout:
            failed += 1
            print("FAIL %s: expected %r" % (name, phrase))
            print(result.stdout)
            continue
        passed += 1
        print("ok   %-28s is accepted" % name)

    for name, stream, phrase in REFUSED:
        path = os.path.join(EXAMPLES, name)
        result = run(path)
        if result.returncode != 1:
            failed += 1
            print("FAIL %s: expected exit 1, got %d" % (name, result.returncode))
            continue
        text = result.stderr if stream == "stderr" else result.stdout
        if phrase not in text:
            failed += 1
            print("FAIL %s: expected %r in %s" % (name, phrase, stream))
            print(text)
            continue
        passed += 1
        print("ok   %-28s is refused, saying %r" % (name, phrase))

    # The demonstration: the same proof, two sample sets, two verdicts.
    liar = os.path.join(EXAMPLES, "liar.delta")
    result = run(liar)
    if result.returncode == 0 and "no counterexample" in result.stdout:
        passed += 1
        print("ok   %-28s passes the default sample" % "liar.delta")
    else:
        failed += 1
        print("FAIL liar.delta: expected it to pass the default sample")
        print(result.stdout)

    result = run(liar, eps="1/100000000,1")
    if result.returncode == 1 and "A COUNTEREXAMPLE" in result.stdout:
        passed += 1
        print("ok   %-28s is caught when the sample is widened" % "liar.delta")
    else:
        failed += 1
        print("FAIL liar.delta: expected a counterexample, exit %d"
              % result.returncode)
        print(result.stdout)

    # One proof, two notations.
    def notation(command, name):
        return subprocess.run(
            [PYTHON, DELTA, command, os.path.join(EXAMPLES, name)],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            universal_newlines=True)

    result = notation("show", "reciprocal.delta")
    if "for every eps, where eps > 0" in result.stdout \
            and "        there is N" in result.stdout:
        passed += 1
        print("ok   %-28s renders the indented form" % "show")
    else:
        failed += 1
        print("FAIL show: indentation missing")
        print(result.stdout)

    result = notation("symbols", "reciprocal.delta")
    if "\u2200eps" in result.stdout and "\u2203N" in result.stdout:
        passed += 1
        print("ok   %-28s renders the symbolic form" % "symbols")
    else:
        failed += 1
        print("FAIL symbols")
        print(result.stdout)

    # The game view.
    def play(path, eps=None):
        command = [PYTHON, DELTA, "play"]
        if eps is not None:
            command += ["--eps", eps]
        command.append(path)
        return subprocess.run(command, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, universal_newlines=True)

    result = play(os.path.join(EXAMPLES, "reciprocal.delta"))
    if "You won" in result.stdout and "order of play" in result.stdout:
        passed += 1
        print("ok   %-28s plays out as a win" % "reciprocal.delta")
    else:
        failed += 1
        print("FAIL play reciprocal.delta")
        print(result.stdout)

    result = play(os.path.join(EXAMPLES, "liar.delta"), eps="1/100000000")
    if "The Challenger won" in result.stdout:
        passed += 1
        print("ok   %-28s shows the Challenger winning" % "liar.delta")
    else:
        failed += 1
        print("FAIL play liar.delta")
        print(result.stdout)

    print()
    print("%d passed, %d failed" % (passed, failed))
    return 1 if failed else 0

if __name__ == "__main__":
    sys.exit(main())
