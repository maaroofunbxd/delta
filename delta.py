#!/usr/bin/env python3
"""
Delta
=====
A small language for writing epsilon-delta arguments in words, and having the
one mistake that matters caught immediately.

Why the notation is hard
------------------------
In Lean you write:

    example (ε : ℝ) (hε : 0 < ε) : ∃ N : ℕ, ∀ n ≥ N, |(1:ℝ)/n - 0| < ε := by
      obtain ⟨N, hN⟩ := exists_nat_gt (1 / ε)
      refine ⟨N, fun n hn => ?_⟩
      ...

The symbols are not the real obstacle, and neither are the tactics.  The real
obstacle is the *game*: in `∀ε ∃N ∀n`, N is allowed to depend on ε and is not
allowed to depend on n.  Almost every beginner mistake in analysis is a
violation of that rule, and it is invisible in ordinary mathematical writing
because prose does not show you scopes.

Why N cannot depend on n is not a deep theorem.  It is just that **ε is
introduced first, so N is inside ε's scope, and n is introduced afterwards,
so n is not yet in scope.**  Nesting does the work.

That is what this language gives you, in words:

    given eps with eps > 0
    choose N = ceil(1 / eps)
    take n with n > N
    conclude abs(a(n) - 0) < eps

Write `choose N = floor(n / 2)` and you get told, at that line, why it is
impossible -- because `n` does not exist yet.

What this is not
----------------
It does not prove anything.  It checks the shape of the argument, enforces the
scoping, and then *spot checks* your choice of N by exact rational arithmetic
at sampled values of eps.  Getting a clean run is reassuring.  Getting a
counterexample is conclusive.  Neither is a proof, and the tool says so.

Usage:
    python3 delta.py run   path/to/proof.delta
    python3 delta.py show  path/to/proof.delta
"""

from __future__ import annotations

import math
import sys
from dataclasses import dataclass, field
from fractions import Fraction


# ---------------------------------------------------------------------------
# 1. Errors
# ---------------------------------------------------------------------------

class DeltaError(Exception):
    def __init__(self, message, line=None, col=None, hint=None, kind="error"):
        super().__init__(message)
        self.message = message
        self.line = line
        self.col = col
        self.hint = hint
        self.kind = kind


def render_error(err, source, filename):
    lines = source.split("\n")
    out = ["%s: %s: %s" % (filename, err.kind, err.message)]
    if err.line is not None:
        out.append("")
        out.append("  at line %d" % err.line)
        if 1 <= err.line <= len(lines):
            out.append("      " + lines[err.line - 1])
            if err.col:
                out.append("      " + " " * (err.col - 1) + "^")
    if err.hint:
        out.append("")
        for i, hint_line in enumerate(err.hint.split("\n")):
            out.append(("  hint: " if i == 0 else "        ") + hint_line)
    return "\n".join(out)


# ---------------------------------------------------------------------------
# 2. Tokens and the reader
# ---------------------------------------------------------------------------

KEYWORDS = {
    # the indented form: plain quantifier phrases, no new vocabulary
    "for", "every", "there", "is", "where",
    # the original flat form, still accepted
    "sequence", "claim", "proof", "end",
    "given", "with", "choose", "take", "conclude",
}

SYMBOLS = set("(),=+-*/<>:")
TWO_CHAR = {"->", ">=", "<=", "=="}


class Token:
    __slots__ = ("kind", "text", "line", "col", "value")

    def __init__(self, kind, text, line, col, value=None):
        self.kind = kind
        self.text = text
        self.line = line
        self.col = col
        self.value = value


def describe(tok):
    if tok.kind == "NEWLINE":
        return "the end of the line"
    if tok.kind == "EOF":
        return "the end of the file"
    if tok.kind in ("NAME", "NUMBER"):
        return "'%s'" % tok.text
    return "'%s'" % tok.kind


def tokenize(source):
    tokens = []
    i = 0
    line = 1
    col = 1
    n = len(source)

    def add(kind, text, ln, cl, value=None):
        tokens.append(Token(kind, text, ln, cl, value))

    while i < n:
        c = source[i]

        if c == "\n":
            add("NEWLINE", "\n", line, col)
            i += 1
            line += 1
            col = 1
            continue

        if c in " \t\r":
            i += 1
            col += 1
            continue

        if c == "#":
            while i < n and source[i] != "\n":
                i += 1
            continue

        if c.isdigit():
            start_line, start_col = line, col
            start = i
            while i < n and (source[i].isdigit() or source[i] == "."):
                i += 1
                col += 1
            text = source[start:i]
            if text.count(".") > 1:
                raise DeltaError("'%s' is not a number" % text,
                                 start_line, start_col)
            if "." in text:
                add("NUMBER", text, start_line, start_col, Fraction(text))
            else:
                add("NUMBER", text, start_line, start_col, Fraction(int(text)))
            continue

        if c.isalpha() or c == "_":
            start_line, start_col = line, col
            start = i
            while i < n and (source[i].isalnum() or source[i] == "_"):
                i += 1
                col += 1
            text = source[start:i]
            add(text if text in KEYWORDS else "NAME", text, start_line,
                start_col)
            continue

        pair = source[i:i + 2]
        if pair in TWO_CHAR:
            add(pair, pair, line, col)
            i += 2
            col += 2
            continue

        if c in SYMBOLS:
            add(c, c, line, col)
            i += 1
            col += 1
            continue

        raise DeltaError("I do not know the character '%s'" % c, line, col)

    add("EOF", "", line, col)
    return tokens


