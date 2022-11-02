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
from .configurable import Configurable


class FunctionConfiguration(Configurable):
    def __init__(
        self,
        name,
        configuration_dict: dict,
        activity_configuration: dict,
        activity_dummy_configuration,
    ):
        super().__init__(
            name, configuration_dict, activity_configuration, activity_dummy_configuration
        )
        # pylint: disable-next=unused-private-member
        self.__configuration_dict = configuration_dict
