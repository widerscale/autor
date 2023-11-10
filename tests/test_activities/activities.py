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
from autor.framework.activity_block_callback import ActivityBlockCallback
from autor.framework.activity_registry import ActivityRegistry
from autor.framework.constants import Status
from autor.framework.context_properties_registry import ContextPropertiesRegistry

output = ContextPropertiesRegistry.output
# pylint: disable-next=redefined-builtin
input = ContextPropertiesRegistry.input



# Calculate return the maximum value of the current max (received through property) and
# my max (received through configuration)
@ActivityRegistry.activity(type="MAX")
class Max(Activity):
    def __init__(self):
        super().__init__()
        # initial value that is used if no value has been provided by flow context
        self.__max: int = None


    @property
    @input(mandatory=False, type=int)  # load the value before run() is called
    @output(mandatory=True, type=int)  # save the value after run() is finished
    def max(self) -> int:  # getter
        return self.__max

    @max.setter
    def max(self, n) -> None:  # setter
        self.__max = n

    def run(self):
        my_val = self.configuration["val"]  # Read my max from Flow Configuration file
        logging.info(f"Property:        'max': {self.max} (initial value)")
        logging.info(f"Configuration:   'val:' {my_val}")
        if self.max is None:
            self.max = my_val
        else:
            self.max = max(self.max, my_val)  # Calculate the new max
        logging.info(f"Property:        'max': {self.max} (final value)")




    def _run(self):
        my_val = self.configuration["val"]  # Read my max from Flow Configuration file
        self.max = self.helper_max(self.max, my_val)



    def helper_max(self, self_max, my_val):
        if self_max is None:
            return my_val
        else:
            return max(self_max, my_val)  # Calculate the new max