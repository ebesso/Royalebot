"""Game state: a snapshot of the match, reconstructed from screen frames.

Only the current snapshot and the Play log are kept; there is no frame-by-frame
history. See game-state.md for the full model.
"""

import itertools
from collections.abc import Iterator
from dataclasses import dataclass, field

from royalebot.catalog import CardCatalog, CardName, NamedEnum, UnitTypeName
from royalebot.geometry import Position

MATCH_LENGTH = 180.0  # seconds on the clock at the start of the match
DECK_SIZE = 8
HAND_SIZE = 4
STARTING_ELIXIR = 5.0
MAX_ELIXIR = 10.0
SECONDS_PER_ELIXIR = 2.8  # Known limitation: no match phase, so double elixir is ignored.

_ids = itertools.count(1)


def _next_id() -> int:
    return next(_ids)


class Owner(NamedEnum):
    OPPONENT = "opponent"
    ROYALEBOT = "royalebot"

    @property
    def enemy(self) -> "Owner":
        return Owner.ROYALEBOT if self is Owner.OPPONENT else Owner.OPPONENT


@dataclass(frozen=True)
class MatchInfo:
    """Fixed for the whole match. One per Owner."""

    name: str
    trophies: int


# --- Entities --------------------------------------------------------------


class TowerPosition(NamedEnum):
    LEFT = "left"
    RIGHT = "right"
    KING = "king"


@dataclass(kw_only=True)
class Tower:
    """Towers count as buildings and can attack air."""

    owner: Owner
    position: TowerPosition
    health: int  # absolute HP as read from screen, zero if destroyed
    active: bool = True  # only meaningful for the king tower

    @property
    def destroyed(self) -> bool:
        return self.health <= 0


@dataclass(kw_only=True)
class DeployedUnit:
    owner: Owner
    unit_type: UnitTypeName
    source_card: CardName | None  # None for spawned units, e.g. Witch Skeletons
    level: int
    health: float  # percent, 0–100
    position: Position
    deploy_remaining: float  # seconds, 0 = active
    last_seen: float  # game time
    id: int = field(default_factory=_next_id)

    @property
    def is_deploying(self) -> bool:
        return self.deploy_remaining > 0


@dataclass(kw_only=True)
class DeployedSpell:
    """Kept for as long as it is in play. Position updates while travelling."""

    owner: Owner
    card: CardName
    position: Position
    last_seen: float  # game time
    id: int = field(default_factory=_next_id)


@dataclass
class Arena:
    """Holds every entity in play, for both owners."""

    towers: list[Tower] = field(default_factory=list)
    units: list[DeployedUnit] = field(default_factory=list)
    spells: list[DeployedSpell] = field(default_factory=list)

    def towers_of(self, owner: Owner) -> list[Tower]:
        return [tower for tower in self.towers if tower.owner is owner]

    def units_of(self, owner: Owner) -> list[DeployedUnit]:
        return [unit for unit in self.units if unit.owner is owner]

    def spells_of(self, owner: Owner) -> list[DeployedSpell]:
        return [spell for spell in self.spells if spell.owner is owner]


# --- Play log --------------------------------------------------------------


@dataclass(frozen=True)
class Play:
    owner: Owner
    card: CardName
    game_time: float
    position: Position


@dataclass
class PlayLog:
    """Append-only list of every card played, by both players.

    Royalebot's plays are logged by the action layer; opponent plays are
    detected by vision.
    """

    plays: list[Play] = field(default_factory=list)

    def append(self, play: Play) -> None:
        self.plays.append(play)

    def by(self, owner: Owner) -> list[Play]:
        return [play for play in self.plays if play.owner is owner]

    def __iter__(self) -> Iterator[Play]:
        return iter(self.plays)

    def __len__(self) -> int:
        return len(self.plays)


# --- Players ---------------------------------------------------------------


