from pathlib import Path
from typing import Final, Iterator

INPUT_FOLDER: Final[Path] = Path(__file__).parent.parent / "input"


def read_file(file: str) -> Iterator[str]:
    with (INPUT_FOLDER / file).open() as f:
        yield from f


def read_file_with_filter(file: str) -> Iterator[str]:
    for line in read_file(file):
        if line:
            yield line


def read_file_with_filter_stripped(file: str) -> Iterator[str]:
    for line in read_file(file):
        stripped_line = line.strip()
        if stripped_line:
            yield stripped_line
