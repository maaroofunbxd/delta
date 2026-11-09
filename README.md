# Delta

Write epsilon-delta arguments in words. Get the one mistake that matters
caught at the line where you make it.

```
$ python3 delta.py run examples/reciprocal.delta

  the sequence:   a(n) = 1 / n
  the claim:      a(n) -> 0

  the proof, as I read it:

            for every eps, where eps > 0
                there is N = ceil(1 / eps)
                    for every n, where n > N
                        abs(a(n) - 0) < eps

  N may depend on:  eps
  N may not depend on:  n
      because n is introduced after N, so it is not yet in
      scope. That is what 'for every eps there is an N such that for
      every n' means, and it is why the order matters.

  spot check, exact arithmetic:

      eps          N            n tried                  result
      1            1            2, 3                     ok
      1/2          2            3, 4                     ok
      1/4          4            5, 6, 8                  ok
      1/10         10           11, 12, 20               ok
      1/100        100          101, 102, 200            ok
      1/1000       1000         1001, 1002, 2000         ok
      1/1000000    1000000      1000001, 1000002, 2000000 ok

  7 values of eps, no counterexample.

  This is a spot check, not a proof. It samples rational values and
  does not reason about the general case. A counterexample would be
  conclusive; a clean run is only reassuring.
```

## The idea

Lean enforces the quantifier rule `∀ε ∃N ∀n` through dependent types. That is
the right way to do it and it is also why the notation is heavy.

But the rule is not deep. **N cannot depend on n simply because ε is
introduced first and n is introduced afterwards.** That is nesting — ordinary
lexical scope — and scope is cheap to implement and easy to explain.

So Delta is a language where the rule is visible in the shape of the text:

```
proof:
    for every eps, where eps > 0
        there is N = ceil(1 / eps)
            for every n, where n > N
                abs(a(n) - 0) < eps
end
```

`N` sits inside `eps`'s body. `n` sits inside `N`'s. A name that does not
exist yet is not merely unknown — it is *forbidden*, and Delta says why:

```
$ python3 delta.py run examples/errors/wrong_order.delta

error: 'n' does not exist yet

  at line 8
          there is N = floor(n / 2)
                          ^

  hint: 'n' is introduced by 'for every n', which comes
        AFTER this line.

        That is the whole rule. When you write

            for every eps
                there is N
                    for every n

        the N is chosen before n exists, so N is not allowed to
        depend on n. It may depend on eps, because eps comes first.

        If you want N to depend on n, you have written the
        quantifiers in the wrong order.
```

That error is the whole point of the language. It is the mistake almost every
beginner makes, it is invisible in ordinary prose, and here it is impossible
to make silently.

## The notation, and the two rules it follows

The first version of this used `given`, `choose`, `take`, `conclude`. That was
a mistake worth naming: those four words are a **relabelling** of `∀ ∃ ∀`, not
a clarification. Same three moves, same opacity, new glyphs. Anyone who has to
learn that `choose` means `∃` has paid the learning cost twice.

The notation now follows two rules.

**1. No new vocabulary.** Use the words that are already in the textbook.
`for every` *is* `∀`; you have known the word since you were six.

**2. Indentation is the scope.** The containment you can see is the scope the
checker enforces. You would not write `there is N = floor(n / 2)` inside
`for every eps`, because `n` is not on the page yet — it appears *below and
further in*, which is to say, in a narrower world. The mistake the whole tool
exists to catch becomes something that looks wrong before you run it.

Extra words help only when they expose structure the symbols hide. `for every`
passes that test: it names the kind of move. Something like *"the distance
from a(n) to 0 is less than eps"* fails it — `<` hides nothing, so the words
would be noise. The arithmetic is left alone.

## One proof, three notations

The proof is invariant under re-notation. Choosing `N = ceil(1/eps)` is the
content; `there is N =` is packaging. So notation is a *view*, and there is no
reason to have only one:

