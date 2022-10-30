#  Copyright 2022-Present Autor contributors
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
from datetime import timedelta
from typing import List

from .activity_configuration import ActivityConfiguration
from .configurable import Configurable


class Worker:
    def __init__(self, configuration_dict: dict):
        self.__resource_set_id = configuration_dict.get("resourceSetId", None)
        self.__resource_set_pool_id = configuration_dict.get("resourceSetPoolId", None)
        self.__resource_set_capabilities = configuration_dict.get("resourceSetCapabilities", None)
        self.__agent_id = configuration_dict.get("agentId", None)
        self.__agent_labels = configuration_dict.get("agentLabels", None)
        self.__priority_order = configuration_dict.get("priorityOrder", None)
        self.__expected_max_duration = configuration_dict.get("expectedMaxDuration", None)

    @property
    def resource_set_id(self) -> str:
        return self.__resource_set_id

    @property
    def resource_set_pool_id(self) -> str:
        return self.__resource_set_pool_id

    @property
    def resource_set_capabilities(self) -> List[str]:
        return self.__resource_set_capabilities

    @property
    def agent_id(self) -> str:
        return self.__agent_id

    @property
    def agent_labels(self) -> List[str]:
        return self.__agent_labels

    @property
    def priority_order(self) -> int:
        return self.__priority_order

    @property
    def expected_max_duration(self) -> timedelta:
        return self.__expected_max_duration


# pylint: disable=singleton-comparison
class ActivityBlockConfiguration(Configurable):
    def __init__(
        self,
        name: str,
        configuration_dict: dict,
        flow_configuration: dict,
        flow_dummy_configuration,
    ):
        super().__init__(name, configuration_dict, flow_configuration, flow_dummy_configuration)
        self.__configuration_dict = configuration_dict
        self.__activities = None
        self.__before_block = None
        self.__after_block = None
        self.__before_activity = None
        self.__after_activity = None

    @property
    def worker(self) -> Worker:
        if "worker" in self.__configuration_dict:
            return Worker(self.__configuration_dict["worker"])
        raise RuntimeError(f"No 'worker' config in: {self.__configuration_dict!r}")

    @property
    def activities(self) -> List[ActivityConfiguration]:
        if self.__activities == None:
            activity_list = []
            if "activities" in self.__configuration_dict:
                for activity in self.__configuration_dict["activities"]:
                    activity_list.append(
                        ActivityConfiguration(
                            activity, self.configuration, self.dummy_configuration
                        )
                    )
            self.__activities = activity_list

        return self.__activities

    @property
    def before_block(self) -> List[ActivityConfiguration]:
        if self.__before_block == None:
            self.__before_block = self._activity_list("beforeBlock")

        return self.__before_block

    @property
    def after_block(self) -> List[ActivityConfiguration]:
        if self.__after_block == None:
            self.__after_block = self._activity_list("afterBlock")

        return self.__after_block

    @property
    def before_activity(self) -> List[ActivityConfiguration]:
        if self.__before_activity == None:
            self.__before_activity = self._activity_list("beforeActivity")

        return self.__before_activity

    @property
    def after_activity(self) -> List[ActivityConfiguration]:
        if self.__after_activity == None:
            self.__after_activity = self._activity_list("afterActivity")

        return self.__after_activity

    def _activity_list(self, activity_group_type: str) -> List[ActivityConfiguration]:
        activity_list = []
        if activity_group_type in self.__configuration_dict:
            for activity in self.__configuration_dict[activity_group_type]["activities"]:
                activity_list.append(
                    ActivityConfiguration(activity, self.configuration, self.dummy_configuration)
                )

        return activity_list
