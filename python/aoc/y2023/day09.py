from __future__ import annotations

import itertools
from dataclasses import dataclass
from functools import cached_property
from typing import Iterator, Self

from aoc import utils


@dataclass
class HistorySequence:
    data: list[int]

    @cached_property
    def end(self) -> bool:
        return all(x == 0 for x in self.data)

    def next_sequence(self) -> HistorySequence | None:
        if self.end:
            return None
        return HistorySequence(
            [after - before for before, after in itertools.pairwise(self.data)],
        )

    def next_sequences(self: HistorySequence) -> Iterator[HistorySequence]:
        seq: HistorySequence | None = self
        while True:
            if seq is None:
                break

            yield seq
            seq = seq.next_sequence()


@dataclass
class History:
    data: list[HistorySequence]

    @classmethod
    def from_str(cls: type[Self], s: str) -> Self:
        start = HistorySequence(list(map(int, s.split())))
        data = list(start.next_sequences())
        return cls(data)

    def get_last_history(self) -> int:
        start = 0
        for seq in self.data[::-1]:
            start = start + seq.data[-1]
        return start

    def get_first_history(self) -> int:
        start = 0
        for seq in self.data[::-1]:
            start = seq.data[0] - start
        return start


def solve_case_1() -> int:
    histories = map(
        History.from_str,
        utils.read_file_with_filter_stripped(2023, "day09.txt"),
    )
    return sum(h.get_last_history() for h in histories)


def solve_case_2() -> int:
    histories = map(
        History.from_str,
        utils.read_file_with_filter_stripped(2023, "day09.txt"),
    )
    return sum(h.get_first_history() for h in histories)


def test_next_sequence() -> None:
    assert HistorySequence([0, 3, 6, 9, 12, 15]).next_sequence() == HistorySequence(
        [3, 3, 3, 3, 3],
    )
    assert HistorySequence([3]).next_sequence() == HistorySequence(
        [],
    )


def test_history() -> None:
    assert History.from_str("1 3 6 10 15 21") == History(
        [
            HistorySequence([1, 3, 6, 10, 15, 21]),
            HistorySequence([2, 3, 4, 5, 6]),
            HistorySequence([1, 1, 1, 1]),
            HistorySequence([0, 0, 0]),
        ],
    )

    assert History.from_str("1 3 6 10 15 21").get_last_history() == 28


def test_case_1() -> None:
    assert solve_case_1() == 1637452029


def test_case_2() -> None:
    assert solve_case_2() == 908
