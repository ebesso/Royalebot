"""Arena geometry. See game-state.md → Geometry."""

from collections.abc import Iterator
from dataclasses import dataclass

ARENA_WIDTH = 18
ARENA_HEIGHT = 32


@dataclass(frozen=True)
class Position:
    """A point on the arena in tiles, with (0, 0) at the top left.

    The opponent's side has low y values.
    """

    x: float
    y: float

    def __post_init__(self) -> None:
        if not (0 <= self.x <= ARENA_WIDTH and 0 <= self.y <= ARENA_HEIGHT):
            raise ValueError(f"{self} is outside the {ARENA_WIDTH}x{ARENA_HEIGHT} arena")

    @property
    def tile(self) -> "Tile":
        """The tile this point lies on. Points on the far edges belong to the last tile."""
        return Tile(min(int(self.x), ARENA_WIDTH - 1), min(int(self.y), ARENA_HEIGHT - 1))


@dataclass(frozen=True, order=True)
class Tile:
    """One square of the arena grid. Tile (col, row) spans [col, col + 1) × [row, row + 1)."""

    col: int
    row: int

    def __post_init__(self) -> None:
        if not (0 <= self.col < ARENA_WIDTH and 0 <= self.row < ARENA_HEIGHT):
            raise ValueError(f"{self} is outside the {ARENA_WIDTH}x{ARENA_HEIGHT} arena")

    @property
    def center(self) -> Position:
        return Position(self.col + 0.5, self.row + 0.5)


@dataclass(frozen=True)
class Area:
    """A rectangle of whole tiles, from (x, y) at the top left, `width` × `height` tiles."""

    x: int
    y: int
    width: int
    height: int

    @property
    def center(self) -> Position:
        return Position(self.x + self.width / 2, self.y + self.height / 2)

    @property
    def tiles(self) -> frozenset[Tile]:
        return frozenset(self)

    def contains(self, point: Position | Tile) -> bool:
        if isinstance(point, Tile):
            point = point.center
        return self.x <= point.x < self.x + self.width and self.y <= point.y < self.y + self.height

    def __iter__(self) -> Iterator[Tile]:
        for row in range(self.y, self.y + self.height):
            for col in range(self.x, self.x + self.width):
                yield Tile(col, row)
