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
from typing import Dict

from autor.framework.activity_block_information import ActivityBlockInformation
from autor.framework.activity_information import ActivityInformation
from autor.framework.flow_information import FlowInformation
from autor.framework.util import Util
from autor.framework.keys import StateKeys as sta



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
    CONTEXT_SYNCHRONIZED = "CONTEXT_SYNCHRONIZED"
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
    def __init__(self, name: str, data_dict: dict):
        self._data_dict = data_dict  # Dictionary containing the raw state.
        self._name = name  # The state name

    def print_state(self, message=None):
        logging.info("STATE: " + self.name)
        Util.print_dict(self._data_dict, message, level='info')


    # region property: name:str
    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value
    # endregion

    # region property: data_dict:Dict
    @property
    def data_dict(self) -> Dict:
        return self._data_dict
    # endregion

    # region property: flow_information:FlowInformation
    @property
    def flow_information(self) -> FlowInformation:
        return self._data_dict["FLOW_INFORMATION"]

    @flow_information.setter
    def flow_information(self, value: FlowInformation) -> None:
        self._data_dict["FLOW_INFORMATION"] = value
    # endregion

    # region property: activity_block_information:ActivityBlockInformation
    @property
    def activity_block_information(self) -> ActivityBlockInformation:
        return self._data_dict["ACTIVITY_BLOCK_INFORMATION"]

    @activity_block_information.setter
    def activity_block_information(self, value: ActivityBlockInformation) -> None:
        self._data_dict["ACTIVITY_BLOCK_INFORMATION"] = value
    # endregion

    # region property: activity_information:ActivityInformation
    @property
    def activity_information(self) -> ActivityInformation:
        return self._data_dict["ACTIVITY_INFORMATION"]

    @activity_information.setter
    def activity_information(self, value: ActivityInformation) -> None:
        self._data_dict["ACTIVITY_INFORMATION"] = value
    # endregion


# ______________________  S T A T E   C L A S S E S  ___________________________#


class Bootstrap(State):
    """
    Bootstrap state has very limited access to data. It only contains parameters that can
    be provided when Autor is first called.
    """
    def __init__(self, data_dict: dict):
        super().__init__(name=State.BOOTSTRAP, data_dict=data_dict)


    # region property: activity_information:ActivityInformation
    @property
    def activity_information(self) -> ActivityInformation:
        return self._activity_information

    @activity_information.setter
    def activity_information(self, value: ActivityInformation) -> None:
        self._activity_information = value
    # endregion




    # -------------------- mode -------------------------#
    @property
    def mode(self) -> str:  # getter
        return self._data_dict[sta.MODE]

    @mode.setter
    def mode(self, n:str) -> None:  # setter
        self._data_dict[sta.MODE] = n


    #---------------- flow_config_path --------------------#
    @property
    def flow_config_path(self) -> str: # getter
        return self._data_dict[sta.FLOW_CONFIG_PATH]

    @flow_config_path.setter
    def flow_config_path(self, n:str) -> None:  # setter
        self._data_dict[sta.FLOW_CONFIG_PATH] = n


    # --------------- activity_block_id --------------------#
    @property
    def activity_block_id(self) -> str:  # getter
        return self._data_dict[sta.ACTIVITY_BLOCK_ID]

    @activity_block_id.setter
    def activity_block_id(self, n:str) -> None:  # setter
        self._data_dict[sta.ACTIVITY_BLOCK_ID] = n

    # --------------- activity_block_run_id --------------------#
    @property
    def activity_block_run_ids(self) -> str:  # getter
        return self._data_dict[sta.ACTIVITY_BLOCK_RUN_ID]

    @activity_block_run_ids.setter
    def activity_block_run_ids(self, n: str) -> None:  # setter
        self._data_dict[sta.ACTIVITY_BLOCK_RUN_ID] = n


    # ------------------ flow_run_id ----------------------#
    @property
    def flow_run_id(self) -> str:  # getter
        return self._data_dict[sta.FLOW_RUN_ID]

    @flow_run_id.setter
    def flow_run_id(self, n:str) -> None:  # setter
        self._data_dict[sta.FLOW_RUN_ID] = n


    # ---------------- activity_name ---------------------#
    @property
    def activity_name_special(self) -> str:  # getter
        return self._data_dict[sta.ACTIVITY_NAME_SPECIAL]

    @activity_name_special.setter
    def activity_name_special(self, n:str) -> None:  # setter
        self._data_dict[sta.ACTIVITY_NAME_SPECIAL] = n


    # ---------------- activity_id ---------------------#
    @property
    def activity_id_special(self) -> str:  # getter
        return self._data_dict[sta.ACTIVITY_ID_SPECIAL]

    @activity_id_special.setter
    def activity_id_special(self, n: str) -> None:  # setter
        self._data_dict[sta.ACTIVITY_ID_SPECIAL] = n


    # ---------------- custom_data ---------------------#
    @property
    def custom_data(self) -> dict:  # getter
        return self._data_dict[sta.CUSTOM_DATA]

    @custom_data.setter
    def custom_data(self, n:dict) -> None:  # setter
        self._data_dict[sta.CUSTOM_DATA] = n


    # ------------------- flags -------------------------#
    @property
    def flags(self) -> dict:  # getter
        return self._data_dict[sta.flags]

    @flags.setter
    def flags(self, n:dict) -> None:  # setter
        self._data_dict[sta.FLAGS] = n



    # ------------- bootstrap_extension ------------------#
    @property
    def additional_extensions(self) -> list:  # getter
        return self._data_dict[sta.ADDITIONAL_EXTENSIONS]

    @additional_extensions.setter
    def additional_extensions(self, n:list) -> None:  # setter
        self._data_dict[sta.ADDITIONAL_EXTENSIONS] = n




    #------------------------------------------------------------#
    #-------------------- mode: ACTIVITY ------------------------#
    # -----------------------------------------------------------#

    # ---------------- activity_name ---------------------#
    @property
    def activity_module(self) -> str:  # getter
        return self._data_dict[sta.ACTIVITY_MODULE]

    @property
    def activity_type(self) -> str:  # getter
        return self._data_dict[sta.ACTIVITY_TYPE]

    @property
    def activity_config(self) -> dict:  # getter
        return self._data_dict[sta.ACTIVITY_CONFIG]

    @property
    def input(self) -> dict:  # getter
        return self._data_dict[sta.INPUT]


