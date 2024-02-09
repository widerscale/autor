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
from autor.framework.constants import Status
from autor.framework.context_properties_registry import ContextPropertiesRegistry

output = ContextPropertiesRegistry.output
# pylint: disable-next=redefined-builtin
input = ContextPropertiesRegistry.input
config = ContextPropertiesRegistry.config


# Calculate return the maximum value of the current max (received through property) and
# my max (received through configuration)
@ActivityRegistry.activity(type="max")
class Max(Activity):

    # region property: max @input/output(mandatory=False/True, type=int)
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
        # ---------------- Prepare inputs -------------------#
        logging.info(f"Property:        'max': {self.max} (initial value read from context)")
        logging.info(f"Configuration:   'val': {self.val} (value provided through configuration)")

        # --------------- Calculate max --------------------#
        new_max = max(self.val, self.max)

        # ------------------ Set output --------------------#
        self.max = new_max
        logging.info(f"Property:        'max': {new_max} (final value written to context)")
        # ------------------ Set status --------------------#
        if "status" in self.configuration:
            self.status = self.configuration["status"]


# Calculate return the maximum value of the current max (received through property) and
# my max (received through configuration). Every second run the activity casts an exception.
# Use this activity to simulate a failure that will be fixed when re-run.
# The first run will fail, the second will succeed.
@ActivityRegistry.activity(type="max-with-exception-every-second-run")
class MaxWithExceptionEverySecondRun(Activity):
    # region constructor
    def __init__(self):
        super().__init__()
        # initial values that is used if no value has been provided by flow context
        self.__max: int = None
        self.__run_nbr: int = 0
    # endregion
    # region property: max @input(mandatory=False, type=int
    @property
    @input(mandatory=False, type=int)  # load the value before run() is called
    @output(mandatory=True, type=int)  # save the value after run() is finished
    def max(self) -> int:  # getter
        return self.__max
    @max.setter
    def max(self, n) -> None:  # setter
        self.__max = n
    # endregion
    # region property: run_nbr:int

    @property
    @input(mandatory=False, type=int)  # load the value before run() is called
    def run_nbr(self) -> int:      # getter
        return self.__run_nbr

    @run_nbr.setter
    def run_nbr(self, n) -> None:  # setter
        self.__run_nbr = n
    # endregion

    def run(self):
        # ---------------- Prepare inputs -------------------#
        my_val = self.configuration["val"]  # Read my max from Flow Configuration file
        logging.info(f"Property:        'max': {self.max} (initial value read from context)")
        logging.info(f"Configuration:   'val': {my_val} (value provided through configuration)")
        logging.info(f"Property:        'run_nbr': {self.run_nbr} (initial value read from context)")

        if self.run_nbr % 2 == 0:
            logging.info("odd run -> throw an exception")
            raise Exception("This is a planned exception for an odd run number.")

        else:
            logging.info("Not odd run -> not throwing exception")
            # ----------------- Call helper ----------------------#
            new_max = Helper.max(val1=my_val, val2=self.max)
            logging.info(f"Property:        'max': {new_max} (final value written to context)")

        # --------------- Prepare outputs --------------------#
        self.max = new_max







# Increase 'runNbr' in context each time the activity is run.
@ActivityRegistry.activity(type="run-nbr")
class CountRuns(Activity):
    # region constructor
    def __init__(self):
        super().__init__()
        # initial values that is used if no value has been provided by flow context
        self.__run_nbr: int = 0
    # endregion
    # region property: run_nbr:int

    @property
    @input(mandatory=False, type=int)  # load the value before run() is called
    @output(mandatory=True, type=int)  # save the value after run() is finished
    def run_nbr(self) -> int:      # getter
        return self.__run_nbr

    @run_nbr.setter
    def run_nbr(self, n) -> None:  # setter
        self.__run_nbr = n
    # endregion

    def run(self):
        self.run_nbr = self.run_nbr + 1
        logging.info(f"Setting run_nbr: {self.run_nbr}")