# ---------------------------------------------------------------------------
# 3. Syntax tree
# ---------------------------------------------------------------------------

@dataclass
class Node:
    line: int = 0
    col: int = 0


@dataclass
class Num(Node):
    value: object = None


@dataclass
class Name(Node):
    name: str = ""


@dataclass
class Call(Node):
    name: str = ""
    args: list = field(default_factory=list)


@dataclass
class BinOp(Node):
    op: str = ""
    left: object = None
    right: object = None


@dataclass
class Neg(Node):
    expr: object = None


@dataclass
class Compare(Node):
    op: str = ""
    left: object = None
    right: object = None


@dataclass
class Given(Node):
    name: str = ""
    condition: object = None


@dataclass
class Choose(Node):
    name: str = ""
    expr: object = None


@dataclass
class Take(Node):
    name: str = ""
    condition: object = None


@dataclass
class Conclude(Node):
    condition: object = None


@dataclass
class Sequence(Node):
    name: str = ""
    variable: str = ""
    expr: object = None


@dataclass
class Claim(Node):
    name: str = ""
    variable: str = ""
    limit: object = None


@dataclass
class Proof(Node):
    name: str = ""
    sequence: object = None
    claim: object = None
    steps: list = field(default_factory=list)


# ---------------------------------------------------------------------------
# 4. Parser
# ---------------------------------------------------------------------------

