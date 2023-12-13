from __future__ import annotations

import enum
import itertools
from dataclasses import dataclass
from typing import Self

from aoc import utils


@enum.unique
class SpringType(enum.StrEnum):
    OPERATIONAL = "."
    DAMAGED = "#"
    UNKNOWN = "?"

    @classmethod
    def from_str(cls: type[Self], s: str) -> SpringType:
        for spring_type in SpringType:
            if spring_type == s:
                return spring_type
        raise ValueError(f"Invalid spring type: {s}")


@dataclass
class SpringRow:
    row: list[SpringType]
    damaged: list[int]

    @classmethod
    def from_str(cls: type[Self], line: str) -> Self:
        row_str, damaged_str = line.strip().split()
        row = list(map(SpringType.from_str, row_str))
        damaged = list(map(int, damaged_str.split(",")))
        return cls(row, damaged)

    @classmethod
    def from_str_multiple(cls: type[Self], line: str) -> Self:
        row_str, damaged_str = line.strip().split()
        row_str = "?".join([row_str] * 5)
        damaged_str = ",".join([damaged_str] * 5)
        row = list(map(SpringType.from_str, row_str))
        damaged = list(map(int, damaged_str.split(",")))
        return cls(row, damaged)

    @property
    def row_str(self) -> list[str]:
        return list(map(str, self.row))

    def total_arrangements(self) -> int:
        total_damaged = list(
            itertools.chain(
                (0,),
                itertools.accumulate(
                    0 if x is SpringType.OPERATIONAL else 1 for x in self.row
                ),
            ),
        )
        dp = [
            [0 for _ in range(len(self.row) + 1)] for _ in range(len(self.damaged) + 1)
        ]
        dp[0][0] = 1
        for y, spring_type in enumerate(self.row, 1):
            dp[0][y] = 0 if spring_type is SpringType.DAMAGED else dp[0][y - 1]

        for x, group in enumerate(self.damaged, 1):
            for y, spring_type in enumerate(self.row, 1):
                if spring_type in (SpringType.OPERATIONAL, SpringType.UNKNOWN):
                    dp[x][y] = dp[x][y - 1]

                if total_damaged[y] - total_damaged[y - group] != group:
                    continue

                if spring_type is SpringType.OPERATIONAL:
                    continue

                if x == 1 and y == group:
                    dp[x][y] += 1
                elif (
                    y >= group + 1 and self.row[y - group - 1] is not SpringType.DAMAGED
                ):
                    dp[x][y] += dp[x - 1][y - group - 1]

        return dp[len(self.damaged)][len(self.row)]


def solve_case_1() -> int:
    return sum(
        row.total_arrangements()
        for row in map(
            SpringRow.from_str,
            utils.read_file_with_filter_stripped(2023, "day12.txt"),
        )
    )


def solve_case_2() -> int:
    return sum(
        row.total_arrangements()
        for row in map(
            SpringRow.from_str_multiple,
            utils.read_file_with_filter_stripped(2023, "day12.txt"),
        )
    )


def test_total_arrangements() -> None:
    assert SpringRow.from_str("???.### 1,1,3").total_arrangements() == 1
    assert SpringRow.from_str("????.######..#####. 1,6,5").total_arrangements() == 4
    assert SpringRow.from_str("?###???????? 3,2,1").total_arrangements() == 10


def test_case_1() -> None:
    assert solve_case_1() == 6827


def test_case_2() -> None:
    assert solve_case_2() == 1537505634471
