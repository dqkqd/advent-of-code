from __future__ import annotations

import math
import unittest

from aoc import utils


def get_count(line: str) -> int:
    _, numbers = line.split(":")
    winning_numbers_str, own_numbers_str = numbers.split("|")
    winning_numbers = {*map(int, winning_numbers_str.strip().split())}
    matched_numbers = list(
        filter(
            lambda v: v in winning_numbers,
            map(int, own_numbers_str.strip().split()),
        ),
    )
    return len(matched_numbers)


def solve_case_1() -> int:
    answer = 0
    for line in utils.read_file_with_filter_stripped(2023, "day04.txt"):
        matched_count = get_count(line)
        if matched_count > 0:
            answer += int(math.pow(2, matched_count - 1))

    return answer


def solve_case_2() -> int:
    winning_counts: list[int] = [
        get_count(line)
        for line in utils.read_file_with_filter_stripped(2023, "day04.txt")
    ]
    cards_instances = [1] * len(winning_counts)
    for i, count in enumerate(winning_counts):
        for j in range(i + 1, min(i + 1 + count, len(cards_instances))):
            cards_instances[j] += cards_instances[i]
    return sum(cards_instances)


def test_case_1() -> None:
    assert solve_case_1() == 32001


def test_case_2() -> None:
    assert solve_case_2() == 5037841


if __name__ == "__main__":
    unittest.main()
