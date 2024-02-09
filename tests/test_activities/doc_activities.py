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

import logging

from autor import Activity
from autor.framework.activity_registry import ActivityRegistry
from autor.framework.constants import Status
from autor.framework.context_properties_registry import ContextPropertiesRegistry

output = ContextPropertiesRegistry.output
# pylint: disable-next=redefined-builtin
input = ContextPropertiesRegistry.input
config = ContextPropertiesRegistry.config


@ActivityRegistry.activity(type="max")
class Max(Activity):

    # region property: max @input/output(mandatory=False/True, type=int, default=0)
    @property
    @input(mandatory=False, type=int, default=0)
    @output(mandatory=True, type=int)
    def max(self) -> int:
        return self._max

    @max.setter
    def max(self, n) -> None:
        self._max = n
    # endregion
    # region property: val @config(mandatory=True, type=int)
    @property
    @config(mandatory=True, type=int)
    def val(self) -> int:
        return self._val

    @val.setter
    def val(self, value: int) -> None:
        self._val = value
    # endregion


    def run(self):
        logging.info(f"Input:  'max': {self.max} (initial value read from context or default)")
        logging.info(f"Config: 'val': {self.val} (value provided through configuration)")

        self.max = max(self.val, self.max)

        logging.info(f"Output: 'max': {self.max} (output written to context)")




