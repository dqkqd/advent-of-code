import math

from aoc import utils


def solve(total_time: int, distance: int) -> int:
    delta = total_time * total_time - 4 * (distance + 1)
    if delta < 0:
        return 0
    delta_sqrt = math.sqrt(delta)
    x1 = math.ceil((total_time - delta_sqrt) / 2)
    x2 = math.floor((total_time + delta_sqrt) / 2)
    return x2 - x1 + 1


def solve_case_1() -> int:
    lines = utils.read_file_with_filter_stripped(2023, "day06.txt")
    times = map(
        int,
        (v for v in next(lines).split(":")[-1].split(" ") if len(v) > 0),
    )
    distances = map(
        int,
        (v for v in next(lines).split(":")[-1].split(" ") if len(v) > 0),
    )

    return math.prod(solve(t, d) for t, d in zip(times, distances))


def solve_case_2() -> int:
    lines = utils.read_file_with_filter_stripped(2023, "day06.txt")
    total_time = int(next(lines).split(":")[-1].replace(" ", ""))
    distance = int(next(lines).split(":")[-1].replace(" ", ""))
    return solve(total_time, distance)


def test_case_1() -> None:
    assert solve_case_1() == 4811940


def test_case_2() -> None:
    assert solve_case_2() == 30077773
