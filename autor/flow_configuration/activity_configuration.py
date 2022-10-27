"""Activity configuration module."""

from typing import Any, Dict, List

from autor.flow_configuration._configurable import Configurable


class ActivityConfiguration(Configurable):
    """Configuration for an activity."""

    def __init__(
        self, configuration_dict: Dict[str, Any], activity_block_configuration: Dict[str, Any]
    ):
        """TODO."""
        super().__init__(
            configuration_dict.get("name", None), configuration_dict, activity_block_configuration
        )
        self.__configuration_dict = configuration_dict

    @property
    def activity_type(self) -> str:
        """TODO."""
        return self.__configuration_dict.get("type", None)

    @property
    def run_on(self) -> Dict[str, Any]:
        """TODO."""
        return self.__configuration_dict.get("runOn", None)

    @property
    def continue_on(self) -> List[str]:
        """TODO."""
        return self.__configuration_dict.get("continueOn", None)
