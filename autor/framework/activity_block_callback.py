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
import abc
from typing import List

from autor.framework.check import Check

# from autor.framework.activity import Activity
from autor.framework.constants import Status


class ActivityBlockCallback:
    """
    ActivityBlockCallbacks are callbacs that are created by activities and run after an activity \
        block has finished running.
    Each callback has a run_on condition, that is a list of statuses that make up the running \
        condition for the callback.
    The running condition is compared to the status of the activity that owns the callback \
        and if the running condition is fulfilled, the callback is run.

    To create callbacks, inherit this class, implement the run() method and attatch an instance of \
        this object to your activity.
    """

    __metaclass__ = abc.ABCMeta

    def __init__(self, activity, run_on: List[Status]):
        """[summary]

        Args:
            activity (Activity): The activity that the callback belongs to.
            run_on (List[Status]): Activity statuses that should trigger the callback.
        """
        Check.not_none(activity, "Activity may not be None in the ActivityBlockCallback")
        # Check.is_instance_of(activity, Activity)
        Check.not_empty_list(
            run_on, "ActivityBlockCallback must have at least one run-on condition."
        )
        self.__activity = activity
        self.__run_on = run_on

    @property
    def run_on(self) -> List[Status]:
        """A list of activity statuses that should trigger the callback"""
        return self.__run_on

    def should_run(self) -> bool:
        return self.__activity.status in self.__run_on

    @abc.abstractmethod
    def run(self):
        """ The logic of the callback. Implemented by the inheriting class.
        This method will be called after all the activities in the activity block have finished \
            running AND the run_on condition provided in the constructor is fulfilled. """

    def __str__(self):
        return f"{self.__class__.__name__}: {str(vars(self))}"
