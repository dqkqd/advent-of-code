from __future__ import annotations

import unittest
from dataclasses import dataclass
from typing import Self

import utils


@dataclass(kw_only=True)
class GameSet:
    r: int = 0
    g: int = 0
    b: int = 0

    def __add__(self, other: Self) -> Self:
        self.r = self.r + other.r
        self.g = self.g + other.g
        self.b = self.b + other.b
        return self

    @staticmethod
    def parse_without_comma(s: str, sub: str) -> int | None:
        index = s.find(sub)
        if index == -1:
            return None

        digit = s[:index].strip()
        return int(digit) if digit.isnumeric() else 0

    @classmethod
    def from_str(cls: type[Self], s: str) -> GameSet:
        game_set = cls(r=0, g=0, b=0)
        for separated in s.split(","):
            game_set.r += cls.parse_without_comma(separated, "red") or 0
            game_set.g += cls.parse_without_comma(separated, "green") or 0
            game_set.b += cls.parse_without_comma(separated, "blue") or 0
        return game_set

    def possible(self, *, r: int, g: int, b: int) -> bool:
        return self.r <= r and self.g <= g and self.b <= b


@dataclass(kw_only=True)
class Game:
    game_id: int
    game_sets: list[GameSet]

    @classmethod
    def from_str(cls: type[Self], s: str) -> Game:
        game_title, game_desc = s.split(":")
        game_id = int(game_title.split(" ")[-1])
        game_sets = list(map(GameSet.from_str, game_desc.split(";")))
        return Game(game_id=game_id, game_sets=game_sets)

    def power(self) -> int:
        r = max(x.r for x in self.game_sets)
        g = max(x.g for x in self.game_sets)
        b = max(x.b for x in self.game_sets)
        return r * g * b


def solve_case_1() -> int:
    def possible(game_set: GameSet) -> bool:
        return game_set.possible(r=12, g=13, b=14)

    answer = 0
    for line in utils.read_file_with_filter("day02.txt"):
        game = Game.from_str(line)
        possible_game = all(map(possible, game.game_sets))
        answer += game.game_id if possible_game else 0
    return answer


def solve_case_2() -> int:
    answer = 0
    for line in utils.read_file_with_filter("day02.txt"):
        answer += Game.from_str(line).power()
    return answer


class TestDay02(unittest.TestCase):
    def test_case_1(self) -> None:
        self.assertEqual(solve_case_1(), 2317)

    def test_case_2(self) -> None:
        self.assertEqual(solve_case_2(), 74804)


if __name__ == "__main__":
    unittest.main()
