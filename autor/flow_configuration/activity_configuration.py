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

from .configurable import Configurable
from .function_configuration import FunctionConfiguration


class ActivityConfiguration(Configurable):
    def __init__(
        self,
        configuration_dict: dict,
        activity_block_configuration: dict,
        activity_block_dummy_configuration,
    ):
        super().__init__(
            configuration_dict.get("name", None),
            configuration_dict,
            activity_block_configuration,
            activity_block_dummy_configuration,
        )
        self.__configuration_dict = configuration_dict

    @property
    def activity_type(self) -> dict:
        return self.__configuration_dict.get("type", None)

    @property
    def run_on(self) -> dict:
        return self.__configuration_dict.get("runOn", None)

    @property
    def continue_on(self) -> List[str]:
        return self.__configuration_dict.get("continueOn", None)

    def function(self, name: str) -> FunctionConfiguration:
        configuration_dict = {}
        if name in self.__configuration_dict["functions"]:
            configuration_dict = self.__configuration_dict["functions"][name]

        return FunctionConfiguration(
            name, configuration_dict, self.configuration, self.dummy_configuration
        )
