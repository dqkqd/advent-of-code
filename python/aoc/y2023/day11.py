from __future__ import annotations

import bisect
import enum
from dataclasses import dataclass
from typing import Iterator, Self

from aoc import utils


@enum.unique
class AreaType(enum.StrEnum):
    SPACE = "."
    GALAXY = "#"

    @classmethod
    def from_char(cls: type[Self], c: str) -> Self:
        for area in AreaType:
            if area == c:
                return area
        raise ValueError(f"Invalid area : {c}")


@dataclass
class Image:
    data: list[list[AreaType]]

    @classmethod
    def from_lines(cls: type[Self], lines: Iterator[str]) -> Self:
        data = [list(map(AreaType.from_char, line)) for line in lines]
        return cls(data)

    def show(self) -> None:
        for areas in self.data:
            print("".join(map(str, areas)))

    def vertical_expansion_cols(self) -> Iterator[int]:
        for x, areas in enumerate(self.data):
            if all(area == AreaType.SPACE for area in areas):
                yield x

    def horizontal_expansion_cols(self) -> Iterator[int]:
        rows = len(self.data)
        for y in range(len(self.data[0])):
            if all(self.data[x][y] == AreaType.SPACE for x in range(rows)):
                yield y

    def collect_all_galaxies(
        self,
        expansion_offset: int = 2,
    ) -> Iterator[tuple[int, int]]:
        xs = list(self.vertical_expansion_cols())
        ys = list(self.horizontal_expansion_cols())
        for x, areas in enumerate(self.data):
            x_expanded = bisect.bisect_left(xs, x)
            x_offset = 0
            if x_expanded != 0:
                x_offset = x_expanded * (expansion_offset - 1)

            for y, area in enumerate(areas):
                y_expanded = bisect.bisect_left(ys, y)
                y_offset = 0
                if y_expanded != 0:
                    y_offset = y_expanded * (expansion_offset - 1)

                if area == AreaType.GALAXY:
                    yield (x + x_offset, y + y_offset)


def pairwise_distance_sum(arr: list[int]) -> int:
    arr_sum = sum(arr)
    n = len(arr)
    total = 0
    for i, a in enumerate(arr):
        total += arr_sum - (n - i) * a
        arr_sum -= a
    return total


def solve_case_1() -> int:
    image = Image.from_lines(utils.read_file_with_filter_stripped(2023, "day11.txt"))
    galaxies = list(image.collect_all_galaxies(2))
    xs = sorted(g[0] for g in galaxies)
    ys = sorted(g[1] for g in galaxies)
    return pairwise_distance_sum(xs) + pairwise_distance_sum(ys)


def solve_case_2() -> int:
    image = Image.from_lines(utils.read_file_with_filter_stripped(2023, "day11.txt"))
    galaxies = list(image.collect_all_galaxies(1000000))
    xs = sorted(g[0] for g in galaxies)
    ys = sorted(g[1] for g in galaxies)
    return pairwise_distance_sum(xs) + pairwise_distance_sum(ys)


def test_case_1() -> None:
    assert solve_case_1() == 10422930


def test_case_2() -> None:
    assert solve_case_2() == 699909023130
