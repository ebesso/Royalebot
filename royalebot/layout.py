"""Constant arena layout: towers, river and bridges, in arena tiles.

Left and right are as seen on screen (Royalebot's view), for both owners. The
opponent's left tower is the one on the low-x side of the screen.

Values follow the standard 18×32 arena: a 2-row river across the middle, two
3-wide bridges, 3×3 princess towers in line with the bridges and 4×4 king towers.
"""

from royalebot.geometry import ARENA_WIDTH, Area, Position, Tile
from royalebot.state import Owner, TowerPosition

RIVER = Area(x=0, y=15, width=ARENA_WIDTH, height=2)

LEFT_BRIDGE = Area(x=2, y=15, width=3, height=2)
RIGHT_BRIDGE = Area(x=13, y=15, width=3, height=2)
BRIDGES = (LEFT_BRIDGE, RIGHT_BRIDGE)

BRIDGE_TILES: frozenset[Tile] = LEFT_BRIDGE.tiles | RIGHT_BRIDGE.tiles
RIVER_TILES: frozenset[Tile] = RIVER.tiles - BRIDGE_TILES  # water only, bridges excluded

TOWERS: dict[tuple[Owner, TowerPosition], Area] = {
    (Owner.OPPONENT, TowerPosition.KING): Area(x=7, y=1, width=4, height=4),
    (Owner.OPPONENT, TowerPosition.LEFT): Area(x=2, y=5, width=3, height=3),
    (Owner.OPPONENT, TowerPosition.RIGHT): Area(x=13, y=5, width=3, height=3),
    (Owner.ROYALEBOT, TowerPosition.LEFT): Area(x=2, y=24, width=3, height=3),
    (Owner.ROYALEBOT, TowerPosition.RIGHT): Area(x=13, y=24, width=3, height=3),
    (Owner.ROYALEBOT, TowerPosition.KING): Area(x=7, y=27, width=4, height=4),
}


def tower_area(owner: Owner, position: TowerPosition) -> Area:
    """The tiles a tower stands on."""
    return TOWERS[owner, position]


def tower_center(owner: Owner, position: TowerPosition) -> Position:
    return TOWERS[owner, position].center


def is_river(point: Position | Tile) -> bool:
    """True on water, False on a bridge."""
    tile = point.tile if isinstance(point, Position) else point
    return tile in RIVER_TILES


def is_bridge(point: Position | Tile) -> bool:
    tile = point.tile if isinstance(point, Position) else point
    return tile in BRIDGE_TILES


def side_of(point: Position | Tile) -> Owner | None:
    """Whose half of the arena a point is on, or None in the river row."""
    y = point.y if isinstance(point, Position) else point.row
    if y < RIVER.y:
        return Owner.OPPONENT
    if y >= RIVER.y + RIVER.height:
        return Owner.ROYALEBOT
    return None
