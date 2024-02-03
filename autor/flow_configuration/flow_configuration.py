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
from typing import List

from .activity_block_configuration import ActivityBlockConfiguration


class FlowConfiguration:
    def __init__(self, flow_configuration_dictionary: dict):
        self.__flow_configuration_dictionary = flow_configuration_dictionary

    @property
    def flow_id(self) -> str:
        return self.__flow_configuration_dictionary["flowId"]

    @property
    def configuration(self) -> dict:
        if "configuration" in self.__flow_configuration_dictionary:
            return self.__flow_configuration_dictionary["configuration"]
        return {}

    @property
    def dummy_configuration(self) -> dict:
        if "dummyConfiguration" in self.__flow_configuration_dictionary:
            return self.__flow_configuration_dictionary["dummyConfiguration"]
        return {}

    @property
    def extensions(self) -> List[str]:
        if "extensions" in self.__flow_configuration_dictionary:
            return self.__flow_configuration_dictionary["extensions"]
        return []

    @property
    def activity_modules(self) -> List[str]:
        if "activityModules" in self.__flow_configuration_dictionary:
            return self.__flow_configuration_dictionary["activityModules"]
        return []

    @property
    def helpers(self) -> dict:
        if "helpers" in self.__flow_configuration_dictionary:
            return self.__flow_configuration_dictionary["helpers"]
        return {}

    @property
    def activity_block_ids(self) -> List[str]:
        return self.__flow_configuration_dictionary["activityBlocks"].keys()

    def activity_block(self, name: str) -> ActivityBlockConfiguration:
        if name not in self.__flow_configuration_dictionary["activityBlocks"]:
            raise ValueError(f"No activity block named '{name}' was found.")

        configuration = self.__flow_configuration_dictionary["activityBlocks"][name]
        return ActivityBlockConfiguration(
            name, configuration, self.configuration, self.dummy_configuration
        )

    def get_raw_configuration(self)->dict:
        return self.__flow_configuration_dictionary
