"""Print the example game state.

Run `python -i -m royalebot` to land in a REPL with `state` and `catalog` loaded.
"""

from royalebot.example import example_state
from royalebot.explore import inspect, install, show  # noqa: F401  (for the REPL)
from royalebot import layout  # noqa: F401  (for the REPL)
from royalebot.state import Owner  # noqa: F401  (for the REPL)

state = example_state()
catalog = state.catalog

install()
show(state)
print("\nTry: state.opponent, state.crowns, state.arena.units_of(Owner.OPPONENT), layout.TOWERS, inspect(state)")
