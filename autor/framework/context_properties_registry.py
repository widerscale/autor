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
"""
    A registry of properties for all calsses that are decorated with @input and @output decorators.
    The decoartors are also provided by this class.

Examples:

    # -------- Optional input property --------
    @property
    @input(mandatory=False, type=str)
    def x(self) -> str:
        return self.__x

    @x.setter
    def x(self, n):
        self.__x = n



    # -------- Mandatory ouput property --------
    @property
    @output(mandatory=True, type=str)
    def y(self) -> str:
        return self.__y

    @y.setter
    def y(self, n):
        self.__y = n


    # -------- Optional input property --------
    # -------- Mandatory ouput property --------
    @property
    @input(mandatory=False, type=str)
    @output(mandatory=True, type=str)
    def z(self) -> str:
        return self.__z

    @z.setter
    def z(self, n):
        self.__z = n

"""
import inspect
from typing import Dict, List

from autor.framework.check import Check
from autor.framework.context_property import ContextProperty


class ContextPropertiesRegistry:
    """Class for keeping a registry of context properties.
    The class provides decorators (see input() and output()) that can used for decorationg \
        properties to make them
    act as context properties.
    """

    # Input and output properties dictionaries contain ContextProperty objects for all
    #  class properties that are decorated with @input or/and @output decorators.
    # The lists are updated whenever a module is imported.
    __inputs = {}  # type: Dict[str, ContextProperty]
    __outputs = {}  # type: Dict[str, ContextProperty]

    #  -------------------------------------- D E C O R A T O R S ---------------------------------#
    @staticmethod
    # pylint: disable-next=redefined-builtin
    def input(mandatory, type):
        """
        A property decorator.
        Properties that are decorated with this decorator indicate that the value of this
        property should be read from the context and considered as an input to the entity
        that has this property.
        Arguments:
            mandatory {bool} -- True if the parameter is mandatory
            type {python type} -- The type of the argument (str, int, long etc.)
        Returns:
            function
        """

        def inp(func):
            ContextPropertiesRegistry._add_property(
                mandatory, type, ContextPropertiesRegistry.__inputs, func
            )
            return func

        return inp

    @staticmethod
    # pylint: disable-next=redefined-builtin
    def output(mandatory, type):
        """
        A property decorator.
        Properties that are decorated with this decorator indicate that the value of this
        property should be saved in the context and considered as an output of the entity
        that has this property.
        Arguments:
            mandatory {bool} -- True if the parameter is mandatory
            type {python type} -- The type of the argument (str, int, long etc.)
        Returns:
            function
        """

        def out(func):
            # logging.debug(f"OUTPUT :  {str(func.__qualname__)}")
            ContextPropertiesRegistry._add_property(
                mandatory, type, ContextPropertiesRegistry.__outputs, func
            )
            return func

        return out

    #  ------------------------------- P U B L I C   M E T H O D S -------------------------------#
    @staticmethod
    def get_input_properties(instance: object):
        """
        Get registered @input properties for the instance. If the instance does not contain \
            any @input properties,
        an empty list is returned.

        Arguments:  instance {object} - The instance whose @input parameters should be returned.
        Returns:    {[Property]} - The list of @input parameters for the instance."""
        return ContextPropertiesRegistry.__get_properties(
            instance, ContextPropertiesRegistry.__inputs
        )

    @staticmethod
    def get_output_properties(instance: object):
        """
        Get registered @output properties for the instance. If the instance does not contain any \
            @output properties,
        an empty list is returned.

        Arguments:  instance {object} - The instance whose @output parameters should be returned.
        Returns:    {[Property]} - The list of @output parameters for the instance."""
        return ContextPropertiesRegistry.__get_properties(
            instance, ContextPropertiesRegistry.__outputs
        )

    # --------------------------- P R I V A T E   M E T H O D S ---------------------------------#
    @staticmethod
    def __get_properties(instance, properties: Dict[str, ContextProperty]) -> List[ContextProperty]:
        """Return a list of properties for the given instance."""

        class_names = ContextPropertiesRegistry.__get_instance_class_names(instance)

        # Create a list of all properties that are declared by the classes of the instance.
        instance_properties = []
        # pylint: disable-next=redefined-builtin
        for id in properties:
            if properties[id].class_name in class_names:
                instance_properties.append(properties[id])
        return instance_properties

    @staticmethod
    def __get_instance_class_names(instance: object) -> List[str]:
        Check.not_none(instance, "The object to inspect for properties is None")
        classes = inspect.getmro(instance.__class__)

        # The class name and the inherited class names for the instance.
        class_names = []
        for cl in classes:
            class_names.append(cl.__name__)
        return class_names

    @staticmethod
    # pylint: disable-next=redefined-builtin
    def _add_property(mandatory, type, property_list, func):

        # The name of the class where the property is defined
        class_name = func.__qualname__.split(".")[0]
        property_name = func.__name__
        property_list[class_name + "_" + property_name] = ContextProperty(
            property_name, class_name, mandatory, type
        )
