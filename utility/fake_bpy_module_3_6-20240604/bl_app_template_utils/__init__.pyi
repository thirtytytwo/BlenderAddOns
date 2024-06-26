import typing
import collections.abc

GenericType1 = typing.TypeVar("GenericType1")
GenericType2 = typing.TypeVar("GenericType2")

def activate(template_id=None, reload_scripts=False): ...
def import_from_id(template_id, ignore_not_found=False): ...
def import_from_path(path, ignore_not_found=False): ...
def reset(reload_scripts=False):
    """Sets default state."""

    ...