```
$ python3 delta.py show examples/reciprocal.delta
    for every eps, where eps > 0
        there is N = ceil(1 / eps)
            for every n, where n > N
                abs(a(n) - 0) < eps

$ python3 delta.py symbols examples/reciprocal.delta
  ∀eps, eps > 0  ∃N = ceil(1 / eps)  ∀n, n > N  : abs(a(n) - 0) < eps

$ python3 delta.py play examples/reciprocal.delta
  Challenger   eps = 1/100
  You          N = 100
  Challenger   n = 101   (the hardest move it has)
  You          the distance is 1/101, and that is less than 1/100.  You hold.
```

The original flat form still parses to the identical object
(`examples/old_style.delta`), which is the point: **no notation is the
language.** Verbosity is a property of the view, not of the language.

And the ceiling this implies: if the proof is the same under every notation,
then **no notation makes the mathematics easier.** Re-notation makes it easier
to write and easier to read. It cannot make it easier to *find*.

## The game

`play` shows the same proof as two players taking turns, because that is what
a quantifier actually is.

```
$ python3 delta.py play examples/reciprocal.delta

    Two players.  The Challenger moves first.

    Challenger   eps = 1/100
    You          N = 100
    Challenger   n = 101   (the hardest move it has)
    You          the distance is 1/101, and that is less
                 than 1/100.  You hold.
```

And the false proof, from the same view:

```
    Challenger   eps = 1/100000000
    You          N = 99999999
    Challenger   n = 100000000
    You          the distance is 1/100000000, and that is NOT
                 less than 1/100000000.
                 The Challenger wins on this move.
```

`∀ε ∃N ∀n` is not algebra you have to decode. It is: **they move, you move,
they move — and you do not get to change your move after seeing theirs.**
That is why `N` cannot depend on `n`, and it is obvious the moment it is
framed this way. It is nearly impossible to see in the symbols.

## The second check

Scope and order are checked exactly. The *arithmetic* is not, because that
would need a real prover. Instead Delta samples: for each of seven values of
`eps` it computes your `N`, picks `n` values your own `for every n` line
admits, and evaluates the conclusion in **exact rational arithmetic**. `1/3`
really is one third.

Write a bad `N` and you get a counterexample:

```
  A COUNTEREXAMPLE.

      eps = 1,  N = 0,  n = 1

      at those values the conclusion is false, so this N does not
      work. A counterexample is conclusive: the proof is wrong.
```

A counterexample proves you are wrong. A clean run does **not** prove you are
right, and the tool says so on every single run.

## What it is not

**It does not prove anything.** Seven values of `eps` are seven values of
`eps`. This is not a caveat, it is a hole you can drive through:

```
$ python3 delta.py run examples/liar.delta
  7 values of eps, no counterexample.

$ python3 delta.py run --eps 1/100000000,1 examples/liar.delta
  A COUNTEREXAMPLE.
      eps = 1/100000000,  N = 99999999,  n = 100000000
```

Same proof. Same tool. Opposite verdicts, and the only thing that changed is
which points were sampled. `examples/liar.delta` is a false proof that passes
every default check, because its `N` is short by exactly one for values of
`eps` below 10⁻⁸ — and the default sample stops at 10⁻⁶.

Widening the sample makes the tool better at its job without ever making it
correct, because verifying infinitely many values of `eps` is not something
you can do by trying more of them.

**It is about limits of sequences.** Not continuity, not differentiation, not
integration, not metric spaces.

**It has no library.** `ceil`, `floor`, `abs`, `min`, `max`, and arithmetic.
It does not know that `1/n` decreases, or anything else about your sequence.

## On writing this as poetry

Mathematics was prose and verse for far longer than it has been symbols.
Euclid has no notation. Newton wrote the *Principia* geometrically, on
purpose, because he distrusted algebra. The Kerala school did calculus in
verse, and Bhāskara's *Līlāvatī* is a poem addressed to his daughter.

Symbols won in the seventeenth century for one specific reason: **you can
rearrange them.** `ax² + bx + c = 0` can be manipulated mechanically; a
sentence cannot. So `∀ε ∃N` is a compression built for manipulation, and what
it costs is exactly what it costs a beginner — you cannot think in it.

