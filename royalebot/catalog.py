"""Card catalog: fixed reference data, the same in every match.

Game state refers to Cards and Unit types by name and never copies their stats.
"""

from dataclasses import dataclass, field
from enum import StrEnum

type CardName = str
type UnitTypeName = str


class NamedEnum(StrEnum):
    """A string enum that prints as `Type.NAME`, which reads better when exploring."""

    def __repr__(self) -> str:
        return f"{type(self).__name__}.{self.name}"


class CardType(NamedEnum):
    TROOP = "troop"
    BUILDING = "building"
    SPELL = "spell"


class UnitKind(NamedEnum):
    GROUND = "ground"
    AIR = "air"
    BUILDING = "building"


@dataclass(frozen=True)
class Deploy:
    """Units a card puts on the arena when played, e.g. 15 Skeletons for Skeleton Army."""

    unit_type: UnitTypeName
    count: int = 1


@dataclass(frozen=True)
class Card:
    name: CardName
    elixir_cost: int
    type: CardType
    deploy_time: float = 1.0  # seconds
    deploys: tuple[Deploy, ...] = ()
    # Tiles, spells only. Known limitation: the Log hits a strip, not a circle.
    radius: float | None = None


@dataclass(frozen=True)
class UnitType:
    name: UnitTypeName
    kind: UnitKind
    can_attack_air: bool
    targets_buildings_only: bool  # e.g. Hog Rider, Giant, Balloon
    max_health: dict[int, int] = field(default_factory=dict, hash=False)  # level -> HP

    def max_health_at(self, level: int) -> int:
        return self.max_health[level]


@dataclass
class CardCatalog:
    cards: dict[CardName, Card] = field(default_factory=dict)
    unit_types: dict[UnitTypeName, UnitType] = field(default_factory=dict)

    @classmethod
    def of(cls, cards: list[Card], unit_types: list[UnitType]) -> "CardCatalog":
        return cls(
            cards={card.name: card for card in cards},
            unit_types={unit_type.name: unit_type for unit_type in unit_types},
        )

    def card(self, name: CardName) -> Card:
        return self.cards[name]

    def unit_type(self, name: UnitTypeName) -> UnitType:
        return self.unit_types[name]
