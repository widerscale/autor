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

from autor.framework.autor_framework_exception import AutorFrameworkException
from autor.framework.check import Check
from autor.framework.context import Context
from autor.framework.context_properties_registry import (
    ContextPropertiesRegistry,
)
from autor.framework.context_property import ContextProperty
from autor.framework.key_handler import KeyHandler
from autor.framework.keys import ClassPropertiesKeys as prp
from autor.framework.keys import FlowContextKeys as ctx
from autor.framework.util import Util


class ContextPropertiesHandlerException(AutorFrameworkException):
    """Exception for errors in ContextPropertiesHandler"""


class ContextPropertiesHandlerValueException(ContextPropertiesHandlerException):
    """Exception for errors detected in the ContextPropertiesHandler \
        caused by incorrect usage by a user"""


class ContextPropertiesHandler:
    """
    ContextPropertiesHandler loads/saves and validates context properties for instances that use
    @input or/and @output decorators for their properties (see ContextPropertiesRegistry).
    The values for these properties will be read from context with load_input_properties() and
    saved to context with save_output_properties().
    """

    # pylint: disable-next=redefined-builtin
    def __init__(self, object: object, context: Context):
        """Creates and initiates the ContextPropertiesHandler instance for the 'object'
        that uses 'context' for storing its properties.

        Arguments:
            object {Object} -- An object whose properties need to be read/written
            Context {Context} -- The context used for storing properties.
        """

        Check.not_none(
            object,
            (
                "Mandatory parameter None - "
                + "An object whose properties need to be read/written may not be None."
            ),
        )
        self._object = object

        Check.is_instance_of(context, Context)
        self._context = context

    def load_input_properties(self, mandatory_inputs_check: bool = True):
        """Load the input properties values from the context.
        Args:
            mandatory_inputs_check (bool, optional): If true, check that the mandatory input \
                properties can be loaded from the context. Defaults to True.
        Raises:
            ContextPropertiesHandlerValueException: If mandatory input properties are not found \
                and mandatory_inputs_check==True
            ContextPropertiesHandlerValueException: If an input property has a wrong type
        """

        # Get a list of input properties for the object.
        props: List[ContextProperty] = ContextPropertiesRegistry.get_input_properties(self._object)

        for prop in props:
            Check.is_instance_of(prop, ContextProperty)

            # Get the property value
            ctx_key = KeyHandler.convert_key(
                prop.name, from_format=prp.format, to_format=ctx.format
            )


            prop_value = self._context.get(key=ctx_key, default=None, search=True)
            # prop_value = self._context.get_from_activity(key=ctx_key, default=None)

            # Check that the mandatory properties have a value
            if mandatory_inputs_check:
                if prop.mandatory and not prop_value:
                    raise ContextPropertiesHandlerValueException(
                        (
                            f"Could not find in context mandatory input property: '{ctx_key},"
                            + f" for activity: '{str(self._object.__class__.__name__)}'"
                        )
                    )

            # Check that the value type is correct.
            if prop_value is not None:
                if not isinstance(prop_value, prop.property_type):
                    raise ContextPropertiesHandlerValueException(
                        (
                            f"Type error in Object: {str(self._object.__class__.__name__)}."
                            + f" Expected input context property: {ctx_key} of type:"
                            + f" {str(prop.property_type)}, "
                            + f"received type: {str(prop_value.__class__.__name__)}"
                        )
                    )
                setattr(self._object, prop.name, prop_value)

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
                if prop.mandatory and not prop_value:
                    raise ContextPropertiesHandlerValueException(
                        (
                            f"Mandatory output context property: '{prop.name}' not set in activity:"
                            + f" '{str(self._object.__class__.__name__)}'"
                        )
                    )

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
                ctx_key = KeyHandler.convert_key(
                    prop.name, from_format=prp.format, to_format=ctx.format
                )
                self._context.set(ctx_key, prop_value)


        # Synchronize the context with the remote context (if it exists)
        self._context.sync_remote()
