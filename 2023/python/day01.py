from __future__ import annotations

import unittest
from typing import Callable

import utils

NUMBERS = ["one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]


def solve_case_1() -> int:
    total = 0
    for line in utils.read_file_with_filter("day01.txt"):
        digits = list(map(int, filter(str.isdigit, line)))
        total += digits[0] * 10 + digits[-1]
    return total


def get_num(s: str) -> int | None:
    if not s:
        return None
    if s[0].isdigit():
        return int(s[0])

    for i, num in enumerate(NUMBERS):
        if s.startswith(num):
            return i + 1
    return None


def get_num_from(line: str) -> Callable[[int], int | None]:
    def get_num_at(i: int) -> int | None:
        return get_num(line[i:])

    return get_num_at


def solve_case_2() -> int:
    total = 0
    for line in utils.read_file_with_filter("day01.txt"):
        get_num_at = get_num_from(line)
        mapped_values = map(get_num_at, range(len(line)))
        digits = [x for x in mapped_values if x is not None]
        total += digits[0] * 10 + digits[-1]
    return total


class TestDay01(unittest.TestCase):
    def test_case_1(self) -> None:
        self.assertEqual(solve_case_1(), 54338)

    def test_case_2(self) -> None:
        self.assertEqual(solve_case_2(), 53389)


if __name__ == "__main__":
    unittest.main()
