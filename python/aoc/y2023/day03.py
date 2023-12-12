from __future__ import annotations

import enum
import itertools
import math
import unittest
from dataclasses import dataclass
from functools import cached_property
from typing import Iterator, Self

from aoc import utils


@dataclass(kw_only=True)
class Point:
    x: int
    y: int


@enum.unique
class SchemaStyle(enum.Enum):
    NUMBER = 0
    PERIOD = 1
    SYMBOL = 2


DEFAULT_REGION = 0


@dataclass(kw_only=True)
class SchemaKey:
    key: str
    region: int
    style: SchemaStyle

    def __repr__(self) -> str:
        return f"(key={self.key}, region={self.region}, style={self.style.name})"

    def good(self) -> bool:
        return self.region != DEFAULT_REGION

    @classmethod
    def from_char(cls: type[Self], key: str) -> SchemaKey:
        if len(key) > 1:
            raise ValueError(f"invalid key: {key}")
        match key:
            case ".":
                style = SchemaStyle.PERIOD
            case x if x.isdigit():
                style = SchemaStyle.NUMBER
            case _:
                style = SchemaStyle.SYMBOL
        return cls(key=key, region=DEFAULT_REGION, style=style)


@dataclass
class Engine:
    schema: list[list[SchemaKey]]

    current_region = DEFAULT_REGION

    @property
    def next_region(self) -> int:
        self.current_region += 1
        return self.current_region

    @classmethod
    def from_lines(cls: type[Engine], lines: Iterator[str]) -> Engine:
        return Engine([[SchemaKey.from_char(c) for c in line] for line in lines])

    @cached_property
    def rows(self) -> int:
        return len(self.schema)

    @cached_property
    def cols(self) -> int:
        return len(self.schema[0])

    def adjacent_points(self, x: int, y: int) -> Iterator[tuple[int, int]]:
        d = [-1, 0, 1]
        for dx, dy in itertools.product(d, d):
            if dx == 0 and dy == 0:
                continue
            nx = x + dx
            ny = y + dy
            if nx < 0 or nx >= self.rows or ny < 0 or ny >= self.cols:
                continue
            yield nx, ny

    def scan_row_for_numbers(self, x: int, y: int, region: int) -> None:
        if self.schema[x][y].style != SchemaStyle.NUMBER:
            return

        def good(col: int) -> bool:
            return (
                not self.schema[x][col].good()
                and self.schema[x][col].style == SchemaStyle.NUMBER
            )

        ly = y
        while ly >= 0 and good(ly):
            self.schema[x][ly].region = region
            ly -= 1

        ry = y + 1
        while ry < self.cols and good(ry):
            self.schema[x][ry].region = region
            ry += 1

    def symbols(self) -> Iterator[tuple[int, int]]:
        return (
            (x, y)
            for x in range(self.rows)
            for y in range(self.cols)
            if self.schema[x][y].style == SchemaStyle.SYMBOL
        )

    def fill_state(self) -> None:
        for x, y in self.symbols():
            for nx, ny in self.adjacent_points(x, y):
                self.scan_row_for_numbers(nx, ny, self.next_region)

    @staticmethod
    def collect_row(keys: list[SchemaKey]) -> dict[int, int]:
        row_integers: dict[int, int] = {}
        key_iter = iter(keys)

        while True:
            key_iter = itertools.dropwhile(lambda key: not key.good(), key_iter)

            value = 0
            region = None
            for key in itertools.takewhile(lambda key: key.good(), key_iter):
                region = key.region
                value = value * 10 + int(key.key)
            if region is None:
                break

            row_integers[region] = value

        return row_integers

    def collect(self) -> dict[int, int]:
        collection: dict[int, int] = {}
        for keys in self.schema:
            collection.update(self.collect_row(keys))
        return collection

    def get_adjacent_regions(
        self,
        number_of_adjacent_regions: int,
    ) -> Iterator[set[int]]:
        for x, y in self.symbols():
            adjacent_regions = {
                self.schema[nx][ny].region for nx, ny in self.adjacent_points(x, y)
            }
            adjacent_regions.remove(DEFAULT_REGION)
            if len(adjacent_regions) != number_of_adjacent_regions:
                continue
            yield adjacent_regions


def solve_case_1() -> int:
    engine = Engine.from_lines(utils.read_file_with_filter_stripped(2023, "day03.txt"))
    engine.fill_state()
    return sum(engine.collect().values())


def solve_case_2() -> int:
    engine = Engine.from_lines(utils.read_file_with_filter_stripped(2023, "day03.txt"))
    engine.fill_state()
    collection = engine.collect()
    total = 0
    for adjacent_regions in engine.get_adjacent_regions(number_of_adjacent_regions=2):
        assert len(adjacent_regions) == 2
        total += math.prod(
            value for region, value in collection.items() if region in adjacent_regions
        )
    return total


def test_case_1() -> None:
    assert solve_case_1() == 549908


def test_case_2() -> None:
    assert solve_case_2() == 81166799


if __name__ == "__main__":
    unittest.main()
