"""Flow configuration module."""

from typing import Any, Dict, List

from autor.flow_configuration.activity_block_configuration import (
    ActivityBlockConfiguration,
)


class FlowConfiguration:
    """Configuration for a flow (multiple activity blocks)."""

    def __init__(self, flow_configuration_dictionary: Dict[str, Any]):
        """TODO."""
        self.__flow_configuration_dictionary = flow_configuration_dictionary

    @property
    def flow_id(self) -> str:
        """TODO."""
        return self.__flow_configuration_dictionary["flowId"]

    @property
    def default_activity_configuration(self) -> Dict[str, Any]:
        """TODO."""
        if "default_activity_configuration" in self.__flow_configuration_dictionary:
            return self.__flow_configuration_dictionary["default_activity_configuration"]
        return {}

    @property
    def extensions(self) -> List[str]:
        """TODO."""
        if "extensions" in self.__flow_configuration_dictionary:
            return self.__flow_configuration_dictionary["extensions"]
        return []

    @property
    def activity_modules(self) -> List[str]:
        """TODO."""
        if "activityModules" in self.__flow_configuration_dictionary:
            return self.__flow_configuration_dictionary["activityModules"]
        return []

    @property
    def helpers(self) -> Dict[str, Any]:
        """TODO."""
        if "helpers" in self.__flow_configuration_dictionary:
            return self.__flow_configuration_dictionary["helpers"]
        return {}

    @property
    def activity_block_ids(self) -> List[str]:
        """TODO."""
        return self.__flow_configuration_dictionary["activityBlocks"].keys()

    def activity_block(self, name: str) -> ActivityBlockConfiguration:
        """TODO."""
        if name not in self.__flow_configuration_dictionary["activityBlocks"]:
            raise ValueError(f"No activity block named '{name}' was found")

        configuration = self.__flow_configuration_dictionary["activityBlocks"][name]
        return ActivityBlockConfiguration(
            # TODO: It is probably wrong to send flow_configuration to the activity block, send something else instead.
            name,
            configuration,
            self.__flow_configuration_dictionary,
        )