class Parser:
    def __init__(self, tokens, source):
        self.toks = tokens
        self.pos = 0
        self.source = source

    def peek(self, ahead=0):
        return self.toks[min(self.pos + ahead, len(self.toks) - 1)]

    def at(self, kind):
        return self.peek().kind == kind

    def advance(self):
        tok = self.toks[self.pos]
        if self.pos < len(self.toks) - 1:
            self.pos += 1
        return tok

    def accept(self, kind):
        if self.at(kind):
            return self.advance()
        return None

    def expect(self, kind, after=None):
        if self.at(kind):
            return self.advance()
        tok = self.peek()
        msg = "expected '%s'" % kind
        if after:
            msg += " " + after
        msg += ", but found %s" % describe(tok)
        raise DeltaError(msg, tok.line, tok.col)

    def skip_newlines(self):
        while self.at("NEWLINE"):
            self.advance()

    def parse(self):
        self.skip_newlines()
        sequence = None
        claim = None
        proof = None

        while not self.at("EOF"):
            if self.at("sequence"):
                sequence = self.parse_sequence()
            elif self.at("claim"):
                claim = self.parse_claim()
            elif self.at("proof"):
                proof = self.parse_proof()
            else:
                tok = self.peek()
                raise DeltaError(
                    "expected 'sequence', 'claim' or 'proof', but found %s"
                    % describe(tok), tok.line, tok.col)
            self.skip_newlines()

        if sequence is None:
            raise DeltaError("this file has no 'sequence'")
        if proof is None:
            raise DeltaError(
                "this file has no 'proof'",
                hint="a proof looks like:\n"
                     "  proof:\n"
                     "      given eps with eps > 0\n"
                     "      choose N = ceil(1 / eps)\n"
                     "      take n with n > N\n"
                     "      conclude abs(a(n) - 0) < eps\n"
                     "  end")

        proof.sequence = sequence
        proof.claim = claim
        return proof

    def parse_sequence(self):
        start = self.expect("sequence")
        name = self.expect("NAME", "after the word 'sequence'")
        self.expect("(", "after the sequence name")
        variable = self.expect("NAME", "as the sequence's variable")
        self.expect(")", "to close the variable")
        self.expect("=", "after the variable")
        expr = self.parse_expression()
        return Sequence(line=start.line, col=start.col, name=name.text,
                        variable=variable.text, expr=expr)

    def parse_claim(self):
        start = self.expect("claim")
        name = self.expect("NAME", "after the word 'claim'")
        self.expect("(", "after the sequence name")
        variable = self.expect("NAME", "as the sequence's variable")
        self.expect(")", "to close the variable")
        self.expect("->", "to say what the sequence tends to")
        limit = self.parse_expression()
        return Claim(line=start.line, col=start.col, name=name.text,
                     variable=variable.text, limit=limit)

    def parse_proof(self):
        start = self.expect("proof")
        self.expect(":", "after the word 'proof'")
        self.skip_newlines()

        if self.peek().kind in ("for", "there"):
            steps = self.parse_indented_proof()
        else:
            steps = self.parse_flat_proof(start)

        self.expect("end", "to close the proof")
        return Proof(line=start.line, col=start.col, steps=steps)

    def parse_flat_proof(self, start):
        steps = []
        while not self.at("end"):
            if self.at("EOF"):
                raise DeltaError("this proof is never closed",
                                 start.line, start.col,
                                 hint="add 'end' on its own line")
            steps.append(self.parse_step())
            self.skip_newlines()
        return steps

    # -- the indented form --------------------------------------------------

    def parse_indented_proof(self):
        """Read a proof whose nesting is shown by indentation.

        `for every` and `there is` open a scope; whatever is indented under
        one is inside it.  That is the whole notation: the containment you
        can see is the scope the checker enforces.
        """
        steps = []
        seen_for = 0
        kind, payload, body = self.parse_quantifier()

        while True:
            if kind == "for":
                seen_for += 1
                cls = Given if seen_for == 1 else Take
                steps.append(cls(line=payload["line"], col=payload["col"],
                                 name=payload["name"],
                                 condition=payload["condition"]))
            elif kind == "there":
                steps.append(Choose(line=payload["line"], col=payload["col"],
                                    name=payload["name"],
                                    expr=payload["expr"]))
            else:
                steps.append(Conclude(line=payload["line"], col=payload["col"],
                                      condition=payload["condition"]))
            if body is None:
                break
            kind, payload, body = body

        return steps

    def parse_quantifier(self):
        tok = self.peek()
        indent = tok.col

        if tok.kind == "for":
            self.advance()
            self.expect("every", "after the word 'for'")
            name = self.expect("NAME", "as the thing being quantified over")
            self.expect(",", "after the name '%s'" % name.text)
            self.expect("where", "after the comma")
            condition = self.parse_condition()
            self.end_of_line()
            body = self.parse_under(indent, tok)
            return ("for", {"line": tok.line, "col": tok.col,
                            "name": name.text, "condition": condition}, body)

        if tok.kind == "there":
            self.advance()
            self.expect("is", "after the word 'there'")
            name = self.expect("NAME", "as the name you are choosing")
            self.expect("=", "after the name '%s'" % name.text)
            expr = self.parse_expression()
            self.end_of_line()
            body = self.parse_under(indent, tok)
            return ("there", {"line": tok.line, "col": tok.col,
                              "name": name.text, "expr": expr}, body)

        condition = self.parse_condition()
        self.end_of_line()
        return ("conclude", {"line": tok.line, "col": tok.col,
                             "condition": condition}, None)

    def parse_under(self, opener_indent, opener):
        if self.at("end") or self.at("EOF"):
            raise DeltaError(
                "this line has nothing underneath it",
                opener.line, opener.col,
                hint="whatever is indented under 'for every' or 'there is' "
                     "is the part that may depend on it. Indent one more "
                     "step and put the next line there.")
        if self.peek().col <= opener_indent:
            raise DeltaError(
                "this line needs to be indented further than '%s'"
                % opener.text,
                self.peek().line, self.peek().col,
                hint="the indentation is what shows the scope. A line at the "
                     "same level is not inside the one above it.")
        return self.parse_quantifier()

    def end_of_line(self):
        if self.at("NEWLINE"):
            self.advance()
            self.skip_newlines()
            return
        if self.at("end") or self.at("EOF"):
            return
        tok = self.peek()
        raise DeltaError("found %s at the end of this line" % describe(tok),
                         tok.line, tok.col)

    def parse_step(self):
        tok = self.peek()

        if tok.kind == "given":
            self.advance()
            name = self.expect("NAME", "after the word 'given'")
            self.expect("with", "after the name '%s'" % name.text)
            return Given(line=tok.line, col=tok.col, name=name.text,
                         condition=self.parse_condition())

        if tok.kind == "choose":
            self.advance()
            name = self.expect("NAME", "after the word 'choose'")
            self.expect("=", "after the name '%s'" % name.text)
            return Choose(line=tok.line, col=tok.col, name=name.text,
                          expr=self.parse_expression())

        if tok.kind == "take":
            self.advance()
            name = self.expect("NAME", "after the word 'take'")
            self.expect("with", "after the name '%s'" % name.text)
            return Take(line=tok.line, col=tok.col, name=name.text,
                        condition=self.parse_condition())

        if tok.kind == "conclude":
            self.advance()
            return Conclude(line=tok.line, col=tok.col,
                            condition=self.parse_condition())

        raise DeltaError(
            "expected 'given', 'choose', 'take' or 'conclude', but found %s"
            % describe(tok), tok.line, tok.col,
            hint="the shape of an epsilon-delta proof is:\n"
                 "  given eps with eps > 0\n"
                 "  choose N = <something using eps>\n"
                 "  take n with n > N\n"
                 "  conclude abs(a(n) - L) < eps")

    # -- expressions --------------------------------------------------------

    def parse_condition(self):
        left = self.parse_expression()
        tok = self.peek()
        if tok.kind not in ("<", ">", "<=", ">=", "=="):
            raise DeltaError(
                "expected a comparison such as '>', but found %s"
                % describe(tok), tok.line, tok.col)
        self.advance()
        return Compare(line=left.line, col=left.col, op=tok.kind, left=left,
                       right=self.parse_expression())

    def parse_expression(self):
        left = self.parse_term()
        while self.peek().kind in ("+", "-"):
            op = self.advance()
            left = BinOp(line=left.line, col=left.col, op=op.kind, left=left,
                         right=self.parse_term())
        return left

    def parse_term(self):
        left = self.parse_unary()
        while self.peek().kind in ("*", "/"):
            op = self.advance()
            left = BinOp(line=left.line, col=left.col, op=op.kind, left=left,
                         right=self.parse_unary())
        return left

    def parse_unary(self):
        tok = self.peek()
        if tok.kind == "-":
            self.advance()
            return Neg(line=tok.line, col=tok.col, expr=self.parse_unary())
        return self.parse_primary()

    def parse_primary(self):
        tok = self.peek()
        if tok.kind == "NUMBER":
            self.advance()
            return Num(line=tok.line, col=tok.col, value=tok.value)
        if tok.kind == "(":
            self.advance()
            inner = self.parse_expression()
            self.expect(")", "to close the group")
            return inner
        if tok.kind == "NAME":
            self.advance()
            if self.at("("):
                self.advance()
                args = []
                if not self.at(")"):
                    while True:
                        args.append(self.parse_expression())
                        if self.accept(","):
                            continue
                        break
                self.expect(")", "to close the call to '%s'" % tok.text)
                return Call(line=tok.line, col=tok.col, name=tok.text, args=args)
            return Name(line=tok.line, col=tok.col, name=tok.text)
        raise DeltaError("expected a value, but found %s" % describe(tok),
                         tok.line, tok.col)


