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

# The entry point to Autor
# Call run() to run Autor.

import importlib
import json
import logging
import os.path
import shutil
import uuid
from datetime import datetime
from typing import List, Dict

import yaml

from autor import Activity
from autor.flow_configuration.activity_configuration import ActivityConfiguration
from autor.flow_configuration.flow_configuration import FlowConfiguration
from autor.flow_configuration.flow_configuration_factory import (
    load_flow_configuration,
)
from autor.framework.activity_block_context import ActivityBlockContext
from autor.framework.activity_block_information import ActivityBlockInformation
from autor.framework.activity_block_rules import ActivityBlockRules
from autor.framework.activity_context import ActivityContext
#from autor.framework.activity_context import ActivityContext
from autor.framework.activity_data import ActivityData
from autor.framework.activity_information import ActivityInformation
from autor.framework.activity_property import ActivityProperty
from autor.framework.activity_property_information import ActivityPropertyInformation
from autor.framework.activity_runner import ActivityRunner
from autor.framework.autor_framework_activity_input_modifier import AutorFrameworkActivityInputModifier
from autor.framework.autor_framework_bootstrap import AutorFrameworkBootstrap
from autor.framework.autor_framework_exception import (
    AutorFrameworkException,
    AutorFrameworkValueException,
)
from autor.framework.check import Check
from autor.framework.constants import (
    AbortType,
    Action,
    ActivityGroupType,
    ExceptionType,
    Mode,
    Status, ContextPropertyPrefix, Inparam, Constants, NodeStatus, InterruptMode, PropertyCategory,
)
from autor.framework.context import Context
from autor.framework.context_properties_registry import ContextPropertiesRegistry
from autor.framework.debug_config import DebugConfig
from autor.framework.exception_handler import ExceptionHandler
from autor.framework.file_context import FileContext
from autor.framework.flags import Flags
from autor.framework.flow_context import FlowContext
from autor.framework.flow_information import FlowInformation
from autor.framework.graph import ActivityBlockGraph
from autor.framework.keys import FlowConfigurationKeys as cfg
from autor.framework.keys import FlowContextKeys as ctx
from autor.framework.keys import StateKeys as sta
from autor.framework.logging_config import LoggingConfig
from autor.framework.monitor import ActivityBlockMonitor
from autor.framework.node import Node
from autor.framework.state import State
from autor.framework.state_handler import StateHandler
from autor.framework.state_listener import StateListener
from autor.framework.state_print_extension import StatePrintExtension
from autor.framework.state_producer import StateProducer
from autor.framework.util import Util


