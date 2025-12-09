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
from typing import List

#from autor import Activity
from autor.flow_configuration.activity_configuration import ActivityConfiguration
from autor.framework.check import Check
from autor.framework.constants import ActivityGroupType, NodeStatus


class Node:
    def __init__(self, activity_id:str, activity_group_type:ActivityGroupType, activity_config:ActivityConfiguration, rerun:bool):
        self._activity_id = activity_id
        Check.is_true(isinstance(activity_config, ActivityConfiguration),f"Expected activity_config to be of type ActivityConfig. Was: {type(activity_config)}")
        self._activity_config = activity_config
        self._activity_group_type = activity_group_type
        self._rerun:bool = rerun # Indicates if the node should be re-run
        self._rerun_initiated_by:str = None # Activity id of the node that has initiated the re-run of this node.
        self._children:List[Node] = []
        self._parents:List[Node] = []
        self._ancestors_by_activity_id:dict = {}
        self._status:NodeStatus = NodeStatus.BLOCKED
        self._main_activity_node = None # Used for before-activities. Needed for rules.
        self._before_activity_nodes:List = [] # Used for main and after-activities. Needed for rules.
        self._activity = None # Added when the activity is created #type:Activity
        self._activity_data = None # Added when the activity data is created. # type:ActivityData
        self._activity_runner = None # Added when the activity is being run. # type:ActivityRunner
        self._previous_activity_in_running_order_during_last_run = None # Activity ID
        self._interrupted:bool = False # True if this node should not run


    def print(self):
        logging.info(f"_activity_id:         {self._activity_id}")
       # logging.info(f"_activity_group_type: {self._activity_group_type}")
        logging.info(f"_parents:")
        for parent in self._parents:
            logging.info(f"                      {parent._activity_id}")
        logging.info(f"_children:")
        for child in self._children:
            logging.info(f"                      {child._activity_id}")
        logging.info("----------------------------------------------------------------")

    @property
    def previous_activity_in_running_order_during_last_run(self) -> str:
        return self._previous_activity_in_running_order_during_last_run

    @previous_activity_in_running_order_during_last_run.setter
    def previous_activity_in_running_order_during_last_run(self, value:str):
        self._previous_activity_in_running_order_during_last_run = value

    @property
    def interrupted(self) -> bool:
        return self._interrupted

    @interrupted.setter
    def interrupted(self, value:bool):
        self._interrupted = value

    @property
    def status(self) -> NodeStatus:
        return self._status
    @status.setter
    def status(self, value:NodeStatus):
        self._status = value

    @property
    def ancestors(self) -> dict:
        return self._ancestors_by_activity_id

    @property
    def main_activity_node(self):
        return self._main_activity_node
    @main_activity_node.setter
    def main_activity_node(self, value):
        self._main_activity_node = value

    @property
    def before_activity_nodes(self)->List:
        return self._before_activity_nodes

    @before_activity_nodes.setter
    def before_activity_nodes(self, value:list):
        self._before_activity_nodes = value

    @property
    def activity(self):
        return self._activity

    @activity.setter
    def activity(self, value):
        self._activity = value

    @property
    def rerun(self)->bool:
        return self._rerun

    @rerun.setter
    def rerun(self, value:bool):
        self._rerun = value

    @property
    def rerun_initiated_by(self)->str:
        return self._rerun_initiated_by

    @rerun_initiated_by.setter
    def rerun_initiated_by(self, value:str):
        self._rerun_initiated_by = value


    @property
    def activity_data(self):
        return self._activity_data

    @activity_data.setter
    def activity_data(self, value):
        self._activity_data = value


    @property
    def activity_runner(self):
        return self._activity_runner

    @activity_runner.setter
    def activity_runner(self, value):
        self._activity_runner = value

    @property
    def children(self) -> List:
        return self._children

    @property
    def parents(self) -> List:
        return self._parents

    @property
    def activity_id(self) -> str:
        return self._activity_id

    @property
    def activity_config(self) -> ActivityConfiguration:
        return self._activity_config

    @property
    def activity_group_type(self) -> ActivityGroupType:
        return self._activity_group_type

    def add_child(self, node):
        self._children.append(node)

    def add_parent(self, node):
        self._ancestors_by_activity_id[node.activity_id] = node
        self._parents.append(node)