# ---------------------------------------------------------------------------
# 5. Walking an expression
# ---------------------------------------------------------------------------

def names_in(node):
    """Every name mentioned in an expression, in the order they appear."""
    found = []

    def walk(n):
        if isinstance(n, Num):
            return
        if isinstance(n, Name):
            found.append(n)
        elif isinstance(n, Call):
            for arg in n.args:
                walk(arg)
        elif isinstance(n, BinOp):
            walk(n.left)
            walk(n.right)
        elif isinstance(n, Neg):
            walk(n.expr)
        elif isinstance(n, Compare):
            walk(n.left)
            walk(n.right)

    walk(node)
    return found


def render_expr(node, nested=False):
    """Show an expression back to the reader without ambiguity.

    Parentheses go in wherever a sub-expression is itself a binary
    operation, so what is printed cannot be read a different way from what
    was evaluated.
    """
    if isinstance(node, Num):
        value = node.value
        if value.denominator == 1:
            return str(value.numerator)
        return "%s/%s" % (value.numerator, value.denominator)
    if isinstance(node, Name):
        return node.name
    if isinstance(node, Call):
        return "%s(%s)" % (node.name, ", ".join(render_expr(a)
                                                for a in node.args))
    if isinstance(node, BinOp):
        text = "%s %s %s" % (render_expr(node.left, True), node.op,
                             render_expr(node.right, True))
        return "(" + text + ")" if nested else text
    if isinstance(node, Neg):
        text = "-%s" % render_expr(node.expr, True)
        return "(" + text + ")" if nested else text
    if isinstance(node, Compare):
        return "%s %s %s" % (render_expr(node.left, True), node.op,
                             render_expr(node.right, True))
    return "?"


# ---------------------------------------------------------------------------
# 6. Evaluating exactly
# ---------------------------------------------------------------------------

FUNCTIONS = {"ceil", "floor", "abs", "min", "max"}


