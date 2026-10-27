"""A sample catalog and mid-match game state, for exploring the model.

Stats and HP values are illustrative placeholders, not real game data.
"""

from royalebot.catalog import Card, CardCatalog, CardType, Deploy, UnitKind, UnitType
from royalebot.geometry import Position
from royalebot.state import (
    Arena,
    DeployedSpell,
    DeployedUnit,
    GameState,
    MatchInfo,
    Owner,
    Play,
    PlayLog,
    Royalebot,
    Tower,
    TowerPosition,
)


def _troop(name: str, cost: int, unit: str, count: int = 1) -> Card:
    return Card(name, cost, CardType.TROOP, deploys=(Deploy(unit, count),))


def _building(name: str, cost: int) -> Card:
    return Card(name, cost, CardType.BUILDING, deploys=(Deploy(name),))


def _spell(name: str, cost: int, radius: float | None) -> Card:
    return Card(name, cost, CardType.SPELL, deploy_time=0.0, radius=radius)


def _unit(name: str, kind: UnitKind, air: bool = False, buildings_only: bool = False, hp: int = 1000) -> UnitType:
    return UnitType(name, kind, can_attack_air=air, targets_buildings_only=buildings_only, max_health={11: hp})


def example_catalog() -> CardCatalog:
    G, A, B = UnitKind.GROUND, UnitKind.AIR, UnitKind.BUILDING
    return CardCatalog.of(
        cards=[
            # Royalebot's deck
            _troop("Knight", 3, "Knight"),
            _troop("Musketeer", 4, "Musketeer"),
            _troop("Hog Rider", 4, "Hog Rider"),
            _spell("Fireball", 4, radius=2.5),
            _spell("The Log", 2, radius=None),
            _troop("Skeleton Army", 3, "Skeleton", count=15),
            _building("Cannon", 3),
            _troop("Ice Spirit", 1, "Ice Spirit"),
            # Opponent's deck
            _troop("Giant", 5, "Giant"),
            _troop("Witch", 5, "Witch"),
            _troop("Minions", 3, "Minion", count=3),
            _spell("Arrows", 3, radius=4.0),
            _spell("Zap", 2, radius=2.5),
            _troop("Valkyrie", 4, "Valkyrie"),
            _troop("Baby Dragon", 4, "Baby Dragon"),
            _building("Tombstone", 3),
        ],
        unit_types=[
            _unit("Knight", G, hp=1766),
            _unit("Musketeer", G, air=True, hp=720),
            _unit("Hog Rider", G, buildings_only=True, hp=1696),
            _unit("Skeleton", G, hp=81),
            _unit("Cannon", B, hp=824),
            _unit("Ice Spirit", G, air=True, hp=230),
            _unit("Giant", G, buildings_only=True, hp=4091),
            _unit("Witch", G, air=True, hp=838),
            _unit("Minion", A, air=True, hp=252),
            _unit("Valkyrie", G, hp=1908),
            _unit("Baby Dragon", A, air=True, hp=1152),
            _unit("Tombstone", B, hp=530),
        ],
    )


def _towers() -> list[Tower]:
    towers = []
    for owner in Owner:
        towers += [
            Tower(owner=owner, position=TowerPosition.LEFT, health=3052),
            Tower(owner=owner, position=TowerPosition.RIGHT, health=3052),
            Tower(owner=owner, position=TowerPosition.KING, health=4824, active=False),
        ]
    towers[0].health = 1204  # opponent's left tower has taken damage
    return towers


def example_state() -> GameState:
    def opp(card: str, time: float, x: float, y: float) -> Play:
        return Play(Owner.OPPONENT, card, time, Position(x, y))

    def bot(card: str, time: float, x: float, y: float) -> Play:
        return Play(Owner.ROYALEBOT, card, time, Position(x, y))

    play_log = PlayLog([
        opp("Giant", 170, 3.5, 2),
        bot("Knight", 165, 3.5, 24),
        opp("Witch", 160, 3.5, 3),
        opp("Minions", 150, 6, 12),
        opp("Arrows", 140, 4, 22),
        opp("Zap", 130, 3, 25),
        bot("Hog Rider", 120, 3.5, 17),
        opp("Valkyrie", 120, 4, 9),
        opp("Baby Dragon", 110, 14, 5),
        opp("Tombstone", 100, 9, 9),
        opp("Giant", 97, 3.5, 10),
        bot("Fireball", 96, 3.5, 10),
    ])

    arena = Arena(
        towers=_towers(),
        units=[
            DeployedUnit(owner=Owner.OPPONENT, unit_type="Giant", source_card="Giant", level=11,
                         health=100, position=Position(3.5, 10.5), deploy_remaining=0.0, last_seen=95),
            DeployedUnit(owner=Owner.OPPONENT, unit_type="Tombstone", source_card="Tombstone", level=11,
                         health=70, position=Position(9, 9), deploy_remaining=0.0, last_seen=95),
            DeployedUnit(owner=Owner.OPPONENT, unit_type="Skeleton", source_card=None, level=11,
                         health=100, position=Position(9, 10), deploy_remaining=0.0, last_seen=95),
            DeployedUnit(owner=Owner.OPPONENT, unit_type="Baby Dragon", source_card="Baby Dragon", level=11,
                         health=45, position=Position(13, 14), deploy_remaining=0.0, last_seen=95),
        ],
        spells=[
            DeployedSpell(owner=Owner.ROYALEBOT, card="Fireball", position=Position(4, 18), last_seen=95),
        ],
    )

    return GameState(
        catalog=example_catalog(),
        match_info={
            Owner.OPPONENT: MatchInfo(name="Opponent", trophies=5120),
            Owner.ROYALEBOT: MatchInfo(name="Royalebot", trophies=5080),
        },
        game_time=95,
        royalebot=Royalebot(
            deck=["Knight", "Musketeer", "Hog Rider", "Fireball", "The Log", "Skeleton Army", "Cannon", "Ice Spirit"],
            current_elixir=4.3,
            next_card="Ice Spirit",
            hand=["The Log", "Skeleton Army", "Musketeer", "Cannon"],
        ),
        arena=arena,
        play_log=play_log,
    )
