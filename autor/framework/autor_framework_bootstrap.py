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
from collections import OrderedDict

import yaml
import json

from autor.framework.autor_framework_exception import AutorFrameworkValueException
from autor.framework.check import Check
from autor.framework.constants import Mode
from autor.framework.context import Context, RemoteContext
from autor.framework.debug_config import DebugConfig
from autor.framework.file_context import FileContext
from autor.framework.key_handler import KeyConverter
from autor.framework.keys import StateKeys as sta
from autor.framework.state import Bootstrap, FrameworkStart, BeforeActivityBlock
from autor.framework.state_listener import StateListener
from autor.framework.keys import StateKeys as sta

# pylint: disable=no-member, abstract-method


class AutorFrameworkBootstrap(StateListener):





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

        if state.activity_module is not None:
            logging.info('activity-module is provided -> Preparing to run one activity separately')
            logging.info(f'activity_module: {state.activity_module}')
            logging.info(f'activity_type:   {state.activity_type}')
            logging.info(f'activity_config: {state.activity_config}')
            logging.info(f'activity_input:  {state.activity_input}')
            logging.info(f'flow_run_id:     {state.flow_run_id}')
            state.flow_config_url, state.activity_block_id = self._create_flow_configuration(state.activity_module, state.activity_type, state.activity_config)

        elif state.activity_name is not None:
            logging.info('activity-name is provided -> Preparing to run the specified activity within activity block')

        else:
            logging.info('Preparing to run activity block')




    def _is_camel_case(self, string:str):
        return string.isalnum() and not string.istitle()


    def _create_activity_name(self, activity_block_context:Context) ->str:
        # To allow to build up context in mode ACTIVITY, the activity names
        # need to be different. We use a counter to create for names.
        # In this callback the context has been synced with remote.

        counter_key = f'__{self.__class__.__name__}_activityModeCounter'
        counter:int = activity_block_context.get(counter_key, 0)
        counter = counter + 1
        activity_block_context.set(counter_key, counter)
        return f'activity-{counter}'


    def _add_activity_inputs_to_context(self, activity_input:dict, activity_block_context:Context):
        if activity_input is not None and len(activity_input) > 0:
            logging.debug("Activity inputs found -> adding inputs to context. (Note that keys must be camelCase)")

            for key, value in activity_input.items():
                if self._is_camel_case(key):
                    activity_block_context.set(key, value)
                else:
                    # self.interrupt_on_exception = True
                    raise AutorFrameworkValueException(f"activity_input must be in camelCase. Found: {key}")
        else:
            logging.debug("No activity inputs found -> not adding inputs to context.")


    def on_before_activity_block(self, state: BeforeActivityBlock):

        if state.dict[sta.MODE] == Mode.ACTIVITY:

            # We will be working with Context and it should be the closest
            # layer to the Activity Context. In Autor the closest layer is
            # Activity Block layer.
            activity_block_context: Context = state.dict[sta.ACTIVITY_BLOCK_CONTEXT]


            # --------------- Create activity name --------------------------#
            activity_name = self._create_activity_name(activity_block_context)
            state.dict[sta.ACTIVITY_NAME] = activity_name
            logging.debug(f'Generated activity name: {state.dict[sta.ACTIVITY_NAME]}')


            # -------------- Add activity inputs to context -----------------#
            activity_input:dict = state.dict[sta.ACTIVITY_INPUT]
            self._add_activity_inputs_to_context(activity_input, activity_block_context)





    def _create_flow_configuration(self, activity_module: str, activity_type: str, activity_config: dict):

        Check.is_non_empty_string(activity_type)
        Check.is_non_empty_string(activity_module)


        flow_id = 'autor-flow'
        activity_block_id = 'autor-activity-block'
        flow_config_url = 'autor-config.yml'

        # flow_config:OrderedDict = OrderedDict()
        flow_config: dict = {'flowId': flow_id}
        flow_config['extensions'] = ['getting_started.extensions.context.AddFileContext']

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


        with open(flow_config_url, 'w') as outfile:
            yaml.dump(flow_config, outfile, default_flow_style=False, sort_keys = False)

        # Log the created flow configuration.
        logging.debug('')
        logging.debug('')
        logging.debug(f'Generated flow configuration:')
        logging.debug('')

        yaml_flow_config = yaml.dump(flow_config, sort_keys=False)
        lines = yaml_flow_config.split('\n')
        for line in lines:
            logging.debug(line)

        return flow_config_url, activity_block_id
