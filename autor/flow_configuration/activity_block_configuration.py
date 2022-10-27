"""Activity block configuration module."""

from typing import Any, Dict, List, Optional

from autor.flow_configuration._configurable import Configurable
from autor.flow_configuration.activity_configuration import (
    ActivityConfiguration,
)


class ActivityBlockConfiguration(Configurable):
    """Configuration for an activity block."""

    def __init__(
        self, name: str, configuration_dict: Dict[str, Any], flow_configuration: Dict[str, Any]
    ):
        """TODO."""
        super().__init__(name, configuration_dict, flow_configuration)
        self.__configuration_dict = configuration_dict
        self.__activities: Optional[List[ActivityConfiguration]] = None
        self.__before_block: Optional[List[ActivityConfiguration]] = None
        self.__after_block: Optional[List[ActivityConfiguration]] = None
        self.__before_activity: Optional[List[ActivityConfiguration]] = None
        self.__after_activity: Optional[List[ActivityConfiguration]] = None

    @property
    def default_activity_configuration(self) -> Dict[str, Any]:
        """TODO."""
        if "default_activity_configuration" in self.__configuration_dict:
            return self.__configuration_dict["default_activity_configuration"]
        return {}

    @property
    def activities(self) -> List[ActivityConfiguration]:
        """TODO."""
        if self.__activities is None:
            activity_list = []
            if "activities" in self.__configuration_dict:
                for activity in self.__configuration_dict["activities"]:
                    activity_list.append(ActivityConfiguration(activity, self.configuration))
            self.__activities = activity_list

        return self.__activities

    @property
    def before_block(self) -> List[ActivityConfiguration]:
        """TODO."""
        if self.__before_block is None:
            self.__before_block = self._activity_list("beforeBlock")

        return self.__before_block

    @property
    def after_block(self) -> List[ActivityConfiguration]:
        """TODO."""
        if self.__after_block is None:
            self.__after_block = self._activity_list("afterBlock")

        return self.__after_block

    @property
    def before_activity(self) -> List[ActivityConfiguration]:
        """TODO."""
        if self.__before_activity is None:
            self.__before_activity = self._activity_list("beforeActivity")

        return self.__before_activity

    @property
    def after_activity(self) -> List[ActivityConfiguration]:
        """TODO."""
        if self.__after_activity is None:
            self.__after_activity = self._activity_list("afterActivity")

        return self.__after_activity

    def _activity_list(self, activity_group_type: str) -> List[ActivityConfiguration]:
        activity_list = []
        if activity_group_type in self.__configuration_dict:
            for activity in self.__configuration_dict[activity_group_type]["activities"]:
                activity_list.append(
                    ActivityConfiguration(activity, self.default_activity_configuration)
                )

        return activity_list
