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
#    License for the specific language governing permi
#     *******************ssions and limitations
#    under the License.

import logging

from autor import Activity
from autor.framework.activity_registry import ActivityRegistry
from autor.framework.context_properties_registry import ContextPropertiesRegistry

output = ContextPropertiesRegistry.output
# pylint: disable-next=redefined-builtin
input = ContextPropertiesRegistry.input


# Calculate return the maximum value of the current max (received through property) and
# my max (received through configuration)
@ActivityRegistry.activity(type="max2")
class Max(Activity):
    # region constructor
    def __init__(self):
        super().__init__()
        # initial value that is used if no value has been provided by flow context
        self.__max: int = None
    # endregion
    # region property: max:int
    @property
    @input(mandatory=False, type=int)  # load the value before run() is called
    @output(mandatory=True, type=int)  # save the value after run() is finished
    def max(self) -> int:  # getter
        return self.__max

    @max.setter
    def max(self, n) -> None:  # setter
        self.__max = n
    # endregion

    def run(self):
        # ---------------- Prepare inputs -------------------#
        my_val = self.configuration["val"]  # Read my max from Flow Configuration file
        logging.info(f"Property:        'max': {self.max} (initial value read from context)")
        logging.info(f"Configuration:   'val': {my_val} (value provided through configuration)")

        # ----------------- Call helper ----------------------#
        new_max = max(my_val, self.max)
        logging.info(f"Property:        'max': {new_max} (final value written to context)")

        # --------------- Prepare outputs --------------------#
        self.max = new_max

        # ------------------ Set status ----------------------#
        if "status" in self.configuration:
            self.status = self.configuration["status"]



