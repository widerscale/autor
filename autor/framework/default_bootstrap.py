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
from autor.framework.file_context import FileContext
from autor.framework.keys import StateKeys as sta
from autor.framework.state import Bootstrap
from autor.framework.state_listener import StateListener

# pylint: disable=no-member, abstract-method


class DefaultBootstrap(StateListener):
    def on_bootstrap(self, state: Bootstrap):  # Override

        logging.debug(f'flow_config_url:     {state.low_config_url}')
        logging.debug(f'custom_data:         {state.custom_data}')
        logging.debug(f'activity_name:       {state.activity_name}')
        logging.debug(f'flow_run_id:         {state.flow_run_id}')
        logging.debug(f'bootstrap_extension: {state.bootstrap_extension}')

        state.print_state()