def evaluate(node, values, sequence_name=None, sequence_expr=None,
             sequence_var=None):
    """Evaluate using exact rationals.  Returns a Fraction or an int."""
    if isinstance(node, Num):
        return node.value
    if isinstance(node, Name):
        if node.name not in values:
            raise DeltaError("'%s' has no value here" % node.name,
                             node.line, node.col)
        return values[node.name]
    if isinstance(node, Neg):
        return -evaluate(node.expr, values, sequence_name, sequence_expr,
                         sequence_var)
    if isinstance(node, BinOp):
        left = evaluate(node.left, values, sequence_name, sequence_expr,
                        sequence_var)
        right = evaluate(node.right, values, sequence_name, sequence_expr,
                         sequence_var)
        if node.op == "+":
            return left + right
        if node.op == "-":
            return left - right
        if node.op == "*":
            return left * right
        if right == 0:
            raise DeltaError("division by zero", node.line, node.col)
        return Fraction(left, 1) / Fraction(right, 1)
    if isinstance(node, Call):
        if node.name == sequence_name:
            if len(node.args) != 1:
                raise DeltaError("'%s' takes one argument" % sequence_name,
                                 node.line, node.col)
            inner = dict(values)
            inner[sequence_var] = evaluate(node.args[0], values,
                                           sequence_name, sequence_expr,
                                           sequence_var)
            return evaluate(sequence_expr, inner, sequence_name, sequence_expr,
                            sequence_var)
        args = [evaluate(a, values, sequence_name, sequence_expr, sequence_var)
                for a in node.args]
        if node.name == "ceil":
            return Fraction(math.ceil(args[0]))
        if node.name == "floor":
            return Fraction(math.floor(args[0]))
        if node.name == "abs":
            return abs(args[0])
        if node.name == "min":
            return min(args)
        if node.name == "max":
            return max(args)
        raise DeltaError("there is no function called '%s'" % node.name,
                         node.line, node.col,
                         hint="the functions are ceil, floor, abs, min, max")
    raise DeltaError("I do not know how to work that out", node.line, node.col)


def holds(condition, values, **kw):
    left = evaluate(condition.left, values, **kw)
    right = evaluate(condition.right, values, **kw)
    op = condition.op
    if op == "<":
        return left < right
    if op == ">":
        return left > right
    if op == "<=":
        return left <= right
    if op == ">=":
        return left >= right
    return left == right


# ---------------------------------------------------------------------------
# 7. Checking the shape and the scopes
# ---------------------------------------------------------------------------

def check_scopes(proof):
    """Walk the steps in order, enforcing what may depend on what.

    This is the whole point.  `given` opens a scope, `choose` is written
    inside it, `take` opens a narrower one.  A name that has not been
    introduced yet is not merely unknown -- it is *forbidden*, and saying
    why is the lesson.
    """
    given = None
    chosen = None
    taken = None
    concluded = None

    introduced = []

    for index, step in enumerate(proof.steps):
        if isinstance(step, Given):
            if given is not None:
                raise DeltaError(
                    "there is more than one 'given'",
                    step.line, step.col,
                    hint="a limit is defined with one eps: "
                         "for every eps > 0, there is an N, ...")
            for name in names_in(step.condition):
                blame_later(proof, index, name, introduced)
            given = step
            introduced.append(step.name)

        elif isinstance(step, Choose):
            if given is None:
                raise DeltaError(
                    "'choose' comes before anything was 'given'",
                    step.line, step.col,
                    hint="first say what you are given:\n"
                         "  given eps with eps > 0")
            if chosen is not None:
                raise DeltaError("there is more than one 'choose'",
                                 step.line, step.col)
            for name in names_in(step.expr):
                blame_later(proof, index, name, introduced)
            chosen = step
            introduced.append(step.name)

        elif isinstance(step, Take):
            if chosen is None:
                raise DeltaError(
                    "'take' comes before anything was 'choose'n",
                    step.line, step.col,
                    hint="N has to exist before you can take an n beyond it")
            for name in names_in(step.condition):
                blame_later(proof, index, name, introduced)
            taken = step
            introduced.append(step.name)

        elif isinstance(step, Conclude):
            for name in names_in(step.condition):
                blame_later(proof, index, name, introduced)
            concluded = step

    if given is None or chosen is None or taken is None or concluded is None:
        missing = []
        if given is None:
            missing.append("given eps with eps > 0")
        if chosen is None:
            missing.append("choose N = ...")
        if taken is None:
            missing.append("take n with n > N")
        if concluded is None:
            missing.append("conclude abs(a(n) - L) < eps")
        raise DeltaError(
            "this proof is missing: " + ", ".join(missing),
            proof.line, proof.col)

    order = [type(s).__name__ for s in proof.steps if isinstance(
        s, (Given, Choose, Take, Conclude))]
    expected = ["Given", "Choose", "Take", "Conclude"]
    if order != expected:
        raise DeltaError(
            "the steps are out of order: " + " then ".join(order),
            proof.line, proof.col,
            hint="the order has to be " + " then ".join(expected)
                 + ", because that is what the definition says:\n"
                   "  for every eps > 0, there is an N, such that for\n"
                   "  every n > N, |a(n) - L| < eps")

    return given, chosen, taken, concluded


