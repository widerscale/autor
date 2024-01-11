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

import humps

from autor.framework.autor_framework_exception import AutorFrameworkException
from autor.framework.check import Check
from autor.framework.context import Context
from autor.framework.context_properties_registry import (
    ContextPropertiesRegistry,
)
from autor.framework.context_property import ContextProperty
from autor.framework.debug_config import DebugConfig
from autor.framework.key_handler import KeyHandler
from autor.framework.keys import ClassPropertiesKeys as prp
from autor.framework.keys import FlowContextKeys as ctx
from autor.framework.keys import FlowConfigurationKeys as cfg
from autor.framework.util import Util


class ContextPropertiesHandlerException(AutorFrameworkException):
    """Exception for errors in ContextPropertiesHandler"""


class ContextPropertiesHandlerValueException(ContextPropertiesHandlerException):
    """Exception for errors detected in the ContextPropertiesHandler \
        caused by incorrect usage by a user"""


class ContextPropertiesHandler:
    """
    ContextPropertiesHandler loads/saves and validates context properties for instances that use
    @input, @output or @config decorators for their properties (see ContextPropertiesRegistry).
    The values for these properties will be read from context with load_input_properties(),
    load_config_properties() and saved to context with save_output_properties().
    """

    # pylint: disable-next=redefined-builtin
    def __init__(self, object: object, context: Context = None, config: dict = None):
        """Creates and initiates the ContextPropertiesHandler instance for the 'object'
        that uses 'context' for storing its properties and/or 'configuration' for reading
        configuration properties from.

        Arguments:
            object {Object} -- An object whose properties need to be read/written
            context {Context} -- The context used for storing properties.
            configuration {dict} -- Configuration from where the configuration properties are read from.
        """

        Check.not_none(object, "Mandatory parameter None - An object whose properties need to be read/written may not be None.")
        self._object = object

        if context is not None:
            Check.is_instance_of(context, Context)
            self._context = context

        if config is not None:
            Check.is_instance_of(config, dict)
            self._config = config



    def load_config_properties(self, check_mandatory_properties: bool = True):
        self._load_properties(check_mandatory_properties, property_category="config")

    def load_input_properties(self, check_mandatory_properties: bool = True):
        self._load_properties(check_mandatory_properties, property_category="input")

    def _load_properties(self, check_mandatory_properties:bool, property_category:str):
        """Load the input properties values from the context.
        Args:
            check_mandatory_properties (bool, optional): If true, check that the mandatory input \
                properties can be loaded from the context. Defaults to True.
        Raises:
            ContextPropertiesHandlerValueException: If mandatory input properties are not found \
                and check_mandatory_properties==True
            ContextPropertiesHandlerValueException: If an input property has a wrong type
        """

        # Get a list of input properties for the object.
        props: List[ContextProperty] = ContextPropertiesRegistry.get_input_properties(self._object)
        if property_category == "config":
            props: List[ContextProperty] = ContextPropertiesRegistry.get_config_properties(self._object)
        elif property_category == "input":
            props: List[ContextProperty] = ContextPropertiesRegistry.get_input_properties(self._object)
        else:
            raise AutorFrameworkException(f"Unhandled property category: {property_category}. Cannot load properties of that category.")


        for prop in props:
            Check.is_instance_of(prop, ContextProperty)

            # Get the property value
            if property_category == "config":
                prop_value = self._config.get(prop.name, None) # configurations are stored in config dict
            elif property_category == "input":
                prop_value = self._context.get(key=prop.name, default=None, search=True) # inputs are stored in context
            else:
                raise AutorFrameworkException(f"Unhandled property category: {property_category}. Cannot load properties of that category.")


            # Check that the mandatory properties have a value
            if check_mandatory_properties:
                if prop.mandatory and (prop_value is None):
                    raise ContextPropertiesHandlerValueException(f"Could not find mandatory {property_category} property '{prop.name}' value to load for activity: '{str(self._object.__class__.__name__)}'")

            # Check that the value type is correct and set all non-None properties
            if prop_value is not None:
                if not isinstance(prop_value, prop.property_type):
                    raise ContextPropertiesHandlerValueException(f"Type error in Object: {str(self._object.__class__.__name__)}. Expected {property_category} context property: {prop.name} of type: {str(prop.property_type)}, received type: {str(prop_value.__class__.__name__)}")
                setattr(self._object, prop.name, prop_value)

            # Check that non-mandatory


            # Rules
            # ___________________________________________________________
            # Mandatory inputs must not have default values in decorators
            # Mandatory inputs must not have default values in constructor
            # Mandatory inputs must have a value in context/configuration
            # Non-mandatory inputs must not have default values defined BOTH in constructor and decorator
            # Non-mandatory inputs are set to None if no default value is found in constructor nor decorator
            # Outputs may not have default values
            # Provided values must be of right type
            # Provided default values must be of right type



            else:
                # If a (non-mandatory) property is None, check if the class has defined a default value. If not,
                # set the default value to None. This way there will not be a case when a class does not have a property
                # attribute defined at all.


                if self._object_has_defined_property_value(self._object, prop.name):

                    if prop.default != ContextPropertiesRegistry.DEFAULT_PROPERTY_VALUE_NOT_DEFINED: # both object and property have defined a default property value
                        def_val = getattr(self._object, prop.name)

                        err_msg = (
                            f"Default values for properties may not be defined both in constructor and in property decorator." +
                            f"Class: {str(self._object.__class__.__name__)}. " +
                            f"Property: {prop.name}. " +
                            f"Decorator: @{property_category}(mandatory=False, type={self._get_type_name(prop.property_type)}, default={prop.default}). " +
                            f"Defined default value in constructor: {def_val}. " +
                            f"To fix this error: Remove property default value definition in the constructor OR remove the default value definition in the decorator."
                        )
                        raise ContextPropertiesHandlerValueException(err_msg)


                else: # property not defined by object
                    if prop.default != ContextPropertiesRegistry.DEFAULT_PROPERTY_VALUE_NOT_DEFINED:
                        setattr(self._object, prop.name, prop.default) # if default value was defined in the decorator @input -> set the decorator default value
                    else:
                        setattr(self._object, prop.name, None) # if no default value is available, set None
                        logging.warning(f"{DebugConfig.autor_info_prefix}Warning while trying to set optional input property {self._object.__class__.__name__}.{prop.name}:")
                        logging.warning(f"{DebugConfig.autor_info_prefix}No value found for key: '{prop.name}' -> setting property: {self._object.__class__.__name__}.{prop.name} = None")







    def _check_input_properties_rules(self, prop:ContextProperty, prop_value, resource_name:str, resource_key:str, check_if_mandatory_values_provided:bool):

        # Rules
        # ___________________________________________________________
        # Mandatory inputs must not have default values in decorators
        # Mandatory inputs must not have default values in constructor

        # Non-mandatory inputs must not have default values defined BOTH in constructor and decorator
        # Non-mandatory inputs are set to None if no default value is found in constructor nor decorator
        # Outputs may not have default values

        # Provided default values must have correct type (both in constructor and in decorator)
        object_name = str(self._object.__class__.__name__)
        if self._object_has_defined_property_value(self._object, prop.name):
            object_constructor_val = getattr(self._object, prop.name)
            if (object_constructor_val is not None) and (not isinstance(object_constructor_val, prop.property_type)):
                raise ContextPropertiesHandlerValueException(
                     f"Property default value type error in Object: {object_name} constructor. Expected {prop.property_type} property '{prop.name}' default value of type: {str(prop.property_type)}, found in constructor type: {str(object_constructor_val.__class__.__name__)}")


        # Provided property values (context/config) values must have correct type
        if prop_value is not None:
            if not isinstance(prop_value, prop.property_type):
                raise ContextPropertiesHandlerValueException(
                    f"Property type error in Object: {object_name}. Expected {prop.property_type} property '{prop.name}' of type: {str(prop.property_type)}, received type: {str(prop_value.__class__.__name__)}")



        # Mandatory inputs must have a value in context/configuration
        if check_if_mandatory_values_provided:
            if prop.mandatory and (prop_value is None):
                raise ContextPropertiesHandlerValueException(
                    f"Could not find mandatory {prop.property_type} property '{prop.name}' value for Object '{object_name}' " +
                    f"Expected to find key '{resource_key}' in '{resource_name}'")






    def _get_type_name(self, t:type)->str:
        str_type = str(t)
        str_name = str_type.split("'")[1]
        return str_name

    def _object_has_defined_property_value(self, o:object, prop_name:str)->bool:
        try:
            getattr(o, prop_name)
            return True
        except Exception as e:
            return False


    def save_output_properties(self, mandatory_outputs_check: bool = True):
        """Save the output properties values to the context and synchronize the \
            context with the remote context.
        Args:
            mandatory_outputs_check (bool, optional): If true, check that the mandatory \
                output properties are provided by the object.
        Raises:
            ContextPropertiesHandlerValueException: If mandatory output properties are not \
                provided and mandatory_outputs_check==True
            ContextPropertiesHandlerValueException: If an output property has a wrong type
        """

        # Get a list of output properties for the object
        props: List[ContextProperty] = ContextPropertiesRegistry.get_output_properties(self._object)

        for prop in props:
            Check.is_instance_of(prop, ContextProperty)

            # Get the property value from the object
            prop_value = None
            try:
                prop_value = getattr(self._object, prop.name)
            except Exception as e:
                raise ContextPropertiesHandlerValueException(str(e)).with_traceback(
                    e.__traceback__
                )  # Getter implementation error.

            # Check that the mandatory property values are provided
            if mandatory_outputs_check:
                if prop.mandatory and (prop_value is None):
                    raise ContextPropertiesHandlerValueException(f"Mandatory output context property: '{prop.name}' not set in activity: '{str(self._object.__class__.__name__)}'")

            # Check that the provided property values have correct type
            if prop_value is not None:
                if not isinstance(prop_value, prop.property_type):
                    raise ContextPropertiesHandlerValueException(
                        (
                            "Unexpected property type in Object:"
                            + f" {self._object.__class__.__name__}."
                            + " Expected output context property with name:"
                            + f" {prop.name} and of type: {str(prop.property_type)},"
                            + f" actual type: {prop_value.__class__.__name__}"
                        )
                    )
                # Set the property value to the context
                #ctx_key = KeyHandler.convert_key(
                   # prop.name, from_format=prp.format, to_format=ctx.format
               # )
                self._context.set(prop.name, prop_value)


        # Synchronize the context with the remote context (if it exists)
        self._context.sync_remote()
