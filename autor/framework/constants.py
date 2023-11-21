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

# fmt: off
class Constants():
    AUTOR_ENVIRONMENT_VARIABLE_PREFIX = "AUTOR_ARGUMENT_"
    DEBUG_LINE_LENGTH = 50

class ActivityGroupType:
    BEFORE_BLOCK = "BEFORE_BLOCK"                   # BBA
    BEFORE_ACTIVITY = "BEFORE_ACTIVITY"             # BA
    MAIN_ACTIVITY = "MAIN_ACTIVITY"                 # MA
    AFTER_ACTIVITY = "AFTER_ACTIVITY"               # AA
    AFTER_BLOCK = "AFTER_BLOCK"                     # ABA


class Status:
    SUCCESS = 'SUCCESS'
    FAIL = 'FAIL'
    ERROR = 'ERROR'
    SKIPPED = 'SKIPPED'
    ABORTED = 'ABORTED'
    UNKNOWN = 'UNKNOWN'
    ALL = 'ALL'


class Action():
    RUN = 'RUN'
    SKIP_BY_FRAMEWORK = "SKIP_BY_FRAMEWORK"
    SKIP_BY_CONFIGURATION = "SKIP_BY_CONFIGURATION"
    REUSE = 'REUSE'
    SKIP_WITH_OUTPUT_VALUES = 'SKIP_WITH_OUTPUT_VALUES'
    KEEP_AS_IS = 'KEEP_AS_IS'

# Type for SKIP status
class SkipType():
    SKIPPED_BY_FRAMEWORK = "SKIPPED_BY_FRAMEWORK"
    SKIPPED_BY_CONFIGURATION = "SKIPPED_BY_CONFIGURATION"
    SKIPPED_BY_ACTIVITY = "SKIPPED_BY_ACTIVITY"

class AbortType():
    ABORTED_BY_FRAMEWORK = "ABORTED_BY_FRAMEWORK"
    ABORTED_BY_ACTIVITY = "ABORTED_BY_ACTIVITY"


# Values used in configurations.
class Configuration():
    ANY = "_any"
    PREVIOUS = "_previous"
    LATEST = "_latest"


# Run modes for Autor
class Mode:
    # run an activity block
    ACTIVITY_BLOCK = "ACTIVITY_BLOCK"
    # run one specified activity using the activity block config.
    ACTIVITY_IN_BLOCK = "ACTIVITY_IN_BLOCK"
    # run the specified activity using a provided activity config.
    ACTIVITY = "ACTIVITY"
    # re-run the specified the activity block run from the specified activity
    ACTIVITY_BLOCK_RERUN = "ACTIVITY_BLOCK_RERUN"

# Exception types in Autor context @TODO - do we need it?
class ExceptionType:
    ACTIVITY_BLOCK_CALLBACK = "ACTIVITY_BLOCK_CALLBACK"
    ACTIVITY = "ACTIVITY"
    EXTENSION = "EXTENSION"
    FLOW_CONFIGURATION = "FLOW_CONFIGURATION"
    SET_UP = "SET_UP"
    TEAR_DOWN = "TEAR_DOWN"
    ACTIVITY_BLOCK = "ACTIVITY_BLOCK"


# fmt: on