# Problematic activity - mandatory input may not have default value.
@ActivityRegistry.activity(type="max-problem-1")
class MaxProblem1(Activity):
    # region property: max @input/output(mandatory=True/True, type=int)
    @property
    @input(mandatory=True, type=int, default=99)
    @output(mandatory=True, type=int)
    def max(self) -> int:
        return self._max

    @max.setter
    def max(self, n) -> None:  # setter
        self._max = n
    # endregion

    def run(self):
        # ---------------- Prepare inputs -------------------#
        my_val = self.configuration["val"]  # Read my max from Flow Configuration file
        logging.info(f"Property:        'max': {self.max} (initial value read from context)")
        logging.info(f"Configuration:   'val': {my_val} (value provided through configuration)")

        # ----------------- Call helper ----------------------#
        new_max = Helper.max(val1=my_val, val2=self.max)
        logging.info(f"Property:        'max': {new_max} (final value written to context)")

        # --------------- Prepare outputs --------------------#
        self.max = new_max

        # ------------------ Set status ----------------------#
        if "status" in self.configuration:
            self.status = self.configuration["status"]





@ActivityRegistry.activity(type="configurable-status")
class ConfigurableStatus(Activity):

    # region property: status_to_set @config(mandatory=True, type=str)
    @property
    @config(mandatory=True, type=str)
    def status_to_set(self) -> str:
        return self._status_to_set

    @status_to_set.setter
    def status_to_set(self, value: str) -> None:
        self._status_to_set = value
    # endregion

    def run(self):
        logging.info(f"Setting status from configuration to: {self.status_to_set}")
        self.status = self.status_to_set

@ActivityRegistry.activity(type="fail-every-second-run")
class FailEverySecondRun(Activity):
    
    # region property: nbr_runs @input/@output(mandatory=False, type=int, default=0)
    @property
    @input(mandatory=False, type=int, default=0)
    @output(mandatory=True, type=int)
    def nbr_runs(self) -> int:
        return self._nbr_runs
    
    @nbr_runs.setter
    def nbr_runs(self, value: int) -> None:
        self._nbr_runs = value
    # endregion

    def run(self):
        logging.info(type(self.nbr_runs))
        logging.info(f"nbr_runs: {self.nbr_runs}")
        self.nbr_runs = self.nbr_runs + 1
        if self.nbr_runs % 2 != 0:
            self.status = Status.FAIL
        else:
            self.status = Status.SUCCESS







# Problematic activity - mandatory input may not have default value.
@ActivityRegistry.activity(type="max-problem-2")
class MaxProblem2(Activity):

    def __init__(self):
        super().__init__()
        # initial values that is used if no value has been provided by flow context
        self._max: int = 88


    # region property: max @input/output(mandatory=True/True, type=int)
    @property
    @input(mandatory=True, type=int)
    @output(mandatory=True, type=int)
    def max(self) -> int:
        return self._max

    @max.setter
    def max(self, n) -> None:  # setter
        self._max = n
    # endregion

    def run(self):
        # ---------------- Prepare inputs -------------------#
        my_val = self.configuration["val"]  # Read my max from Flow Configuration file
        logging.info(f"Property:        'max': {self.max} (initial value read from context)")
        logging.info(f"Configuration:   'val': {my_val} (value provided through configuration)")

        # ----------------- Call helper ----------------------#
        new_max = Helper.max(val1=my_val, val2=self.max)
        logging.info(f"Property:        'max': {new_max} (final value written to context)")

        # --------------- Prepare outputs --------------------#
        self.max = new_max

        # ------------------ Set status ----------------------#
        if "status" in self.configuration:
            self.status = self.configuration["status"]





# Problematic activity - mandatory input may not have default value.
@ActivityRegistry.activity(type="mandatory-max")
class MandatoryMax(Activity):

    # region property: max @input(mandatory=True, type=int)
    @property
    @input(mandatory=True, type=int)
    def max(self) -> int:
        return self._max

    @max.setter
    def max(self, value: int) -> None:
        self._max = value
    # endregion


    def run(self):
        logging.info(f"Expected mandatory input: {self.max}")


@ActivityRegistry.activity(type="divide-by-zero")
class DivideByZero(Activity):

    def run(self):
        logging.info("Creating trouble on purpose and dividing with zero to create an exception.")
        x = 15/0











class Helper:

    @staticmethod
    def max(val1: int, val2: int):
        if val1 is None and val2 is None:
            raise ValueError("Both parameters to Helper.max() were None.")
        if val1 is None:
            return val2
        if val2 is None:
            return val1
        return max(val1,val2)

