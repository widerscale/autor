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


from autor.framework.context import Context, RemoteContext
from autor.framework.debug_config import DebugConfig
from autor.framework.extension_exception import AutorExtensionException
from autor.framework.file_context import FileContext
from autor.framework.keys import StateKeys as ste
from autor.framework.state import State, BeforeActivityRun, FrameworkStart, Bootstrap
from autor.framework.state_listener import StateListener
from autor.framework.util import Util


# pylint: disable=no-member, abstract-method


class GenerateException(StateListener):
    def on_before_activity_run(self, state: BeforeActivityRun):
        logging.debug("Generating exception division with zero...")
        temp = 1.2 / 0.0

class ProvideConfigThroughBootstrapExtension(StateListener):
    def on_bootstrap(self, state: Bootstrap):

        """
        Provide flow-config-url and/or activity-block-id values in case these were not provided as input arguments.
        The values to set should be provided through the custom_data argument to Autor.
        """
        flow_config_url = state.custom_data.get("ProvideConfigThroughBootstrapExtension", {}).get("flowConfigUrl", None)
        activity_block_id = state.custom_data.get("ProvideConfigThroughBootstrapExtension", {}).get("activityBlockId", None)

        if state.flow_config_url is None or state.flow_config_url == "":
            if flow_config_url is None:
                raise AutorExtensionException("Expected ProvideConfigThroughBootstrapExtension.flowConfigUrl in custom_data (command-line argument)")
            else:
                self.log_info(f'flow-config-url: {state.flow_config_url} -> {flow_config_url}')
                state.flow_config_url = flow_config_url


        if state.activity_block_id is None or state.activity_block_id == "":
            if activity_block_id is None:
                raise AutorExtensionException("Expected ProvideConfigThroughBootstrapExtension.activityBlockId in custom_data (command-line argument)")
            else:
                self.log_info(f'activity-block-id: {state.activity_block_id} -> {activity_block_id}')
                state.activity_block_id = activity_block_id


