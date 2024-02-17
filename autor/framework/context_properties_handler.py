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
from typing import List

import humps

from autor.framework.autor_framework_exception import AutorFrameworkException
from autor.framework.check import Check
from autor.framework.constants import ContextPropertyPrefix
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
    def __init__(self, object: object, input_context: Context, output_context:Context, config: dict = None):
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

        if input_context is not None:
            Check.is_instance_of(input_context, Context)
            self._input_context = input_context
        if output_context is not None:
            Check.is_instance_of(output_context, Context)
            self._output_context = output_context
        if config is not None:
            Check.is_instance_of(config, dict)
            self._config = config

        self._props = {}
        self._output_context.set(ContextPropertyPrefix.props, self._props, propagate_value=False)



    def load_config_properties(self, check_mandatory_properties: bool = True):
        self._load_properties(check_mandatory_properties, property_category="CONFIG")

    def load_input_properties(self, check_mandatory_properties: bool = True):
        self._load_properties(check_mandatory_properties, property_category="INPUT")

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
        if property_category == "CONFIG":
            property_source = "configuration"
            print_str = "config"
            prefix_provide = ContextPropertyPrefix.cfg_provide
            prefix_default = ContextPropertyPrefix.cfg_default
            #property_prefix = ContextPropertyPrefix.config
            props: List[ContextProperty] = ContextPropertiesRegistry.get_config_properties(self._object)
        elif property_category == "INPUT":
            property_source = "context"
            print_str = "input "
            prefix_provide = ContextPropertyPrefix.inp_provide
            prefix_default = ContextPropertyPrefix.inp_default
            #property_prefix = ContextPropertyPrefix.input
            props: List[ContextProperty] = ContextPropertiesRegistry.get_input_properties(self._object)
        else:
            raise AutorFrameworkException(f"Unhandled property category: {property_category}. Cannot load properties of that category.")


        for prop in props:
            Check.is_instance_of(prop, ContextProperty)

            # Get the property value
            if property_category == "CONFIG":
                prop_value = self._config.get(prop.name, None) # configurations are stored in config dict
            elif property_category == "INPUT":
                prop_value = self._input_context.get(key=prop.name, default=None, search=True) # inputs are stored in context
            else:
                raise AutorFrameworkException(f"Unhandled property category: {property_category}. Cannot load properties of that category.")

            self._check_input_properties_rules(prop, prop_value, property_category, property_source, check_mandatory_properties)

            # Check that the mandatory properties have a value
            if check_mandatory_properties:
                if prop.mandatory and (prop_value is None):
                    raise ContextPropertiesHandlerValueException(f"Could not find mandatory {property_category} property '{prop.name}' value to load for activity: '{str(self._object.__class__.__name__)}'")

            # Check that the value type is correct and set all non-None properties
            if prop_value is not None:
                if not isinstance(prop_value, prop.property_type):
                    raise ContextPropertiesHandlerValueException(f"Type error in Object: {str(self._object.__class__.__name__)}. Expected {property_category} property: {prop.name} of type: {str(prop.property_type)}, received type: {str(prop_value.__class__.__name__)}")
                setattr(self._object, prop.name, prop_value)
                self._props[f"{prefix_provide}{prop.name}"] = prop_value
                if DebugConfig.print_activity_properties_details:
                    logging.info(f"{DebugConfig.autor_info_prefix}{print_str} (provided): {prop.name}={prop_value}")



            # Check that non-mandatory


            # Rules
            # ___________________________________________________________
            # Mandatory inputs must not have default values in decorators
            # Mandatory inputs must not have default values in constructor
            # Mandatory inputs must have a value in context/configuration
            # Non-mandatory inputs must have default value defined either in decorator or constructor, but not in both.
            # Outputs may not have default values
            # Provided values must be of right type
            # Provided default values must be of right type



            else:
                # If a (non-mandatory) property is None, check if the class has defined a default value. If not,
                # throw an exception.


                # Default value provided by constructor
                if self._default_value_in_constructor(self._object, prop.name):

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


                else:
                    if prop.default != ContextPropertiesRegistry.DEFAULT_PROPERTY_VALUE_NOT_DEFINED: # Default value provided by decorator

                        if (prop.default is not None) and (not isinstance(prop.default, prop.property_type)): # Ok if None, otherwise must be correct type.
                            raise ContextPropertiesHandlerValueException(
                                f"Type error in Object: {str(self._object.__class__.__name__)}. For {property_category} property '{prop.name}' expected default value of type: {str(prop.property_type)}, received type: {str(prop.default.__class__.__name__)}")

                        setattr(self._object, prop.name, prop.default) # if default value was defined in the decorator @input -> set the decorator default value
                        #self._output_context.set(f"{property_category}_{prop.name}", prop.default, propagate_value=False)
                        self._props[f"{prefix_default}{prop.name}"] = prop.default
                        if DebugConfig.print_activity_properties_details:
                            #logging.info(f"{DebugConfig.autor_info_prefix}{property_prefix}default_{prop.name}: {prop.default}")
                            logging.info(f"{DebugConfig.autor_info_prefix}{print_str} (default):  {prop.name}={prop.default}")



                    else: # Default value not provided by constructor nor decorator -> problem!

                        #setattr(self._object, prop.name, None) # if no default value is available, set None
                        #self._output_context.set(f"{property_category}_{prop.name}", None, propagate_value=False)
                        #self._props[f"{property_prefix}{prop.name}"] = None
                        #if DebugConfig.print_activity_properties_details:
                            #logging.info(f"{DebugConfig.autor_info_prefix}{property_prefix}None_{prop.name}: None")
                            #logging.info(f"{DebugConfig.autor_info_prefix}{print_str} (None):     {prop.name}=None")
                        raise ContextPropertiesHandlerValueException(
                            f"No default value found for optional property: '{prop.name}' in class {self._object.__class__.__name__}. Default porperties must have a default value.")








    def _check_input_properties_rules(self, prop:ContextProperty, prop_value, prop_category:str, resource_name:str, check_if_mandatory_values_provided:bool):
        cls = self._object.__class__
        # Rules
        # ___________________________________________________________

        #logging.info(f"Checking property: {prop.name}")
        #prop.print()

        # Mandatory inputs must not have default values in decorators
        if prop.mandatory and self._default_value_in_decorator(prop):
            logging.warning(f"{DebugConfig.autor_info_prefix}Mandatory Activity inputs should not have default values defined in decorator.")
            logging.warning(f"{DebugConfig.autor_info_prefix}The provided default value will be ignored during the execution.")
            logging.warning(f"{DebugConfig.autor_info_prefix}   class:    {cls.__name__}")
            logging.warning(f"{DebugConfig.autor_info_prefix}   property: {prop.name}")
            logging.warning(f"{DebugConfig.autor_info_prefix}   type:     {prop.property_type}")
            logging.warning(f"{DebugConfig.autor_info_prefix}   default:  {prop.default}")
            logging.warning(f"{DebugConfig.autor_info_prefix}   file:     {inspect.getfile(cls)}")
            logging.warning(f"{DebugConfig.autor_info_prefix}")

        # Mandatory inputs must not have default values in constructor
        if prop.mandatory and self._default_value_in_constructor(self._object, prop.name):
            logging.warning(f"{DebugConfig.autor_info_prefix}Mandatory Activity inputs properties should not have default values defined in constructor.")
            logging.warning(f"{DebugConfig.autor_info_prefix}The provided default value will be ignored during the execution.")
            logging.warning(f"{DebugConfig.autor_info_prefix}   class:             {cls.__name__}")
            logging.warning(f"{DebugConfig.autor_info_prefix}   property:          {prop.name}")
            logging.warning(f"{DebugConfig.autor_info_prefix}   type:              {prop.property_type}")
            logging.warning(f"{DebugConfig.autor_info_prefix}   default (constr):  {getattr(self._object, prop.name)}")
            logging.warning(f"{DebugConfig.autor_info_prefix}   file:              {inspect.getfile(cls)}")
            logging.warning(f"{DebugConfig.autor_info_prefix}")





        # Non-mandatory inputs must have a default value defined either in decorator or constructor
        if not prop.mandatory and (not self._default_value_in_constructor(self._object, prop.name) and not self._default_value_in_decorator(prop)):
            err_msg = f"Missing default value for Activity property: {prop.name}. Optional Activity properties must have a default value defined. " \
                      f"Class: {cls.__name__}, " \
                      f"property: {prop.name}, " \
                      f"type: {prop.property_type}, " \
                      f"file: {inspect.getfile(cls)}"
            raise ContextPropertiesHandlerValueException(err_msg)








        # Non-mandatory inputs must not have default values defined BOTH in constructor and decorator
        # Non-mandatory inputs are set to None if no default value is found in constructor nor decorator
        # Outputs may not have default values (<- will be handled by python)

        # Provided default values must have correct type (both in constructor and in decorator)

        if self._default_value_in_constructor(self._object, prop.name):
            object_constructor_val = getattr(self._object, prop.name)
            if (object_constructor_val is not None) and (not isinstance(object_constructor_val, prop.property_type)):
                raise ContextPropertiesHandlerValueException(
                     f"Property default value type error in class: {cls} constructor. Expected {prop.property_type} property '{prop.name}' default value of type: {str(prop.property_type)}, found in constructor type: {str(object_constructor_val.__class__.__name__)}")


        # Provided property values (context/config) values must have correct type
        if prop_value is not None:
            if not isinstance(prop_value, prop.property_type):
                raise ContextPropertiesHandlerValueException(
                    f"Property type error in class: {cls}. Expected {prop.property_type} property '{prop.name}' of type: {str(prop.property_type)}, received type: {str(prop_value.__class__.__name__)}")



        # Mandatory inputs must have a value in context/configuration
        if check_if_mandatory_values_provided:
            if prop.mandatory and (prop_value is None):

                msg = f"Could not find mandatory property value in {resource_name}:" \
                      f"\nException details:" \
                      f"\nclass:    {cls.__name__}" \
                      f"\nproperty: {prop.name}" \
                      f"\ntype:     {prop.property_type}" \
                      f"\nfile:     {inspect.getfile(cls)}"

                raise ContextPropertiesHandlerValueException(msg)








    def _default_value_in_decorator(self, prop:ContextProperty):
        return prop.default != ContextPropertiesRegistry.DEFAULT_PROPERTY_VALUE_NOT_DEFINED

    def _get_type_name(self, str_type:str)->str:
        logging.info(f"33RRRRRRRRRRRRRRRRRRR: {str_type}")
        str_name = str(str_type).split("'")[1]
        return str_name

    def _default_value_in_constructor(self, o:object, prop_name:str)->bool:
        try:
            getattr(o, prop_name)
            return True
        except Exception as e:
            return False




    def get_output_properties_values(self, status_only:bool = False):
        # Get a list of output properties for the object
        props: List[ContextProperty] = ContextPropertiesRegistry.get_output_properties(self._object)
        vals: dict = {}
        for prop in props:
            if (status_only and prop.name == "status") or (not status_only):
                try:
                    prop_value = getattr(self._object, prop.name)
                    vals[prop.name] = prop_value
                except Exception as e:
                    logging.warning(f"Could not fetch attribute: {prop.name}") # ok, with just a print.
        return vals

    def get_input_properties_values(self):
        # Get a list of output properties for the object
        props: List[ContextProperty] = ContextPropertiesRegistry.get_input_properties(self._object)
        vals: dict = {}
        for prop in props:
            try:
                prop_value = getattr(self._object, prop.name)
                vals[prop.name] = prop_value
            except Exception as e:
                logging.warning(f"Could not fetch attribute: {prop.name}") # ok, with just a print.
        return vals

    def get_config_properties_values(self):
        # Get a list of output properties for the object
        props: List[ContextProperty] = ContextPropertiesRegistry.get_config_properties(self._object)
        vals: dict = {}
        for prop in props:
            try:
                prop_value = getattr(self._object, prop.name)
                vals[prop.name] = prop_value
            except Exception as e:
                logging.warning(f"Could not fetch attribute: {prop.name}") # ok, with just a print.
        return vals



    def save_output_properties(self, mandatory_outputs_check: bool = True, save_status_only = False):
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

            if (save_status_only and prop.name == "status") or (not save_status_only):

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
                    self._output_context.set(prop.name, prop_value)
                    self._props[f"{ContextPropertyPrefix.out_provide}{prop.name}"] = prop_value
                    if DebugConfig.print_activity_properties_details:
                        logging.info(f"{DebugConfig.autor_info_prefix}output: {prop.name}={prop_value}")


        # Synchronize the context with the remote context (if it exists)
        self._output_context.sync_remote()