def blame_later(proof, index, name, introduced):
    """Explain a name that is not in scope yet, if we can be specific."""
    if name.name in [n for n in introduced]:
        return
    for later in proof.steps[index + 1:]:
        opens = None
        if isinstance(later, Given):
            opens = later.name
        elif isinstance(later, Choose):
            opens = later.name
        elif isinstance(later, Take):
            opens = later.name
        if opens == name.name:
            if isinstance(later, Take):
                raise DeltaError(
                    "'%s' does not exist yet" % name.name,
                    name.line, name.col,
                    hint="'%s' is introduced by 'for every %s', which comes\n"
                         "AFTER this line.\n" % (name.name, later.name) +
                         "That is the whole rule. When you write\n"
                         "\n"
                         "    for every eps\n"
                         "        there is N\n"
                         "            for every n\n"
                         "\n"
                         "the N is chosen before n exists, so N is not "
                         "allowed to\n"
                         "depend on n. It may depend on eps, because eps "
                         "comes first.\n"
                         "\n"
                         "If you want N to depend on n, you have written the\n"
                         "quantifiers in the wrong order.")
            raise DeltaError(
                "'%s' does not exist yet" % name.name,
                name.line, name.col,
                hint="'%s' is introduced later in this proof" % name.name)


# ---------------------------------------------------------------------------
# 8. Spot checking the choice of N
# ---------------------------------------------------------------------------

EPSILONS = [
    Fraction(1),
    Fraction(1, 2),
    Fraction(1, 4),
    Fraction(1, 10),
    Fraction(1, 100),
    Fraction(1, 1000),
    Fraction(1, 1000000),
]


def parse_eps_list(text):
    """Read a comma-separated list of positive values from the command line."""
    values = []
    for piece in text.split(","):
        piece = piece.strip()
        if not piece:
            continue
        try:
            values.append(Fraction(piece))
        except (ValueError, ZeroDivisionError):
            raise DeltaError("'%s' is not a number" % piece)
    if not values:
        raise DeltaError("--eps needs at least one value")
    for value in values:
        if value <= 0:
            raise DeltaError("--eps values have to be positive")
    return values


def spot_check(proof, given, chosen, taken, concluded, epsilons=None):
    """Try the argument at concrete values of eps with exact arithmetic."""
    if epsilons is None:
        epsilons = EPSILONS
    rows = []
    failures = []

    for eps in epsilons:
        values = {given.name: eps}
        try:
            n_bound = evaluate(chosen.expr, values, proof.sequence.name,
                               proof.sequence.expr, proof.sequence.variable)
        except DeltaError as err:
            raise DeltaError(
                "could not work out N when %s = %s: %s"
                % (given.name, render_num(eps), err.message),
                chosen.line, chosen.col)

        if n_bound.denominator != 1:
            raise DeltaError(
                "N came out as %s, which is not a whole number"
                % render_num(n_bound), chosen.line, chosen.col,
                hint="N is the index of a term in the sequence, so it has to "
                     "be a whole number. Did you mean ceil(...)?")

        bound = n_bound.numerator
        ok = True
        tested = 0
        for n in (bound + 1, bound + 2, max(bound + 1, 2 * bound)):
            local = dict(values)
            local[chosen.name] = n_bound
            local[taken.name] = Fraction(n)
            # Only test n that your own `take` line admits.
            if not holds(taken.condition, local,
                         sequence_name=proof.sequence.name,
                         sequence_expr=proof.sequence.expr,
                         sequence_var=proof.sequence.variable):
                continue
            tested += 1
            good = holds(concluded.condition, local,
                         sequence_name=proof.sequence.name,
                         sequence_expr=proof.sequence.expr,
                         sequence_var=proof.sequence.variable)
            if not good:
                ok = False
                failures.append((eps, bound, n))
                break
        if tested == 0:
            raise DeltaError(
                "when %s = %s, N = %d, no n satisfies your 'take' line "
                "'%s'" % (given.name, render_num(eps), bound,
                          render_expr(taken.condition)),
                taken.line, taken.col)
        rows.append((eps, bound, ok))

    return rows, failures


def render_num(value):
    if isinstance(value, Fraction):
        if value.denominator == 1:
            return str(value.numerator)
        return "%s/%s" % (value.numerator, value.denominator)
    return str(value)


# ---------------------------------------------------------------------------
# 9. Output
# ---------------------------------------------------------------------------

