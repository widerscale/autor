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
#    under the License.from autor.framework.activity import Activity
from autor.framework.activity_registry import ActivityRegistry


class ActivityFactory:
    """
    A class for creating activities using the class type as an identifier \
         for the class to be intantiated.
    """

    @staticmethod
    # pylint: disable-next=redefined-builtin
    def create(type: str) -> Activity:
        """Create an activity of a class that is decorated with an activity decorator and has the
        provided 'type'.

        Args:
            type (str): Class type provided in the activity decorator

        Returns:
            Activity: The created activity instance
        """

        return ActivityRegistry.get_class(type)()
