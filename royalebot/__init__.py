"""Royalebot: plays Clash Royale from screen frames. See game-state.md."""

from royalebot.catalog import Card, CardCatalog, CardType, Deploy, UnitKind, UnitType
from royalebot import layout
from royalebot.geometry import ARENA_HEIGHT, ARENA_WIDTH, Area, Position, Tile
from royalebot.state import (
    Arena,
    DeployedSpell,
    DeployedUnit,
    GameState,
    MatchInfo,
    Opponent,
    Owner,
    Play,
    PlayLog,
    Royalebot,
    Tower,
    TowerPosition,
)

__all__ = [
    "ARENA_HEIGHT",
    "ARENA_WIDTH",
    "Arena",
    "Area",
    "Card",
    "CardCatalog",
    "CardType",
    "Deploy",
    "DeployedSpell",
    "DeployedUnit",
    "GameState",
    "MatchInfo",
    "Opponent",
    "Owner",
    "Play",
    "PlayLog",
    "Position",
    "Royalebot",
    "Tower",
    "Tile",
    "TowerPosition",
    "UnitKind",
    "UnitType",
    "layout",
]
