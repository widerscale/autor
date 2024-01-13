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
import inspect
import logging

from autor.framework.autor_framework_exception import (
    AutorFrameworkValueException,
)
from autor.framework.check import Check
from autor.framework.debug_config import DebugConfig
from autor.framework.util import Util


class ActivityRegistry:
    """
        A class that enables annotating classes as activities by using and @activity decorator \
            and finding these classes on run time.

        This class offers two main functionalities:
        - A class decorator (@activity(type)) for annotating classes that should be considered as \
            activities and providing a 'type'.
        - A registry for activity classes that can be retrieved by their 'type'.


        By decorating a class the class will be automatically registered in ActivityRegistry \
            when the class file is imported.


    --------------------------------
    Example:

    The decorated class:

        from autor.framework.activity_registry import ActivityRegistry


        @ActivityRegistry.activity(type="ENVIRONMENT_TESTER")
        class EnvironmentReliabilityTester(Activity):

        def run(self):
            ....


    Example usage of ActivityRegistry:

        activity = ActivityRegistry.get_class(type)()
        activity.run()
    -----------------------------------------------------

    """

    activities = {}

    @staticmethod
    # pylint: disable-next=redefined-builtin
    def activity(type:str="activity-type-not-set-in-the-activity"):

        """
        A class decorator for registering a class as an activity of a certain type.
        Arguments:
            type {str} -- The activity type name.
        Returns:
            function -- The function that registers the activity in the registry.
        """

        def act(cls):
            # pylint: disable=no-else-raise
            #path:str =
            #Check.true(type is not None, ValueError, f"Missing mandatory 'type' in decorator: @ActivityRegistry.activity decorator in class: {cls.__name__}.")
            #Check.true(Util.is_lower_case_dashed(type), ValueError, f"@ActivityRegistry.activity decorator expects 'type' to have format: 'lower-case-separated-with-dash'. Actual format: {type}. \nclass: {cls.__name__}\nfile: {inspect.getfile(cls)}")

            ok_to_register = True

            if type == "activity-type-not-set-in-the-activity":
                logging.warning(f"{DebugConfig.autor_info_prefix}Missing mandatory 'type' in decorator: @ActivityRegistry.activity decorator.")
                logging.warning(f"{DebugConfig.autor_info_prefix}This activity will not be made available for execution:")
                logging.warning(f"{DebugConfig.autor_info_prefix}  class: {cls.__name__}")
                logging.warning(f"{DebugConfig.autor_info_prefix}  file:  {inspect.getfile(cls)}")
                logging.warning(f"{DebugConfig.autor_info_prefix}")
                ok_to_register = False

            if type is None:
                logging.warning(f"{DebugConfig.autor_info_prefix}Value error: None. @ActivityRegistry.activity decorator may not have a type value 'None'.")
                logging.warning(f"{DebugConfig.autor_info_prefix}This activity will not be made available for execution:")
                logging.warning(f"{DebugConfig.autor_info_prefix}  class: {cls.__name__}")
                logging.warning(f"{DebugConfig.autor_info_prefix}  file:  {inspect.getfile(cls)}")
                logging.warning(f"{DebugConfig.autor_info_prefix}")
                ok_to_register = False

            elif not Util.is_lower_case_dashed(type):
                logging.warning(f"{DebugConfig.autor_info_prefix}@ActivityRegistry.activity decorator expects 'type' to have format: 'lower-case-separated-with-dash'. Actual format: {type}.")
                logging.warning(f"{DebugConfig.autor_info_prefix}  class: {cls.__name__}")
                logging.warning(f"{DebugConfig.autor_info_prefix}  file:  {inspect.getfile(cls)}")
                logging.warning(f"{DebugConfig.autor_info_prefix}")

            elif type in ActivityRegistry.activities.keys():
                existing_activity = ActivityRegistry.activities[type]
                logging.warning(f"{DebugConfig.autor_info_prefix}An attempt to register an activity with type '{type}' while the type is already used by another activity.")
                logging.warning(f"{DebugConfig.autor_info_prefix}")
                logging.warning(f"{DebugConfig.autor_info_prefix}Activity that is trying to register:")
                logging.warning(f"{DebugConfig.autor_info_prefix}  class: {cls.__name__}")
                logging.warning(f"{DebugConfig.autor_info_prefix}  file:  {inspect.getfile(cls)}")
                logging.warning(f"{DebugConfig.autor_info_prefix}")
                logging.warning(f"{DebugConfig.autor_info_prefix}Already registered activity with type '{type}':")
                logging.warning(f"{DebugConfig.autor_info_prefix}  class: {existing_activity.__name__}")
                logging.warning(f"{DebugConfig.autor_info_prefix}  file:  {inspect.getfile(existing_activity)}")
                logging.warning(f"{DebugConfig.autor_info_prefix}")
                logging.warning(f"{DebugConfig.autor_info_prefix}Select another type name for one of the activities.")
                logging.warning(f"{DebugConfig.autor_info_prefix}")
                ok_to_register = False

            if ok_to_register:
                ActivityRegistry.activities[type] = cls

            return cls
        return act

    @staticmethod
    # pylint: disable-next=redefined-builtin
    def get_class(type: str):  # -> class
        """
        Get the class of the activity that is registered with the 'type' \
            using the activity decorator.
        Arguments:
            type {str} -- The activity type.
        Return:
            class -- The registered activity class.
        Raises:
            AutorFrameworkValueException if activity with 'type' not registered.
        """

        if type not in ActivityRegistry.activities:
            raise AutorFrameworkValueException(
                (
                    f"No activity with the type: '{str(type)}' registered. \n"
                    f"          - Check the spelling of the 'type' int the activity decorator. \n"
                    f"          - Make sure the activity module has been added to the Flow Configuration (if it is used) or provided as a parameter to Autor."
                )
            )

        return ActivityRegistry.activities[type]
