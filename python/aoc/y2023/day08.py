from __future__ import annotations

import enum
import math
from dataclasses import dataclass
from typing import Iterator, Self

from aoc import utils


def extended_euclidean(a: int, b: int) -> tuple[int, int, int]:
    # solve ax + by = gcd(a,b)
    if b == 0:
        return 1, 0, a
    x, y, g = extended_euclidean(b, a % b)
    return y, x - y * (a // b), g


@dataclass
class Root:
    x: int
    offset: int


def diophantine(a: int, b: int, c: int) -> tuple[Root, Root] | tuple[None, None]:
    # solve ax + by = c
    if a == 0 and b == 0:
        raise ValueError("Invalid a = 0, b = 0")

    xg, yg, g = extended_euclidean(a, b)

    if c % g != 0:
        return None, None

    x0 = xg * c // g
    y0 = yg * c // g

    assert a * x0 + b * y0 == c

    return Root(x0, b // g), Root(y0, -a // g)


class Direction(enum.Enum):
    LEFT = 0
    RIGHT = 1

    @classmethod
    def from_char(cls: type[Self], c: str) -> Direction:
        if c == "L":
            return cls.LEFT
        if c == "R":
            return cls.RIGHT
        raise ValueError(f"Invalid direction: {c}")


@dataclass
class Path:
    data: list[Direction]

    @classmethod
    def from_str(cls: type[Self], s: str) -> Path:
        data = list(map(Direction.from_char, s))
        return cls(data)

    def get_direction(self, at: int) -> Direction:
        return self.data[at % len(self.data)]

    def __len__(self) -> int:
        return len(self.data)


@dataclass(kw_only=True)
class NodeCounter:
    node_ids: dict[str, int]
    counter: int

    def get_id(self, node_repr: str) -> int:
        if node_repr not in self.node_ids:
            self.node_ids[node_repr] = self.counter
            self.counter += 1
        return self.node_ids[node_repr]

    def get_ids(self, *nodes_repr: str) -> tuple[int, ...]:
        return tuple([self.get_id(node_repr) for node_repr in nodes_repr])


@dataclass(kw_only=True)
class Node:
    node_repr: str
    node_id: int
    left: int
    right: int

    @classmethod
    def from_str(cls: type[Self], s: str, node_counter: NodeCounter) -> Node:
        node_repr, node_desc = s.split("=")
        left_repr, right_repr = node_desc.strip().lstrip("(").rstrip(")").split(",")

        node_repr = node_repr.strip()
        left_repr = left_repr.strip()
        right_repr = right_repr.strip()

        node_id, left_id, right_id = node_counter.get_ids(
            node_repr,
            left_repr,
            right_repr,
        )

        return cls(node_repr=node_repr, node_id=node_id, left=left_id, right=right_id)

    def go_next(self, direction: Direction) -> int:
        if direction == Direction.LEFT:
            return self.left
        return self.right


@dataclass(kw_only=True)
class Step:
    value: int
    offset: int

    def step(self, loop: int) -> int:
        return self.value + loop * self.offset

    def merge(self, other: Step) -> Step | None:
        if self.offset == 0 and other.offset == 0:
            return self if self.value == other.value else None

        root, _ = diophantine(self.offset, -other.offset, other.value - self.value)
        if root is None:
            return None

        value = self.value + root.x * self.offset
        offset = self.offset * root.offset

        # find k that value - k * offset is the minimum that higher than self.value and other.value
        min_value = max(self.value, other.value)
        if value < min_value:
            k = math.ceil((min_value - value) / offset)
            value += k * offset

        if value > min_value:
            k = math.floor((value - min_value) / offset)
            value -= k * offset

        return Step(value=value, offset=offset)


@dataclass(kw_only=True)
class Graph:
    path: Path
    nodes: list[Node]
    node_counter: NodeCounter

    @classmethod
    def from_lines(cls: type[Self], lines: Iterator[str]) -> Graph:
        path = Path.from_str(next(lines).strip())

        node_counter = NodeCounter(node_ids={}, counter=0)
        node_data: dict[int, Node] = {}
        for line in lines:
            node = Node.from_str(line, node_counter)
            node_data[node.node_id] = node

        nodes: list[Node] = []
        for node_id, node in sorted(node_data.items(), key=lambda x: x[0]):
            assert node_id == len(nodes)
            nodes.append(node)

        return cls(path=path, nodes=nodes, node_counter=node_counter)

    def steps_iter(self, start: str, end: str) -> list[Step]:
        start_id = self.node_counter.get_id(start)
        end_id = self.node_counter.get_id(end)
        counter = 0

        # key: node_id, value: step
        visited_nodes: dict[int, int] = {}

        steps_int: list[int] = []

        current_node_id = start_id
        while True:
            if current_node_id == end_id:
                steps_int.append(counter)

            at_the_end_path = counter % len(self.path) == len(self.path) - 1
            if at_the_end_path:
                if current_node_id in visited_nodes:
                    break
                visited_nodes[current_node_id] = counter

            node = self.nodes[current_node_id]
            current_node_id = node.go_next(self.path.get_direction(counter))

            counter += 1

        start_loop = visited_nodes[current_node_id]
        offset = counter - start_loop

        def to_step(v: int) -> Step:
            if v > start_loop:
                return Step(value=v, offset=offset)
            return Step(value=v, offset=0)

        return list(map(to_step, steps_int))


def solve_case_1() -> int:
    graph = Graph.from_lines(utils.read_file_with_filter_stripped(2023, "day08.txt"))
    steps = graph.steps_iter("AAA", "ZZZ")
    return steps[0].value


def solve_case_2() -> int:
    graph = Graph.from_lines(utils.read_file_with_filter_stripped(2023, "day08.txt"))
    start_nodes = [k for k in graph.node_counter.node_ids if k.endswith("A")]
    end_nodes = [k for k in graph.node_counter.node_ids if k.endswith("Z")]

    paths: list[list[Step]] = []
    for start in start_nodes:
        counters: list[Step] = []
        for end in end_nodes:
            counters.extend(
                graph.steps_iter(start, end),
            )
        paths.append(counters)

    assert paths

    def merge_path(path1: list[Step], path2: list[Step]) -> Iterator[Step]:
        for step1 in path1:
            for step2 in path2:
                step = step1.merge(step2)
                if step is not None:
                    yield step

    result = paths[0]
    for path in paths[1:]:
        # merge two paths
        result = list(merge_path(result, path))

    assert result
    result = sorted(result, key=lambda x: x.value)
    return result[0].value


def test_case_1() -> None:
    assert solve_case_1() == 12361


def test_case_2() -> None:
    assert solve_case_2() == 18215611419223