The game framing is the repair, and for this purpose it beats verse, because
verse makes a definition *memorable* while the game makes it *simulable*. You
can play it in your head. Two players, a clear rule about whose turn it is,
and the answer falls out.

It does not help you prove anything. The Challenger tried seven moves. In
verse, in symbols, or in dialogue, seven moves are still seven moves.

## Where this stops, and why it is a cliff

The notation is friendly and it will not get any harder. Everything else does.
Here is the first course in analysis, and what each step needs:

| Page of the course | What it needs that Delta has not got |
|---|---|
| Sequences, ε-N | — Delta has this |
| Sum, product, quotient, squeeze | A **lemma system**. You instantiate the sum lemma at `eps/2`, take `max(N₁, N₂)`, and discharge `eps/2 > 0`. Substitution, unification, arithmetic |
| Monotone convergence, Bolzano–Weierstrass | **Supremum** and completeness. `sup` takes a *set* |
| Series | Partial sums: functions of functions |
| Continuity, ε-δ | **Functions as first-class values** |
| Uniform continuity | Delta's scoping idea *does* extend — see below |
| Derivatives | Limits of difference quotients |
| Riemann integral | `sup` over an **infinite family of partitions** |
| Uniform convergence | Quantifying over sequences of functions |
| Metric spaces, topology | **Abstract structures** — parameterised by a space |

**The left column is the same notation throughout.** The right column goes
from a twenty-line scoping check to a dependently typed proof assistant with a
library. Mathlib is around a million and a half lines and has had hundreds of
contributors over a decade.

One honest point in Delta's favour: the idea generalises further than you
might expect. Continuous versus uniformly continuous is *exactly* the
dependency question — for continuity `delta` may depend on the point, for
uniform continuity it may not — and that is an indentation difference:

```
# continuous at x0              # uniformly continuous
for every eps, where eps > 0    for every eps, where eps > 0
    for every x0, where ...         there is delta = ...
        there is delta = ...            for every x0, where ...
            for every x, where ...          for every x, where ...
```

The same lines, reordered, and the nesting separates them for free. That is a
genuinely good sign for the idea.

It is also the last thing it does for free.

## The verdict

Delta makes the *first* thing in analysis easy to practise, and that is worth
something, because the quantifier rule is where most people get lost and it is
genuinely invisible in ordinary prose.

But if the question is "can a friendlier language be the way forward for real
analysis," then this is the answer, and it is not a rhetorical one: **the
friendly notation carried me two pages.** Everything past that is machinery,
and the machinery is what Lean is. Building it again with nicer words is not a
shortcut — it is the same decade of work with a different parser.

## Using it

```sh
python3 delta.py run     examples/reciprocal.delta
python3 delta.py play    examples/reciprocal.delta   # as two players
python3 delta.py show    examples/reciprocal.delta   # the indented form
python3 delta.py symbols examples/reciprocal.delta   # the same proof, terse
python3 tests/run_tests.py
python3 delta.py run -        # read a proof from stdin
python3 delta.py run --eps 1,1/1000,1/100000000 examples/liar.delta
```

## The language

```
sequence <name>(<variable>) = <expression>
claim <name>(<variable>) -> <expression>

proof:
    for every <name>, where <comparison>
        there is <name> = <expression>
            for every <name>, where <comparison>
                <comparison>
end
```

Each line is indented further than the one it sits inside. That indentation
*is* the scope: everything under `for every eps` may depend on `eps`, and
nothing may depend on a name that only appears further in.

The three moves have to come in that order — one `for every`, then one
`there is`, then one `for every`, then the conclusion — because that is what
the definition says. Getting them out of order is refused, and the refusal
says which order you wrote.

Comparisons use `<`, `>`, `<=`, `>=`, `==`. Expressions use `+ - * /`,
parentheses, and `ceil`, `floor`, `abs`, `min`, `max`. Numbers are exact
rationals — `1 / 3` really is one third, not 0.333.

The original flat form is still accepted and parses to the identical proof:

```
proof:
    given <name> with <comparison>
    choose <name> = <expression>
    take <name> with <comparison>
    conclude <comparison>
end
```