def report(path, proof, given, chosen, taken, concluded, rows, failures):
    out = []
    out.append("")
    out.append("  %s" % path)
    out.append("")
    out.append("  the sequence:   %s(%s) = %s"
               % (proof.sequence.name, proof.sequence.variable,
                  render_expr(proof.sequence.expr)))
    if proof.claim is not None:
        out.append("  the claim:      %s(%s) -> %s"
                   % (proof.claim.name, proof.claim.variable,
                      render_expr(proof.claim.limit)))
    out.append("")
    out.append("  the proof, as I read it:")
    out.append("")
    for line in render_nested(proof.steps, base=3).split("\n"):
        out.append(line)
    out.append("")
    out.append("  %s may depend on:  %s" % (chosen.name, given.name))
    out.append("  %s may not depend on:  %s" % (chosen.name, taken.name))
    out.append("      because %s is introduced after %s, so it is not yet in"
               % (taken.name, chosen.name))
    out.append("      scope. That is what 'for every eps there is an N such "
               "that for")
    out.append("      every n' means, and it is why the order matters.")
    out.append("")
    out.append("  spot check, exact arithmetic:")
    out.append("")
    out.append("      %-12s %-12s %-24s %s"
               % ("eps", "N", "n tried", "result"))
    for eps, bound, ok in rows:
        candidates = sorted({bound + 1, bound + 2,
                             max(bound + 1, 2 * bound)})
        tried = ", ".join(str(n) for n in candidates)
        out.append("      %-12s %-12d %-24s %s"
                   % (render_num(eps), bound, tried,
                      "ok" if ok else "FAILED"))

    out.append("")
    if failures:
        first = failures[0]
        out.append("  A COUNTEREXAMPLE.")
        out.append("")
        out.append("      eps = %s,  N = %d,  n = %d"
                   % (render_num(first[0]), first[1], first[2]))
        out.append("")
        out.append("      at those values the conclusion is false, so this N "
                   "does not")
        out.append("      work. A counterexample is conclusive: the proof is "
                   "wrong.")
    else:
        out.append("  %d values of eps, no counterexample." % len(rows))
        out.append("")
        out.append("  This is a spot check, not a proof. It samples rational "
                   "values and")
        out.append("  does not reason about the general case. A "
                   "counterexample would be")
        out.append("  conclusive; a clean run is only reassuring.")
    out.append("")
    return "\n".join(out)


# ---------------------------------------------------------------------------
# 9a. The same proof, in other notations
# ---------------------------------------------------------------------------

def render_nested(steps, base=1):
    """The proof with its scopes shown by indentation."""
    lines = []
    depth = base
    for step in steps:
        pad = "    " * depth
        if isinstance(step, Given):
            lines.append("%sfor every %s, where %s"
                         % (pad, step.name, render_expr(step.condition)))
            depth += 1
        elif isinstance(step, Choose):
            lines.append("%sthere is %s = %s"
                         % (pad, step.name, render_expr(step.expr)))
            depth += 1
        elif isinstance(step, Take):
            lines.append("%sfor every %s, where %s"
                         % (pad, step.name, render_expr(step.condition)))
            depth += 1
        elif isinstance(step, Conclude):
            lines.append("%s%s" % (pad, render_expr(step.condition)))
    return "\n".join(lines)


def render_symbols(steps):
    """The same proof in the notation you would meet in a textbook."""
    parts = []
    for step in steps:
        if isinstance(step, Given):
            parts.append("\u2200%s, %s" % (step.name,
                                          render_expr(step.condition)))
        elif isinstance(step, Choose):
            parts.append("\u2203%s = %s" % (step.name, render_expr(step.expr)))
        elif isinstance(step, Take):
            parts.append("\u2200%s, %s" % (step.name,
                                          render_expr(step.condition)))
        elif isinstance(step, Conclude):
            parts.append(": %s" % render_expr(step.condition))
    return "  ".join(parts)


# ---------------------------------------------------------------------------
# 9b. The same proof, as a game
# ---------------------------------------------------------------------------

