from __future__ import annotations

import enum
import itertools
from collections import deque
from dataclasses import dataclass
from functools import cached_property
from typing import Callable, Iterator, Literal, Self

import more_itertools

from aoc import utils


@enum.unique
class Pipe(enum.StrEnum):
    UD = "|"
    LR = "-"
    UR = "L"
    UL = "J"
    DL = "7"
    DR = "F"
    Ground = "."
    Start = "S"

    @classmethod
    def from_char(cls: type[Self], c: str) -> Self:
        return next(p for p in Pipe if p.value == c)

    def get_middle_horizontal(self, other: Self | None) -> Literal[Pipe.LR] | None:
        if self in (Pipe.Start, Pipe.LR, Pipe.UR, Pipe.DR) and other in (
            Pipe.LR,
            Pipe.UL,
            Pipe.DL,
        ):
            return Pipe.LR
        if other is Pipe.Start and self in (Pipe.LR, Pipe.UR, Pipe.DR):
            return Pipe.LR
        return None

    def get_middle_vertical(self, other: Self | None) -> Literal[Pipe.UD] | None:
        if self in (Pipe.Start, Pipe.UD, Pipe.DR, Pipe.DL) and other in (
            Pipe.UD,
            Pipe.UR,
            Pipe.UL,
        ):
            return Pipe.UD
        if other is Pipe.Start and self in (Pipe.UD, Pipe.DL, Pipe.DR):
            return Pipe.UD

        return None


@dataclass(kw_only=True)
class Point:
    x: int
    y: int

    def left(self) -> Self:
        return Point(x=self.x, y=self.y - 1)

    def right(self) -> Self:
        return Point(x=self.x, y=self.y + 1)

    def up(self) -> Self:
        return Point(x=self.x - 1, y=self.y)

    def down(self) -> Self:
        return Point(x=self.x + 1, y=self.y)


@enum.unique
class TileType(enum.StrEnum):
    UNVISITED = "i"
    VISITED = "x"
    BORDER = "o"


@dataclass
class Tile:
    tile_type: TileType
    score: int


