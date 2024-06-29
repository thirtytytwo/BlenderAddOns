import typing
import collections.abc

GenericType1 = typing.TypeVar("GenericType1")
GenericType2 = typing.TypeVar("GenericType2")

class I18nSettings:
    """Class allowing persistence of our settings!
    Saved in JSon format, so settings should be JSon'able objects!
    """

    BRANCHES_DIR: typing.Any
    FILE_NAME_POT: typing.Any
    GIT_I18N_PO_DIR: typing.Any
    GIT_I18N_ROOT: typing.Any
    MO_PATH_ROOT: typing.Any
    MO_PATH_TEMPLATE: typing.Any
    POTFILES_SOURCE_DIR: typing.Any
    PRESETS_DIR: typing.Any
    PY_SYS_PATHS: typing.Any
    TEMPLATES_DIR: typing.Any
    TRUNK_DIR: typing.Any
    TRUNK_MO_DIR: typing.Any
    TRUNK_PO_DIR: typing.Any

    def from_dict(self, mapping):
        """

        :param mapping:
        """
        ...

    def from_json(self, string):
        """

        :param string:
        """
        ...

    def load(self, fname, reset=False):
        """

        :param fname:
        :param reset:
        """
        ...

    def save(self, fname):
        """

        :param fname:
        """
        ...

    def to_dict(self): ...
    def to_json(self): ...
