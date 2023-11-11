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
from autor.framework.activity_context import ActivityContext
from autor.framework.autor_framework_exception import AutorFrameworkException
from autor.framework.constants import ActivityGroupType
from autor.framework.context import Context
from autor.framework.context_properties_handler import ContextPropertiesHandler


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
        self.activity_config:str = None
        self.activity_type:str = None

        self.activity_context:ActivityContext = None
        self.input_context:Context = None # To read input props from (Activity Block level)
        self.output_context:Context = None # To write output props to (Activity level)
        self.output_context_properties_handler:ContextPropertiesHandler = None

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
