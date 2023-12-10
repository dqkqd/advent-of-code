from pathlib import Path
from typing import Final, Iterator

INPUT_FOLDER: Final[Path] = Path(__file__).parent / "input"


def read_file(year: int, file: str) -> Iterator[str]:
    with (INPUT_FOLDER / str(year) / file).open() as f:
        yield from f


def read_file_with_filter(year: int, file: str) -> Iterator[str]:
    for line in read_file(year, file):
        if line:
            yield line


def read_file_with_filter_stripped(year: int, file: str) -> Iterator[str]:
    for line in read_file(year, file):
        stripped_line = line.strip()
        if stripped_line:
            yield stripped_line