@dataclass
class Field:
    pipes: list[list[Pipe]]
    tiles: list[list[Tile]]
    rows: int
    cols: int

    @classmethod
    def from_lines(cls: type[Self], lines: Iterator[str]) -> Self:
        def all_ground_pipes(size: int) -> list[Pipe]:
            return [Pipe.Ground for _ in range(size)]

        field: list[list[Pipe]] = []
        for line in lines:
            pipes = list(
                itertools.chain(
                    (Pipe.Ground,),
                    more_itertools.intersperse(Pipe.Ground, map(Pipe.from_char, line)),
                    (Pipe.Ground,),
                ),
            )
            field.append(all_ground_pipes(len(pipes)))
            field.append(pipes)

        cols = len(field[0])
        field.append(all_ground_pipes(cols))

        rows = len(field)

        tiles = [
            [Tile(TileType.UNVISITED, score=0) for _ in range(cols)]
            for _ in range(rows)
        ]

        return cls(field, tiles, rows, cols)

    @cached_property
    def start(self) -> Point:
        return next(
            Point(x=x, y=y)
            for x, pipes in enumerate(self.pipes)
            for y, pipe in enumerate(pipes)
            if pipe is Pipe.Start
        )

    def in_bound(self, point: Point) -> bool:
        return (
            point.x >= 0
            and point.x < self.rows
            and point.y >= 0
            and point.y < self.cols
        )

    def get_pipe(self, point: Point) -> Pipe | None:
        return self.pipes[point.x][point.y] if self.in_bound(point) else None

    def _connect_horizontal(self) -> None:
        for x in range(1, self.rows, 2):
            for y in range(1, self.cols - 2, 2):
                connected_pipe = self.pipes[x][y].get_middle_horizontal(
                    self.pipes[x][y + 2],
                )
                if connected_pipe is not None:
                    self.pipes[x][y + 1] = connected_pipe

    def _connect_vertical(self) -> None:
        for y in range(1, self.cols, 2):
            for x in range(1, self.rows - 2, 2):
                connected_pipe = self.pipes[x][y].get_middle_vertical(
                    self.pipes[x + 2][y],
                )
                if connected_pipe is not None:
                    self.pipes[x + 1][y] = connected_pipe

    def build(self) -> Self:
        self._connect_horizontal()
        self._connect_vertical()
        return self

    def connected_point(self, point1: Point, point2: Point) -> Point | None:
        point, next_point = point1, point2
        if point1.x > point2.x or point1.y > point2.y:
            point, next_point = next_point, point

        pipe = self.get_pipe(point)
        if pipe is None:
            return None

        next_pipe = self.get_pipe(next_point)
        if next_pipe is None:
            return None

        dx = point.x - next_point.x
        dy = point.y - next_point.y

        if not (dx == 0 and dy in {-2, 2}) and not (dy == 0 and dx in {-2, 2}):
            return None

        connected_point = Point(
            x=(point.x + next_point.x) // 2,
            y=(point.y + next_point.y) // 2,
        )
        connected_pipe = self.get_pipe(connected_point)
        if connected_pipe is None:
            return None

        if (dx == 0 and connected_pipe == pipe.get_middle_horizontal(next_pipe)) or (
            dy == 0 and connected_pipe == pipe.get_middle_vertical(next_pipe)
        ):
            return connected_point

        return None

    def flood_scores(self) -> Self:
        self.tiles[self.start.x][self.start.y] = Tile(TileType.VISITED, 0)
        points: deque[Point] = deque([self.start])

        def update(p0: Point, next_point_func: Callable[[Point], Point]) -> None:
            p2 = next_point_func(next_point_func(p0))
            p1 = self.connected_point(p0, p2)
            if p1 is None:
                return

            if self.tiles[p1.x][p1.y].tile_type != TileType.VISITED:
                self.tiles[p1.x][p1.y].tile_type = TileType.VISITED
                self.tiles[p1.x][p1.y].score = self.tiles[p0.x][p0.y].score + 1

            if self.tiles[p2.x][p2.y].tile_type != TileType.VISITED:
                self.tiles[p2.x][p2.y].tile_type = TileType.VISITED
                self.tiles[p2.x][p2.y].score = self.tiles[p0.x][p0.y].score + 2
                points.append(p2)

        while len(points) > 0:
            p = points.popleft()
            update(p, Point.up)
            update(p, Point.down)
            update(p, Point.left)
            update(p, Point.right)

        return self

    def flood_border(self) -> Self:
        start = Point(x=0, y=0)
        points: deque[Point] = deque([start])

        while len(points) > 0:
            p = points.popleft()
            if (
                not self.in_bound(p)
                or self.tiles[p.x][p.y].tile_type != TileType.UNVISITED
            ):
                continue
            self.tiles[p.x][p.y].tile_type = TileType.BORDER
            points.extend((p.up(), p.down(), p.left(), p.right()))

        return self

    def good_tiles(self) -> Iterator[Tile]:
        for tile in itertools.islice(self.tiles, 1, None, 2):
            yield from itertools.islice(tile, 1, None, 2)

    def max_score(self) -> int:
        return max(t.score for t in self.good_tiles())

    def max_borders(self) -> int:
        return sum(t.tile_type == TileType.UNVISITED for t in self.good_tiles())


def solve_case_1() -> int:
    return (
        Field.from_lines(
            utils.read_file_with_filter_stripped(2023, "day10.txt"),
        )
        .build()
        .flood_scores()
        .max_score()
        // 2
    )


def solve_case_2() -> int:
    return (
        Field.from_lines(
            utils.read_file_with_filter_stripped(2023, "day10.txt"),
        )
        .build()
        .flood_scores()
        .flood_border()
        .max_borders()
    )


def test_case_1() -> None:
    assert solve_case_1() == 6838


def test_case_2() -> None:
    assert solve_case_2() == 451
