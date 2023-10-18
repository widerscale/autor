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
import abc

# All key names (keys to context, command-line parameters, configuration files etc.)
#  used in the Activity Framework.
# The keys from this list will be converted into the formats listed in class KeyFormat.

# pylint: disable=too-few-public-methods
class KeyFormat:
    # Key formats
    UCU = "UPPER_CASE_UNDERSCORE"
    LCD = "lower-case-dash"
    SNAKE = "snake_case"
    CAMEL = "camelCase"
    PASCAL = "PascalCase"


# __________________ U T I L I T I E S ____________________#
###########################################################

# pylint: disable=invalid-name
class KeyConverter:
    @staticmethod
    def UCU_to_LCD(key):
        # EXAMPLE_KEY -> example-key
        return key.lower().replace("_", "-")

    @staticmethod
    def UCU_to_SNAKE(key):
        # EXAMPLE_KEY -> example_key
        return key.lower()

    @staticmethod
    def UCU_to_CAMEL(key):
        # EXAMPE_KEY -> exampeKey
        components = key.lower().split("_")
        return components[0] + "".join(x.title() for x in components[1:])

    @staticmethod
    def LCD_to_UCU(key):
        # example-key -> EXAMPLE_KEY
        return key.upper().replace("-", "_")

    @staticmethod
    def SNAKE_to_UCU(key):
        # example_key -> EXAMPLE_KEY
        return key.upper()

    @staticmethod
    def SNAKE_to_CAMEL(key):
        # example_key -> exampleKey
        key = KeyConverter.SNAKE_to_UCU(key)
        key = KeyConverter.UCU_to_CAMEL(key)
        return key

    @staticmethod
    def UCU_to_PASCAL(key):
        # EXAMPLE_KEY -> ExampleKey
        key = KeyConverter.UCU_to_SNAKE(key)
        key = ''.join(x.title() for x in key.split('_'))
        return key


class KeyHandler:
    @staticmethod
    def convert_keys(keys, from_format, to_format):
        if from_format == to_format:
            return keys

        formatted_keys = []
        for key in keys:
            formatted_keys.append(KeyHandler.convert_key(key, from_format, to_format))
        return formatted_keys

    @staticmethod
    def convert_key(key, from_format, to_format):
        if from_format == to_format:
            return key

        if from_format == KeyFormat.UCU:  # pylint:disable=R1705
            if to_format == KeyFormat.LCD:  # pylint:disable=R1705
                return KeyConverter.UCU_to_LCD(key)
            elif to_format == KeyFormat.SNAKE:
                return KeyConverter.UCU_to_SNAKE(key)
            elif to_format == KeyFormat.CAMEL:
                return KeyConverter.UCU_to_CAMEL(key)
            else:
                raise KyHandlerException(KeyHandler._exception_message(from_format, to_format))
        elif from_format == KeyFormat.SNAKE:
            if to_format == KeyFormat.CAMEL:  # pylint:disable=R1705
                return KeyConverter.SNAKE_to_CAMEL(key)
            elif to_format == KeyFormat.UCU:
                return KeyConverter.SNAKE_to_UCU(key)
            else:
                raise KyHandlerException(KeyHandler._exception_message(from_format, to_format))
        else:
            raise KyHandlerException(KeyHandler._exception_message(from_format, to_format))

    @staticmethod
    def _exception_message(from_format, to_format):
        return f"Conversion from {from_format} to {to_format} not implemented."

    ################################################################
    #            Populate key classes on import
    ################################################################

    @staticmethod
    def create_keys() -> None:
        key_classes = Keys.__subclasses__()

        for key_class in key_classes:
            keys = key_class.keys
            for k in keys:
                setattr(key_class, k, KeyHandler.convert_key(k, KeyFormat.UCU, key_class.format))


class Keys:
    __metaclass__ = abc.ABCMeta


class KyHandlerException(Exception):
    """Exception for all activity KeyHandler errors."""
