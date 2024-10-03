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
from abc import ABC
from collections import OrderedDict

import yaml
import json

from autor import Activity
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

# This extension is used to assist in Autor framework testing. It allows to provide values that can
# be injected into Activity properties. For example, if a test activity has a property 'outcome' that is
# normally set through the configuration, the input modifier allows to override the value provided by
# the configuration.
class AutorFrameworkActivityInputModifier(StateListener):

    def on_before_activity_run(self, state: State):
        my_data:dict = state.data_dict[sta.CUSTOM_DATA].get("AutorFrameworkActivityInputModifier", {})
        ab_id:str = state.data_dict[sta.ACTIVITY_BLOCK_ID]
        a_id:str = state.data_dict[sta.ACTIVITY_ID]
        activity:Activity = state.data_dict[sta.ACTIVITY_INSTANCE]

        for key,val in my_data.items():
            if key == a_id or f"{ab_id}-{key}" == a_id:
                for prop_name,prop_val in val.items():
                    logging.info(f"Overriding property {prop_name} for activity_id: {a_id}")
                    logging.info(f"Setting property: {prop_name} = {prop_val}")
                    activity.__setattr__(prop_name,prop_val)


