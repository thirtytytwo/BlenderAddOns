import typing
import collections.abc

GenericType1 = typing.TypeVar("GenericType1")
GenericType2 = typing.TypeVar("GenericType2")

def connect_sockets(input, output):
    """Connect sockets in a node tree.This is useful because the links created through the normal Python API are
    invalid when one of the sockets is a virtual socket (grayed out sockets in
    Group Input and Group Output nodes).It replaces node_tree.links.new(input, output)

    """

    ...

def find_node_input(node, name): ...
def find_node_input(node, name): ...
