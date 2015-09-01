from mock import MagicMock


def test_ConfigObject():
    """
    Test the ConfigObject class
    """
    from paradrop.backend.pdconfd.config.base import ConfigObject

    config = ConfigObject()
    config.typename = "type"
    config.name = "name"
    assert str(config) == "config type name"


def test_base():
    from paradrop.backend.pdconfd.config import base

    m = MagicMock()
    assert base.ConfigObject().update(m, m) == None
