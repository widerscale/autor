"""Provide access to Flow Configuration contents."""
import yaml

from autor.flow_configuration.activity_block_configuration import (
    ActivityBlockConfiguration,
)
from autor.flow_configuration.activity_configuration import (
    ActivityConfiguration,
)
from autor.flow_configuration.flow_configuration import FlowConfiguration

__all__ = ["FlowConfiguration", "ActivityBlockConfiguration", "ActivityConfiguration"]


def load_flow_configuration(path: str) -> FlowConfiguration:
    """Loads a flow configuration from the given path."""
    with open(path, "r", encoding="utf-8") as _file:
        configuration_dict = yaml.load(_file.read(), Loader=yaml.FullLoader)
        return FlowConfiguration(configuration_dict)
