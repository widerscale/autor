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


class TransitionSummary:
    def __init__(self):
        self._activity_names: List[str] = []
        self._activity_status: List[str] = []
        self._activity_action: List[str] = []
        self._current_block_status: List[str] = []
        self._new_block_status: List[str] = []

    def add(self, activity_name:str, activity_status:str, activity_action:str, current_block_status:str, new_block_status:str):
        self._activity_names.append(activity_name)
        self._activity_status.append(activity_status)
        self._activity_action.append(activity_action)
        self._current_block_status.append(current_block_status)
        self._new_block_status.append(new_block_status)


    def print(self):

        longest_activity_name_length = self.longest_length(self._activity_names)
        longest_activity_status_length = self.longest_length(self._activity_status)
        longest_activity_action_length = self.longest_length(self._activity_action)
        longest_current_block_length = self.longest_length(self._activity_status)
        longest_new_block_length = self.longest_length(self._activity_status)

        name_title = "Activity ID".ljust(longest_activity_name_length)
        status_title = "Status".ljust(longest_activity_status_length)
        action_title = "Action".ljust(longest_activity_action_length)
        activity_block_status_title = "Activity block status"



        longest_activity_name_length = max(longest_activity_name_length, len(name_title))
        longest_activity_status_length = max(longest_activity_status_length, len(status_title))
        longest_activity_action_length = max(longest_activity_action_length, len(action_title))

        line_len:int = longest_activity_name_length + \
                       longest_activity_status_length + \
                       longest_activity_action_length + \
                       longest_current_block_length + \
                       25

        logging.info('-' * line_len)
        logging.info(f'{name_title}   {status_title}   {action_title}   {activity_block_status_title}')
        logging.info('-'*line_len)

        for i in range(len(self._activity_names)):
            name_str = self._activity_names[i].ljust(longest_activity_name_length)
            status_str = self._activity_status[i].ljust(longest_activity_status_length)
            action_str = self._activity_action[i].ljust(longest_activity_action_length)
            curr_str = self._current_block_status[i].ljust(longest_current_block_length)
            new_str = self._new_block_status[i].ljust(longest_new_block_length)
            logging.info(f'{name_str}   {status_str}   {action_str}   {curr_str} -> {new_str}')

        logging.info('-' * line_len)



    def longest_length(self, list:List[str]):
        longest = 0
        for elem in list:
            longest = max(longest, len(elem))
        return longest
