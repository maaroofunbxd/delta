# Delta practice corpus

Every proof here is checked by `tests/corpus.py`. None of them
is hand-verified: if one breaks, the runner says so.

| # | file | sequence | limit | N | family |
|---|---|---|---|---|---|
| 1 | `001_constant.delta` | `0` | `0` | `0` | constant |
| 2 | `002_constant.delta` | `1` | `1` | `0` | constant |
| 3 | `003_constant.delta` | `-1` | `(-1)` | `0` | constant |
| 4 | `004_constant.delta` | `5` | `5` | `0` | constant |
| 5 | `005_constant.delta` | `42` | `42` | `0` | constant |
| 6 | `006_constant.delta` | `-7` | `(-7)` | `0` | constant |
| 7 | `007_constant.delta` | `1/2` | `1/2` | `0` | constant |
| 8 | `008_constant.delta` | `-3/4` | `(-3/4)` | `0` | constant |
| 9 | `009_c_n.delta` | `1 / n` | `0` | `ceil(1 / eps)` | c / n |
| 10 | `010_c_n.delta` | `2 / n` | `0` | `ceil(2 / eps)` | c / n |
| 11 | `011_c_n.delta` | `3 / n` | `0` | `ceil(3 / eps)` | c / n |
| 12 | `012_c_n.delta` | `5 / n` | `0` | `ceil(5 / eps)` | c / n |
| 13 | `013_c_n.delta` | `10 / n` | `0` | `ceil(10 / eps)` | c / n |
| 14 | `014_c_n.delta` | `100 / n` | `0` | `ceil(100 / eps)` | c / n |
| 15 | `015_c_n.delta` | `-1 / n` | `0` | `ceil(1 / eps)` | c / n |
| 16 | `016_c_n.delta` | `-2 / n` | `0` | `ceil(2 / eps)` | c / n |
| 17 | `017_c_n.delta` | `1 / (2 * n)` | `0` | `ceil(1 / (2 * eps))` | c / n |
| 18 | `018_c_n.delta` | `3 / (4 * n)` | `0` | `ceil(3 / (4 * eps))` | c / n |
| 19 | `019_c_n.delta` | `-5 / n` | `0` | `ceil(5 / eps)` | c / n |
| 20 | `020_c_n.delta` | `7 / n` | `0` | `ceil(7 / eps)` | c / n |
| 21 | `021_c_n_2.delta` | `1 / (n * n)` | `0` | `ceil(1 / eps)` | c / n^2 |
| 22 | `022_c_n_2.delta` | `2 / (n * n)` | `0` | `ceil(2 / eps)` | c / n^2 |
| 23 | `023_c_n_2.delta` | `3 / (n * n)` | `0` | `ceil(3 / eps)` | c / n^2 |
| 24 | `024_c_n_2.delta` | `5 / (n * n)` | `0` | `ceil(5 / eps)` | c / n^2 |
| 25 | `025_c_n_2.delta` | `10 / (n * n)` | `0` | `ceil(10 / eps)` | c / n^2 |
| 26 | `026_c_n_2.delta` | `-1 / (n * n)` | `0` | `ceil(1 / eps)` | c / n^2 |
| 27 | `027_c_n_2.delta` | `-4 / (n * n)` | `0` | `ceil(4 / eps)` | c / n^2 |
| 28 | `028_c_n_2.delta` | `1 / (2 * n * n)` | `0` | `ceil(1 / (2 * eps))` | c / n^2 |
| 29 | `029_c_n_2.delta` | `2 / (3 * n * n)` | `0` | `ceil(2 / (3 * eps))` | c / n^2 |
| 30 | `030_c_n_2.delta` | `-7 / (n * n)` | `0` | `ceil(7 / eps)` | c / n^2 |
| 31 | `031_c_n_2.delta` | `20 / (n * n)` | `0` | `ceil(20 / eps)` | c / n^2 |
| 32 | `032_c_n_2.delta` | `50 / (n * n)` | `0` | `ceil(50 / eps)` | c / n^2 |
| 33 | `033_c_n_3.delta` | `1 / (n * n * n)` | `0` | `ceil(1 / eps)` | c / n^3 |
| 34 | `034_c_n_3.delta` | `2 / (n * n * n)` | `0` | `ceil(2 / eps)` | c / n^3 |
| 35 | `035_c_n_3.delta` | `6 / (n * n * n)` | `0` | `ceil(6 / eps)` | c / n^3 |
| 36 | `036_c_n_3.delta` | `-1 / (n * n * n)` | `0` | `ceil(1 / eps)` | c / n^3 |
| 37 | `037_c_n_3.delta` | `10 / (n * n * n)` | `0` | `ceil(10 / eps)` | c / n^3 |
| 38 | `038_c_n_3.delta` | `24 / (n * n * n)` | `0` | `ceil(24 / eps)` | c / n^3 |
| 39 | `039_a_n_b_n.delta` | `(2 * n + (1)) / n` | `2` | `ceil(1 / eps)` | (a n + b) / n |
| 40 | `040_a_n_b_n.delta` | `(3 * n + (2)) / n` | `3` | `ceil(2 / eps)` | (a n + b) / n |
| 41 | `041_a_n_b_n.delta` | `(-1 * n + (4)) / n` | `-1` | `ceil(4 / eps)` | (a n + b) / n |
| 42 | `042_a_n_b_n.delta` | `(5 * n + (-3)) / n` | `5` | `ceil(3 / eps)` | (a n + b) / n |
| 43 | `043_a_n_b_n.delta` | `(1 * n + (7)) / n` | `1` | `ceil(7 / eps)` | (a n + b) / n |
| 44 | `044_a_n_b_n.delta` | `(4 * n + (1)) / n` | `4` | `ceil(1 / eps)` | (a n + b) / n |
| 45 | `045_a_n_b_n.delta` | `(-2 * n + (-5)) / n` | `-2` | `ceil(5 / eps)` | (a n + b) / n |
| 46 | `046_a_n_b_n.delta` | `(7 * n + (10)) / n` | `7` | `ceil(10 / eps)` | (a n + b) / n |
| 47 | `047_a_n_b_n.delta` | `(1 * n + (-1)) / n` | `1` | `ceil(1 / eps)` | (a n + b) / n |
| 48 | `048_a_n_b_n.delta` | `(6 * n + (2)) / n` | `6` | `ceil(2 / eps)` | (a n + b) / n |
| 49 | `049_n_n_k.delta` | `n / (n + 1)` | `1` | `ceil(1 / eps)` | n / (n + k) |
| 50 | `050_n_n_k.delta` | `n / (n + 2)` | `1` | `ceil(2 / eps)` | n / (n + k) |
| 51 | `051_n_n_k.delta` | `n / (n + 3)` | `1` | `ceil(3 / eps)` | n / (n + k) |
| 52 | `052_n_n_k.delta` | `n / (n + 5)` | `1` | `ceil(5 / eps)` | n / (n + k) |
| 53 | `053_n_n_k.delta` | `n / (n + 10)` | `1` | `ceil(10 / eps)` | n / (n + k) |
| 54 | `054_n_n_k.delta` | `n / (n + 100)` | `1` | `ceil(100 / eps)` | n / (n + k) |
| 55 | `055_n_n_k.delta` | `n / (n + 7)` | `1` | `ceil(7 / eps)` | n / (n + k) |
| 56 | `056_n_n_k.delta` | `n / (n + 25)` | `1` | `ceil(25 / eps)` | n / (n + k) |
| 57 | `057_c_n_d_n_2.delta` | `(1) / n + (1) / (n * n)` | `0` | `ceil(2 / eps)` | c/n + d/n^2 |
| 58 | `058_c_n_d_n_2.delta` | `(2) / n + (1) / (n * n)` | `0` | `ceil(3 / eps)` | c/n + d/n^2 |
| 59 | `059_c_n_d_n_2.delta` | `(1) / n + (3) / (n * n)` | `0` | `ceil(4 / eps)` | c/n + d/n^2 |
| 60 | `060_c_n_d_n_2.delta` | `(3) / n + (2) / (n * n)` | `0` | `ceil(5 / eps)` | c/n + d/n^2 |
| 61 | `061_c_n_d_n_2.delta` | `(-1) / n + (1) / (n * n)` | `0` | `ceil(2 / eps)` | c/n + d/n^2 |
| 62 | `062_c_n_d_n_2.delta` | `(5) / n + (-1) / (n * n)` | `0` | `ceil(6 / eps)` | c/n + d/n^2 |
| 63 | `063_c_n_d_n_2.delta` | `(2) / n + (7) / (n * n)` | `0` | `ceil(9 / eps)` | c/n + d/n^2 |
| 64 | `064_c_n_d_n_2.delta` | `(4) / n + (4) / (n * n)` | `0` | `ceil(8 / eps)` | c/n + d/n^2 |
| 65 | `065_a_n_b_c_n_d.delta` | `(1 * n + (1)) / (2 * n + (3))` | `1 / 2` | `ceil(1 / (4 * eps))` | (a n + b) / (c n + d) |
| 66 | `066_a_n_b_c_n_d.delta` | `(3 * n + (1)) / (1 * n + (2))` | `3 / 1` | `ceil(5 / (1 * eps))` | (a n + b) / (c n + d) |
| 67 | `067_a_n_b_c_n_d.delta` | `(2 * n + (-1)) / (5 * n + (1))` | `2 / 5` | `ceil(7 / (25 * eps))` | (a n + b) / (c n + d) |
| 68 | `068_a_n_b_c_n_d.delta` | `(1 * n + (4)) / (3 * n + (-2))` | `1 / 3` | `ceil(14 / (9 * eps))` | (a n + b) / (c n + d) |
| 69 | `069_a_n_b_c_n_d.delta` | `(5 * n + (2)) / (2 * n + (7))` | `5 / 2` | `ceil(31 / (4 * eps))` | (a n + b) / (c n + d) |
| 70 | `070_a_n_b_c_n_d.delta` | `(-1 * n + (3)) / (4 * n + (1))` | `-1 / 4` | `ceil(13 / (16 * eps))` | (a n + b) / (c n + d) |
| 71 | `071_a_n_b_c_n_d.delta` | `(7 * n + (1)) / (3 * n + (5))` | `7 / 3` | `ceil(32 / (9 * eps))` | (a n + b) / (c n + d) |
| 72 | `072_a_n_b_c_n_d.delta` | `(2 * n + (5)) / (1 * n + (6))` | `2 / 1` | `ceil(7 / (1 * eps))` | (a n + b) / (c n + d) |
| 73 | `073_a_n_b_c_n_d.delta` | `(4 * n + (-3)) / (2 * n + (1))` | `4 / 2` | `ceil(10 / (4 * eps))` | (a n + b) / (c n + d) |
| 74 | `074_a_n_b_c_n_d.delta` | `(9 * n + (2)) / (3 * n + (4))` | `9 / 3` | `ceil(30 / (9 * eps))` | (a n + b) / (c n + d) |
| 75 | `075_a_n_b_c_n_d.delta` | `(1 * n + (-5)) / (6 * n + (2))` | `1 / 6` | `ceil(32 / (36 * eps))` | (a n + b) / (c n + d) |
| 76 | `076_a_n_b_c_n_d.delta` | `(8 * n + (1)) / (4 * n + (3))` | `8 / 4` | `ceil(20 / (16 * eps))` | (a n + b) / (c n + d) |
| 77 | `077_a_n_2_b_c_n_2_d.delta` | `(1 * n * n + (1)) / (2 * n * n + (3))` | `1 / 2` | `ceil(1 / (4 * eps))` | (a n^2 + b) / (c n^2 + d) |
| 78 | `078_a_n_2_b_c_n_2_d.delta` | `(3 * n * n + (2)) / (1 * n * n + (5))` | `3 / 1` | `ceil(13 / (1 * eps))` | (a n^2 + b) / (c n^2 + d) |
| 79 | `079_a_n_2_b_c_n_2_d.delta` | `(2 * n * n + (-1)) / (4 * n * n + (1))` | `2 / 4` | `ceil(6 / (16 * eps))` | (a n^2 + b) / (c n^2 + d) |
| 80 | `080_a_n_2_b_c_n_2_d.delta` | `(1 * n * n + (7)) / (3 * n * n + (2))` | `1 / 3` | `ceil(19 / (9 * eps))` | (a n^2 + b) / (c n^2 + d) |
| 81 | `081_a_n_2_b_c_n_2_d.delta` | `(5 * n * n + (1)) / (2 * n * n + (9))` | `5 / 2` | `ceil(43 / (4 * eps))` | (a n^2 + b) / (c n^2 + d) |
| 82 | `082_a_n_2_b_c_n_2_d.delta` | `(-1 * n * n + (2)) / (3 * n * n + (1))` | `-1 / 3` | `ceil(7 / (9 * eps))` | (a n^2 + b) / (c n^2 + d) |
| 83 | `083_a_n_2_b_c_n_2_d.delta` | `(4 * n * n + (3)) / (1 * n * n + (8))` | `4 / 1` | `ceil(29 / (1 * eps))` | (a n^2 + b) / (c n^2 + d) |
| 84 | `084_a_n_2_b_c_n_2_d.delta` | `(7 * n * n + (-2)) / (2 * n * n + (1))` | `7 / 2` | `ceil(11 / (4 * eps))` | (a n^2 + b) / (c n^2 + d) |
| 85 | `085_a_n_2_b_c_n_2_d.delta` | `(1 * n * n + (5)) / (5 * n * n + (2))` | `1 / 5` | `ceil(23 / (25 * eps))` | (a n^2 + b) / (c n^2 + d) |
| 86 | `086_a_n_2_b_c_n_2_d.delta` | `(6 * n * n + (1)) / (3 * n * n + (7))` | `6 / 3` | `ceil(39 / (9 * eps))` | (a n^2 + b) / (c n^2 + d) |
| 87 | `087_1_n_n.delta` | `(2 * (n - 2 * floor(n / 2)) - 1) / n` | `0` | `ceil(1 / eps)` | (+-1)^n / n |
| 88 | `088_1_n_n.delta` | `(2 * (n - 2 * floor(n / 2)) - 1) / n` | `0` | `ceil(1 / eps)` | (+-1)^n / n |
| 89 | `089_1_n_n.delta` | `(2 * (n - 2 * floor(n / 2)) - 1) / n` | `0` | `ceil(1 / eps)` | (+-1)^n / n |
| 90 | `090_1_n_n.delta` | `(2 * (n - 2 * floor(n / 2)) - 1) / n` | `0` | `ceil(1 / eps)` | (+-1)^n / n |
| 91 | `091_mixed.delta` | `n / (n * n + 1)` | `0` | `ceil(1 / eps)` | mixed |
| 92 | `092_mixed.delta` | `(n - 1) / (n + 1)` | `1` | `ceil(2 / eps)` | mixed |
| 93 | `093_mixed.delta` | `(n + 1) / (2 * n + 3)` | `1 / 2` | `ceil(1 / (4 * eps))` | mixed |
| 94 | `094_mixed.delta` | `(3 * n * n + n) / (n * n + 1)` | `3` | `ceil(1 / eps)` | mixed |
| 95 | `095_mixed.delta` | `(n * n - 1) / (n * n + n)` | `1` | `ceil(1 / eps)` | mixed |
| 96 | `096_mixed.delta` | `(2 * n + 1) / n` | `2` | `ceil(1 / eps)` | mixed |
| 97 | `097_mixed.delta` | `(n + 5) / (2 * n)` | `1 / 2` | `ceil(5 / (2 * eps))` | mixed |
| 98 | `098_mixed.delta` | `(4 * n + 1) / (2 * n + 1)` | `2` | `ceil(1 / (2 * eps))` | mixed |
| 99 | `099_mixed.delta` | `(n * n + 3) / (2 * n * n + 1)` | `1 / 2` | `ceil(5 / (4 * eps))` | mixed |
| 100 | `100_mixed.delta` | `(1) / (n + 1)` | `0` | `ceil(1 / eps)` | mixed |

100 proofs.
