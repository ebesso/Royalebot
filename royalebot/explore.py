"""Helpers for exploring game state objects in a terminal or REPL."""

import rich
import rich.pretty


def show(obj: object) -> None:
    """Pretty-print any model object, including derived values on GameState."""
    rich.pretty.pprint(obj, expand_all=False, indent_guides=True)


def inspect(obj: object) -> None:
    """List an object's fields, properties and methods with their docs."""
    rich.inspect(obj, methods=True, docs=True)


def install() -> None:
    """Make the REPL pretty-print every result automatically."""
    rich.pretty.install(indent_guides=True)
