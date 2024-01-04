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
        self._echo_nbr: int = 0

    #region property: name @config(mandatory=True, type=str)
    @property
    @config(mandatory=True, type=str)
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, n:str) -> None:
        self._name = n
    #endregion

    #region property: echo_nbr @input(mandatory=False, type=int)
    @property
    @input(mandatory=False, type=int, default=0)
    @output(mandatory=True, type=int)
    def echo_nbr(self) -> int:
        return self._echo_nbr
    #endregion

    #region property: echo_nbr @output(mandatory=True, type=int)
    @echo_nbr.setter
    def echo_nbr(self, n:int) -> None:
        self._echo_nbr = n
    #endregion

    def run(self):
        self.echo_nbr = self._echo_nbr +1
        logging.info(f"{self.name}")
        for i in range(self.echo_nbr):
            logging.info("Echo!")



