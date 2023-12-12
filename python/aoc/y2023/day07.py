from __future__ import annotations

import enum
from collections import Counter
from dataclasses import dataclass
from typing import Self

from aoc import utils

CARDS = [
    "A",
    "K",
    "Q",
    "J",
    "T",
    "9",
    "8",
    "7",
    "6",
    "5",
    "4",
    "3",
    "2",
]

CARDS2 = [
    "A",
    "K",
    "Q",
    "T",
    "9",
    "8",
    "7",
    "6",
    "5",
    "4",
    "3",
    "2",
    "J",
]


@enum.unique
class HandType(enum.IntEnum):
    Unknown = 10
    FiveOfKind = 7
    FourOfKind = 6
    FullHouse = 5
    ThreeOfKind = 4
    TwoPair = 3
    OnePair = 2
    HighCard = 1

    @classmethod
    def from_str(cls: type[Self], s: str) -> HandType:
        counter = Counter(s.strip())
        hand_type = HandType.Unknown
        match len(counter):
            case 1:
                hand_type = HandType.FiveOfKind
            case 2:
                hand_type = (
                    HandType.FourOfKind
                    if counter.most_common(1)[0][1] == 4
                    else HandType.FullHouse
                )
            case 3:
                hand_type = (
                    HandType.ThreeOfKind
                    if counter.most_common(1)[0][1] == 3
                    else HandType.TwoPair
                )
            case 4:
                hand_type = HandType.OnePair
            case 5:
                hand_type = HandType.HighCard
            case _:
                pass

        return hand_type

    @classmethod
    def from_str_part_2(cls: type[Self], s: str) -> HandType:
        counter = Counter(s.strip())
        hand_type = HandType.Unknown
        match len(counter):
            case 1:
                hand_type = HandType.FiveOfKind
            case 2:
                if "J" in counter:
                    # JJJJ1 => 11111
                    # 1111J => 11111
                    hand_type = HandType.FiveOfKind
                else:
                    hand_type = (
                        HandType.FourOfKind
                        if counter.most_common(1)[0][1] == 4
                        else HandType.FullHouse
                    )
            case 3:
                if "J" in counter:
                    if counter.most_common(1)[0][1] == 3 or counter["J"] == 2:
                        # most common = 3, J = 3: JJJ12 => 11112
                        # most common = 3, J = 1: J1112 => 11112
                        # most common = 2, J = 2: JJ112 => 11112
                        hand_type = HandType.FourOfKind
                    else:
                        # most common = 2, J = 1: J1122 => 11122
                        hand_type = HandType.FullHouse
                else:
                    hand_type = (
                        HandType.ThreeOfKind
                        if counter.most_common(1)[0][1] == 3
                        else HandType.TwoPair
                    )
            case 4:
                hand_type = (
                    # JJ123 => 11123
                    # J1123 => 11123
                    HandType.ThreeOfKind
                    if "J" in counter
                    else HandType.OnePair
                )
            case 5:
                hand_type = HandType.OnePair if "J" in counter else HandType.HighCard
            case _:
                pass

        return hand_type


@dataclass
class Hand:
    hand_repr: str
    bid: int
    hand_type: HandType = HandType.Unknown

    @classmethod
    def from_str(cls: type[Self], s: str) -> Self:
        hand_repr, bid = s.split()
        return cls(
            hand_repr=hand_repr,
            bid=int(bid),
            hand_type=HandType.from_str(hand_repr),
        )

    def __lt__(self, other: Hand) -> bool:
        assert self.hand_type != HandType.Unknown
        assert other.hand_type != HandType.Unknown

        if self.hand_type.value != other.hand_type.value:
            return self.hand_type.value < other.hand_type.value

        for c1, c2 in zip(self.hand_repr, other.hand_repr):
            i1 = CARDS.index(c1)
            i2 = CARDS.index(c2)
            if i1 == i2:
                continue
            return i1 > i2

        raise ValueError(f"card equal: {self.hand_repr} == {other.hand_repr}")


@dataclass
class Hand2:
    hand_repr: str
    bid: int
    hand_type: HandType = HandType.Unknown

    @classmethod
    def from_str(cls: type[Self], s: str) -> Self:
        hand_repr, bid = s.split()
        return cls(
            hand_repr=hand_repr,
            bid=int(bid),
            hand_type=HandType.from_str_part_2(hand_repr),
        )

    def __lt__(self, other: Hand) -> bool:
        assert self.hand_type != HandType.Unknown
        assert other.hand_type != HandType.Unknown

        if self.hand_type.value != other.hand_type.value:
            return self.hand_type.value < other.hand_type.value

        for c1, c2 in zip(self.hand_repr, other.hand_repr):
            i1 = CARDS2.index(c1)
            i2 = CARDS2.index(c2)
            if i1 == i2:
                continue
            return i1 > i2

        raise ValueError(f"card equal: {self.hand_repr} == {other.hand_repr}")


def solve_case_1() -> int:
    hands = map(Hand.from_str, utils.read_file_with_filter_stripped(2023, "day07.txt"))
    sorted_hands = sorted(hands)
    return sum(i * v.bid for i, v in enumerate(sorted_hands, start=1))


def solve_case_2() -> int:
    hands = map(Hand2.from_str, utils.read_file_with_filter_stripped(2023, "day07.txt"))
    sorted_hands = sorted(hands)
    return sum(i * v.bid for i, v in enumerate(sorted_hands, start=1))


def test_case_1() -> None:
    assert solve_case_1() == 246912307


def test_case_2() -> None:
    assert solve_case_2() == 246894760
