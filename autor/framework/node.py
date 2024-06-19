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

from autor import Activity
from autor.flow_configuration.activity_configuration import ActivityConfiguration
from autor.framework.constants import ActivityGroupType, NodeStatus


class Node:
    def __init__(self, activity_id:str, activity_group_type:ActivityGroupType, activity_config:ActivityConfiguration):
        self._activity_id = activity_id
        self._activity_config = activity_config
        self._activity_group_type = activity_group_type
        self._children:List[Node] = []
        self._parents:List[Node] = []
        self._status:NodeStatus = NodeStatus.BLOCKED
        self._main_activity_node = None # Used for before-activities. Needed for rules.
        self._before_activity_nodes:List = [] # Used for main and after-activities. Needed for rules.
        self._activity:Activity = None # Added when the activity is created

    def print(self):
        logging.info(f"_activity_id:         {self._activity_id}")
        logging.info(f"_activity_group_type: {self._activity_group_type}")
        logging.info(f"_children:            {self._children}")
        logging.info(f"_parents:             {self._parents}")
        logging.info(f"_activity_group_type: {self._activity_group_type}")
        logging.info("----------------------------------------------------------------")

    @property
    def status(self) -> NodeStatus:
        return self._status
    @status.setter
    def status(self, value:NodeStatus):
        self._status = value

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
    def activity(self) -> Activity:
        return self._activity

    @activity.setter
    def activity(self, value:Activity):
        self._activity = value

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
        self._parents.append(node)