class ContextSynchronized(State):
    def __init__(self, data_dict: dict):
        super().__init__(name=State.CONTEXT_SYNCHRONIZED, data_dict=data_dict)


class FrameworkStart(State):
    def __init__(self, data_dict: dict):
        super().__init__(name=State.FRAMEWORK_START, data_dict=data_dict)


class BeforeActivityBlock(State):
    def __init__(self, data_dict: dict):
        super().__init__(name=State.BEFORE_ACTIVITY_BLOCK, data_dict=data_dict)


class SelectActivity(State):
    def __init__(self, data_dict: dict):
        super().__init__(name=State.SELECT_ACTIVITY, data_dict=data_dict)


class BeforeActivityPreprocess(State):
    def __init__(self, data_dict: dict):
        super().__init__(name=State.BEFORE_ACTIVITY_PREPROCESS, data_dict=data_dict)


class BeforeActivityRun(State):
    def __init__(self, data_dict: dict):
        super().__init__(name=State.BEFORE_ACTIVITY_RUN, data_dict=data_dict)


class AfterActivityRun(State):
    def __init__(self, data_dict: dict):
        super().__init__(name=State.AFTER_ACTIVITY_RUN, data_dict=data_dict)


class AfterActivityPostprocess(State):
    def __init__(self, data_dict: dict):
        super().__init__(name=State.AFTER_ACTIVITY_POSTPROCESS, data_dict=data_dict)


class BeforeActivityBlockCallbacks(State):
    def __init__(self, data_dict: dict):
        super().__init__(name=State.BEFORE_ACTIVITY_BLOCK_CALLBACKS, data_dict=data_dict)


class AfterActivityBlock(State):
    def __init__(self, data_dict: dict):
        super().__init__(name=State.AFTER_ACTIVITY_BLOCK, data_dict=data_dict)


class FrameworkEnd(State):
    def __init__(self, data_dict: dict):
        super().__init__(name=State.FRAMEWORK_END, data_dict=data_dict)


class Error(State):
    def __init__(self, data_dict: dict):
        super().__init__(name=State.ERROR, data_dict=data_dict)
