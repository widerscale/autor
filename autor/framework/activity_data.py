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

from autor.flow_configuration.activity_configuration import ActivityConfiguration
from autor.framework.activity_context import ActivityContext
from autor.framework.autor_framework_exception import AutorFrameworkException
from autor.framework.constants import ActivityGroupType
from autor.framework.context import Context
from autor.framework.context_properties_handler import ContextPropertiesHandler
from autor.framework.debug_config import DebugConfig


class ActivityData:
    # A data container for activity-related data.
    # This container class should not be exposed outside the framework.
    def __init__(self):
        # fmt: off
        self.flow_id:str = None
        self.flow_run_id:str = None

        self.activity_block_id:str = None
        self.activity_block_run_id:str = None
        self.activity_block_status = None
        self.interrupted = None

        self.action = None # See Constants.Action
        self.activity = None
        self.activity_id:str = None
        self.activity_run_id = None
        self.activity_name:str = None
        self.activity_group_type = None
        self.activity_config:ActivityConfiguration = None
        self.activity_type:str = None

        self.activity_context:ActivityContext = None
        self.input_context:Context = None # To read input props from (Activity Block level)
        self.output_context:Context = None # To write output props to (Activity level)
        #self.output_context_properties_handler:ContextPropertiesHandler = None


        self.inputs: dict = None # Set when activity is created
        self.configs: dict = None # Set when activity is created
        self.outputs: dict = None # Set AFTER activity has run, skipped etc.

        self.activities = []
        self.activities_by_name = {}

        self.before_block_activities = []
        self.before_activities = []
        self.main_activities = []
        self.after_activities = []
        self.after_block_activities = []


        self.before_block_activities_configurations = []
        self.before_activities_configurations       = []
        self.main_activities_configurations         = []
        self.after_activities_configurations        = []
        self.after_block_activities_configurations  = []

        self.next_main_activity_data = None
        # fmt: on

    def _print(self, msg:str):
        logging.info(f"{DebugConfig.selected_activity_prefix}: {msg}")
        
    def print(self):
        self._print(f"flow_id: {self.flow_id}")
        self._print(f"flow_run_id: {self.flow_run_id}")
        self._print(f"activity_block_id: {self.activity_block_id}")
        self._print(f"activity_block_run_id: {self.activity_block_run_id}")
        self._print(f"activity_block_status: {self.activity_block_status}")
        self._print(f"interrupted: {self.interrupted}")
        self._print(f"action: {self.action}")
        self._print(f"activity: {self.activity}")
        self._print(f"activity_id: {self.activity_id}")
        self._print(f"activity_run_id: {self.activity_run_id}")
        self._print(f"activity_name: {self.activity_name}")
        self._print(f"activity_group_type: {self.activity_group_type}")
        self._print(f"activity_config: {self.activity_config}")
        self._print(f"activity_type: {self.activity_type}")
        self._print(f"activity_context: {self.activity_context}")
        self._print(f"input_context: {self.input_context}")
        self._print(f"output_context: {self.output_context}")
        #self._print(f"output_context_properties_handler: {self.output_context_properties_handler}")
        self._print(f"activities: {self.activities}")
        self._print(f"activities_by_name: {self.activities_by_name}")
        self._print(f"before_block_activities: {self.before_block_activities}")
        self._print(f"before_activities: {self.before_activities}")
        self._print(f"main_activities: {self.main_activities}")
        self._print(f"after_activities: {self.after_activities}")
        self._print(f"after_block_activities: {self.after_block_activities}")
        self._print(f"before_block_activities_configurations: {self.before_block_activities_configurations}")
        self._print(f"before_activities_configurations: {self.before_activities_configurations}")
        self._print(f"main_activities_configurations: {self.main_activities_configurations}")
        self._print(f"after_activities_configurations: {self.after_activities_configurations}")
        self._print(f"after_block_activities_configurations: {self.after_block_activities_configurations}")
        self._print(f"next_main_activity_data: {self.next_main_activity_data}")



    def get_activities(self, activity_group_type):
        # pylint: disable-next=no-else-return
        if activity_group_type == ActivityGroupType.BEFORE_BLOCK:
            return self.before_block_activities
        elif activity_group_type == ActivityGroupType.BEFORE_ACTIVITY:
            return self.before_activities
        elif activity_group_type == ActivityGroupType.MAIN_ACTIVITY:
            return self.main_activities
        elif activity_group_type == ActivityGroupType.AFTER_ACTIVITY:
            return self.after_activities
        elif activity_group_type == ActivityGroupType.AFTER_BLOCK:
            return self.after_block_activities

        raise AutorFrameworkException(
            f"Unexpected activity_group_type: {str(activity_group_type)!r}"
        )