@dataclass
class Royalebot:
    deck: list[CardName]  # set in configuration before the match
    current_elixir: float  # 0–10, read from the elixir bar
    next_card: CardName
    hand: list[CardName]  # slot order, left to right

    def __post_init__(self) -> None:
        if len(self.deck) != DECK_SIZE:
            raise ValueError(f"deck must have {DECK_SIZE} cards, got {len(self.deck)}")
        if len(self.hand) > HAND_SIZE:
            raise ValueError(f"hand holds at most {HAND_SIZE} cards, got {len(self.hand)}")
        if not 0 <= self.current_elixir <= MAX_ELIXIR:
            raise ValueError(f"elixir must be within 0–{MAX_ELIXIR}, got {self.current_elixir}")


@dataclass(frozen=True)
class Opponent:
    """Everything known about the opponent, derived from the Play log."""

    seen_cards: list[CardName]
    latest_time_played: dict[CardName, float]
    current_elixir: float  # estimate
    hand: list[CardName] | None  # estimate, known once all 8 cards are seen
    next_card: CardName | None  # estimate, known once all 8 cards are seen

    @classmethod
    def from_play_log(cls, play_log: PlayLog, game_time: float, catalog: CardCatalog) -> "Opponent":
        plays = play_log.by(Owner.OPPONENT)
        seen_cards = list(dict.fromkeys(play.card for play in plays))
        latest_time_played = {play.card: play.game_time for play in plays}

        hand = next_card = None
        if len(seen_cards) == DECK_SIZE:
            cycle = [play.card for play in plays[-HAND_SIZE:]]
            hand = [card for card in seen_cards if card not in cycle]
            next_card = cycle[0]

        return cls(
            seen_cards=seen_cards,
            latest_time_played=latest_time_played,
            current_elixir=_estimate_elixir(plays, game_time, catalog),
            hand=hand,
            next_card=next_card,
        )


def _estimate_elixir(plays: list[Play], game_time: float, catalog: CardCatalog) -> float:
    """Start at 5, gain 1 per 2.8s, stay within 0–10, drop by each card's cost.

    Known limitation: ignores Elixir Collector, Elixir Golem and Mirror's variable cost.
    """

    def regen(elixir: float, from_time: float, to_time: float) -> float:
        # Game time counts down; clamp so an overtime clock reset never drains elixir.
        elapsed = max(0.0, from_time - to_time)
        return min(MAX_ELIXIR, elixir + elapsed / SECONDS_PER_ELIXIR)

    elixir, last_time = STARTING_ELIXIR, MATCH_LENGTH
    for play in plays:
        elixir = regen(elixir, last_time, play.game_time)
        elixir = max(0.0, elixir - catalog.card(play.card).elixir_cost)
        last_time = play.game_time
    return round(regen(elixir, last_time, game_time), 2)


# --- Game state ------------------------------------------------------------


@dataclass
class GameState:
    catalog: CardCatalog = field(repr=False)
    match_info: dict[Owner, MatchInfo]
    game_time: float  # remaining time on the match clock, seconds
    royalebot: Royalebot
    arena: Arena = field(default_factory=Arena)
    play_log: PlayLog = field(default_factory=PlayLog)

    @property
    def opponent(self) -> Opponent:
        return Opponent.from_play_log(self.play_log, self.game_time, self.catalog)

    @property
    def crowns(self) -> dict[Owner, int]:
        """Crowns per player, from destroyed enemy towers; king tower destroyed = 3."""

        def crowns_for(owner: Owner) -> int:
            enemy_towers = self.arena.towers_of(owner.enemy)
            if any(t.destroyed and t.position is TowerPosition.KING for t in enemy_towers):
                return 3
            return sum(t.destroyed for t in enemy_towers)

        return {owner: crowns_for(owner) for owner in Owner}

    def __rich_repr__(self):
        """Pretty-print stored fields and derived values together (used by rich)."""
        yield "game_time", self.game_time
        yield "crowns", self.crowns
        yield "match_info", self.match_info
        yield "royalebot", self.royalebot
        yield "opponent", self.opponent
        yield "arena", self.arena
        yield "play_log", self.play_log
