import typing
import collections.abc

GenericType1 = typing.TypeVar("GenericType1")
GenericType2 = typing.TypeVar("GenericType2")

def add_node_type(layout, node_type, label=None):
    """Add a node type to a menu."""

    ...

def add_simulation_zone(layout, label):
    """Add simulation zone to a menu."""

    ...

def draw_assets_for_catalog(layout, catalog_path): ...
def draw_node_group_add_menu(context, layout):
    """Add items to the layout used for interacting with node groups."""

    ...

def draw_root_assets(layout): ...
