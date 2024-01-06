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
import inspect
import logging

from autor import Activity
from autor.framework.activity_block_callback import ActivityBlockCallback
from autor.framework.activity_registry import ActivityRegistry
from autor.framework.constants import Status
from autor.framework.context_properties_registry import ContextPropertiesRegistry


output = ContextPropertiesRegistry.output
# pylint: disable-next=redefined-builtin
input = ContextPropertiesRegistry.input
config = ContextPropertiesRegistry.config


@ActivityRegistry.activity(type="ECHO")
class Echo(Activity):

    def __init__(self):
        super().__init__()



    #region property: name @config(mandatory=True, type=str)
    @property
    @config(mandatory=True, type=str)
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, n:str) -> None:
        self._name = n
    #endregion

    #region property: times_to_echo @input(mandatory=False, type=int)
    @property
    @input(mandatory=False, type=int, default=1)
    @output(mandatory=True, type=int)
    def times_to_echo(self) -> int:
        return self._times_to_echo
    #endregion

    #region property: times_to_echo @output(mandatory=True, type=int)
    @times_to_echo.setter
    def times_to_echo(self, n:int) -> None:
        self._times_to_echo = n
    #endregion

    def run(self):
        logging.info(f"{self.name}")
        for i in range(self.times_to_echo):
            logging.info("Echo!")
        self.times_to_echo = self.times_to_echo + 1



