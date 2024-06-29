import typing
import collections.abc
import bpy.types

GenericType1 = typing.TypeVar("GenericType1")
GenericType2 = typing.TypeVar("GenericType2")

def attribute_add(
    override_context: bpy.types.Context | dict[str, typing.Any] | None = None,
    execution_context: int | str | None = None,
    undo: bool | None = None,
    *,
    name: str | typing.Any = "Attribute",
    domain: str | None = "POINT",
    data_type: str | None = "FLOAT",
):
    """Add attribute to geometry

    :type override_context: bpy.types.Context | dict[str, typing.Any] | None
    :type execution_context: int | str | None
    :type undo: bool | None
    :param name: Name, Name of new attribute
    :type name: str | typing.Any
    :param domain: Domain, Type of element that attribute is stored on
    :type domain: str | None
    :param data_type: Data Type, Type of data stored in attribute
    :type data_type: str | None
    """

    ...

def attribute_convert(
    override_context: bpy.types.Context | dict[str, typing.Any] | None = None,
    execution_context: int | str | None = None,
    undo: bool | None = None,
    *,
    mode: str | None = "GENERIC",
    domain: str | None = "POINT",
    data_type: str | None = "FLOAT",
):
    """Change how the attribute is stored

    :type override_context: bpy.types.Context | dict[str, typing.Any] | None
    :type execution_context: int | str | None
    :type undo: bool | None
    :param mode: Mode
    :type mode: str | None
    :param domain: Domain, Which geometry element to move the attribute to
    :type domain: str | None
    :param data_type: Data Type
    :type data_type: str | None
    """

    ...

def attribute_remove(
    override_context: bpy.types.Context | dict[str, typing.Any] | None = None,
    execution_context: int | str | None = None,
    undo: bool | None = None,
):
    """Remove attribute from geometry

    :type override_context: bpy.types.Context | dict[str, typing.Any] | None
    :type execution_context: int | str | None
    :type undo: bool | None
    """

    ...

def color_attribute_add(
    override_context: bpy.types.Context | dict[str, typing.Any] | None = None,
    execution_context: int | str | None = None,
    undo: bool | None = None,
    *,
    name: str | typing.Any = "Color",
    domain: str | None = "POINT",
    data_type: str | None = "FLOAT_COLOR",
    color: typing.Any | None = (0.0, 0.0, 0.0, 1.0),
):
    """Add color attribute to geometry

    :type override_context: bpy.types.Context | dict[str, typing.Any] | None
    :type execution_context: int | str | None
    :type undo: bool | None
    :param name: Name, Name of new color attribute
    :type name: str | typing.Any
    :param domain: Domain, Type of element that attribute is stored on
    :type domain: str | None
    :param data_type: Data Type, Type of data stored in attribute
    :type data_type: str | None
    :param color: Color, Default fill color
    :type color: typing.Any | None
    """

    ...

def color_attribute_convert(
    override_context: bpy.types.Context | dict[str, typing.Any] | None = None,
    execution_context: int | str | None = None,
    undo: bool | None = None,
    *,
    domain: str | None = "POINT",
    data_type: str | None = "FLOAT_COLOR",
):
    """Change how the color attribute is stored

    :type override_context: bpy.types.Context | dict[str, typing.Any] | None
    :type execution_context: int | str | None
    :type undo: bool | None
    :param domain: Domain, Type of element that attribute is stored on
    :type domain: str | None
    :param data_type: Data Type, Type of data stored in attribute
    :type data_type: str | None
    """

    ...

def color_attribute_duplicate(
    override_context: bpy.types.Context | dict[str, typing.Any] | None = None,
    execution_context: int | str | None = None,
    undo: bool | None = None,
):
    """Duplicate color attribute

    :type override_context: bpy.types.Context | dict[str, typing.Any] | None
    :type execution_context: int | str | None
    :type undo: bool | None
    """

    ...

def color_attribute_remove(
    override_context: bpy.types.Context | dict[str, typing.Any] | None = None,
    execution_context: int | str | None = None,
    undo: bool | None = None,
):
    """Remove color attribute from geometry

    :type override_context: bpy.types.Context | dict[str, typing.Any] | None
    :type execution_context: int | str | None
    :type undo: bool | None
    """

    ...

def color_attribute_render_set(
    override_context: bpy.types.Context | dict[str, typing.Any] | None = None,
    execution_context: int | str | None = None,
    undo: bool | None = None,
    *,
    name: str | typing.Any = "Color",
):
    """Set default color attribute used for rendering

    :type override_context: bpy.types.Context | dict[str, typing.Any] | None
    :type execution_context: int | str | None
    :type undo: bool | None
    :param name: Name, Name of color attribute
    :type name: str | typing.Any
    """

    ...
