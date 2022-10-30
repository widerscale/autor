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
import logging

from autor.framework.util import Util


# ------------------------------------------------------------------------------#
#                              State classes                                   #
# ------------------------------------------------------------------------------#
# redefined-builtin: dict
# pylint: disable=redefined-builtin
class State:
    __metaclass__ = abc.ABCMeta

    # ----------------------   S T A T I C  S T A R T  -------------------------#
    # State names
    UNKNOWN = "UNKNOWN"
    FRAMEWORK_START = "FRAMEWORK_START"
    BEFORE_ACTIVITY_BLOCK = "BEFORE_ACTIVITY_BLOCK"
    SELECT_ACTIVITY = "SELECT_ACTIVITY"
    BEFORE_ACTIVITY_PREPROCESS = "BEFORE_ACTIVITY_PREPROCESS"
    BEFORE_ACTIVITY_RUN = "BEFORE_ACTIVITY_RUN"
    AFTER_ACTIVITY_RUN = "AFTER_ACTIVITY_RUN"
    AFTER_ACTIVITY_POSTPROCESS = "AFTER_ACTIVITY_POSTPROCESS"
    BEFORE_ACTIVITY_BLOCK_CALLBACKS = "BEFORE_ACTIVITY_BLOCK_CALLBACKS"
    AFTER_ACTIVITY_BLOCK = "AFTER_ACTIVITY_BLOCK"
    FRAMEWORK_END = "FRAMEWORK_END"
    ERROR = "ERROR"

    # ----------------------   S T A T I C  E N D   --------------------------#
    # State consturctor. All states have a name.
    def __init__(self, name: str, dict: dict):
        self._dict = dict  # Dictionary containing the raw state.
        self._name = name  # The state name

    def print_state(self, message=None):
        logging.debug("STATE: " + self.name)
        Util.print_dict(self._dict, message)

    @property
    def name(self) -> str:
        return self._name

    @property
    def dict(self) -> dict:
        return self._dict


# ______________________  S T A T E   C L A S S E S  ___________________________#


class FrameworkStart(State):
    def __init__(self, dict: dict):
        super().__init__(name=State.FRAMEWORK_START, dict=dict)


class BeforeActivityBlock(State):
    def __init__(self, dict: dict):
        super().__init__(name=State.BEFORE_ACTIVITY_BLOCK, dict=dict)


class SelectActivity(State):
    def __init__(self, dict: dict):
        super().__init__(name=State.SELECT_ACTIVITY, dict=dict)


class BeforeActivityPreprocess(State):
    def __init__(self, dict: dict):
        super().__init__(name=State.BEFORE_ACTIVITY_PREPROCESS, dict=dict)


class BeforeActivityRun(State):
    def __init__(self, dict: dict):
        super().__init__(name=State.BEFORE_ACTIVITY_RUN, dict=dict)


class AfterActivityRun(State):
    def __init__(self, dict: dict):
        super().__init__(name=State.AFTER_ACTIVITY_RUN, dict=dict)


class AfterActivityPostprocess(State):
    def __init__(self, dict: dict):
        super().__init__(name=State.AFTER_ACTIVITY_POSTPROCESS, dict=dict)


class BeforeActivityBlockCallbacks(State):
    def __init__(self, dict: dict):
        super().__init__(name=State.BEFORE_ACTIVITY_BLOCK_CALLBACKS, dict=dict)


class AfterActivityBlock(State):
    def __init__(self, dict: dict):
        super().__init__(name=State.AFTER_ACTIVITY_BLOCK, dict=dict)


class FrameworkEnd(State):
    def __init__(self, dict: dict):
        super().__init__(name=State.FRAMEWORK_END, dict=dict)


class Error(State):
    def __init__(self, dict: dict):
        super().__init__(name=State.ERROR, dict=dict)