# pylint: disable=no-self-use
class ActivityBlock(StateProducer):

    # pylint: disable=no-member

    def __init__(
            self,
            mode,
            additional_extensions: list = None,
            activity_block_id: str = None,
            activity_config: dict = None,  # mode: ACTIVITY
            activity_id: str = None,
            activity_ids: List = None,
            input: dict = None,  # mode: ACTIVITY
            activity_module: str = None,  # mode: ACTIVITY
            activity_name: str = None,
            activity_names: List = None,
            activity_type: str = None,  # mode: ACTIVITY
            custom_data: dict = None,
            flags: dict = None,
            flow_run_id: str = None,
            flow_config_path: str = None
    ):

        # region -------------- Debug functionality region --------------
        # -------------------------- debug START -----------------------------------#
        try:
            # Build inputs string that is used for creating a file name where the context is saved for the purpose of
            # creating test cases for Autor Framework. This is not used for Autor functionality.
            # Note that MODE will not be a part of this string.
            self._debug_input_str: str = ""
            self._debug_separator: str = "___"

            frame = inspect.currentframe()
            args, _, _, values = inspect.getargvalues(frame)
            self._create_debug_input_string(args, values)

        except Exception as ex:
            # Store the problem information, but don't interrupt Autor.
            descr = "Could not create a debug string used for test case creation support. This error can be ignored."
            ExceptionHandler.register_exception(ex=ex, description=descr, ex_type=ExceptionType.INTERNAL)
        # -------------------------- debug END -----------------------------------#
        # endregion

        """
        Autor constructor lists all autor attributes and initiates
        the ones that con be initiated.

        The following attributes can be overriden in state BOOTSTRAP:
        - self._flow_config_path
        - self._activity_block_id
        - self._flow_run_id
        - self._activity_name_special

        The following attributes are initiated after state BOOTSTRAP as they can be affected by values set in BOOTSTRAP:
        - self._mode
        - self._flow_id
        - self._flow_config
        - self._flow_context_id
        - self._flow_context
        - self._activity_block_id
        - self._activity_block_context
        """

        # fmt: off
        string = r"""

          _    _ _______ ____  _____
     /\  | |  | |__   __/ __ \|  __ \
    /  \ | |  | |  | | | |  | | |__) |
   / /\ \| |  | |  | | | |  | |  _  /
  / ____ \ |__| |  | | | |__| | | \ \
 /_/    \_\____/   |_|  \____/|_|  \_\


        """
        logging.info(f'{DebugConfig.autor_info_prefix}{string}')

        # Make sure no None values exist for collections.
        if additional_extensions is None:
            additional_extensions = []
        if activity_config is None:
            activity_config = {}
        if input is None:
            input = {}
        if custom_data is None:
            custom_data = {}
        if flags is None:
            flags = {}
        if activity_names is None:
            activity_names = []
        if activity_ids is None:
            activity_ids = []

        # Check that the expected values are correct
        Check.is_true(Mode.is_valid(mode),
                      msg=f'Unknown mode: {mode}. The valid modes are: {Mode.get_valid_constants(Mode)}')

        self._flags = flags
        self._concurrent_interrupt_mode = InterruptMode.INTERRUPT_ALL_ACTIVITIES

        #------------------------- mode: ACTIVITY ------------------------------#
        self._activity_module: str = activity_module  # mode: ACTIVITY
        self._activity_type: str = activity_type  # mode: ACTIVITY
        self._input: dict = input  # mode: ACTIVITY
        self._activity_config: dict = activity_config  # mode: ACTIVITY
        # ------------------------- mode: ACTIVITY ------------------------------#

        # Extension classes that should be added to the extensions
        # provided in the flow configuration.
        # These additional extensions will be able to get on_bootstrap()
        # callbacks, that is not available for the extensions provided
        # through flow configuration.
        self._additional_extensions: list = additional_extensions

        # After each run Autor adds 'skip-with-outputs' configuration to the flow
        # configuration. The attribute holds the URL to the updated configuration.
        self._skip_with_outputs_flow_configuration_url = None

        # Any data that the user of Autor would like to provide for
        # extensions.
        self._custom_data: dict = custom_data

        # True, if the activity block has been aborted by the framework
        self._autor_aborted = False
        self._autor_aborted_reason = ""

        # The name of the activity that should be treated in a special manner.
        # How it should be treated depends on Autor mode.
        # Note that self._activity_name_special is never used for decision-making. For
        # decisions the name is first converted into self._activity_id_special to make
        # sure that we have a unique activity occurrence within the activity block (as an activity
        # can be a before/after activity etc).
        self._activity_name_special = activity_name  # Can be overriden by extensions in state BOOTSTRAP
        self._activity_names_special = activity_names

        # The id of the activity that should be treated in a special manner.
        # How it should be treated depends on Autor mode.
        self._activity_id_special = activity_id  # Can be overriden by extensions in state BOOTSTRAP
        self._activity_ids_special = activity_ids

        # Autor mode - Initiated after state BOOTSTRAP
        #
        # 1. ACTIVITY_BLOCK
        #    Runs all activities in the specified activity block.
        #
        # 2. ACTIVITY_IN_BLOCK
        #    Runs the specified activity inside the specified activity block.
        #
        # 3. ACTIVITY
        #    Runs the specified activity with the provided activity
        #       configuration (and context).
        #
        self._mode = mode

        # ----------------------------------  F L O W   D A T A  -----------------------------------#

        # Attributes that may be OVERRIDEN in state BOOTSTRAP
        self._flow_run_id = flow_run_id
        self._flow_config_path = flow_config_path
        self._flow_run_id_generated = False  # Will be set to true if Autor will generate the flow_run_id

        # Attributes that are INITIATED after state BOOTSTRAP
        self._flow_id = None  # Unique identifier of the flow provided by flow configuration.
        self._flow_context_id = None  # Unique identifier of a context for a flow run.
        self._flow_config: FlowConfiguration = None  # The configuration object representing the whole flow.
        self._flow_context: Context = None  # Context, focused on the root (flow) level.

        # ------------------------------  A C T I V I T Y   B L O C K   D A T A   -----------------#

        self._activity_block_run_id = None
        self._activity_block_activities: List[
            Activity] = []  # A list of activities that is created as the activities are run.
        self._activity_block_activities_data: List[
            ActivityData] = []  # A list of activity data that is created as the activities are run.
        self._activity_block_activities_id: List[
            str] = []  # A list of activity ids that is created as the activities are run.
        self._activity_block_callback_exceptions = []  # [dict{str:str}] Exceptions in activity block callbacks.
        self._activity_block_status = Status.UNKNOWN  # Current status of the activity block. Updated as the activities are run or from context
        self._activity_block_latest_activity = None  # The latest activity that has been run (or skipped) in the activity block.
        # Set to true when the activity-block is considered to be interrupted
        #  (== before or main activities interrupted)
        self._activity_block_interrupted = False

        self._activity_block_config = None
        self._activity_block_configs_main_activities = None
        self._activity_block_configs_before_block = None
        self._activity_block_configs_after_block = None
        self._activity_block_configs_before_activity = None
        self._activity_block_configs_after_activity = None

        self._before_block_activities = []
        #self._before_activities = []  # Reset for each main-loop iteration
        self._main_activities = []
        #self._after_activities = []
        self._after_block_activities = []
        self._activities_by_name = {}
        self._activities_by_unique_name = {}  # BeforeActivities and AfterActivities are prefixed with the MainActivity.

        # Keep track of the configuration for the next main activity.
        self._next_main_index = 0

        # Attributes that may be OVERRIDEN in state BOOTSTRAP
        self._activity_block_id = activity_block_id

        # Attributes that are INITIATED after state BOOTSTRAP
        self._activity_block_context: Context = None  # Empty context focused on the activity block level

        # List of strings where each line is a summary of an outcome of one activity run.
        # Used only for logging purposes.
        self._activity_block_run_summary: List[str] = []

        # Counters used for generating unique activity ids
        self._bb_counter = 0
        self._ba_counter = 0
        self._ma_counter = 0
        self._aa_counter = 0
        self._ab_counter = 0

        self._rules = ActivityBlockRules()

        # Concurrency-safe area.
        self._monitor: ActivityBlockMonitor = None

        # Context from the latest run. Used for extracting activity
        # results in case of REUSE.
        self._rerun_context_dict: dict = None

        # ---------------------------------  A C T I V I T Y   D A T A   --------------------------#
        self._activity_data: ActivityData = None  # Contains activity data and the activity instance

        # Activity ID. Needed for handling activity order during re-run.
        # Activities that do not generate output are activities with status ERROR or SKIPPED_BY_FRAMEWORK or SKIPPED_BY_CONFIGURATION.
        # Status is not considered as an output.
        self._latest_activity_that_finished_running: str = None

        self._graph: ActivityBlockGraph = None

        #---------------------------------- DEBUGGING SUPPORT -------------------------------------#
        # This value will be added to the state data for the extensions to play around with.
        # Key: DBG_EXTENSION_TEST_STR
        self._dbg_extension_test_str = ""

        # Nodes listed in the order that they started running. For writing concurrency tests.
        self._nodes_started_order: List[Node] = []

        # Nodes listed in the order that they finished running. For writing concurrency tests.
        self._nodes_finished_order: List[Node] = []

        # fmt: on

    def run(self) -> dict:

        try:
            LoggingConfig.activate_framework_logging()
            self._set_up()
            self._run()
            #ActivityRegistry.reset_static_data()
            #ContextPropertiesRegistry.reset_static_data()
            self._tear_down()

        except Exception as e:
            self._abort_and_register_exception(e, "Unhandled exception in Autor", ex_type=ExceptionType.UNKNOWN)

        finally:
            if self._autor_aborted:
                logging.error("\n%s", Util.format_banner("A U T O R   A B O R T E D"))
                logging.error(f"Reason: {self._autor_aborted_reason}")

            logging.info(f'{DebugConfig.autor_info_prefix}Activity block status: {self._activity_block_status}')

            # Print all exceptions that occurred during the run
            ExceptionHandler.print_all_exceptions()
            LoggingConfig.activate_external_logging()  # If any other calls are made to autor these logs should be distinguishable

    def _set_up(self):
        try:
            # In cases when Autor is run several times within the same process
            # the static data needs to be reset. Can be a case during testing Autor.
            ActivityBlockRules.reset_static_data()
            Context.reset_static_data()
            Flags.reset_static_data()
            ExceptionHandler.debug_reset()
            StateHandler.reset_static_data()
            #self._activity_data = None

            Flags.set_flags(self._flags)

            Context.remote_context = FileContext()  # Default is to use file DB locally. Can be overridden in extensions.

            if DebugConfig.print_autor_info:
                self._print_input_args_before_bootstrap()

            # Register extensions that were provided through arguments or that
            # are needed internally in Autor framework.
            self._register_bootstrap_extensions(self._additional_extensions)

            StateHandler.add_state_producer(self)
            # ---------------------------------------------------------------#
            StateHandler.change_state(State.BOOTSTRAP)
            # ---------------------------------------------------------------#

            # Inputs finalized from user perspective -> perform internal trim
            self._check_and_trim_inputs()

            if DebugConfig.print_final_input or DebugConfig.print_autor_info:
                self._print_input_args_after_bootstrap()

            # Initiate attributes that may be affected by changes done in
            # state BOOTSTRAP.
            #self._initiate_autor_mode()
            self._initiate_flow()
            self._initiate_context()

            # Create extension classes from configuration
            self._register_extensions_from_flow_configuration(self._flow_config)

            # Load activity classes and make them discoverable.
            self._load_activity_modules(self._flow_config)

            # ---------------------------------------------------------------#
            StateHandler.change_state(State.FRAMEWORK_START)
            # ---------------------------------------------------------------#
            self._flow_context.sync_remote()

            # If this activity block is being run for the first time within this flow run
            # (no snapshot of the initial state of the activity block run has been saved)
            # then create and save a snapshot of the context. This can be later used for
            # re-runs.
            context_key = "_initialContextSnapshot"
            initial_context_snapshot: dict = self._activity_block_context.get(key=context_key, default=None, search=False)
            if initial_context_snapshot is None:
                initial_context_snapshot: dict = Context.get_context_dict_copy()
                self._activity_block_context.set(key=context_key, value=initial_context_snapshot)
                #logging.warning("Saved initial context.")
            else:
                #logging.warning("Initial context found.")
                pass

            if self._mode == Mode.ACTIVITY_BLOCK_RERUN:
                # Save the context from the previous run. Will be used to extract parameters to reuse.
                self._rerun_context_dict = Context.get_context_dict_copy()
                # Reset the official context to the initial snapshot.
                Context.set_context(initial_context_snapshot)
                # Make sure to save the initial snapshot again.
                initial_context_snapshot: dict = Context.get_context_dict_copy()
                self._activity_block_context.set(key=context_key, value=initial_context_snapshot)

                logging.warning("Mode ACTIVITY-BLOCK-RERUN -> resetting context to initial snapshot")

            self._add_additional_context()

            # ---------------------------------------------------------------#
            StateHandler.change_state(State.CONTEXT_SYNCHRONIZED)
            # ---------------------------------------------------------------#

            if self._mode == Mode.ACTIVITY:
                self._flow_config = load_flow_configuration(self._flow_config_path)
                self._activity_block_context = Context(activity_block=self._activity_block_id)

            #self._create_activities_configurations()
            self._activity_block_context.set(ctx.MODE, self._mode)


        except Exception as e:
            self._abort_and_register_exception(e, "Unhandled exception during Autor set up",
                                               ex_type=ExceptionType.SET_UP)

    def _confirm_mode(self, val):
        Check.is_autor_mode(val, exception_type=ValueError)

    def _confirm_generated_activity_block_id(self, val):
        Check.is_true(val == Constants.AUTOGEN_ACTIVITY_BLOCK_ID, exception_type=ValueError,
                      msg=f"In mode: {self._mode} the only allowed activity block id is: {Constants.AUTOGEN_ACTIVITY_BLOCK_ID}. This value is generated internally by Autor and need not be provided.")

    def _confirm_string(self, name: str, val):
        Check.is_non_empty_string(val, exception_type=ValueError, msg=f"Mandatory parameter '{name}' not provided.")

    def _confirm_generated_flow_configuration_name(self, val):
        Check.is_true(val == Constants.GENERATED_FLOW_CONFIG_PATH, exception_type=ValueError,
                      msg=f"In mode: {self._mode} the only allowed flow configuration url is: {Constants.GENERATED_FLOW_CONFIG_PATH}. This value is generated internally by Autor and need not be provided.")

    def _assure_absence(self, name: str, val):
        Check.is_none_or_empty(val, exception_type=ValueError,
                               msg=f"Parameter '{name}' must not be provided in mode: {self._mode}")

    def _check_mode_ACTIVITY_BLOCK_params(self, params: dict):
        all_possible_params = Inparam.get_valid_constants(Inparam)
        for name in all_possible_params:
            val = params[name]
            if name == Inparam.MODE:  # Mandatory
                self._confirm_mode(val)
            elif name == Inparam.ACTIVITY_BLOCK_ID:  # Mandatory
                self._confirm_string(name, val)
            elif name == Inparam.ACTIVITY_CONFIG:  # No
                self._assure_absence(name, val)
            elif name == Inparam.ACTIVITY_ID:  # No
                self._assure_absence(name, val)
            elif name == Inparam.ACTIVITY_IDS:  # No
                self._assure_absence(name, val)
            elif name == Inparam.INPUT:  # Optional
                pass
            elif name == Inparam.ACTIVITY_MODULE:  # No
                self._assure_absence(name, val)
            elif name == Inparam.ACTIVITY_NAME:  # No
                self._assure_absence(name, val)
            elif name == Inparam.ACTIVITY_NAMES:  # No
                self._assure_absence(name, val)
            elif name == Inparam.ACTIVITY_TYPE:  # No
                self._assure_absence(name, val)
            elif name == Inparam.CUSTOM_DATA:  # Optional (advanced usage)
                pass
            elif name == Inparam.FLOW_RUN_ID:  # Optional
                pass
            elif name == Inparam.FLOW_CONFIG_PATH:  # Mandatory
                self._confirm_string(name, val)
            elif name == Inparam.ADDITIONAL_EXTENSIONS:  # Optional (advanced usage)
                pass
            else:
                raise AutorFrameworkException(
                    f"Internal error: Unhandled parameter name: {name} -> add to implementation!")

    def _check_mode_ACTIVITY_IN_BLOCK_params(self, params: dict):
        all_possible_params = Inparam.get_valid_constants(Inparam)

        activity_id_value: str = None
        activity_name_value: str = None

        for name in all_possible_params:
            val = params[name]
            if name == Inparam.MODE:  # Mandatory
                self._confirm_mode(val)
            elif name == Inparam.ACTIVITY_BLOCK_ID:  # Mandatory
                self._confirm_string(name, val)
            elif name == Inparam.ACTIVITY_CONFIG:  # No
                self._assure_absence(name, val)
            elif name == Inparam.ACTIVITY_NAME:  # Mandatory within group
                activity_name_value = val
            elif name == Inparam.ACTIVITY_NAMES:  # No
                self._assure_absence(name, val)
            elif name == Inparam.ACTIVITY_ID:  # Mandatory within group
                activity_id_value = val
            elif name == Inparam.ACTIVITY_IDS:  # No
                self._assure_absence(name, val)
            elif name == Inparam.INPUT:  # Optional
                pass
            elif name == Inparam.ACTIVITY_MODULE:  # No
                self._assure_absence(name, val)
            elif name == Inparam.ACTIVITY_TYPE:  # No
                self._assure_absence(name, val)
            elif name == Inparam.CUSTOM_DATA:  # Optional (advanced usage)
                pass
            elif name == Inparam.FLOW_RUN_ID:  # Optional
                pass
            elif name == Inparam.FLOW_CONFIG_PATH:  # Mandatory
                self._confirm_string(name, val)
            elif name == Inparam.ADDITIONAL_EXTENSIONS:  # Optional (advanced usage)
                pass
            else:
                raise AutorFrameworkException(
                    f"Internal error: Unhandled parameter name: {name} -> add to implementation!")

        # Checking mandatory within group values
        self._confirm_activity_name_or_id(id=activity_id_value, name=activity_name_value)

    def _check_mode_ACTIVITY_BLOCK_RERUN_params(self, params: dict):
        all_possible_params = Inparam.get_valid_constants(Inparam)
        activity_id_value: str = None
        activity_id_values: str = None
        activity_name_value: str = None
        activity_name_values: str = None

        for name in all_possible_params:
            val = params[name]
            if name == Inparam.MODE:  # Mandatory
                self._confirm_mode(val)
            elif name == Inparam.ACTIVITY_BLOCK_ID:  # Mandatory
                self._confirm_string(name, val)
            elif name == Inparam.ACTIVITY_CONFIG:  # No
                self._assure_absence(name, val)
            elif name == Inparam.ACTIVITY_NAME:  # Mandatory within group
                activity_name_value = val
            elif name == Inparam.ACTIVITY_NAMES:  # Mandatory within group
                activity_name_values = val
            elif name == Inparam.ACTIVITY_ID:  # Mandatory within group
                activity_id_value = val
            elif name == Inparam.ACTIVITY_IDS:  # Mandatory within group
                activity_id_values = val
            elif name == Inparam.INPUT:  # Optional
                pass
            elif name == Inparam.ACTIVITY_MODULE:  # No
                self._assure_absence(name, val)
            elif name == Inparam.ACTIVITY_TYPE:  # No
                self._assure_absence(name, val)
            elif name == Inparam.CUSTOM_DATA:  # Optional (advanced usage)
                pass
            elif name == Inparam.FLOW_RUN_ID:  # Mandatory
                self._confirm_string(name, val)
            elif name == Inparam.FLOW_CONFIG_PATH:  # Mandatory
                self._confirm_string(name, val)
            elif name == Inparam.ADDITIONAL_EXTENSIONS:  # Optional (advanced usage)
                pass
            else:
                raise AutorFrameworkException(
                    f"Internal error: Unhandled parameter name: {name} -> add to implementation!")

        # Checking mandatory within group values
        self._confirm_activity_names_or_ids(name=activity_name_value, names=activity_name_values, id=activity_id_value,
                                            ids=activity_id_values)

    def _check_mode_ACTIVITY_params(self, params: dict):

        all_possible_params = Inparam.get_valid_constants(Inparam)

        for name in all_possible_params:
            val = params[name]
            if name == Inparam.MODE:  # Mandatory
                self._confirm_mode(val)
            elif name == Inparam.ACTIVITY_BLOCK_ID:  # No. Generated by Autor later after Context sync.
                self._assure_absence(name, val)
            elif name == Inparam.ACTIVITY_CONFIG:  # Optional
                pass
            elif name == Inparam.INPUT:  # Optional
                pass
            elif name == Inparam.ACTIVITY_MODULE:  # Mandatory
                self._confirm_string(name, val)
            elif name == Inparam.ACTIVITY_NAME:  # No
                self._assure_absence(name, val)
            elif name == Inparam.ACTIVITY_NAMES:  # No
                self._assure_absence(name, val)
            elif name == Inparam.ACTIVITY_ID:  # No
                self._assure_absence(name, val)
            elif name == Inparam.ACTIVITY_IDS:  # No
                self._assure_absence(name, val)
            elif name == Inparam.ACTIVITY_TYPE:  # Mandatory
                self._confirm_string(name, val)
            elif name == Inparam.CUSTOM_DATA:  # Optional (advanced usage)
                pass
            elif name == Inparam.FLOW_RUN_ID:  # Optional
                pass
            elif name == Inparam.FLOW_CONFIG_PATH:  # Generated by Autor
                self._confirm_generated_flow_configuration_name(val)
            elif name == Inparam.ADDITIONAL_EXTENSIONS:  # Optional (advanced usage)
                pass
            else:
                raise AutorFrameworkException(
                    f"Internal error: Unhandled parameter name: {name} -> add to implementation!")

    def _confirm_activity_names_or_ids(self, name: str, names: List, id: str, ids: List):
        valid_name = Util.is_non_empty_string(name)
        valid_id = Util.is_non_empty_string(id)

        valid_names = True
        valid_ids = True
        for n in names:
            valid_names = valid_names and Util.is_non_empty_string(n)
        for i in ids:
            valid_ids = valid_ids and Util.is_non_empty_string(i)

        if valid_names and valid_name:
            if name not in names:  # ok to have both name and names as long as the name is contained in names.
                logging.warning(
                    f"{DebugConfig.autor_info_prefix}Both {Inparam.ACTIVITY_NAMES} and {Inparam.ACTIVITY_NAME} were provided. Autor will ignore {Inparam.ACTIVITY_NAME}:{name} and use {Inparam.ACTIVITY_NAMES} {' '.join(names)}")

        if valid_ids and valid_id:
            if id not in ids:  # ok to have both id and ids as long the id is contained in ids.
                logging.warning(
                    f"{DebugConfig.autor_info_prefix}Both {Inparam.ACTIVITY_IDS} and {Inparam.ACTIVITY_ID} were provided. Autor will ignore {Inparam.ACTIVITY_ID}:{id} and use {Inparam.ACTIVITY_IDS} {' '.join(ids)}")

        elif not valid_names and not valid_ids and not valid_name and not valid_id:
            raise ValueError(
                f"Parameter not found. Expected either: {Inparam.ACTIVITY_IDS} or {Inparam.ACTIVITY_NAMES} or {Inparam.ACTIVITY_ID} or {Inparam.ACTIVITY_NAME}")

    def _confirm_activity_name_or_id(self, name: str, id: str):
        valid_name = Util.is_non_empty_string(name)
        valid_id = Util.is_non_empty_string(id)
        if valid_name and valid_id:
            logging.warning(
                f"{DebugConfig.autor_info_prefix}Found both {Inparam.ACTIVITY_ID} and {Inparam.ACTIVITY_NAME}, whereas only one of them should be provided.")

            if not id.endswith(name):
                raise ValueError(
                    f"The provided values are not compatible: {Inparam.ACTIVITY_ID}={id} and {Inparam.ACTIVITY_NAME}={name}. Provide only one of them.")

        elif not valid_name and not valid_id:
            raise ValueError(f"Parameter not found. Expected either: {Inparam.ACTIVITY_ID} or {Inparam.ACTIVITY_NAME}.")

    def _check_and_trim_inputs(self):

        # Create a temporary dict for parameter validation. The dict contains
        # pairs (parameter,checked:bool)
        params: dict = {}
        params[Inparam.MODE] = self._mode
        params[Inparam.ACTIVITY_BLOCK_ID] = self._activity_block_id
        params[Inparam.FLOW_CONFIG_PATH] = self._flow_config_path
        params[Inparam.FLOW_RUN_ID] = self._flow_run_id
        params[Inparam.ACTIVITY_CONFIG] = self._activity_config
        params[Inparam.ACTIVITY_MODULE] = self._activity_module
        params[Inparam.ACTIVITY_NAME] = self._activity_name_special
        params[Inparam.ACTIVITY_NAMES] = self._activity_names_special
        params[Inparam.ACTIVITY_ID] = self._activity_id_special
        params[Inparam.ACTIVITY_IDS] = self._activity_ids_special
        params[Inparam.ACTIVITY_TYPE] = self._activity_type
        params[Inparam.INPUT] = self._input
        params[Inparam.CUSTOM_DATA] = self._custom_data
        params[Inparam.ADDITIONAL_EXTENSIONS] = self._additional_extensions

        if self._mode == Mode.ACTIVITY_BLOCK:
            self._check_mode_ACTIVITY_BLOCK_params(params)
        elif self._mode == Mode.ACTIVITY_IN_BLOCK:
            self._check_mode_ACTIVITY_IN_BLOCK_params(params)
        elif self._mode == Mode.ACTIVITY:
            self._check_mode_ACTIVITY_params(params)
        elif self._mode == Mode.ACTIVITY_BLOCK_RERUN:
            self._check_mode_ACTIVITY_BLOCK_RERUN_params(params)
        else:
            raise ValueError(f"Unknown mode: {self._mode}.")

        # self._activity_name_special is always provided by users as an input parameter, but in Autor we only use self._activity_id_special,
        # so we need to be able to create self._activity_id_special if self._activity_name_special has been provided.
        if self._activity_name_special is not None and self._activity_id_special is None:
            Check.is_non_empty_string(self._activity_block_id,
                                      msg=f"Missing activity_block_id. Cannot create special activity-id from special activity name: {self._activity_name_special}.")
            self._activity_id_special = f"{self._activity_block_id}-{self._activity_name_special}"

        if len(self._activity_names_special) > 0 and len(self._activity_ids_special) == 0:
            Check.is_non_empty_string(self._activity_block_id,
                                      msg=f"Missing activity_block_id. Cannot create special activity-ids from special activity names: {','.join(self._activity_names_special)}.")
            for name in self._activity_names_special:
                self._activity_ids_special.append(f"{self._activity_block_id}-{name}")

        if len(self._activity_names_special) == 0:
            if self._activity_name_special is not None:
                self._activity_names_special.append(self._activity_name_special)

        if len(self._activity_ids_special) == 0:
            if self._activity_id_special is not None:
                self._activity_ids_special.append(self._activity_id_special)

    def _add_additional_context(self):
        for key, val in self._input.items():
            self._activity_block_context.set(key, val)

    def _run(self):
        if self._autor_aborted:
            logging.info("Autor aborted -> not running any activities")
            return

        # Run activities
        try:
            # ---------------------------------------------------------------#
            StateHandler.change_state(State.BEFORE_ACTIVITY_BLOCK)
            # ---------------------------------------------------------------#
            if DebugConfig.print_activity_block_started_inputs_summary:
                self._print_activity_block_started()
            if DebugConfig.print_context_before_activities_are_run:
                self._flow_context.print_context("Context before activities are run")

            self._run_activity_block()


        except Exception as e:
            self._abort_and_register_exception(e, "Unhandled exception during activity block execution",
                                               ex_type=ExceptionType.ACTIVITY_BLOCK)

        # Run callbacks
        try:
            # ---------------------------------------------------------------#
            StateHandler.change_state(State.BEFORE_ACTIVITY_BLOCK_CALLBACKS)
            # ---------------------------------------------------------------#
            self._run_activity_block_callbacks()
        except Exception as e:
            self._abort_and_register_exception(e, "Unhandled exception during activity block callbacks execution",
                                               ex_type=ExceptionType.ACTIVITY_BLOCK)

        # Finalize activity block run
        try:
            # ---------------------------------------------------------------#
            StateHandler.change_state(State.AFTER_ACTIVITY_BLOCK)
            # ---------------------------------------------------------------#
            self._activity_block_context.set(ctx.ACTIVITY_BLOCK_STATUS, self._activity_block_status)
            #self._activity_block_context.set(ctx.ACTIVITY_BLOCK_INTERRUPTED, self._activity_block_interrupted)

            if len(self._activity_block_callback_exceptions) > 0:
                self._activity_block_context.set(ctx.CALLBACK_EXCEPTIONS, self._activity_block_callback_exceptions)
            self._flow_context.sync_remote()

            if DebugConfig.print_context_on_finished:
                self._flow_context.print_context("Context at the end of the activity block run")

        except Exception as e:
            self._abort_and_register_exception(e, "Unhandled exception during activity block finalization",
                                               ex_type=ExceptionType.ACTIVITY_BLOCK)
        file_name = "<filename not assigned>"
        try:
            # Print output from Activity Block
            self._print_output_to_file("autor-output")  # prints json and yml
        except Exception as e:
            self._abort_and_register_exception(e,
                                               f"Unhandled exception when trying to write activity block output to file:{file_name}.",
                                               ex_type=ExceptionType.ACTIVITY_BLOCK)


        finally:
            if DebugConfig.create_skip_with_output_flow_config:
                self._dbg_save_skip_with_outputs_flow_config()  # creates a flow config with skip configuration with results from the current run.
            if DebugConfig.print_activity_block_finished_summary:
                self._dbg_print_activity_block_finished()
                Util.print_header(DebugConfig.autor_info_prefix,
                                  'A C T I V I T Y   B L O C K   R U N   S U M M A R Y (started order)', level='info',
                                  line_below=False)

                logging.info(DebugConfig.autor_info_prefix)
                started_order_activity_ids = []
                for n in self._nodes_started_order:
                    started_order_activity_ids.append(n.activity_id)
                ActivityBlockRules.get_transition_summary().print(DebugConfig.autor_info_prefix,
                                                                  print_in_activity_order=started_order_activity_ids)

                Util.print_header(DebugConfig.autor_info_prefix,
                                  'A C T I V I T Y   B L O C K   R U N   S U M M A R Y (finished order)', level='info',
                                  line_below=False)
                logging.info(DebugConfig.autor_info_prefix)
                finished_order_activity_ids = []
                for n in self._nodes_finished_order:
                    finished_order_activity_ids.append(n.activity_id)

                ActivityBlockRules.get_transition_summary().print(DebugConfig.autor_info_prefix,
                                                                  print_in_activity_order=finished_order_activity_ids)
            if DebugConfig.save_activity_block_context_locally:  # can be used for test cases
                self._dbg_save_context()

            if Flags.print_activity_started_and_finished_order:
                self._print_activities_started_and_finished_order()

    def _print_activities_started_and_finished_order(self):
        Util.print_header(DebugConfig.autor_info_prefix, 'Activities started order',
                          level='info', line_below=False)
        i = 0
        for n in self._nodes_started_order:
            i = i + 1
            logging.info(f'{DebugConfig.autor_info_prefix}{i}. {n.activity_id}')

        Util.print_header(DebugConfig.autor_info_prefix, 'Activities finished order',
                          level='info', line_below=False)
        i = 0
        for n in self._nodes_finished_order:
            i = i + 1
            logging.info(f'{DebugConfig.autor_info_prefix}{i}. {n.activity_id}')

        # Print as python code for copy-pasting into tests.
        print("activities_started_order:List[str] = []")
        for n in self._nodes_started_order:
            print(f'activities_started_order.append("{n.activity_id}")')
        print("activities_finished_order:List[str] = []")
        for n in self._nodes_finished_order:
            print(f'activities_finished_order.append("{n.activity_id}")')

    def _print_output_to_file(self, file_name):
        output: dict = {}
        output["mode"] = self._mode
        output["flow_run_id"] = self._flow_run_id
        output["activity_block_id"] = self._activity_block_id
        output["activity_block_status"] = self._activity_block_status

        # If we have a special activity run and Autor has not aborted, add the
        # special activity data to the output.
        if not self._autor_aborted:
            activities: List = []
            output["activities"] = activities

            for data in self._activity_block_activities_data:
                activity = {}
                activities.append(activity)
                activity["activity_id"] = data.activity_id
                activity["activity_name"] = data.activity_name
                activity["activity_outputs"] = {}

                #properties: dict = data.activity_context.get(ContextPropertyPrefix.props)
                properties: dict = data.output_context.get(ContextPropertyPrefix.props)

                for (key, val) in properties.items():
                    if key.startswith(ContextPropertyPrefix.out_provide):
                        prop_name = key[len(ContextPropertyPrefix.out_provide):]
                        activity["activity_outputs"][prop_name] = val

        # datetime object containing current date and time
        now = str(datetime.now())
        now = now.replace(' ', '_')
        now = now.replace('.', '_')
        now = now.replace(':', '_')

        if Flags.print_activity_started_and_finished_order:
            output['activities_started_order'] = []
            for n in self._nodes_started_order:
                output['activities_started_order'].append(n.activity_id)

            output['activities_finished_order'] = []
            for n in self._nodes_finished_order:
                output['activities_finished_order'].append(n.activity_id)

        #shutil.rmtree('output', ignore_errors=True)
        dir_name = 'output'
        if not os.path.exists(dir_name):
            os.mkdir(dir_name)

        file_path_json = os.path.join(dir_name, f"{file_name}_{now}.json")
        file_path_yaml = os.path.join(dir_name, f"{file_name}_{now}.yml")

        #Util.json_to_file(output, f"{file_name}_{now}.json")
        Util.json_to_file(output, file_path_json)

        #with open( f"{file_name}_{now}.yml", 'w') as outfile:
        with open(file_path_yaml, 'w') as outfile:
            yaml.dump(output, outfile, default_flow_style=False, sort_keys=False)

    def _dbg_save_context(self):

        context: dict = Context.get_context_dict()

        if self._mode == Mode.ACTIVITY:
            self._debug_input_str = self._debug_input_str.replace("ACTIVITY___",
                                                                  f"ACTIVITY___{self._activity_block_id}___")

        filename_unmodified = f'{self._mode}_{self._activity_block_id}_{self._activity_block_status}_unmodified.json'
        filename_generic_ab1 = f'{self._mode}_{self._activity_block_id}_{self._activity_block_status}_uc.json'
        filename_generic_ab = f'{self._debug_input_str}{self._debug_separator}{self._activity_block_status}.json'
        filename_generic_ab = filename_generic_ab.replace('/', '.')
        filename_generic_ab = filename_generic_ab.replace('\\', '.')
        filename_generic_ab = filename_generic_ab.replace(',', '_')
        filename_generic_ab = filename_generic_ab.replace(" ", "")
        filename_generic_ab = filename_generic_ab.replace("'", "")
        filename_generic_ab = filename_generic_ab.replace("{", "")
        filename_generic_ab = filename_generic_ab.replace("}", "")
        filename_generic_ab = filename_generic_ab.replace("[", "")
        filename_generic_ab = filename_generic_ab.replace("]", "")
        filename_generic_ab = filename_generic_ab.replace(":", "=")

        shutil.rmtree('context', ignore_errors=True)
        #if not os.path.exists('context'):
        os.mkdir('context')

        path_unmodified = os.path.join('context', filename_unmodified)
        path_generic_ab1 = os.path.join('context', filename_generic_ab1)
        path_generic_ab = os.path.join('context', filename_generic_ab)

        with open(path_unmodified, 'w', encoding='utf-8') as f:
            json.dump(context, f, ensure_ascii=False, indent=4)

        del context[ctx.ACTIVITY_BLOCK_RUN_ID]
        del context[ctx.FLOW_RUN_ID]

        activity_blocks: dict = context['_activityBlocks']

        current_ab = activity_blocks[self._activity_block_id]
        del context['_activityBlocks']

        context['_activityBlocks'] = {}
        context['_activityBlocks'][self._activity_block_id] = current_ab
        del current_ab[ctx.ACTIVITY_BLOCK_RUN_ID]

        #for ab_id, ab in activity_blocks.items():
        #del ab[ctx.ACTIVITY_BLOCK_RUN_ID]

        #ab = context['_activityBlocks'][self._activity_block_id]
        #del ab[ctx.ACTIVITY_BLOCK_RUN_ID]
        with open(path_generic_ab, 'w', encoding='utf-8') as f:
            json.dump(context, f, ensure_ascii=False, indent=4)

        with open(path_generic_ab1, 'w', encoding='utf-8') as f:
            json.dump(context, f, ensure_ascii=False, indent=4)

    def _dbg_save_skip_with_outputs_flow_config(self):
        # Skip-with-outputs data has already been added to flow
        # configuration. We only need to save the configuration
        # to a file.
        config = self._flow_config.get_raw_configuration()

        now_str = Util.get_datetime_str()

        file_name = f"skip-with-outputs-flow-config-{now_str}.yml"
        if not os.path.exists('skip_with_outputs'):
            os.mkdir('skip_with_outputs')

        path = os.path.join('skip_with_outputs', file_name)
        self._skip_with_outputs_flow_configuration_url = path  # save

        with open(path, 'w') as outfile:
            yaml.dump(config, outfile, default_flow_style=False, sort_keys=False)

    def _tear_down(self):

        # Remove all listeners
        try:
            # ---------------------------------------------------------------#
            StateHandler.change_state(State.FRAMEWORK_END)
            # ---------------------------------------------------------------#
            StateHandler().remove_all_listeners()
            # logging.info(f"FLOW ID: {self._flow_id}")

        except Exception as e:
            self._abort_and_register_exception(e, "Unhandled exception during Autor tear down",
                                               ex_type=ExceptionType.TEAR_DOWN)

    '''
    def _initiate_autor_mode(self):
        # Set Autor mode.
        #
        # 1. ACTIVITY_BLOCK
        #    Runs all activities in the specified activity block.
        #
        # 2. ACTIVITY_IN_BLOCK
        #    Runs the specified activity (specified by name) inside the specified activity block.
        #
        # 3. ACTIVITY
        #    Runs the specified activity (specified by type) within the specified module.
        #
        # 4. ACTIVITY_BLOCK_RERUN
        #    Re-runs the specified activity block run (specified by activity block run id)
        #    from a specified activity (specified by the activity name)
        #
        Check.is_non_empty_string(self._flow_config_path, "flow-config-path not provided")

        if self._activity_module is not None:
            self._mode = Mode.ACTIVITY
            Check.is_non_empty_string(self._activity_block_id, "Expected activity-block-id as input. activity-module provided -> run mode ACTIVITY -> activity-block-id is also required")
            Check.is_non_empty_string(self._activity_type, "Expected activity-type as input. activity-module provided -> run mode ACTIVITY -> activity-type is also required")

        elif self._flow_run_id is not None and self._activity_id_special is not None:
            self._mode = Mode.ACTIVITY_BLOCK_RERUN
            Check.is_non_empty_string(self._activity_block_id, "Expected activity-block-id as input. flow-run-id && activity-name provided -> run mode ACTIVITY_BLOCK_RERUN -> activity-block-id required")

        elif self._activity_name_special is not None:
            self._mode = Mode.ACTIVITY_IN_BLOCK
            Check.is_non_empty_string(self._activity_block_id, "Expected activity-block-id as input. activity-name-provided && activity-block-run-id not provided -> run mode ACTIVITY_IN_BLOCK -> activity-block-id required")

        else:
            self._mode = Mode.ACTIVITY_BLOCK
            Check.is_non_empty_string(self._activity_block_id, "Expected activity-block-id as input to run mode ACTIVITY_BLOCK")
    '''

    def _initiate_flow(self):

        # If flow_run_id is provided, then we already have an existing flow and
        # this Autor run is not the first activity block run in the flow.
        # If flow_run_id is not provided, then it is the first job in a flow and
        # a new flow_run_id needs to be created.
        if self._flow_run_id is None:
            self._flow_run_id = str(uuid.uuid4())
            self._flow_run_id_generated = True

        self._flow_config = load_flow_configuration(self._flow_config_path)
        self._flow_id = self._flow_config.flow_id

        # Interrupt is not relevant in mode ACTIVITY.
        if self._mode != Mode.ACTIVITY:
            interrupt_mode = self._flow_config.activity_block(self._activity_block_id).concurrent_interrupt_mode
            if interrupt_mode is not None:
                self._concurrent_interrupt_mode = interrupt_mode

    def _initiate_context(self):
        """
        Create an empty context.
        self._flow_context and self._activity_block_context
        are access points on the flow and activity block level.
        After this method the context will remain empty.
        """
        self._flow_context = Context()  # Empty context, focused on the root (flow) level
        self._flow_context.id = self._flow_run_id
        self._activity_block_context = Context(activity_block=self._activity_block_id)
        pass

    def _do_print(self, obj: object) -> bool:
        return obj or DebugConfig.print_uninitiated_inputs

    def _print_attribute(self, attribute: object, name: str):
        if attribute or DebugConfig.print_uninitiated_inputs:
            logging.info(f'{DebugConfig.autor_info_prefix}{name}{attribute}')

    def _print_attributes(self, title):
        prefix = DebugConfig.autor_info_prefix
        Util.print_header(prefix, title, 'info')
        attr = self._mode
        self._print_attribute(attr, "mode:                      ")
        attr = self._concurrent_interrupt_mode
        self._print_attribute(attr, "concurrent_interrupt_mode: ")
        attr = self._additional_extensions
        self._print_attribute(attr, "additional_extensions:     ")
        attr = self._activity_block_id
        self._print_attribute(attr, "activity_block_id:         ")
        attr = self._activity_config
        self._print_attribute(attr, "activity_config:           ")
        attr = self._activity_id_special
        self._print_attribute(attr, "activity_id_special:       ")
        attr = ','.join(self._activity_ids_special)
        self._print_attribute(attr, "activity_ids_special:      ")
        attr = self._input
        self._print_attribute(attr, "input:                     ")
        attr = self._activity_module
        self._print_attribute(attr, "activity_module:           ")
        attr = self._activity_name_special
        self._print_attribute(attr, "activity_name_special:     ")
        attr = ','.join(self._activity_names_special)
        self._print_attribute(attr, "activity_names_special:    ")
        attr = self._activity_type
        self._print_attribute(attr, "activity_type:             ")
        attr = self._custom_data
        self._print_attribute(attr, "custom_data:               ")
        attr = self._flow_run_id
        self._print_attribute(attr, "flow_run_id:               ")
        attr = self._flow_config_path
        self._print_attribute(attr, "flow_config_path:          ")

        logging.info(f'{prefix}')

    def _print_input_args_before_bootstrap(self):
        self._print_attributes("C O M M A N D - L I N E   A R G U M E N T S")

    def _print_input_args_after_bootstrap(self):
        self._print_attributes("I N P U T S")

    def _print_activity_block_started(self):
        self._print_attributes('A C T I V I T Y   B L O C K   S T A R T E D')

    def _dbg_print_activity_block_finished(self):
        prefix = DebugConfig.autor_info_prefix
        Util.print_header(prefix, 'A C T I V I T Y   B L O C K   F I N I S H E D', level='info')
        logging.info(f'{prefix}mode:                  {self._mode}')
        logging.info(f'{prefix}flow_id:               {self._flow_id}')
        logging.info(f'{prefix}activity_block_id:     {self._activity_block_id}')
        logging.info(f'{prefix}flow_run_id:           {self._flow_run_id}')
        logging.info(f'{prefix}activity_block_run_id: {self._activity_block_run_id}')
        logging.info(f'{prefix}activity_block_status: {self._activity_block_status}')
        logging.info(f'{prefix}')

    # pylint: disable-next=redefined-builtin
    def _abort_and_register_exception(self, e: Exception, description: str, ex_type: ExceptionType):
        # Sanity check
        if self._autor_aborted:
            Check.is_true(self._activity_block_status == Status.ABORTED,
                          msg=f"An activity block that has been aborted by the framework should always have status: {Status.ABORTED}. Current block status: {self._activity_block_status}")

        if not self._autor_aborted:
            self.abort_autor(str(description))

        ExceptionHandler.register_exception(ex=e, description=description, ex_type=ex_type)

    def _print_activity_preparation_msg(self, activity_name, activity_id, activity_group_type, activity_type):
        # fmt: off
        if DebugConfig.print_selected_activity:
            prefix = DebugConfig.selected_activity_prefix
            Util.print_header(prefix, "S E L E C T E D   A C T I V I T Y", level="info")
            logging.info(f"{prefix}ACTIVITY_ID:                {activity_id}")
            logging.info(f"{prefix}ACTIVITY_NAME:              {activity_name}")
            logging.info(f"{prefix}ACTIVITY_TYPE:              {activity_type}")
            logging.info(f"{prefix}ACTIVITY_GROUP_TYPE:        {activity_group_type}")
            logging.info(f"{prefix}ACTIVITY_BLOCK_INTERRUPTED: {self._activity_block_interrupted}")
            logging.info(f"{prefix}")
        # fmt: on

    def _create_data(self, activity_node: Node):  # -> ActivityData
        activity_id = activity_node.activity_id
        activity_group_type = activity_node.activity_group_type
        activity_config = activity_node.activity_config
        Check.is_true(isinstance(activity_config, ActivityConfiguration),
                      f"Expected activity_config to be of type ActivityConfig. Was: {type(activity_config)}")

        self._print_activity_preparation_msg(activity_config.name, activity_id, activity_group_type, activity_config.activity_type)

        # fmt: off
        data = ActivityData()
        data.activity_node = activity_node
        # list of all activities that have run
        data.activities = self._activity_block_activities
        # A dictionary of all activities that have run with their name (not id!) as key.
        # Before/after activities will be overwritten.
        data.activities_by_name = self._activities_by_name
        data.activities_by_unique_name = self._activities_by_unique_name
        data.before_block_activities = self._before_block_activities

        ban: Node = None
        for ban in activity_node.before_activity_nodes:
            if ban.status == NodeStatus.FINISHED:
                Check.is_true(ban.activity is not None,
                              "An activity node that has finished running must have an Activity attatched to it.")
                data.before_activities.append(ban.activity)

        #data.before_activities        = self._before_activities
        data.main_activities = self._main_activities
        #data.after_activities          = self._after_activities
        data.after_block_activities = self._after_block_activities

        # data.before_block_activities_configurations = self._activity_block_configs_before_block
        # data.before_activities_configurations       = self._activity_block_configs_before_activity
        # data.main_activities_configurations         = self._activity_block_configs_main_activities
        # data.after_activities_configurations        = self._activity_block_configs_after_activity
        # data.after_block_activities_configurations  = self._activity_block_configs_after_block

        data.activity = None
        data.activity_id = activity_id
        data.activity_run_id = str(uuid.uuid4())
        data.activity_name = activity_config.name
        data.activity_name_unique = activity_id.split(f"{self._activity_block_id}-")[1]

        data.activity_group_type = activity_group_type
        data.activity_config = activity_config
        data.activity_type = activity_config.activity_type

        data.activity_block_interrupted = self._activity_block_interrupted
        data.activity_block_id = self._activity_block_id
        data.activity_block_run_id = self._activity_block_run_id
        data.flow_run_id = self._flow_run_id
        data.flow_id = self._flow_id
        data.activity_block_status = self._activity_block_status
        # fmt: on
        data.input_context = Context(activity_block=data.activity_block_id)  # Input comes from ActivityBlock level
        data.output_context = Context(activity_block=data.activity_block_id,
                                      activity=data.activity_id)  # Output is written to Activity level (and propagated upwards)
        #data.output_context_properties_handler = None # Initiated in ActivityRunner when activity object is created

        #------------------ rerun preparations -------------------------
        # To prepare for rerun mode save the rerun context and the id of the activity that ran before this activity
        # during the previous run.
        data.rerun_context_dict = self._rerun_context_dict
        orig_dict: dict = Context.get_context_dict()
        Context.set_context(self._rerun_context_dict)
        temp_context: Context = Context(activity_block=data.activity_block_id, activity=data.activity_id)
        data.previous_activity_in_running_order = temp_context.get(ctx.PREVIOUS_ACTIVITY_IN_RUNNING_ORDER, default=None)
        Context.set_context(orig_dict)
        # -------------------------------------------------------------

        #data.activity_context = ActivityContext(activity_block=data.activity_block_id, activity=data.activity_id)

        if activity_group_type == ActivityGroupType.BEFORE_ACTIVITY:
            Check.is_true(activity_node.main_activity_node is not None,
                          "Cannot create before-activity configuration. Main activity node must be provided for each before-activity")

            data.next_main_activity_data = self._create_data(activity_node.main_activity_node)

        return data

    def _update_activity_lists(self, activity_data: ActivityData, activity_config: ActivityConfiguration,
                               activity_group_type):  # TODO take from data object
        activity = activity_data.activity
        self._activity_block_activities.append(activity)
        self._activity_block_activities_data.append(activity_data)
        self._activity_block_activities_id.append(activity_data.activity_id)

        self._activities_by_name[activity_config.name] = activity
        self._activities_by_unique_name[activity_data.activity_name_unique] = activity

        if activity_group_type == ActivityGroupType.BEFORE_BLOCK:
            self._before_block_activities.append(activity)
        elif activity_group_type == ActivityGroupType.BEFORE_ACTIVITY:
            pass
            #activity_data.before_activities.append(activity)
            #self._before_activities.append(activity)
        elif activity_group_type == ActivityGroupType.MAIN_ACTIVITY:
            self._main_activities.append(activity)
        elif activity_group_type == ActivityGroupType.AFTER_ACTIVITY:
            pass
            #activity_data.after_activities.append(activity)
            #self._after_activities.append(activity)
        elif activity_group_type == ActivityGroupType.AFTER_BLOCK:
            self._after_block_activities.append(activity)
        else:
            raise AutorFrameworkException(
                "Unknown activity group type: " + str(activity_group_type)
            )

    def _update_activity_block_status(self, framework_error_occurred):

        data: ActivityData = self._activity_data
        action = data.action

        interrupt = False
        if framework_error_occurred:
            interrupt = True  # All framework and framework usage errors
        else:
            interrupt = not self._rules.continue_on(data, self._mode, action)

        if interrupt:
            self._activity_block_interrupted = True

            if self._concurrent_interrupt_mode == InterruptMode.INTERRUPT_ALL_ACTIVITIES:
                self._graph.mark_all_nodes_as_interrupted()
            elif self._concurrent_interrupt_mode == InterruptMode.INTERRUPT_DESCENDANT_ACTIVITIES:
                self._graph.mark_node_and_all_descendants_as_interrupted(data.activity_node)
            else:
                Check.is_true(False, f"Unhandled InterruptMode: {self._concurrent_interrupt_mode}")

        data.activity_block_interrupted = self._activity_block_interrupted
        self._activity_block_status, state_transition_summary = self._rules.get_activity_block_status(data)
        data.activity_block_status = self._activity_block_status
        self._activity_block_run_summary.append(state_transition_summary)  # For logging purposes only

    def abort_autor(self, abort_reason):
        self._autor_aborted = True
        self._autor_aborted_reason = abort_reason
        self._activity_block_status = Status.ABORTED

        if self._activity_block_context is not None:  # Could theoretically be None before FRAMEWORK_STARTED state.
            self._activity_block_context.set(ctx.ABORT_TYPE, AbortType.ABORTED_BY_FRAMEWORK)

        if self._activity_data is not None:
            self._activity_data.activity_block_status = Status.ABORTED

    def _preprocess_node_run(self, activity_node: Node):
        self._nodes_started_order.append(activity_node)

        # Setting self._activity_data makes it possible for state listeners
        # to know which activity that is being prepared for running.
        self._activity_data: ActivityData = self._create_data(activity_node)
        activity_node.activity_data = self._activity_data

        # ---------------------------------------------------------------------#
        StateHandler.change_state(State.SELECT_ACTIVITY)
        # ---------------------------------------------------------------------#

        # Run the activities in the activity block according to Autor rules.
        # if self._mode == Mode.ACTIVITY_BLOCK or self._mode == Mode.ACTIVITY:
        self._activity_data.action = self._rules.get_action(data=self._activity_data,
                                                            mode=self._mode,
                                                            activity_ids_special=self._activity_ids_special)

        if self._activity_data.action == Action.SKIP_WITH_OUTPUT_VALUES:
            self._activity_data.activity_type = "skip-with-output-values"

        activity_runner = ActivityRunner(data=activity_node.activity_data)
        activity_node.activity_runner = activity_runner

        # ----------------------------------------------------------------#
        StateHandler.change_state(State.BEFORE_ACTIVITY_PREPROCESS)
        # ----------------------------------------------------------------#
        activity_runner.preprocess()

        # BEFORE_ACTIVITY_RUN callback is given only if the Activity.run() method
        # will be called.
        if activity_runner.ok_to_run():
            # ----------------------------------------------------------------#
            StateHandler.change_state(State.BEFORE_ACTIVITY_RUN)
            # ----------------------------------------------------------------#

        return self._activity_data

    def _activity_id_found(self, activity_id: str, nodes: List[Node]) -> bool:
        for node in nodes:
            if node.activity_id == activity_id:
                return True
        return False

    def _run_node(self, activity_node: Node):
        #activity_data = self._preprocess_node_run(activity_node)

        # ---------------------------------------------------------------------#
        # -----------------   R U N   A C T I V I T Y   ---------------------- #
        activity_node.activity_runner.run()
        # activity_data = activity_node.activity_data
        # if self._mode == Mode.ACTIVITY_BLOCK_RERUN and activity_data.action == Action.REUSE:
        #     # In rerun mode we need to make sure that the reused activities finish running
        #     # in the same order as during the original run.
        #
        #     # The id of the activity that run before this activity during the
        #     # previous run.
        #     prev_activity_id = activity_data.previous_activity_in_running_order
        #
        #     if prev_activity_id is not None: # this activity was not first to run
        #
        #         # check with graph is the previous node is going to be re-run. If not, do the same with previous-previous until you either can wait for an
        #         # activity or you can run.
        #
        #         logging.warning(f"{activity_data.activity_id} checking if {prev_activity_id} has finished")
        #         sleep_sec = 0.1
        #         while not self._activity_id_found(prev_activity_id, self._nodes_finished_order):
        #             logging.warning(f"Sleeping ----- {activity_data.activity_id} waiting for {prev_activity_id} to finish. Going to sleep {sleep_sec} seconds")
        #             time.sleep(sleep_sec)
        #
        #         logging.warning(f"Continue +++++ {activity_data.activity_id} constraint: {prev_activity_id} has run")
        #
        #     else:
        #         logging.warning(f"Continue +++++ {activity_data.activity_id} has no constraint")
        # #self._monitor.node_finished(activity_node)

        # ---------------------------------------------------------------------#
        # ---------------------------------------------------------------------#

        #self._postprocess_node_run(activity_node)

    def _postprocess_node_run(self, activity_node: Node):

        # Setting self._activity_data makes it possible for state listeners
        # to know which activity that is being post-processed.
        self._activity_data: ActivityData = activity_node.activity_data
        self._activity_data.activity_block_status = self._activity_block_status

        # If this is not the first activity to finish running, save the id to the
        # previous activity that finished. Needed for rerun reuse.
        # if len(self._nodes_finished_order) > 0:
        #     temp_context:Context = Context(activity_block=self._activity_block_id,activity=activity_node.activity_id)
        #     temp_context.set(ctx.PREVIOUS_ACTIVITY_IN_RUNNING_ORDER, self._nodes_finished_order[-1].activity_id)

        self._nodes_finished_order.append(activity_node)
        activity_node.activity = self._activity_data.activity
        self._update_activity_lists(self._activity_data, activity_node.activity_config,
                                    activity_node.activity_group_type)

        # AFTER_ACTIVITY_RUN callback is given only if the Activity.run() method
        # was be called.
        activity_runner: ActivityRunner = activity_node.activity_runner

        if activity_runner.ok_to_run():
            # ----------------------------------------------------------------#
            StateHandler.change_state(State.AFTER_ACTIVITY_RUN)
            # ----------------------------------------------------------------#

        activity_runner.postprocess()

        # # Save the latest activity that generated output in the context of the current activity. Needed for rerun reuse.
        # if self._latest_activity_that_finished_running is not None:
        #     temp_context:Context = Context(activity_block=self._activity_block_id,activity=activity_node.activity_id)
        #     temp_context.set(ctx.PREVIOUS_ACTIVITY_IN_RUNNING_ORDER, self._latest_activity_that_finished_running)
        #
        #
        # if activity_node.activity_runner._correct_properties_expected():
        #     self._latest_activity_that_finished_running = activity_node.activity_id

        # ----------------------------------------------------------------#
        StateHandler.change_state(State.AFTER_ACTIVITY_POSTPROCESS)
        # ----------------------------------------------------------------#

        need_to_abort = activity_runner.need_to_abort
        abort_reason = activity_runner.need_to_abort_reason

        if need_to_abort and self._autor_aborted is not True:
            self.abort_autor(abort_reason)

        self._update_activity_block_status(need_to_abort)
        self._create_activity_skip_with_outputs_config(self._activity_data)

        if DebugConfig.print_default_config_conditions:
            self._rules.print_default_config_conditions()

    def _create_activity_skip_with_outputs_config(self, data: ActivityData):

        # A part of original flow configuration
        raw_dict = data.activity_config.raw()

        # skip-with-outputs configuration that we want to create
        skip_with_outputs_conf = {}
        raw_dict["skipReuse"] = True
        raw_dict["skipWithOutputsValues"] = skip_with_outputs_conf

        # the outputs that the activity has saved into its context
        context: dict = data.output_context.get_focus_activity_dict()

        for key, val in context.items():
            skip_with_outputs_conf[key] = val

    def _run_activity_block(self):

        # Make sure activity block run id is present.
        if self._activity_block_run_id is None:  # run id can be provided when re-run is performed
            self._activity_block_run_id = str(uuid.uuid4())

        # Save some run info to context. Mostly for information/debugging purposes.
        self._flow_context.set(key=ctx.FLOW_RUN_ID, value=self._flow_run_id)  # for info
        self._activity_block_context.set(key=ctx.ACTIVITY_BLOCK_RUN_ID, value=self._activity_block_run_id)  # for info
        self._activity_block_context.set(key=ctx.FLOW_CONFIG_PATH,
                                         value=self._flow_config_path)  # required for mode ACTIVITY_BLOCK_RERUN

        # Create an ordered list of data tuples that are needed for creating activities.
        # The order is the order in which the activities will be run.
        # if self._activity_block_status == Status.UNKNOWN: # First run of the activity block
        #     self._activity_block_status = Status.SUCCESS

        ######################## new ###############################
        self._graph: ActivityBlockGraph = ActivityBlockGraph()
        self._graph.initiate(self._flow_config.activity_block(self._activity_block_id),
                             rerun_activity_ids=self._activity_ids_special)
        if Flags.print_graph:
            self._graph.print()

        # Graph has created all activity ids. Now we can check that activity ids provided by the user are correct.
        for activity_id in self._activity_ids_special:
            if not self._graph.has_node(activity_id):
                activity_ids: List = self._graph.get_activity_ids()
                activity_ids = "\n".join(activity_ids)
                Check.is_true(False,
                              f"Could not find the provided activity id: {activity_id} in the activity block. Valid activity ids:\n{activity_ids}")

        monitor = ActivityBlockMonitor(activity_block=self, graph=self._graph)
        self._monitor = monitor
        #logging.error("Before monitor.run_nodes()")
        monitor.run_nodes()
        #logging.error("After monitor.run_nodes()")
        # while not graph.graph_finished():
        #     ready_to_run:List[Node] = graph.get_ready_to_run_nodes()
        #
        #     for node in ready_to_run:
        #         graph.set_status_running(node.activity_id)
        #         self._run_node(node)
        #     graph.set_status_finished(node.activity_id)

        ######################## new ###############################

    def _run_activity_block_callbacks(self):

        self._activity_block_callback_exceptions = []
        prefix = DebugConfig.callbacks_trace_prefix  # For debug logging

        if DebugConfig.trace_callbacks:
            Util.print_header(prefix=DebugConfig.callbacks_trace_prefix,
                              text="R U N N I N G   C A L L B A C K S   B L O C K", level="info")

        for activity in self._activity_block_activities:
            callbacks = activity.activity_block_callbacks

            for callback in callbacks:
                # Run the callback if its conditions are fulfilled by the activity it belongs to.
                if callback.should_run():

                    if DebugConfig.trace_callbacks:
                        self._callback_debug_prints(callback, activity, prefix, run=True)

                    try:  # ------------------- RUN CALLBACK ----------------#
                        callback.run()
                    except Exception as exception:
                        logging.error("%s Callback exception during activity: %s. Exception: %s", prefix, activity.id,
                                      exception, )
                        descr = f"Callback exception during activity: {activity.id}. Exception: {exception}"
                        ExceptionHandler.register_exception(exception, description=descr,
                                                            ex_type=ExceptionType.ACTIVITY_BLOCK_CALLBACK)
                        self._activity_block_callback_exceptions.append(
                            self._create_callback_exception(callback, activity, exception))

                else:
                    if DebugConfig.trace_callbacks:
                        self._callback_debug_prints(callback, activity, prefix, run=False)

    def _callback_debug_prints(self, callback, activity, prefix, run):
        if run:
            logging.info("")
            logging.info(prefix + "%s______ R U N N I N G     c a l l b a c k  ______")
            logging.info(prefix + "activity:  " + activity.id)
            logging.info(prefix + "activity.status: " + activity.status)
            logging.info(prefix + "callback.run_on: " + str(callback.run_on))
        else:
            logging.info("")
            logging.info(prefix + "______ I G N O R I N G   c a l l b a c k  _______")
            logging.info(prefix + "activity:  " + activity.id)
            logging.info(prefix + "activity.status: " + activity.status)
            logging.info(prefix + "callback.run_on: " + str(callback.run_on))

    def _create_callback_exception(self, callback, activity, exception) -> dict:
        exception = {}
        exception[ctx.CALLBACK_CLASS] = callback.__class__.__name__
        exception[ctx.EXCEPTION] = str(exception)
        exception[ctx.ACTIVITY] = activity.id
        return exception

    def _register_extension(self, extension: StateListener):
        """
        This method exists only for the testing purposes.
        Normally extensions to use are listed in the FlowConfiguration
        file. For testing purposes additional extensions can be
        provided by calling this method.

        After calling this method the extension will immediately become active.

        Args:
            extension (StateListener): Extension to add to Autor.
        """
        state_handler = StateHandler()
        state_handler.add_state_listener(extension)
        if DebugConfig.print_loaded_extensions:
            Util.print_header(prefix=DebugConfig.autor_info_prefix, text="A D D E D   E X T E N S I O N", level="info")
            logging.info(f"{extension.__class__}")

    def _add_listeners(self, listeners: list):
        """
        Load and add the listeners in the list.
        """

        for listener in listeners:
            [module_name, class_name] = listener.rsplit(".", 1)  # retrieve module name and class name
            module = importlib.import_module(module_name)  # import the module
            class_ = getattr(module, class_name)  # create the class
            instance = class_()  # create a listener instance of the class
            StateHandler.add_state_listener(instance)

    def _register_bootstrap_extensions(self, extensions: List[str]):

        # Register Autor bootstrap
        StateHandler.add_state_listener(AutorFrameworkBootstrap())
        # Register Activity input injector (used for testing)
        StateHandler.add_state_listener(AutorFrameworkActivityInputModifier())
        StateHandler.add_state_listener(StatePrintExtension())

        # Load bootstrap extensions.
        if extensions is not None:
            self._add_listeners(extensions)
        # ----------------- Debug prints -------------------------#
        if DebugConfig.print_loaded_extensions or DebugConfig.print_autor_info:
            self._loaded_items_print_info(
                prefix=DebugConfig.autor_info_prefix,
                item_names=extensions,
                title="L O A D E D   A D D I T I O N A L   E X T E N S I O N S",
                no_extensions_found_msg="No --additional-extensions found -> nothing to load -> OK")
        # ----------------- Debug prints -------------------------#

    def _register_extensions_from_flow_configuration(self, config: FlowConfiguration):
        extensions: List[str] = config.extensions

        if extensions:
            self._add_listeners(extensions)

        # ----------------- Debug prints -------------------------#
        if DebugConfig.print_loaded_extensions or DebugConfig.print_autor_info:
            self._loaded_items_print_info(
                prefix=DebugConfig.autor_info_prefix,
                item_names=extensions,
                title="L O A D E D   E X T E N S I O N S   F R O M   C O N F I G U R A T I O N",
                no_extensions_found_msg="Flow configuration contains no extensions -> nothing to load -> OK")
        # ----------------- Debug prints -------------------------#

    def _loaded_items_print_info(self, prefix: str, item_names: List[str], title: str, no_extensions_found_msg: str):
        Util.print_header(prefix=prefix, text=title, level='info')

        if item_names and len(item_names) > 0:
            for item_name in item_names:
                logging.info(f'{prefix}{item_name}')
        else:
            logging.info(f'{prefix}{no_extensions_found_msg}')
        logging.info(f'{prefix}')

    def _unregister_extensions(self):
        StateHandler.remove_all_listeners()

    def _load_activity_modules(self, config: FlowConfiguration):
        modules = config.activity_modules
        if modules:
            for module in modules:
                importlib.import_module(module)

        # ----------------- Debug prints -------------------------#
        if DebugConfig.print_loaded_modules or DebugConfig.print_autor_info:
            prefix = DebugConfig.autor_info_prefix
            Util.print_header(prefix,
                              "L O A D E D   A C T I V I T Y   M O D U L E S   F R O M   C O N F I G U R A T I O N",
                              level='info')
            if modules and len(modules) > 0:
                for module in modules:
                    logging.info(f'{prefix}{module}')
            else:
                logging.info(f'{prefix}No activity modules found in the flow configuration.')
            logging.info(prefix)

    # ---------------------- StateProducer implementation -----------------------#
    # fmt: off
    # pylint: disable=line-too-long
    def on_before_state(self, state_name, state_data: dict) -> None:

        # General
        state_data[sta.ADDITIONAL_EXTENSIONS] = self._additional_extensions
        state_data[sta.CUSTOM_DATA] = self._custom_data
        state_data[sta.FLAGS] = self._flags
        state_data[sta.MODE] = self._mode

        # Flow
        state_data[sta.FLOW_ID] = self._flow_id
        state_data[sta.FLOW_CONFIG_PATH] = self._flow_config_path
        state_data[sta.FLOW_RUN_ID] = self._flow_run_id
        state_data[sta.FLOW_CONFIG] = self._flow_config
        state_data[sta.FLOW_CONTEXT] = self._flow_context
        state_data[sta.FLOW_INFORMATION] = self._create_flow_info()

        # Activity Block
        state_data[sta.ACTIVITY_BLOCK_ID] = self._activity_block_id
        state_data[sta.ACTIVITY_BLOCK_RUN_ID] = self._activity_block_run_id
        state_data[sta.ACTIVITY_BLOCK_CONFIG] = self._activity_block_config
        state_data[sta.ACTIVITY_BLOCK_CONTEXT] = self._activity_block_context
        state_data[sta.ACTIVITY_BLOCK_ACTIVITIES] = self._activity_block_activities
        state_data[sta.ACTIVITY_BLOCK_CALLBACK_EXCEPTIONS] = self._activity_block_callback_exceptions
        state_data[sta.ACTIVITY_BLOCK_STATUS] = self._activity_block_status
        state_data[sta.ACTIVITY_BLOCK_INTERRUPTED] = self._activity_block_interrupted
        state_data[sta.ACTIVITY_BLOCK_LATEST_ACTIVITY] = self._activity_block_latest_activity

        state_data[sta.ACTIVITY_BLOCK_CONFIGS_MAIN_ACTIVITIES] = self._activity_block_configs_main_activities
        state_data[sta.ACTIVITY_BLOCK_CONFIGS_BEFORE_BLOCK] = self._activity_block_configs_before_block
        state_data[sta.ACTIVITY_BLOCK_CONFIGS_AFTER_BLOCK] = self._activity_block_configs_after_block
        state_data[sta.ACTIVITY_BLOCK_CONFIGS_BEFORE_ACTIVITY] = self._activity_block_configs_before_activity
        state_data[sta.ACTIVITY_BLOCK_CONFIGS_AFTER_ACTIVITY] = self._activity_block_configs_after_activity
        state_data[sta.ACTIVITY_BLOCK_INFORMATION] = self._create_activity_block_info()

        # Mode: ACTIVITY
        # NB! This section must be executed before the Activity section, as
        # the values from self._activity_data have priority.
        state_data[sta.ACTIVITY_MODULE] = self._activity_module
        state_data[sta.ACTIVITY_TYPE] = self._activity_type
        state_data[sta.ACTIVITY_CONFIG] = self._activity_config
        state_data[sta.INPUT] = self._input

        # Mode: ACTIVITY-IN-Block
        state_data[sta.ACTIVITY_NAME_SPECIAL] = self._activity_name_special
        state_data[sta.ACTIVITY_ID_SPECIAL] = self._activity_id_special

        # Activity
        if self._activity_data is not None:
            state_data[sta.INTERNAL_ACTIVITY_DATA] = self._activity_data
            state_data[sta.ACTIVITY_ID] = self._activity_data.activity_id
            state_data[sta.ACTIVITY_RUN_ID] = self._activity_data.activity_run_id
            state_data[sta.ACTIVITY_NAME] = self._activity_data.activity_name
            state_data[sta.ACTIVITY_GROUP_TYPE] = self._activity_data.activity_group_type
            Check.is_true(isinstance(self._activity_data.activity_config, ActivityConfiguration),
                          f"Expected activity_config to be of type ActivityConfig. Was: {type(self._activity_data.activity_config)}")
            state_data[sta.ACTIVITY_CONFIG] = self._activity_data.activity_config
            state_data[sta.ACTIVITY_TYPE] = self._activity_data.activity_type
            state_data[sta.ACTION] = self._activity_data.action

            if self._activity_data.activity is not None:
                state_data[sta.ACTIVITY_INSTANCE] = self._activity_data.activity

            state_data[sta.ACTIVITY_INFORMATION] = self._create_activity_info(self._activity_data)

        # Debug
        state_data[sta.DBG_EXTENSION_TEST_STR] = self._dbg_extension_test_str

    def _create_activity_properties_info_list(self,
                                              properties: Dict[str,ActivityProperty],
                                              category: PropertyCategory,
                                              activity: Activity = None
                                              ) -> List[ActivityPropertyInformation]:
        info_list: List[ActivityPropertyInformation] = []
        prp: ActivityProperty
        for key,prp in properties.items():
            prp = properties[key]
            if activity is None:
                value = None
            else:
                try:
                    value = getattr(activity, prp.name)
                except Exception:
                    value = None
            info: ActivityPropertyInformation = ActivityPropertyInformation(
                name=prp.name,
                type=prp.property_type,
                mandatory=prp.mandatory,
                default=prp.default,
                category=category,
                value=value)
            info_list.append(info)
        return info_list

    def _create_activity_info(self, data: ActivityData) -> ActivityInformation:

        Check.is_true(isinstance(data.activity_config, ActivityConfiguration),
                      f"Expected activity_config to be of type ActivityConfig. Was: {type(data.activity_config)}")

        info: ActivityInformation = ActivityInformation(
            name=data.activity_name,
            id=data.activity_id,
            configuration=data.activity_config.configuration,
            type=data.activity_type
        )

        # if data.activity_config is not None:
        #     info.configuration = data.activity_config.raw()
        # else:
        #     info.configuration = None

        if data.activity is None:
            info.inputs = None
            info.outputs = None
            info.inputs_outputs = None

        else:
            activity: Activity = data.activity
            inp_props: Dict[str,ActivityProperty] = ContextPropertiesRegistry.get_input_properties_as_dict(activity)
            cfg_props: Dict[str,ActivityProperty] = ContextPropertiesRegistry.get_config_properties_as_dict(activity)
            out_props: Dict[str,ActivityProperty] = ContextPropertiesRegistry.get_output_properties_as_dict(activity)


            outputs_to_remove:dict = {} # Dict that contains outputs that are also inputs or configs (inp/out or cfg/out)
            inp_out_props: Dict[str,ActivityProperty] = {}
            for prop_name in inp_props:
                if prop_name in out_props:
                    inp_out_props[prop_name] = inp_props[prop_name]
                    outputs_to_remove[prop_name] = inp_props[prop_name]

            cfg_out_props: Dict[str,ActivityProperty] = {}
            for prop_name in cfg_props:
                if prop_name in out_props:
                    cfg_out_props[prop_name] = cfg_props[prop_name]
                    outputs_to_remove[prop_name] = cfg_props[prop_name]

            for prop_name in outputs_to_remove:
                del out_props[prop_name]
                if prop_name in inp_props:
                    del inp_props[prop_name]
                if prop_name in cfg_props:
                    del cfg_props[prop_name]

            inp_info: List[ActivityPropertyInformation] = (
                self._create_activity_properties_info_list(inp_props,PropertyCategory.inp,activity))
            cfg_info: List[ActivityPropertyInformation] = (
                self._create_activity_properties_info_list(cfg_props,PropertyCategory.cfg,activity))
            out_info: List[ActivityPropertyInformation] = (
                self._create_activity_properties_info_list(out_props,PropertyCategory.out,activity))
            inp_out_info: List[ActivityPropertyInformation] = (
                self._create_activity_properties_info_list(inp_out_props,PropertyCategory.inp_out,activity))
            cfg_out_info: List[ActivityPropertyInformation] = (
                self._create_activity_properties_info_list(cfg_out_props,PropertyCategory.cfg_out,activity))


            info.inputs = inp_info + cfg_info
            info.outputs = out_info
            info.inputs_outputs = inp_info + cfg_info + inp_out_info + cfg_out_info + out_info

            info.run_id = activity.run_id
            info.status = activity.status

            if data.activity_exception is not None:
                info.exception = data.activity_exception

            info.context=ActivityContext(data.activity_block_id, data.activity_id)
        return info

    def _create_activity_block_info(self)->ActivityBlockInformation:
        info:ActivityBlockInformation = ActivityBlockInformation()
        info.id = self._activity_block_id
        info.mode = self._mode

        if self._activity_block_config is not None:
            info.configuration = self._flow_config.activity_block().configuration
        if self._activity_block_context is not None:
            info.context = ActivityBlockContext(self._activity_block_id)
        info.run_id = self._activity_block_run_id
        info.status = self._activity_block_status
        info.exception = ExceptionHandler.get_all_exceptions()
        return info

    def _create_flow_info(self)->FlowInformation:
        info:FlowInformation = FlowInformation()
        info.id = self._flow_id
        info.run_id = self._flow_run_id
        if self._flow_config is not None:
            info.configuration = self._flow_config.configuration
        if self._flow_context is not None:
            info.context = FlowContext()
        return info


    def on_after_state(self, state_name, state_data: dict) -> None:

        # General
        self._additional_extensions = state_data[sta.ADDITIONAL_EXTENSIONS]
        self._custom_data = state_data[sta.CUSTOM_DATA]
        self._flags = state_data[sta.FLAGS]
        self._mode = state_data[sta.MODE]

        # Flow
        self._flow_id = state_data[sta.FLOW_ID]
        self._flow_config_path = state_data[sta.FLOW_CONFIG_PATH]
        self._flow_run_id = state_data[sta.FLOW_RUN_ID]
        self._flow_config = state_data[sta.FLOW_CONFIG]
        self._flow_context = state_data[sta.FLOW_CONTEXT]

        # Activity Block
        self._activity_block_id = state_data[sta.ACTIVITY_BLOCK_ID]
        self._activity_block_run_id = state_data[sta.ACTIVITY_BLOCK_RUN_ID]
        self._activity_block_context = state_data[sta.ACTIVITY_BLOCK_CONTEXT]
        self._activity_block_config = state_data[sta.ACTIVITY_BLOCK_CONFIG]
        self._activity_block_activities = state_data[sta.ACTIVITY_BLOCK_ACTIVITIES]
        self._activity_block_callback_exceptions = state_data[sta.ACTIVITY_BLOCK_CALLBACK_EXCEPTIONS]
        self._activity_block_status = state_data[sta.ACTIVITY_BLOCK_STATUS]
        self._activity_block_interrupted = state_data[sta.ACTIVITY_BLOCK_INTERRUPTED]
        self._activity_block_latest_activity = state_data[sta.ACTIVITY_BLOCK_LATEST_ACTIVITY]

        self._activity_block_configs_main_activities = state_data[sta.ACTIVITY_BLOCK_CONFIGS_MAIN_ACTIVITIES]
        self._activity_block_configs_before_block = state_data[sta.ACTIVITY_BLOCK_CONFIGS_BEFORE_BLOCK]
        self._activity_block_configs_after_block = state_data[sta.ACTIVITY_BLOCK_CONFIGS_AFTER_BLOCK]
        self._activity_block_configs_before_activity = state_data[sta.ACTIVITY_BLOCK_CONFIGS_BEFORE_ACTIVITY]
        self._activity_block_configs_after_activity = state_data[sta.ACTIVITY_BLOCK_CONFIGS_AFTER_ACTIVITY]

        # Mode: ACTIVITY
        self._activity_module = state_data[sta.ACTIVITY_MODULE]
        self._activity_type = state_data[sta.ACTIVITY_TYPE]
        self._activity_config = state_data[sta.ACTIVITY_CONFIG]
        self._input = state_data[sta.INPUT]

        # Mode: ACTIVITY-IN-BLOCK
        self._activity_name_special = state_data[sta.ACTIVITY_NAME_SPECIAL]
        self._activity_id_special = state_data[sta.ACTIVITY_ID_SPECIAL]

        # Activity
        if self._activity_data is not None:
            self._activity_data = state_data[sta.INTERNAL_ACTIVITY_DATA]
            self._activity_data.activity_id = state_data[sta.ACTIVITY_ID]
            self._activity_data.activity_run_id = state_data[sta.ACTIVITY_RUN_ID]
            self._activity_data.activity_name = state_data[sta.ACTIVITY_NAME]
            self._activity_data.activity_group_type = state_data[sta.ACTIVITY_GROUP_TYPE]
            self._activity_data.activity_config = state_data[sta.ACTIVITY_CONFIG]

            Check.is_true(isinstance(self._activity_data.activity_config, ActivityConfiguration),
                          f"Expected activity_config to be of type ActivityConfig. Was: {type(self._activity_data.activity_config)}")

            self._activity_data.activity_type = state_data[sta.ACTIVITY_TYPE]
            self._activity_data.action = state_data[sta.ACTION]

            if sta.ACTIVITY_INSTANCE in state_data:
                self._activity_data.activity = state_data[sta.ACTIVITY_INSTANCE]

        # Debug
        self._dbg_extension_test_str = state_data[sta.DBG_EXTENSION_TEST_STR]

    # fmt: on
    # pylint: enable=line-too-long

    def get_context(self) -> Context:
        return self._flow_context

    def get_activity_context(self, activity_id: str) -> Context:
        return Context(activity_block=self._activity_block_id, activity=activity_id)

    def get_flow_run_id(self) -> str:
        return self._flow_run_id

    def get_activity_block_status(self) -> str:
        return self._activity_block_status

    def get_mode(self) -> str:
        return self._mode

    def get_skip_with_outputs_flow_configuration_url(self) -> str:
        return self._skip_with_outputs_flow_configuration_url

    def get_exception(self) -> Exception:
        return ExceptionHandler.get_first_exception()

    def get_status(self) -> str:
        return self._activity_block_status

    def get_node_started_order(self) -> List:
        return self._nodes_started_order

    def get_node_finished_order(self) -> List:
        return self._nodes_finished_order

    def _create_debug_input_string(self, args, values):
        first_param_detected = False
        for i, name in enumerate(args):
            val = str(values[name])
            if i > 0 and val != "None" and val != "{}" and val != "[]":
                if not first_param_detected:
                    self._debug_input_str = val
                    first_param_detected = True
                else:
                    if name == "flow_config_path":
                        pass
                    elif name == "flow_run_id":
                        self._debug_input_str = self._debug_input_str + self._debug_separator + name
                    else:
                        self._debug_input_str = self._debug_input_str + self._debug_separator + val
