
# Game state

A snapshot of the match, reconstructed from screen frames, used by Royalebot to play live as the bottom player.
Only the current snapshot and the Play log are kept; there is no frame-by-frame history.

Attributes:
- Match info
- Game time (remaining time on the match clock, seconds)
  - Known limitation: no match phase, so double elixir and overtime are not distinguished.
- Opponent
- Royalebot
- Arena
- Play log

Derived:
- Crowns per player (from destroyed enemy towers; king tower destroyed = 3)

# Definitions

## Owner

Either `Opponent` or `Royalebot`.

## Match info

Fixed for the whole match. One per Owner.

Attributes:
- Name
- Trophies

## Player

### Opponent attributes

Derived (from Play log):
- Seen cards (list of Card)
- Latest time played for each seen card (game time at seen)
- Current elixir (estimate)
  - Starts at 5, gains 1 per 2.8s, stays within 0–10, and drops by the card's elixir cost on each Play.
  - Known limitation: ignores elixir from Elixir Collector and Elixir Golem, and Mirror's variable cost.
- Hand (estimate; once all 8 cards are seen, the 4 cards not among the last 4 plays)
- Next card (estimate; the oldest of the last 4 plays)

### Royalebot
- Deck (8 Cards, set in configuration before the match)
- Current elixir (decimal 0–10, read from the elixir bar)
- Next card (Card)
- Hand (4 Cards, in slot order left to right)

## Arena

Holds every entity in play, for both owners.

Attributes:
- Towers
- Deployed units
- Deployed spells

## Play log

Append-only list of every card played, by both players.

- Royalebot's plays are logged by the action layer when it plays a card.
- Opponent plays are detected by vision: a group of new units matching a Card's `Deploys` (or a new spell) is logged as one Play. Other new units are spawns and are not logged.
- Units and spells from both players are still tracked by vision once they are on the arena.

### Play

Attributes:
- Owner
- Card
- Game time
- Position

## Entities:

### Towers

Towers count as buildings (units that target buildings only will target them) and can attack air.

Attributes:
- Owner
- Health (absolute HP as read from screen, zero if destroyed)
- Position (left, right, king)
- Active (only meaningful for the king tower)

### Deployed unit

Attributes:
- ID (Generated)
- Owner
- Unit type
- Source card (Card; empty for spawned units, e.g. Witch Skeletons)
- Level
- Health (%)
- Position
- Deploy remaining (seconds, 0 = active)
- Last seen (game time)

### Deployed spell

Kept for as long as it is in play. Position updates while travelling (e.g. Fireball, Log).

Attributes:
- ID (Generated)
- Owner
- Card
- Position
- Last seen (game time)

# Card catalog

Fixed reference data, the same in every match. Game state refers to Cards and Unit types by name and never copies their stats.

## Card

Attributes:
- Name
- Elixir cost
- Type (troop, building, spell)
- Deploy time (seconds)
- Deploys (list of Unit type + count; e.g. Skeleton Army)
- Radius (tiles, spells only)
  - Known limitation: the Log hits a strip, not a circle.

## Unit type

Attributes:
- Name
- Kind (ground, air, building)
- Can attack air?
- Targets buildings only? (e.g. Hog Rider, Giant, Balloon)
- Max health (per level)

# Geometry

## Position
Given as (x, y) in arena tiles (decimals allowed), with top left as (0, 0).
The arena is 18 tiles wide and 32 tiles tall. The opponent's side has low y values.
Vision converts screen pixels to tiles.

## Tile
One square of the arena grid, given as (col, row). Tile (col, row) covers x in [col, col + 1) and y in [row, row + 1).

## Arena layout (constant)

Left and right are as seen on screen (Royalebot's view), for both owners.

- River: rows 15–16, full width
- Left bridge: columns 2–4, rows 15–16
- Right bridge: columns 13–15, rows 15–16
- River tiles: the river minus the bridge tiles
- Opponent king tower: 4×4, columns 7–10, rows 1–4
- Opponent princess towers: 3×3, rows 5–7, columns 2–4 (left) and 13–15 (right)
- Royalebot princess towers: 3×3, rows 24–26, columns 2–4 (left) and 13–15 (right)
- Royalebot king tower: 4×4, columns 7–10, rows 27–30

# Not modelled

Out of scope for v1:
- Unit movement direction and speed
- Unit current target
- Status effects (frozen, slowed, raged)
- Evolutions
- Combat stats in the Card catalog (range, damage, hit speed, movement speed, building lifetime)
