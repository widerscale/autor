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
from autor.framework.key_handler import KeyFormat
from autor.framework.key_handler import KeyHandler as Handler
from autor.framework.key_handler import Keys

# Classes for handling all kinds of key names with different formats. The solution
# will enable to define a key name and have access to it in different formats (camelCase,
# snake_case etc.).
#
# To create collection of keys with a certain format and for a certain purpose:
# define a key class:
#    - that inherits from class Keys
#    - with a name that reflects the purpose of the keys
#    - that specifies the desired key format
#    - that specifies the key names in UPPERCASE_SNAKE
#
# The classes that inherit from Keys will have an attribute for each element in 'keys'.
# The name  of the attribute will be the list element value and
# the value of the attribute will be the attribute name converted to the KeyFormat
#  specified by the class.
# Create a new class for each new concept that needs a set of keys.
# The keys list itself can be shared between
# classes, which allows to only have on list of keys for a whole system.
#
# EXAMPLE:
#
# class ArgParserKeys(Keys):
#    format = KeyFormat.SNAKE
#    keys = ['FIRST_KEY_NAME', 'SECOND_KEY_NAME']
#
# Usage:
# ArgParserKeys.FIRST_KEY_NAME (will give: 'first_key_name')
#


class KeyHandler:
    # pylint: disable-next=no-self-use
    def create_keys(self):
        Handler.create_keys()


keys = [
    "ABORT_EXCEPTION_MESSAGE",
    "ABORT_TYPE",
    "ACTION",
    "ACTIVITIES",
    "ACTIVITY",
    "ACTIVITY_BLOCKS",
    "ACTIVITY_BLOCK_ACTIVITIES",
    "ACTIVITY_BLOCK_CALLBACK_EXCEPTIONS",
    "ACTIVITY_BLOCK_CONFIG",
    "ACTIVITY_BLOCK_CONFIGS_AFTER_ACTIVITY",
    "ACTIVITY_BLOCK_CONFIGS_AFTER_BLOCK",
    "ACTIVITY_BLOCK_CONFIGS_BEFORE_ACTIVITY",
    "ACTIVITY_BLOCK_CONFIGS_BEFORE_BLOCK",
    "ACTIVITY_BLOCK_CONFIGS_MAIN_ACTIVITIES",
    "ACTIVITY_BLOCK_CONTEXT",
    "ACTIVITY_BLOCK_ID",
    "ACTIVITY_BLOCK_INTERRUPTED",
    "ACTIVITY_BLOCK_LATEST_ACTIVITY",
    "ACTIVITY_BLOCK_STATUS",
    "ACTIVITY_BLOCK_RUN_ID",
    "ACTIVITY_BLOCK_STATUS",
    "ACTIVITY_CONFIG",
    "ACTIVITY_CONTEXT",
    "ACTIVITY_DATA",
    "ACTIVITY_GROUP_TYPE",
    "ACTIVITY_INSTANCE",
    "ACTIVITY_INPUT",
    "ACTIVITY_ID",
    "ACTIVITY_IDS",
    "ACTIVITY_MODULE",
    "ACTIVITY_MODULES",
    "ACTIVITY_NAME",
    "ACTIVITY_RUN_ID",
    "ACTIVITY_SKIP_REQUESTED",
    "ACTIVITY_STATUS",
    "ACTIVITY_TYPE",
    "ADDITIONAL_EXTENSIONS",
    "AFTER_ACTIVITY",
    "AFTER_BLOCK",
    "ARTIFACT_URL",
    "BASELINE_HANDLE",
    "BEFORE_ACTIVITY",
    "BEFORE_BLOCK",
    "BOOTSTRAP",
    "CALLBACK_CLASS",
    "CALLBACK_EXCEPTIONS",
    "CLASS",
    "CONFIG",
    "CONTEXT",
    "CONTINUE_ON",
    "CUSTOM",
    "CUSTOM_DATA",
    "CREDENTIALS_STORE_USER_ID",
    "DBG_EXTENSION_TEST_STR",
    "DEALLOCATION_NEEDED",
    "DESCRIPTION",
    "DETAILED_ACTIVITY_STATUS",
    "EXCEPTION",
    "EXCEPTIONS",
    "EXCEPTION_MESSAGE",
    "EXTENSIONS",
    "FALSE",
    "FIRST_EXCEPTION_MESSAGE",
    "FLOW_CONFIG",
    "FLOW_CONFIG_URL",
    "FLOW_CONTEXT",
    "FLOW_CREATE_NEW_CONTEXT",
    "FLOW_ID",
    "FLOW_RUN_ID",
    "HELPERS",
    "IMPORTS_FILE",
    "INPUT",
    "INSTANCE",
    "INTERNAL_ACTIVITY_DATA",
    "LOGS_URL",
    "MAIN_ACTIVITY_STATUS",
    "MESSAGE",
    "MODE",
    "MODULE",
    "NAMESPACE",
    "PRODUCT_ID",
    "RAS_API_ENDPOINT",
    "RAS_CLIENT_ID",
    "RAS_HOST_URL",
    "RUN_ON",
    "STATE_LISTENERS",
    "STATE_PRODUCERS",
    "SEND_SOURCE_CREATED",
    "SEND_SOURCE_PUBLISHED",
    "SKIP_TYPE",
    "STACK_TRACE",
    "STATE",
    "STRING",
    "TEST_ENVIRONMENT_ID",
    "TRUE",
    "TYPE",
    "VISUALIZE_ACTIVITY",
    "VOLARE_EVENT_ACTIVITY_FINISHED_FAIL",
    "VOLARE_EVENT_ACTIVITY_FINISHED_SUCCESS",
    "WORKSPACE_PATH",
]
""" The list of key names used in Autor """


class CommandLineKeys(Keys):
    format = KeyFormat.LCD
    keys = keys


class ArgParserKeys(Keys):
    format = KeyFormat.SNAKE
    keys = keys


class EnvironmentKeys(Keys):
    format = KeyFormat.UCU
    keys = keys


class FlowContextKeys(Keys):
    format = KeyFormat.CAMEL
    keys = keys


class FlowConfigurationKeys(Keys):
    format = KeyFormat.CAMEL
    keys = keys


class AutorFrameworkKeys(Keys):
    format = KeyFormat.UCU
    keys = keys


class MessageBusMessageKeys(Keys):
    format = KeyFormat.UCU
    keys = keys


class ClassPropertiesKeys(Keys):
    format = KeyFormat.SNAKE
    keys = keys


class StateKeys(Keys):
    format = KeyFormat.UCU
    keys = keys


Handler.create_keys()