def play(path, proof, given, chosen, taken, concluded, epsilons):
    """Show the proof as two players taking turns.

    A quantifier is a move.  `for every eps` means the Challenger picks a
    number.  `there is an N` means you answer.  `for every n` means the
    Challenger tries again, and this time it is trying to break you.

    The rule that N may not depend on n stops being algebra and becomes
    something you already know: you do not get to change your move after
    seeing theirs.
    """
    kw = dict(sequence_name=proof.sequence.name,
              sequence_expr=proof.sequence.expr,
              sequence_var=proof.sequence.variable)

    out = []
    out.append("")
    out.append("  The game")
    out.append("")
    out.append("    Two players.  The Challenger moves first.")
    out.append("")

    losses = []

    for eps in epsilons:
        values = {given.name: eps}
        bound_value = evaluate(chosen.expr, values, **kw)
        bound = bound_value.numerator

        out.append("    Challenger   %s = %s" % (given.name, render_num(eps)))
        out.append("    You          %s = %d" % (chosen.name, bound))

        admitted = []
        for n in (bound + 1, bound + 2, max(bound + 1, 2 * bound)):
            local = dict(values)
            local[chosen.name] = bound_value
            local[taken.name] = Fraction(n)
            if not holds(taken.condition, local, **kw):
                continue
            distance = evaluate(concluded.condition.left, local, **kw)
            admitted.append((n, distance, holds(concluded.condition, local,
                                                **kw)))

        if not admitted:
            out.append("    ...no %s satisfies your own '%s'."
                       % (taken.name, render_expr(taken.condition)))
            out.append("                 You lose before the Challenger "
                       "even tries.")
            losses.append(eps)
            out.append("")
            continue

        n, distance, passed = max(admitted, key=lambda row: row[1])
        out.append("    Challenger   %s = %d   (the hardest move it has)"
                   % (taken.name, n))
        if passed:
            out.append("    You          the distance is %s, and that is less"
                       % render_num(distance))
            out.append("                 than %s.  You hold."
                       % render_num(eps))
        else:
            out.append("    You          the distance is %s, and that is NOT"
                       % render_num(distance))
            out.append("                 less than %s."
                       % render_num(eps))
            out.append("                 The Challenger wins on this move.")
            losses.append(eps)
        out.append("")

    out.append("  " + "-" * 66)
    out.append("")
    if losses:
        out.append("    The Challenger won at %s = %s."
                   % (given.name, render_num(losses[0])))
        out.append("    The proof is wrong, and one move was enough to show "
                   "it.")
    else:
        out.append("    On these %d moves the Challenger found nothing."
                   % len(epsilons))
        out.append("    You won -- on these moves.  The Challenger has "
                   "infinitely")
        out.append("    many others, and this game did not try them.")
    out.append("")

    limit = (render_expr(proof.claim.limit) if proof.claim is not None
             else "the limit")
    out.append("  The same thing in English")
    out.append("")
    out.append("      Name any distance at all -- a thousandth, a millionth,")
    out.append("      whatever you like.  I will find a place in the")
    out.append("      sequence past which every term sits closer to %s"
               % limit)
    out.append("      than the distance you named.")
    out.append("")
    out.append("  Why %s cannot depend on %s" % (chosen.name, taken.name))
    out.append("")
    out.append("      The Challenger chose %s before you chose %s."
               % (given.name, chosen.name))
    out.append("      It chose %s afterwards.  You cannot change %s once"
               % (taken.name, chosen.name))
    out.append("      you have seen %s, because you have already moved."
               % taken.name)
    out.append("")
    out.append("      That is the whole content of 'for every %s, there is "
               "an %s," % (given.name, chosen.name))
    out.append("      such that for every %s'.  Written as ∀ ∃ ∀ it looks "
               "like" % taken.name)
    out.append("      algebra.  It is an order of play.")
    out.append("")
    return "\n".join(out)


# ---------------------------------------------------------------------------
# 10. Command line
# ---------------------------------------------------------------------------

USAGE = """Delta

  python3 delta.py run     path/to/proof.delta
  python3 delta.py play    path/to/proof.delta
  python3 delta.py show    path/to/proof.delta   -- the indented form
  python3 delta.py symbols path/to/proof.delta   -- the same proof, terse

  --eps 1,1/2,1/100    which values of eps to spot check at
                       (default: 1, 1/2, 1/4, 1/10, 1/100, 1/1000, 1/1000000)

A proof looks like this:

  sequence a(n) = 1 / n
  claim a(n) -> 0

  proof:
      given eps with eps > 0
      choose N = ceil(1 / eps)
      take n with n > N
      conclude abs(a(n) - 0) < eps
  end

Delta checks the order and the scopes, then spot checks your N with exact
rational arithmetic. It does not prove anything.
"""


def main(argv):
    args = argv[1:]
    epsilons = EPSILONS
    rest = []
    i = 0
    while i < len(args):
        if args[i] == "--eps":
            if i + 1 >= len(args):
                sys.stderr.write("--eps needs a value, for example "
                                 "--eps 1,1/100\n")
                return 2
            try:
                epsilons = parse_eps_list(args[i + 1])
            except DeltaError as err:
                sys.stderr.write("error: %s\n" % err.message)
                return 2
            i += 2
            continue
        rest.append(args[i])
        i += 1

    if len(rest) < 2 or rest[0] not in ("run", "show", "play", "symbols"):
        sys.stderr.write(USAGE)
        return 2
    command, path = rest[0], rest[1]

    try:
        if path == "-":
            source = sys.stdin.read()
            shown = "<stdin>"
        else:
            with open(path, "r") as handle:
                source = handle.read()
            shown = path
    except FileNotFoundError:
        sys.stderr.write("there is no file called %s\n" % path)
        return 2

    try:
        proof = Parser(tokenize(source), source).parse()
        given, chosen, taken, concluded = check_scopes(proof)

        if command == "show":
            print(render_nested(proof.steps))
            return 0

        if command == "symbols":
            print("  " + render_symbols(proof.steps))
            return 0

        if command == "play":
            sys.stdout.write(play(shown, proof, given, chosen, taken,
                                  concluded, epsilons))
            return 0

        rows, failures = spot_check(proof, given, chosen, taken, concluded,
                                    epsilons)
        sys.stdout.write(report(shown, proof, given, chosen, taken, concluded,
                                rows, failures))
        return 1 if failures else 0
    except DeltaError as err:
        sys.stderr.write(render_error(err, source, shown) + "\n")
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
