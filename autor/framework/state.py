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
from autor.framework.keys import StateKeys as sta

from copy import deepcopy


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
    BOOTSTRAP = "BOOTSTRAP"
    CONTEXT = "CONTEXT"
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
    # State constructor. All states have a name.
    def __init__(self, name: str, dict: dict):
        self._dict = dict  # Dictionary containing the raw state.
        self._name = name  # The state name

    def print_state(self, message=None):
        logging.info("STATE: " + self.name)
        Util.print_dict(self._dict, message, level='info')

    @property
    def name(self) -> str:
        return self._name

    @property
    def dict(self) -> dict:
        return self._dict


# ______________________  S T A T E   C L A S S E S  ___________________________#


class Bootstrap(State):
    """
    Bootstrap state has very limited access to data. It only contains parameters that can
    be provided when Autor is first called.
    """
    def __init__(self, dict: dict):
        super().__init__(name=State.BOOTSTRAP, dict=dict)

    #---------------- flow_config_url --------------------#
    @property
    def flow_config_url(self) -> str: # getter
        return self._dict[sta.FLOW_CONFIG_URL]

    @flow_config_url.setter
    def flow_config_url(self, n:str) -> None:  # setter
        self._dict[sta.FLOW_CONFIG_URL] = n


    # --------------- activity_block_id --------------------#
    @property
    def activity_block_id(self) -> str:  # getter
        return self._dict[sta.ACTIVITY_BLOCK_ID]

    @activity_block_id.setter
    def activity_block_id(self, n:str) -> None:  # setter
        self._dict[sta.ACTIVITY_BLOCK_ID] = n

    # --------------- activity_block_run_id --------------------#
    @property
    def activity_block_fun_ids(self) -> str:  # getter
        return self._dict[sta.ACTIVITY_BLOCK_RUN_ID]

    @activity_block_id.setter
    def activity_block_run_ids(self, n: str) -> None:  # setter
        self._dict[sta.ACTIVITY_BLOCK_RUN_ID] = n


    # ------------------ flow_run_id ----------------------#
    @property
    def flow_run_id(self) -> str:  # getter
        return self._dict[sta.FLOW_RUN_ID]

    @flow_run_id.setter
    def flow_run_id(self, n:str) -> None:  # setter
        self._dict[sta.FLOW_RUN_ID] = n


    # ---------------- activity_name ---------------------#
    @property
    def activity_name_special(self) -> str:  # getter
        return self._dict[sta.ACTIVITY_NAME_SPECIAL]

    @activity_name_special.setter
    def activity_name_special(self, n:str) -> None:  # setter
        self._dict[sta.ACTIVITY_NAME_SPECIAL] = n


    # ---------------- activity_id ---------------------#
    @property
    def activity_id_special(self) -> str:  # getter
        return self._dict[sta.ACTIVITY_ID_SPECIAL]

    @activity_id_special.setter
    def activity_id_special(self, n: str) -> None:  # setter
        self._dict[sta.ACTIVITY_ID_SPECIAL] = n


    # ---------------- custom_data ---------------------#
    @property
    def custom_data(self) -> dict:  # getter
        return deepcopy(self._dict[sta.CUSTOM_DATA])

    @custom_data.setter
    def custom_data(self, n:dict) -> None:  # setter
        self._dict[sta.CUSTOM_DATA] = n


    # ---------------- bootstrap_extension ---------------------#
    @property
    def additional_extensions(self) -> list:  # getter
        return deepcopy(self._dict[sta.ADDITIONAL_EXTENSIONS])




    #------------------------------------------------------------#
    #-------------------- mode: ACTIVITY ------------------------#
    # -----------------------------------------------------------#

    # ---------------- activity_name ---------------------#
    @property
    def activity_module(self) -> str:  # getter
        return self._dict[sta.ACTIVITY_MODULE]

    @property
    def activity_type(self) -> str:  # getter
        return self._dict[sta.ACTIVITY_TYPE]

    @property
    def activity_config(self) -> dict:  # getter
        return deepcopy(self._dict[sta.ACTIVITY_CONFIG])

    @property
    def activity_input(self) -> dict:  # getter
        return deepcopy(self._dict[sta.ACTIVITY_INPUT])


class Context(State):
    def __init__(self, dict: dict):
        super().__init__(name=State.CONTEXT, dict=dict)


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
