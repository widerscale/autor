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
import random
from typing import List
import os.path
import pathlib
from pathlib import Path

from autor import Activity
from autor.framework.activity_block_callback import ActivityBlockCallback
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
        logging.info("Running activity...")
        self.max = max(self.val, self.max)


@ActivityRegistry.activity(type="max-with-failure-chance")
class MaxWithFailureChance(Activity):

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
        logging.info("Running activity...")
        self.max = max(self.val, self.max)
        self.status = random.choice([Status.SUCCESS, Status.FAIL])
        logging.info(f"Setting status to: {self.status}")



@ActivityRegistry.activity(type="max-with-every-other-fail")
class FailEveryOtherRun(Activity):

    # region property: nbr_activity_runs @input/@output(mandatory=False/True, type=int, default=0)
    @property
    @input(mandatory=False, type=int, default=0)
    @output (mandatory=True, type=int)
    def nbr_activity_runs(self) -> int:
        return self._nbr_activity_runs

    @nbr_activity_runs.setter
    def nbr_activity_runs(self, value: int) -> None:
        self._nbr_activity_runs = value
    # endregion
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
        logging.info("Running activity...")
        self.max = max(self.val, self.max)


        if os.path.isfile("time_to_fail"):
            logging.info("Time to fail -> setting status to FAIL")
            os.remove("time_to_fail")
            self.status = Status.FAIL
        else:
 
            Path("time_to_fail").touch()
            self.status = Status.SUCCESS # For clarification only. Status would be SUCCESS by default.


@ActivityRegistry.activity(type="fail-first-time-run")
class FailFirstTimeRun(Activity):

    # region property: nbr_activity_runs @input/@output(mandatory=False/True, type=int, default=0)
    @property
    @input(mandatory=False, type=int, default=0)
    @output (mandatory=True, type=int)
    def nbr_activity_runs(self) -> int:
        return self._nbr_activity_runs

    @nbr_activity_runs.setter
    def nbr_activity_runs(self, value: int) -> None:
        self._nbr_activity_runs = value
    # endregion
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
        # This activity uses files for signalling. Register a callback
        # that will make sure that these files will be cleaned up.
        self.activity_block_callbacks.append(FailFirstTimeRunCleanUp(self))

        logging.info("Running activity...")
        self.max = max(self.val, self.max)


        if not os.path.isfile("failure_performed"):
            logging.info("Time to fail -> setting status to FAIL")
            Path("failure_performed").touch() # Create the file that signals the failure
            self.status = Status.FAIL



class FailFirstTimeRunCleanUp(ActivityBlockCallback):
    def __int__(self, activity:Activity):
        super.__init__(activity=activity, run_on=[Status.ALL])

    def run(self):
        logging.info("Running callback...")

        # Clean up if needed
        if os.path.isfile("failure_performed"):
            os.remove("failure_performed")
            logging("Deleted the signalling file.")
        else:
            logging("Nothing to clean up.")
            
        
    


