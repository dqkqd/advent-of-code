from __future__ import annotations

import itertools
from dataclasses import dataclass
from functools import cached_property
from typing import Iterator, Self

import more_itertools

from aoc import utils


@dataclass(kw_only=True)
class Seeds:
    start: int
    end: int


@dataclass(kw_only=True)
class MapItem:
    src: int
    dst: int
    length: int

    def __repr__(self) -> str:
        return f"(src={self.src}, dst={self.dst}, length={self.length})"

    @cached_property
    def diff(self) -> int:
        return self.dst - self.src

    @cached_property
    def start(self) -> int:
        return self.src

    @cached_property
    def end(self) -> int:
        return self.src + self.length - 1

    def location(self, seeds: Seeds) -> Seeds | None:
        start = max(self.start, seeds.start)
        end = min(self.end, seeds.end)
        if start > end:
            return None
        return Seeds(start=start + self.diff, end=end + self.diff)

    def create_gap_between_items(self, map_item: MapItem) -> MapItem | None:
        assert self.start < map_item.start
        assert self.end < map_item.end

        if self.end + 1 >= map_item.start:
            return None

        return MapItem(
            src=self.end + 1,
            dst=self.end + 1,
            length=map_item.start - self.end - 1,
        )


@dataclass(kw_only=True)
class Map:
    name: str
    data: list[MapItem]

    @classmethod
    def from_iter(cls: type[Self], lines: Iterator[str]) -> Self:
        name = next(lines)
        data: list[MapItem] = []
        for line in itertools.takewhile(lambda x: len(x.strip()) > 0, lines):
            dst, src, length = map(int, line.strip().split())
            data.append(MapItem(src=src, dst=dst, length=length))
        data = sorted(data, key=lambda x: x.src)

        # fill gapped data
        new_data: list[MapItem] = []
        for before, after in itertools.pairwise(data):
            map_item = before.create_gap_between_items(after)
            if map_item is not None:
                new_data.append(map_item)
        data.extend(new_data)

        data = sorted(data, key=lambda x: x.src)
        return cls(name=name, data=data)

    def __repr__(self) -> str:
        return f"(name={self.name}, {" ".join(str(d) for d in self.data)})"

    def location(self, seeds: Seeds) -> Iterator[Seeds]:
        # normal map items
        next_seeds = (x.location(seeds) for x in self.data)
        yield from (s for s in next_seeds if s is not None)

        # edge map items
        if seeds.start < self.data[0].start:
            next_seed = MapItem(
                src=seeds.start,
                dst=seeds.start,
                length=self.data[0].src - seeds.start,
            ).location(seeds)
            if next_seed is not None:
                yield next_seed

        if seeds.end > self.data[-1].end:
            next_seed = MapItem(
                src=self.data[-1].end + 1,
                dst=self.data[-1].end + 1,
                length=seeds.end - self.data[-1].end,
            ).location(seeds)
            if next_seed is not None:
                yield next_seed


@dataclass
class Almanac:
    seeds: list[int]
    maps: list[Map]

    @classmethod
    def from_iter(cls: type[Self], lines: Iterator[str]) -> Self:
        seeds = list(map(int, next(lines).split(":")[-1].strip().split()))

        # empty line
        next(lines)

        maps = [Map.from_iter(lines) for _ in range(7)]

        return cls(seeds=seeds, maps=maps)

    def best_location(self, seeds: Seeds) -> int:
        locs: list[Seeds] = [seeds]
        for m in self.maps:
            locs = list(more_itertools.flatten(m.location(loc) for loc in locs))
        return min(loc.start for loc in locs)


def solve_case_1() -> int:
    almanac = Almanac.from_iter(utils.read_file(2023, "day05.txt"))
    return min(
        almanac.best_location(Seeds(start=seed, end=seed)) for seed in almanac.seeds
    )


def solve_case_2() -> int:
    almanac = Almanac.from_iter(utils.read_file(2023, "day05.txt"))
    return min(
        almanac.best_location(Seeds(start=start, end=start + diff - 1))
        for start, diff in zip(
            itertools.islice(almanac.seeds, 0, None, 2),
            itertools.islice(almanac.seeds, 1, None, 2),
        )
    )


def test_create_gap() -> None:
    map_item1 = MapItem(src=10, dst=20, length=7)
    map_item2 = MapItem(src=20, dst=30, length=5)
    map_item3 = map_item1.create_gap_between_items(map_item2)
    assert map_item3 == MapItem(src=17, dst=17, length=3)


def test_map_item_location() -> None:
    map_item = MapItem(src=50, dst=52, length=48)
    assert map_item.location(Seeds(start=0, end=49)) is None
    assert map_item.location(Seeds(start=0, end=50)) == Seeds(start=52, end=52)
    assert map_item.location(Seeds(start=0, end=51)) == Seeds(start=52, end=53)
    assert map_item.location(Seeds(start=97, end=99)) == Seeds(start=99, end=99)
    assert map_item.location(Seeds(start=98, end=99)) is None


def test_map_location() -> None:
    test_data = [
        "test",
        "30 20 8",
        "20 10 5",
    ]
    maps = Map.from_iter(iter(test_data))
    assert list(maps.location(Seeds(start=10, end=14))) == [Seeds(start=20, end=24)]

    assert list(maps.location(Seeds(start=0, end=9))) == [Seeds(start=0, end=9)]
    assert list(maps.location(Seeds(start=0, end=10))) == [
        Seeds(start=20, end=20),
        Seeds(start=0, end=9),
    ]
    assert list(maps.location(Seeds(start=15, end=19))) == [Seeds(start=15, end=19)]
    assert list(maps.location(Seeds(start=20, end=27))) == [Seeds(start=30, end=37)]
    assert list(maps.location(Seeds(start=28, end=40))) == [Seeds(start=28, end=40)]
    assert list(maps.location(Seeds(start=25, end=40))) == [
        Seeds(start=35, end=37),
        Seeds(start=28, end=40),
    ]


def test_case_1() -> None:
    assert solve_case_1() == 322500873


def test_case_2() -> None:
    assert solve_case_2() == 108956227
