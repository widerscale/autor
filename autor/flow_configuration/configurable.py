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
class Configurable:
    def __init__(
        self,
        name: str,
        configuration_dict: dict,
        parent_configuration: dict,
        parent_dummy_configuration: dict,
    ) -> None:
        self.__name = name
        self.__configuration_dict = configuration_dict
        self.__parent_configuration = parent_configuration
        self.__parent_dummy_configuration = parent_dummy_configuration
        self.__configuration = None
        self.__dummy_configuration = None

    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, n):
        self.__name = n

    @property
    def configuration(self) -> dict:
        if self.__configuration is not None:
            return self.__configuration

        configuration = self.__parent_configuration.copy()

        if "configuration" in self.__configuration_dict:
            configuration.update(self.__configuration_dict["configuration"])

        self.__configuration = configuration
        return self.__configuration

    @property
    def dummy_configuration(self) -> dict:
        if self.__dummy_configuration is not None:
            return self.__dummy_configuration

        dummy_configuration = self.__parent_dummy_configuration.copy()

        if "dummy_configuration" in self.__configuration_dict:
            dummy_configuration.update(self.__configuration_dict["dummy_configuration"])

        self.__dummy_configuration = dummy_configuration
        return self.__dummy_configuration
