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
from typing import List


# fmt: off




# Provides functionality for checking if a value is a valid constant
# and to get a list of valid constants.
# To use this class, extend it and add your constants as static attributes
# to your class.
# Note that the constant attribute names must not begin with __.
# Example: __THIS_IS_AN_INVALID_CONSTANT_ATTRIBUTE_NAME.

class Constant():
    @staticmethod
    def is_valid(constant_name:str)->bool:
        return hasattr(Mode(),constant_name)

    @staticmethod
    def get_valid_constants(klass)->list:
        mmbrs: List[(str, str)] = inspect.getmembers(klass)  # returns [(name,val)]
        values:List[str] = []
        for (name,val) in mmbrs:
            if not name.startswith('__') and name != "is_valid" and  name != "get_valid_constants":
                values.append(val)
        return values


class Constants(Constant):
    AUTOR_ENVIRONMENT_VARIABLE_PREFIX = "AUTOR_ARGUMENT_"
    DEBUG_LINE_LENGTH = 50
    GENERATED_ACTIVITY_BLOCK_ID = "generatedActivityBlock"
    GENERATED_FLOW_CONFIG_PATH = "autor-config.yml"

class ContextPropertyPrefix(Constant):
    input = "inp_"
    output = "out_"
    config = "cfg_"
    props = "__props"


class ActivityGroupType(Constant):
    BEFORE_BLOCK = "BEFORE_BLOCK"                   # BBA
    BEFORE_ACTIVITY = "BEFORE_ACTIVITY"             # BA
    MAIN_ACTIVITY = "MAIN_ACTIVITY"                 # MA
    AFTER_ACTIVITY = "AFTER_ACTIVITY"               # AA
    AFTER_BLOCK = "AFTER_BLOCK"                     # ABA


class Status(Constant):
    SUCCESS = 'SUCCESS'
    FAIL = 'FAIL'
    ERROR = 'ERROR'
    SKIPPED = 'SKIPPED'
    ABORTED = 'ABORTED'
    UNKNOWN = 'UNKNOWN'
    ALL = 'ALL'


class Action(Constant):
    RUN = 'RUN'
    SKIP_BY_FRAMEWORK = "SKIP_BY_FRAMEWORK"
    SKIP_BY_CONFIGURATION = "SKIP_BY_CONFIGURATION"
    REUSE = 'REUSE' # Reuse the values from context provided by previous run.
    SKIP_WITH_OUTPUT_VALUES = 'SKIP_WITH_OUTPUT_VALUES' # Option in Flow Config -> use outputs provided in Flow Config.
    KEEP_AS_IS = 'KEEP_AS_IS'



class AbortType(Constant):
    ABORTED_BY_FRAMEWORK = "ABORTED_BY_FRAMEWORK"
    ABORTED_BY_ACTIVITY = "ABORTED_BY_ACTIVITY"


# Values used in configurations.
class Configuration(Constant):
    ANY = "_any"
    PREVIOUS = "_previous"
    LATEST = "_latest"

# Autor in-parameter names
class Inparam(Constant):
    MODE                    = "mode"
    FLOW_CONFIG_PATH         = "flow-config-path"
    ACTIVITY_BLOCK_ID       = "activity-block-id"
    ACTIVITY_CONFIG         = "activity-config"
    ACTIVITY_ID             = "activity-id"
    INPUT                   = "input"
    ACTIVITY_MODULE         = "activity-module"
    ACTIVITY_NAME           = "activity-name"
    ACTIVITY_TYPE           = "activity-type"
    CUSTOM_DATA             = "custom-data"
    FLOW_RUN_ID             = "flow-run-id"
    ADDITIONAL_EXTENSIONS   = "additional-extensions"







# Run modes for Autor
class Mode(Constant):
    # run an activity block
    ACTIVITY_BLOCK = "ACTIVITY_BLOCK"
    # run one specified activity using the activity block config.
    ACTIVITY_IN_BLOCK = "ACTIVITY_IN_BLOCK"
    # run the specified activity using a provided activity config.
    ACTIVITY = "ACTIVITY"
    # re-run the specified the activity block run from the specified activity
    ACTIVITY_BLOCK_RERUN = "ACTIVITY_BLOCK_RERUN"


# Exception types in Autor context @TODO - do we need it?
class ExceptionType(Constant):
    ACTIVITY_BLOCK_CALLBACK = "ACTIVITY_BLOCK_CALLBACK"
    ACTIVITY_RUN = "ACTIVITY_RUN"
    ACTIVITY_CONFIGURATION = "ACTIVITY_CONFIGURATION"
    ACTIVITY_CREATION = "ACTIVITY_CREATION"
    ACTIVITY_INPUT = "ACTIVITY_INPUT"
    ACTIVITY_OUTPUT = "ACTIVITY_OUTPUT"
    ACTIVITY_POSTPROCESS = "ACTIVITY_POSTPROCESS"
    EXTENSION = "EXTENSION"
    FLOW_CONFIGURATION = "FLOW_CONFIGURATION"
    SET_UP = "SET_UP"
    TEAR_DOWN = "TEAR_DOWN"
    ACTIVITY_BLOCK = "ACTIVITY_BLOCK"
    UNKNOWN = "UNKNOWN"
    AUTOR_INPUT_PARAMETERS = "AUTOR_INPUT_PARAMETERS"
    INTERNAL = "INTERNAL"

class ExceptionSource(Constant):
    AUTOR_INTERNAL = "AUTOR_INTERNAL",

    EXTENSION = "EXTENSION",
    ARGUMENT = "ARGUMENT",
    ACTIVITY = "ACTIVITY",
    ACTIVITY_CHAINING = "ACTIVITY_CHAINING", # Expected inputs not found
    FLOW_CONFIGURATION = "FLOW_CONFIGURATION",
    ENVIRONMENT = "ENVIRONMENT"


#domain - CI ENV
#cat - Autor_Framework, Autor_Activity_Definition, Autor_Activity_Execution, Autor_Arguments,  Autor_Configuration, Autor_Extension
#prob. cause
#identifier



# fmt: on
