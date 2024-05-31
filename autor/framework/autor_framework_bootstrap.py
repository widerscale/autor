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
import uuid
from collections import OrderedDict

import yaml
import json

from autor.framework.autor_framework_exception import AutorFrameworkValueException
from autor.framework.check import Check
from autor.framework.constants import Mode, Constants
from autor.framework.context import Context, RemoteContext
from autor.framework.debug_config import DebugConfig
from autor.framework.file_context import FileContext
from autor.framework.key_handler import KeyConverter
from autor.framework.keys import StateKeys as sta
from autor.framework.state import Bootstrap, FrameworkStart, BeforeActivityBlock, AfterActivityBlock, State
from autor.framework.state_listener import StateListener
from autor.framework.keys import StateKeys as sta
from autor.framework.util import Util


# pylint: disable=no-member, abstract-method


class AutorFrameworkBootstrap(StateListener):

    def __init__(self):
        self._fc_helper:FlowConfigurationHelper = FlowConfigurationHelper()



    def on_bootstrap(self, state: Bootstrap):  # Override

        # Mode: ACTIVITY
        #
        # The presence of either activity_module or activity_type
        # indicates that Autor should create a flow configuration
        # for that activity and run it.
        #
        # The context should also be managed, so that when autor
        # will be called with the same flow_run_id, the context
        # should be intact and a new run should create a new
        # activity context (even if we run the exact same activity).
        # Saving a counter in the context will help to create
        # unique activity context keys for each run.
        #
        # Mandatory arguments:.
        # --------------------
        # activity-module
        # activity-type
        #
        # Optional arguments:
        # -------------------
        # flow-run-id
        # activity-input
        # activity-config

        if state.mode == Mode.ACTIVITY:
            Check.is_non_empty_string(state.activity_module, "activity_mode is mandatory in mode ACTIVITY")
            Check.is_non_empty_string(state.activity_type, "activity_type is mandatory in mode ACTIVITY")

            if state.activity_block_id is not None:
                activity_block_id = state.activity_block_id  # Used for deterministic testing
            else:
                activity_block_id = str(uuid.uuid4())        # Normal case

            self._fc_helper.create_flow_configuration(activity_block_id=activity_block_id, activity_module=state.activity_module, activity_type=state.activity_type, activity_config=state.activity_config)
            state.flow_config_path = self._fc_helper.flow_configuration_url
            state.activity_block_id = activity_block_id


    def _is_camel_case(self, string:str):
        return string.isalnum() and not string.istitle()



    def _add_inputs_to_context(self, input:dict, activity_block_context:Context):
        if input is not None and len(input) > 0:
            logging.debug("Activity inputs found -> adding inputs to context. (Note that keys must be camelCase)")

            for key, value in input.items():
                activity_block_context.set(key, value)
        else:
            logging.debug("No activity inputs found -> not adding inputs to context.")



    def on_before_activity_block(self, state: BeforeActivityBlock):

        if state.dict[sta.MODE] == Mode.ACTIVITY:
            activity_block_context: Context = state.dict[sta.ACTIVITY_BLOCK_CONTEXT]

            # --------------- Create activity name --------------------------#
            #activity_name = self._create_activity_name(activity_block_context)
            state.dict[sta.ACTIVITY_NAME_SPECIAL] = 'activity1'
            logging.debug(f'Generated activity name: activity1')


class FlowConfigurationHelper:

    def __init__(self):
        self._flow_configuration:dict = None
        self._activity_block_id:str = Constants.GENERATED_ACTIVITY_BLOCK_ID
        self._flow_configuration_url:str = 'autor-config.yml'
        self._flow_id:str = 'autor-flow'


    @property
    def flow_configuration(self) -> dict:
        return self._flow_configuration

    @property
    def activity_block_id(self) -> str:
        return self._activity_block_id

    @property
    def flow_configuration_url(self) -> str:
        return self._flow_configuration_url




    def create_flow_configuration(self, activity_block_id: str, activity_module: str, activity_type: str, activity_config: dict)->None:

        Check.is_non_empty_string(activity_type)
        Check.is_non_empty_string(activity_module)



        # flow_config:OrderedDict = OrderedDict()
        flow_config: dict = {'flowId': self._flow_id}
        #flow_config['extensions'] = ['examples.extensions.context.AddFileContext']

        activity_modules: list = [activity_module]
        flow_config['activityModules'] = activity_modules

        activity_blocks: dict = {}
        flow_config['activityBlocks'] = activity_blocks

        activity_block: dict = {}
        activity_blocks[activity_block_id] = activity_block

        activities: list = []
        activity_block['activities'] = activities

        activity: dict = {}
        activities.append(activity)
        activity['type'] = activity_type

        if activity_config is not None:
            activity['configuration'] = activity_config

        self._flow_configuration = flow_config
        self._print_to_file()




    def _print_to_file(self):
        with open(self.flow_configuration_url, 'w') as outfile:
            yaml.dump(self.flow_configuration, outfile, default_flow_style=False, sort_keys = False)

        # Log the created flow configuration.
        logging.debug('')
        logging.debug('')
        logging.debug(f'Generated flow configuration:')
        logging.debug('')

        yaml_flow_config = yaml.dump(self.flow_configuration, sort_keys=False)
        lines = yaml_flow_config.split('\n')
        for line in lines:
            logging.debug(line)


