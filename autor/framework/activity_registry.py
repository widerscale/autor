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
from autor.framework.autor_framework_exception import (
    AutorFrameworkValueException,
)


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
    def activity(type):

        """
        A class decorator for registering a class as an activity of a certain type.
        Arguments:
            type {str} -- The activity type name.
        Returns:
            function -- The function that registers the activity in the registry.
        """

        def act(cls):
            # pylint: disable=no-else-raise
            if type is None:
                raise AutorFrameworkValueException(
                    "Mandatory parameter: 'type' missing in the decorator: 'activity'"
                )
            else:
                # pylint: disable-next=consider-iterating-dictionary, no-else-return
                if type not in ActivityRegistry.activities.keys():
                    ActivityRegistry.activities[type] = cls
                    return cls
                else:
                    existing_activity = ActivityRegistry.activities[type]
                    raise AutorFrameworkValueException(
                        (
                            f"An attempt to register an activity:{cls.__name__} with type:{type}"
                            + " while the type already exists in the registry"
                            + f" for activity: {existing_activity.__name__}."
                        )
                    )

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
                    f"No activity with the type: '{str(type)}' registered. Check if the activity"
                    + " uses the necessary decorators and is bootstrapped."
                    + "To bootstrap an activity it has to be imported BEFORE it is created by"
                    + " the activity factory."
                )
            )

        return ActivityRegistry.activities[type]
