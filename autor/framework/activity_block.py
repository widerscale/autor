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
from typing import List


import yaml

from autor import Activity
from autor.flow_configuration.activity_configuration import ActivityConfiguration
from autor.flow_configuration.flow_configuration import FlowConfiguration
from autor.flow_configuration.flow_configuration_factory import (
    load_flow_configuration,
)
from autor.framework.activity_block_rules import ActivityBlockRules
from autor.framework.activity_context import ActivityContext
from autor.framework.activity_data import ActivityData
from autor.framework.activity_runner import ActivityRunner
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
    Status, ContextPropertyPrefix, Inparam, Constants,
)
from autor.framework.context import Context
from autor.framework.debug_config import DebugConfig
from autor.framework.exception_handler import ExceptionHandler
from autor.framework.file_context import FileContext
from autor.framework.flags import Flags
from autor.framework.keys import FlowConfigurationKeys as cfg
from autor.framework.keys import FlowContextKeys as ctx
from autor.framework.keys import StateKeys as sta
from autor.framework.logging_config import LoggingConfig
from autor.framework.state import State
from autor.framework.state_handler import StateHandler
from autor.framework.state_listener import StateListener
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
        input: dict = None,  # mode: ACTIVITY
        activity_module: str = None,   # mode: ACTIVITY
        activity_name: str = None,
        activity_type: str = None,     # mode: ACTIVITY
        custom_data: dict = None,
        flags: dict = None,
        flow_run_id: str = None,
        flow_config_url: str = None
    ):

        # region -------------- Debug functionality region --------------
        # -------------------------- debug START -----------------------------------#
        try:
            # Build inputs string that is used for creating a file name where the context is saved for the purpose of
            # creating test cases for Autor Framework. This is not used for Autor functionality.
            # Note that MODE will not be a part of this string.
            self._debug_input_str:str = ""
            self._debug_separator:str = "___"

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
        - self._flow_config_url
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


        # Check that the expected values are correct
        Check.is_true(Mode.is_valid(mode), f'Unknown mode: {mode}. The valid modes are: {Mode.get_valid_constants(Mode)}')

        self._flags = flags



        #------------------------- mode: ACTIVITY ------------------------------#
        self._activity_module: str = activity_module   # mode: ACTIVITY
        self._activity_type: str = activity_type     # mode: ACTIVITY
        self._input: dict = input                   # mode: ACTIVITY
        self._activity_config: dict = activity_config     # mode: ACTIVITY
        # ------------------------- mode: ACTIVITY ------------------------------#



        # Extension classes that should be added to the extensions
        # provided in the flow configuration.
        # These additional extensions will be able to get on_bootstrap()
        # callbacks, that is not available for the extensions provided
        # through flow configuration.
        self._additional_extensions:list = additional_extensions


        # After each run Autor adds 'skip-with-outputs' configuration to the flow
        # configuration. The attribute holds the URL to the updated configuration.
        self._skip_with_outputs_flow_configuration_url = None

        # Any data that the user of Autor would like to provide for
        # extensions.
        self._custom_data:dict = custom_data


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

        # The id of the activity that should be treated in a special manner.
        # How it should be treated depends on Autor mode.
        self._activity_id_special = activity_id  # Can be overriden by extensions in state BOOTSTRAP
        if activity_id is None and activity_name is not None and activity_block_id is not None:
            self._activity_id_special = f"{activity_block_id}-{activity_name}"


        # Data that is collected about the special activity. Added to Autor output file in modes
        # ACTIVITY and ACTIVITY_IN_BLOCK
        self._activity_data_special:ActivityData = None

        # Only for mode ACTIVITY_IN_BLOCK.
        # Is set to true once the special activity has been found in configuration.
        # Purpose: helps to detect situations when the provided special activity identification
        # data is not correct and the activity is not found in the configuration file.
        self._activity_found_special:bool = False


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
        self._flow_config_url = flow_config_url
        self._flow_run_id_generated = False  # Will be set to true if Autor will generate the flow_run_id



        # Attributes that are INITIATED after state BOOTSTRAP
        self._flow_id = None                            # Unique identifier of the flow provided by flow configuration.
        self._flow_context_id = None                    # Unique identifier of a context for a flow run.
        self._flow_config:FlowConfiguration = None      # The configuration object representing the whole flow.
        self._flow_context:Context = None               # Context, focused on the root (flow) level.



        # ------------------------------  A C T I V I T Y   B L O C K   D A T A   -----------------#

        self._activity_block_run_id = None
        self._activity_block_activities:List[Activity] = []  # A list of activities that is created as the activities are run.
        self._activity_block_activities_data: List[ActivityData] = []  # A list of activity data that is created as the activities are run.
        self._activity_block_activities_id: List[str] = []  # A list of activity ids that is created as the activities are run.
        self._activity_block_callback_exceptions = []  # [dict{str:str}] Exceptions in activity block callbacks.
        self._activity_block_status = Status.UNKNOWN  # Current status of the activity block. Updated as the activities are run or from context
        self._activity_block_latest_activity = None  # The latest activity that has been run (or skipped) in the activity block.
        # Set to true when the activity-block is considered to be interrupted
        #  (== before or main activities interrupted)
        self._activity_block_interrupted = False

        self._activity_block_config = None
        self._activity_block_configs_main_activities = None
        self._activity_block_configs_before_block    = None
        self._activity_block_configs_after_block     = None
        self._activity_block_configs_before_activity = None
        self._activity_block_configs_after_activity  = None

        self._before_block_activities = []
        self._before_activities = []  # Reset for each main-loop iteration
        self._main_activities = []
        self._after_activities = []
        self._after_block_activities = []
        self._activities_by_name = {}


        # Keep track of the configuration for the next main activity.
        self._next_main_index = 0


        # Attributes that may be OVERRIDEN in state BOOTSTRAP
        self._activity_block_id = activity_block_id

        # Attributes that are INITIATED after state BOOTSTRAP
        self._activity_block_context:Context = None  # Empty context focused on the activity block level

        # List of strings where each line is a summary of an outcome of one activity run.
        # Used only for logging purposes.
        self._activity_block_run_summary:List[str] = []


        # Counters used for generating unique activity ids
        self._bb_counter = 0
        self._ba_counter = 0
        self._ma_counter = 0
        self._aa_counter = 0
        self._ab_counter = 0

        self._rules = ActivityBlockRules()




        # ---------------------------------  A C T I V I T Y   D A T A   --------------------------#
        self._activity_data:ActivityData = None  # Contains activity data and the activity instance



        #---------------------------------- DEBUGGING SUPPORT -------------------------------------#
        # This value will be added to the state data for the extensions to play around with.
        # Key: DBG_EXTENSION_TEST_STR
        self._dbg_extension_test_str = ""

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

            Flags.set_flags(self._flags)

            Context.remote_context = FileContext()  # Default is to use file DB locally. Can be overriden in extensions.

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





            # ---------------------------------------------------------------#
            StateHandler.change_state(State.CONTEXT)
            # ---------------------------------------------------------------#

            # Create extension classes from configuration
            self._register_extensions_from_flow_configuration(self._flow_config)


            # Load activity classes and make them discoverable.
            self._load_activity_modules(self._flow_config)

            # ---------------------------------------------------------------#
            StateHandler.change_state(State.FRAMEWORK_START)
            # ---------------------------------------------------------------#
            self._flow_context.sync_remote()
            self._add_additional_context()
            self._update_activity_block_state_from_context()


            self._create_activities_configurations()
            self._activity_block_context.set(ctx.MODE, self._mode)


        except Exception as e:
            self._abort_and_register_exception(e, "Unhandled exception during Autor set up", ex_type=ExceptionType.SET_UP)

    def _update_activity_block_state_from_context(self):
        #self._activity_block_interrupted = self._activity_block_context.get(ctx.ACTIVITY_BLOCK_INTERRUPTED, search=False, default=False)
        #self._activity_block_status = self._activity_block_context.get(ctx.ACTIVITY_BLOCK_STATUS, search=False, default=Status.UNKNOWN)

        # Currently we don't want activity block status data to be re-loaded when the same run is being used. The status will be
        # re-calculated from activity statuses as if it was a first activity block run. We need this behaviour to support re-runs.
        pass


    def _confirm_mode(self, val):
        Check.is_autor_mode(val, exception_type=ValueError)

    def _confirm_generated_activity_block_id(self, val):
        Check.is_true(value=Constants.GENERATED_ACTIVITY_BLOCK_ID, exception_type=ValueError, msg=f"In mode: {self._mode} the only allowed activity block id is: {Constants.GENERATED_ACTIVITY_BLOCK_ID}. This value is generated internally by Autor and need not be provided.")

    def _confirm_string(self, name:str, val):
        Check.is_non_empty_string(val, exception_type=ValueError, msg=f"Mandatory parameter '{name}' not provided.")

    def _confirm_generated_flow_configuration_name(self, val):
        Check.is_true(value=Constants.GENERATED_FLOW_CONFIG_URL, exception_type=ValueError, msg=f"In mode: {self._mode} the only allowed flow configuration url is: {Constants.GENERATED_FLOW_CONFIG_URL}. This value is generated internally by Autor and need not be provided.")

    def _assure_absence(self, name:str, val):
        Check.is_none_or_empty(val, exception_type=ValueError, msg=f"Parameter '{name}' must not be provided in mode: {self._mode}")




    def _check_mode_ACTIVITY_BLOCK_params(self, params:dict):
        all_possible_params = Inparam.get_valid_constants(Inparam)
        for name in all_possible_params:
            val = params[name]
            if name == Inparam.MODE:                    # Mandatory
                self._confirm_mode(val)
            elif name == Inparam.ACTIVITY_BLOCK_ID:     # Mandatory
                self._confirm_string(name, val)
            elif name == Inparam.ACTIVITY_CONFIG:       # No
                self._assure_absence(name, val)
            elif name == Inparam.ACTIVITY_ID:           # No
                self._assure_absence(name, val)
            elif name == Inparam.INPUT:                 # No
                self._assure_absence(name, val)
            elif name == Inparam.ACTIVITY_MODULE:       # No
                self._assure_absence(name, val)
            elif name == Inparam.ACTIVITY_NAME:         # No
                self._assure_absence(name, val)
            elif name == Inparam.ACTIVITY_TYPE:         # No
                self._assure_absence(name, val)
            elif name == Inparam.CUSTOM_DATA:           # Optional (advanced usage)
                pass
            elif name == Inparam.FLOW_RUN_ID:           # Optional
                pass
            elif name == Inparam.FLOW_CONFIG_URL:       # Mandatory
                self._confirm_string(name, val)
            elif name == Inparam.ADDITIONAL_EXTENSIONS: # Optional (advanced usage)
                pass
            else:
                raise AutorFrameworkException(f"Internal error: Unhandled parameter name: {name} -> add to implementation!")


    def _check_mode_ACTIVITY_IN_BLOCK_params(self, params:dict):
        all_possible_params = Inparam.get_valid_constants(Inparam)


        activity_id_value:str = None
        activity_name_value:str = None

        for name in all_possible_params:
            val = params[name]
            if name == Inparam.MODE:                    # Mandatory
                self._confirm_mode(val)
            elif name == Inparam.ACTIVITY_BLOCK_ID:     # Mandatory
                self._confirm_string(name, val)
            elif name == Inparam.ACTIVITY_CONFIG:       # No
                self._assure_absence(name, val)
            elif name == Inparam.ACTIVITY_NAME:         # Mandatory within group
                activity_name_value = val
            elif name == Inparam.ACTIVITY_ID:           # Mandatory within group
                activity_id_value = val
            elif name == Inparam.INPUT:                 # Optional
                pass
            elif name == Inparam.ACTIVITY_MODULE:       # No
                self._assure_absence(name, val)
            elif name == Inparam.ACTIVITY_TYPE:         # No
                self._assure_absence(name, val)
            elif name == Inparam.CUSTOM_DATA:           # Optional (advanced usage)
                pass
            elif name == Inparam.FLOW_RUN_ID:           # Optional
                pass
            elif name == Inparam.FLOW_CONFIG_URL:       # Mandatory
                self._confirm_string(name, val)
            elif name == Inparam.ADDITIONAL_EXTENSIONS: # Optional (advanced usage)
                pass
            else:
                raise AutorFrameworkException(f"Internal error: Unhandled parameter name: {name} -> add to implementation!")

        # Checking mandatory within group values
        self._confirm_activity_name_or_id(id=activity_id_value, name=activity_name_value)

    def _check_mode_ACTIVITY_BLOCK_RERUN_params(self, params:dict):
        all_possible_params = Inparam.get_valid_constants(Inparam)
        activity_id_value:str = None
        activity_name_value:str = None

        for name in all_possible_params:
            val = params[name]
            if name == Inparam.MODE:                    # Mandatory
                self._confirm_mode(val)
            elif name == Inparam.ACTIVITY_BLOCK_ID:     # Mandatory
                self._confirm_string(name, val)
            elif name == Inparam.ACTIVITY_CONFIG:       # No
                self._assure_absence(name, val)
            elif name == Inparam.ACTIVITY_NAME:         # Mandatory within group
                activity_name_value = val
            elif name == Inparam.ACTIVITY_ID:           # Mandatory within group
                activity_id_value = val
            elif name == Inparam.INPUT:                 # Optional
                pass
            elif name == Inparam.ACTIVITY_MODULE:       # No
                self._assure_absence(name, val)
            elif name == Inparam.ACTIVITY_TYPE:         # No
                self._assure_absence(name, val)
            elif name == Inparam.CUSTOM_DATA:           # Optional (advanced usage)
                pass
            elif name == Inparam.FLOW_RUN_ID:           # Mandatory
                self._confirm_string(name, val)
            elif name == Inparam.FLOW_CONFIG_URL:       # Mandatory
                self._confirm_string(name, val)
            elif name == Inparam.ADDITIONAL_EXTENSIONS: # Optional (advanced usage)
                pass
            else:
                raise AutorFrameworkException(f"Internal error: Unhandled parameter name: {name} -> add to implementation!")

        # Checking mandatory within group values
        self._confirm_activity_name_or_id(name=activity_name_value, id=activity_id_value)

    def _check_mode_ACTIVITY_params(self, params:dict):

        all_possible_params = Inparam.get_valid_constants(Inparam)

        for name in all_possible_params:
            val = params[name]
            if name == Inparam.MODE:                    # Mandatory
                self._confirm_mode(val)
            elif name == Inparam.ACTIVITY_BLOCK_ID:     # Generated by Autor
                self._confirm_generated_activity_block_id(val)
            elif name == Inparam.ACTIVITY_CONFIG:       # Optional
                pass
            elif name == Inparam.INPUT:                 # Optional
                pass
            elif name == Inparam.ACTIVITY_MODULE:       # Mandatory
                self._confirm_string(name, val)
            elif name == Inparam.ACTIVITY_NAME:         # No
                self._assure_absence(name, val)
            elif name == Inparam.ACTIVITY_ID:           # No
                self._assure_absence(name, val)
            elif name == Inparam.ACTIVITY_TYPE:         # Mandatory
                self._confirm_string(name, val)
            elif name == Inparam.CUSTOM_DATA:           # Optional (advanced usage)
                pass
            elif name == Inparam.FLOW_RUN_ID:           # No
                if Flags.allow_flow_run_id_in_mode_activity:
                    pass
                else:
                    self._assure_absence(name, val)
            elif name == Inparam.FLOW_CONFIG_URL:       # Generated by Autor
                self._confirm_generated_flow_configuration_name(val)
            elif name == Inparam.ADDITIONAL_EXTENSIONS: # Optional (advanced usage)
                pass
            else:
                raise AutorFrameworkException(f"Internal error: Unhandled parameter name: {name} -> add to implementation!")








    def _confirm_activity_name_or_id(self, name:str, id:str):
        valid_name = Util.is_non_empty_string(name)
        valid_id = Util.is_non_empty_string(id)
        if valid_name and valid_id:
            logging.warning(f"{DebugConfig.autor_info_prefix}Found both {Inparam.ACTIVITY_ID} and {Inparam.ACTIVITY_NAME}, whereas only one of them should be provided.")

            if not id.endswith(name):
                raise ValueError(f"The provided values are not compatible: {Inparam.ACTIVITY_ID}={id} and {Inparam.ACTIVITY_NAME}={name}. Provide only one of them.")

        elif not valid_name and not valid_id:
            raise ValueError(f"Parameter not found. Expected either: {Inparam.ACTIVITY_ID} or {Inparam.ACTIVITY_NAME}.")




    def _check_and_trim_inputs(self):
        # Create a temporary dict for parameter validation. The dict contains
        # pairs (parameter,checked:bool)
        params:dict = {}
        params[Inparam.MODE] = self._mode
        params[Inparam.ACTIVITY_BLOCK_ID] = self._activity_block_id
        params[Inparam.FLOW_CONFIG_URL] = self._flow_config_url
        params[Inparam.FLOW_RUN_ID] = self._flow_run_id
        params[Inparam.ACTIVITY_CONFIG] = self._activity_config
        params[Inparam.ACTIVITY_MODULE] = self._activity_module
        params[Inparam.ACTIVITY_NAME] = self._activity_name_special
        params[Inparam.ACTIVITY_ID] = self._activity_id_special
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
            Check.is_non_empty_string(self._activity_block_id, f"Missing activity_block_id. Cannot create special activity-id from special activity name: {self._activity_name_special}.")
            self._activity_id_special = f"{self._activity_block_id}-{self._activity_name_special}"

    def _add_additional_context(self):
        for key,val in self._input.items():
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
            self._abort_and_register_exception(e, "Unhandled exception during activity block execution", ex_type=ExceptionType.ACTIVITY_BLOCK)

        # Run callbacks
        try:
            # ---------------------------------------------------------------#
            StateHandler.change_state(State.BEFORE_ACTIVITY_BLOCK_CALLBACKS)
            # ---------------------------------------------------------------#
            self._run_activity_block_callbacks()
        except Exception as e:
            self._abort_and_register_exception(e, "Unhandled exception during activity block callbacks execution", ex_type=ExceptionType.ACTIVITY_BLOCK)

        # Finalize activity block run
        try:
            # ---------------------------------------------------------------#
            StateHandler.change_state(State.AFTER_ACTIVITY_BLOCK)
            # ---------------------------------------------------------------#
            self._activity_block_context.set(ctx.ACTIVITY_BLOCK_STATUS, self._activity_block_status)
            self._activity_block_context.set(ctx.ACTIVITY_BLOCK_INTERRUPTED, self._activity_block_interrupted)

            if len(self._activity_block_callback_exceptions) > 0:
                self._activity_block_context.set(ctx.CALLBACK_EXCEPTIONS, self._activity_block_callback_exceptions)
            self._flow_context.sync_remote()

            if DebugConfig.print_context_on_finished:
                self._flow_context.print_context("Context at the end of the activity block run")

        except Exception as e:
            self._abort_and_register_exception(e, "Unhandled exception during activity block finalization", ex_type=ExceptionType.ACTIVITY_BLOCK)
        file_name = "<filename not assigned>"
        try:
            # Print output from Activity Block
            self._print_output_to_file("autor-output") # prints json and yml
        except Exception as e:
            self._abort_and_register_exception(e, f"Unhandled exception when trying to write activity block output to file:{file_name}.", ex_type=ExceptionType.ACTIVITY_BLOCK)


        finally:
            if DebugConfig.create_skip_with_output_flow_config:
                self._dbg_save_skip_with_outputs_flow_config()  # creates a flow config with skip configuration with results from the current run.
            if DebugConfig.print_activity_block_finished_summary:
                self._dbg_print_activity_block_finished()
                Util.print_header(DebugConfig.autor_info_prefix, 'A C T I V I T Y   B L O C K   R U N   S U M M A R Y', level='info', line_below=False)
                logging.info(DebugConfig.autor_info_prefix)
                ActivityBlockRules.get_transition_summary().print(DebugConfig.autor_info_prefix)
            if DebugConfig.save_activity_block_context_locally:  # can be used for test cases
                self._dbg_save_context()




    def _print_output_to_file(self, file_name):
        output: dict = {}
        output["mode"] = self._mode
        output["flow_run_id"] = self._flow_run_id
        output["activity_block_id"] = self._activity_block_id
        output["activity_block_status"] = self._activity_block_status


        # If we have a special activity run and Autor has not aborted, add the
        # special activity data to the output.
        if not self._autor_aborted:
            # if self._mode == Mode.ACTIVITY or self._mode == Mode.ACTIVITY_IN_BLOCK:
            #     data = self._activity_data_special
            #     output["activity_id"] = data.activity_id
            #     output["activity_name"] = data.activity_name
            #     output["activity_outputs"] = {}
            #
            #     properties:dict = data.activity_context.get(ContextPropertyPrefix.props)
            #
            #     for (key,val) in properties.items():
            #         if key.startswith(ContextPropertyPrefix.output):
            #             prop_name = key[4:]
            #             output["activity_outputs"][prop_name] = val
            #
            # else:
                activities:List = []
                output["activities"] = activities

                for data in self._activity_block_activities_data:
                    activity = {}
                    activities.append(activity)
                    activity["activity_id"] = data.activity_id
                    activity["activity_name"] = data.activity_name
                    activity["activity_outputs"] = {}

                    properties: dict = data.activity_context.get(ContextPropertyPrefix.props)

                    for (key, val) in properties.items():
                        if key.startswith(ContextPropertyPrefix.output):
                            prop_name = key[4:]
                            activity["activity_outputs"][prop_name] = val



        # datetime object containing current date and time
        now = str(datetime.now())
        now = now.replace(' ', '_')
        now = now.replace('.', '_')
        now = now.replace(':', '_')



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

        context:dict = Context.get_context_dict()

        filename_unmodified = f'{self._mode}_{self._activity_block_id}_{self._activity_block_status}_unmodified.json'
        filename_generic_ab1 = f'{self._mode}_{self._activity_block_id}_{self._activity_block_status}_uc.json'
        filename_generic_ab = f'{self._debug_input_str}{self._debug_separator}{self._activity_block_status}.json'
        filename_generic_ab = filename_generic_ab.replace('/','.')
        filename_generic_ab = filename_generic_ab.replace('\\', '.')
        filename_generic_ab = filename_generic_ab.replace(',', '_')
        filename_generic_ab = filename_generic_ab.replace(" ", "")
        filename_generic_ab = filename_generic_ab.replace("'","")
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

        activity_blocks:dict = context['_activityBlocks']


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
        self._skip_with_outputs_flow_configuration_url = path # save

        with open(path, 'w') as outfile:
            yaml.dump(config, outfile, default_flow_style=False, sort_keys = False)



    def _tear_down(self):

        # Remove all listeners
        try:
            # ---------------------------------------------------------------#
            StateHandler.change_state(State.FRAMEWORK_END)
            # ---------------------------------------------------------------#
            StateHandler().remove_all_listeners()
            # logging.info(f"FLOW ID: {self._flow_id}")

        except Exception as e:
            self._abort_and_register_exception(e, "Unhandled exception during Autor tear down", ex_type=ExceptionType.TEAR_DOWN)
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
        Check.is_non_empty_string(self._flow_config_url, "flow-config-url not provided")

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

        self._flow_config = load_flow_configuration(self._flow_config_url)
        self._flow_id = self._flow_config.flow_id



    def _initiate_context(self):
        """
        Create an empty context.
        self._flow_context and self._activity_block_context
        are access points on the flow and activity block level.
        After this method the context will remain empty.
        """
        self._flow_context = Context() # Empty context, focused on the root (flow) level
        self._flow_context.id = self._flow_run_id
        self._activity_block_context = Context(activity_block=self._activity_block_id)


    def _do_print(self, obj:object)->bool:
        return obj or DebugConfig.print_uninitiated_inputs

    def _print_attribute(self, attribute:object, name:str):
        if attribute or DebugConfig.print_uninitiated_inputs:
            logging.info(f'{DebugConfig.autor_info_prefix}{name}{attribute}')



    def _print_attributes(self, title):
        prefix = DebugConfig.autor_info_prefix
        Util.print_header(prefix, title, 'info')
        attr = self._mode
        self._print_attribute(attr, "mode:                  ")
        attr = self._additional_extensions
        self._print_attribute(attr, "additional_extensions: ")
        attr = self._activity_block_id
        self._print_attribute(attr, "activity_block_id:     ")
        attr = self._activity_config
        self._print_attribute(attr, "activity_config:       ")
        attr = self._activity_id_special
        self._print_attribute(attr, "activity_id_special:   ")
        attr = self._input
        self._print_attribute(attr, "input:                 ")
        attr = self._activity_module
        self._print_attribute(attr, "activity_module:       ")
        attr = self._activity_name_special
        self._print_attribute(attr, "activity_name_special: ")
        attr = self._activity_type
        self._print_attribute(attr, "activity_type:         ")
        attr = self._custom_data
        self._print_attribute(attr, "custom_data:           ")
        attr = self._flow_run_id
        self._print_attribute(attr, "flow_run_id:           ")
        attr = self._flow_config_url
        self._print_attribute(attr, "flow_config_url:       ")


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
    def _abort_and_register_exception(self, e:Exception, description:str, ex_type:ExceptionType):
        # Sanity check
        if self._autor_aborted:
            Check.is_true(self._activity_block_status == Status.ABORTED,f"An activity block that has been aborted by the framework should always have status: {Status.ABORTED}. Current block status: {self._activity_block_status}")

        if not self._autor_aborted:
            self._abort_autor(str(description))

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

    def _create_activities_configurations(self):
        try:
            # pylint: disable=line-too-long
            # fmt: off
            self._activity_block_config = self._flow_config.activity_block(self._activity_block_id)
            self._activity_block_configs_main_activities = self._activity_block_config.activities
            self._activity_block_configs_before_block    = self._activity_block_config.before_block
            self._activity_block_configs_after_block     = self._activity_block_config.after_block
            self._activity_block_configs_before_activity = self._activity_block_config.before_activity
            self._activity_block_configs_after_activity  = self._activity_block_config.after_activity

            # fmt: on
            # pylint: enable=line-too-long

            if (
                len(self._activity_block_configs_main_activities) == 0
                and len(self._activity_block_configs_before_block) == 0
                and len(self._activity_block_configs_after_block) == 0
                and len(self._activity_block_configs_before_activity) == 0
                and len(self._activity_block_configs_after_activity) == 0
            ):
                raise AutorFrameworkValueException(
                    (
                        "No activity configurations found in the configuration of the activity"
                        + f" block: {str(self._activity_block_id)!r} -> no activities to run"
                    )
                )

        except Exception as e:
            raise AutorFrameworkException(
                f"Could not create activity configurations: {e.__class__.__name__}: {str(e)}"
            ) from e

    def _create_data(self, activity_id, activity_group_type, activity_config:ActivityConfiguration):  # -> ActivityData

        self._print_activity_preparation_msg(
            activity_config.name, activity_id, activity_group_type, activity_config.activity_type
        )

        # fmt: off
        data = ActivityData()
        # list of all activities that have run
        data.activities              = self._activity_block_activities
        # A dictionary of all activities that have run with their name (not id!) as key.
        # Before/after activities will be overwritten.
        data.activities_by_name      = self._activities_by_name
        data.before_block_activities = self._before_block_activities
        data.before_activities       = self._before_activities
        data.main_activities         = self._main_activities
        data.after_activities        = self._after_activities
        data.after_block_activities  = self._after_block_activities

        data.before_block_activities_configurations = self._activity_block_configs_before_block
        data.before_activities_configurations       = self._activity_block_configs_before_activity
        data.main_activities_configurations         = self._activity_block_configs_main_activities
        data.after_activities_configurations        = self._activity_block_configs_after_activity
        data.after_block_activities_configurations  = self._activity_block_configs_after_block

        data.activity               = None
        data.activity_id            = activity_id
        data.activity_run_id        = str(uuid.uuid4())
        data.activity_name          = activity_config.name
        data.activity_group_type    = activity_group_type
        data.activity_config        = activity_config
        data.activity_type          = activity_config.activity_type

        data.interrupted            = self._activity_block_interrupted
        data.activity_block_id      = self._activity_block_id
        data.activity_block_run_id  = self._activity_block_run_id
        data.flow_run_id            = self._flow_run_id
        data.flow_id                = self._flow_id
        data.activity_block_status  = self._activity_block_status
        # fmt: on
        data.input_context  = Context(activity_block=data.activity_block_id)
        data.output_context = Context(activity_block=data.activity_block_id, activity=data.activity_id)
        data.output_context_properties_handler = None # Initiated in ActivityRunner when activity object is created

        data.activity_context = ActivityContext(activity_block=data.activity_block_id, activity=data.activity_id)

        if activity_group_type == ActivityGroupType.BEFORE_ACTIVITY:
            Check.is_true(
                len(self._activity_block_configs_main_activities) > self._next_main_index,
                "No main activity configuration exists for the before activity.",
            )
            next_main_conf = self._activity_block_configs_main_activities[self._next_main_index]
            data.next_main_activity_data = self._create_data(
                "_NEXT_MAIN_ACTIVITY", ActivityGroupType.MAIN_ACTIVITY, next_main_conf
            )

        return data

    def _update_activity_lists(self, activity_data:ActivityData, activity_config, activity_group_type):  # TODO take from data object
        activity = activity_data.activity
        self._activity_block_activities.append(activity)
        self._activity_block_activities_data.append(activity_data)
        self._activity_block_activities_id.append(activity_data.activity_id)

        self._activities_by_name[activity_config.name] = activity

        if activity_group_type == ActivityGroupType.BEFORE_BLOCK:
            self._before_block_activities.append(activity)
        elif activity_group_type == ActivityGroupType.BEFORE_ACTIVITY:
            self._before_activities.append(activity)
        elif activity_group_type == ActivityGroupType.MAIN_ACTIVITY:
            self._main_activities.append(activity)
        elif activity_group_type == ActivityGroupType.AFTER_ACTIVITY:
            self._after_activities.append(activity)
        elif activity_group_type == ActivityGroupType.AFTER_BLOCK:
            self._after_block_activities.append(activity)
        else:
            raise AutorFrameworkException(
                "Unknown activity group type: " + str(activity_group_type)
            )

    def _update_activity_block_status(self, framework_error_occurred):

        data:ActivityData = self._activity_data
        action = data.action

        if self._activity_block_interrupted is False: # Once the activity block has been interrupted it will remain interrupted.
            if framework_error_occurred:
                self._activity_block_interrupted = True  # All framework and framework usage errors
                data.interrupted = self._activity_block_interrupted
            else:
                self._activity_block_interrupted = not self._rules.continue_on(data, self._mode, action)
                data.interrupted = self._activity_block_interrupted

        self._activity_block_status, state_transition_summary = self._rules.get_activity_block_status(data, self._autor_aborted)
        data.activity_block_status = self._activity_block_status
        self._activity_block_run_summary.append(state_transition_summary) # For logging purposes only

    # Autor is aborted when Autor framework errors occur,
    #   or user does not follow the rules defined by Autor.
    # Autor should NOT be aborted due to activity.run() errors, as these are considered
    #   as expected framework usage errors and are handled by the framework rules.
    # Once the activity block status is set to ABORTED due to Autor being aborted,
    #  the status should not be changed afterward.
    def _abort_autor(self, abort_reason):
        self._autor_aborted = True
        self._autor_aborted_reason = abort_reason
        self._activity_block_status = Status.ABORTED

        if self._activity_block_context is not None: # Could theoretically be None before FRAMEWORK_STARTED state.
            self._activity_block_context.set(ctx.ABORT_TYPE, AbortType.ABORTED_BY_FRAMEWORK)

        if self._activity_data is not None:
            self._activity_data.activity_block_status = Status.ABORTED

    def _run_activity(self, activity_name, activity_id, activity_group_type, activity_config:ActivityConfiguration):
        self._activity_data:ActivityData = self._create_data(activity_id, activity_group_type, activity_config)

        if (self._mode == Mode.ACTIVITY) or (self._mode == Mode.ACTIVITY_IN_BLOCK and (self._activity_data.activity_id == self._activity_id_special)):
            Check.is_true(self._activity_data_special is None, "Internal error: Special activity data may not be created twice.")
            self._activity_data_special = self._activity_data
            self._activity_found_special = True

        # ---------------------------------------------------------------------#
        StateHandler.change_state(State.SELECT_ACTIVITY)
        # ---------------------------------------------------------------------#

        # Run the activities in the activity block according to Autor rules.
        #if self._mode == Mode.ACTIVITY_BLOCK or self._mode == Mode.ACTIVITY:
        self._activity_data.action = self._rules.get_action(data=self._activity_data, mode=self._mode, activity_id_special=self._activity_id_special)


        if self._activity_data.action == Action.REUSE:
            self._activity_data.activity_type = "reuse"
        elif self._activity_data.action == Action.SKIP_WITH_OUTPUT_VALUES:
            self._activity_data.activity_type = "skip-with-output-values"

        # ---------------------------------------------------------------------#
        # -----------------   R U N   A C T I V I T Y   ---------------------- #
        need_to_abort, abort_reason = ActivityRunner().run_activity(self._activity_data)
        # ---------------------------------------------------------------------#
        # ---------------------------------------------------------------------#

        if need_to_abort:
            self._abort_autor(abort_reason)

        self._update_activity_lists(self._activity_data, activity_config, activity_group_type)
        self._update_activity_block_status(need_to_abort)
        self._create_activity_skip_with_outputs_config(self._activity_data)

        if DebugConfig.print_default_config_conditions:
            self._rules.print_default_config_conditions()


    def _create_activity_skip_with_outputs_config(self, data:ActivityData):

        # A part of original flow configuration
        raw_dict = data.activity_config.raw()

        # skip-with-outputs configuration that we want to create
        skip_with_outputs_conf = {}
        raw_dict["skipReuse"] = True
        raw_dict["skipWithOutputsValues"] = skip_with_outputs_conf

        # the outputs that the activity has saved into its context
        context:dict = data.output_context.get_focus_activity_dict()

        for key,val in context.items():
            skip_with_outputs_conf[key] = val




    def _run_activity_block(self):

        # Make sure activity block run id is present.
        if self._activity_block_run_id is None: # run id can be provided when re-run is performed
            self._activity_block_run_id = str(uuid.uuid4())

        # Save some run info to context. Mostly for information/debugging purposes.
        self._flow_context.set(key=ctx.FLOW_RUN_ID, value=self._flow_run_id) # for info
        self._activity_block_context.set(key=ctx.ACTIVITY_BLOCK_RUN_ID, value=self._activity_block_run_id) # for info
        self._activity_block_context.set(key=ctx.FLOW_CONFIG_URL, value=self._flow_config_url) # required for mode ACTIVITY_BLOCK_RERUN

        # Create an ordered list of data tuples that are needed for creating activities.
        # The order is the order in which the activities will be run.
        if self._activity_block_status == Status.UNKNOWN: # First run of the activity block
            self._activity_block_status = Status.SUCCESS


        # --------------------- BEFORE-BLOCK ----------------------------#
        for act_conf_before_block in self._activity_block_configs_before_block:
            activity_id = (
                self._activity_block_id
                + "-"
                + self._get_activity_name(act_conf_before_block, ActivityGroupType.BEFORE_BLOCK)
            )
            self._run_activity(
                act_conf_before_block.name,
                activity_id,
                ActivityGroupType.BEFORE_BLOCK,
                act_conf_before_block,
            )

        # -----------------------   M A I N - B L O C K   B E G I N   ---------------------------#
        for act_conf_main in self._activity_block_configs_main_activities:
            self._before_activities = []
            self._after_activities = []
            main_name = self._get_activity_name(act_conf_main, ActivityGroupType.MAIN_ACTIVITY)

            # ----------------------- BEFORE-ACTIVITY --------------------------#
            for act_conf_before in self._activity_block_configs_before_activity:
                activity_id = (
                    self._activity_block_id
                    + "-"
                    + main_name
                    + "-"
                    + self._get_activity_name(act_conf_before, ActivityGroupType.BEFORE_ACTIVITY)
                )
                self._run_activity(
                    act_conf_before.name,
                    activity_id,
                    ActivityGroupType.BEFORE_ACTIVITY,
                    act_conf_before,
                )

            # ------------------------ MAIN-ACTIVITY ---------------------------#
            activity_id = self._activity_block_id + "-" + main_name
            self._run_activity(
                act_conf_main.name, activity_id, ActivityGroupType.MAIN_ACTIVITY, act_conf_main
            )
            self._next_main_index = self._next_main_index + 1

            # ------------------------ AFTER-ACTIVITY ---------------------------#
            for act_conf_after in self._activity_block_configs_after_activity:
                activity_id = (
                    self._activity_block_id
                    + "-"
                    + main_name
                    + "-"
                    + self._get_activity_name(act_conf_after, ActivityGroupType.AFTER_ACTIVITY)
                )
                self._run_activity(
                    act_conf_after.name,
                    activity_id,
                    ActivityGroupType.AFTER_ACTIVITY,
                    act_conf_after,
                )

        # ----------------------------   M A I N - B L O C K   E N D   ----------------------------#

        # ----------------------- AFTER-BLOCK ------------------------------#
        for act_conf_after_block in self._activity_block_configs_after_block:
            activity_id = (
                self._activity_block_id
                + "-"
                + self._get_activity_name(act_conf_after_block, ActivityGroupType.AFTER_BLOCK)
            )
            self._run_activity(
                self._activity_block_id,
                activity_id,
                ActivityGroupType.AFTER_BLOCK,
                act_conf_after_block,
            )



        if self._mode == Mode.ACTIVITY_IN_BLOCK:
            try:
                Check.is_true(self._activity_found_special, f"Activity with id: {self._activity_id_special} not found.")
            except Exception as ex:
                descr = f"Activity with id: {self._activity_id_special} is not part of activity block: {self._activity_block_id} -> aborting activity block. Check the spelling of the activity id/name. Valid activity ids: {self._activity_block_activities_id}"
                self._abort_and_register_exception(e=ex,description=descr,ex_type=ExceptionType.AUTOR_INPUT_PARAMETERS)






    def _get_activity_name(self, conf, group):

        if self._mode == Mode.ACTIVITY:
            Check.is_non_empty_string(self._activity_name_special, "Internal error. Mode ACTIVITY requires activity_name, which should be created by Autor internal bootstrap extension. In this mode Autor generates a Flow Configuration with the acitivity_name.")
            default_name= self._activity_name_special

        elif group == ActivityGroupType.BEFORE_BLOCK:
            self._bb_counter = self._bb_counter + 1
            default_name = cfg.BEFORE_BLOCK + str(self._bb_counter)

        elif group == ActivityGroupType.BEFORE_ACTIVITY:
            self._ba_counter = self._ba_counter + 1
            default_name = cfg.BEFORE_ACTIVITY + str(self._ba_counter)

        elif group == ActivityGroupType.MAIN_ACTIVITY:
            self._ma_counter = self._ma_counter + 1
            default_name = cfg.ACTIVITY + str(self._ma_counter)

        elif group == ActivityGroupType.AFTER_ACTIVITY:
            self._aa_counter = self._aa_counter + 1
            default_name = cfg.AFTER_ACTIVITY + str(self._aa_counter)

        elif group == ActivityGroupType.AFTER_BLOCK:
            self._ab_counter = self._ab_counter + 1
            default_name = cfg.AFTER_BLOCK + str(self._ab_counter)
        else:
            raise AutorFrameworkException("Unhandled ActivityGroupType: " + str(group))

        if conf.name is not None:
            return conf.name

        conf.name = default_name

        return default_name

    def _run_activity_block_callbacks(self):

        self._activity_block_callback_exceptions = []
        prefix = DebugConfig.callbacks_trace_prefix  # For debug logging

        if DebugConfig.trace_callbacks:
            Util.print_header(prefix=DebugConfig.callbacks_trace_prefix, text="R U N N I N G   C A L L B A C K S   B L O C K", level="info")

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
                        logging.error("%s Callback exception during activity: %s. Exception: %s",prefix,activity.id,exception,)
                        descr = f"Callback exception during activity: {activity.id}. Exception: {exception}"
                        ExceptionHandler.register_exception(exception,description=descr,ex_type=ExceptionType.ACTIVITY_BLOCK_CALLBACK)
                        self._activity_block_callback_exceptions.append(self._create_callback_exception(callback, activity, exception))

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


    def _add_listeners(self, listeners:list):
        """
        Load and add the listeners in the list.
        """

        for listener in listeners:
            [module_name, class_name] = listener.rsplit(".", 1) # retrieve module name and class name
            module = importlib.import_module(module_name)       # import the module
            class_ = getattr(module, class_name)                # create the class
            instance = class_()                                 # create a listener instance of the class
            StateHandler.add_state_listener(instance)


    def _register_bootstrap_extensions(self, extensions:List[str]):

        # Register Autor bootstrap
        StateHandler.add_state_listener(AutorFrameworkBootstrap())

        # Load bootstrap extensions.
        if extensions is not None:
            self._add_listeners(extensions)
        # ----------------- Debug prints -------------------------#
        if DebugConfig.print_loaded_extensions or DebugConfig.print_autor_info:
            self._loaded_items_print_info(
                prefix = DebugConfig.autor_info_prefix,
                item_names = extensions,
                title = "L O A D E D   A D D I T I O N A L   E X T E N S I O N S",
                no_extensions_found_msg = "No --additional-extensions found -> nothing to load -> OK")
        # ----------------- Debug prints -------------------------#


    def _register_extensions_from_flow_configuration(self, config: FlowConfiguration):
        extensions:List[str] = config.extensions

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

    def _loaded_items_print_info(self, prefix:str, item_names:List[str], title:str, no_extensions_found_msg:str):
        Util.print_header(prefix=prefix, text=title, level='info')

        if item_names and len(item_names) > 0:
            for item_name in item_names:
                logging.info(f'{prefix}{item_name}')
        else:
            logging.info(f'{prefix}{no_extensions_found_msg}')
        logging.info(f'{prefix}')



    def ___old_register_extensions_from_flow_configuration(self, config: FlowConfiguration):
        loaded_extension_names = []  # for debug prints

        extensions = config.extensions
        if extensions:
            for extension in extensions:
                [module_name, class_name] = extension.rsplit(".", 1)
                module = importlib.import_module(module_name)
                class_ = getattr(module, class_name)
                instance = class_()
                StateHandler.add_state_listener(instance)
                loaded_extension_names.append(extension)

        # ----------------- Debug prints -------------------------#
        if DebugConfig.print_loaded_extensions or DebugConfig.print_autor_info:
            Util.print_header(prefix=DebugConfig.autor_info_prefix, text="L O A D E D   E X T E N S I O N S   F R O M   C O N F I G U R A T I O N", level="info")
            if len(loaded_extension_names) > 0:
                for extension in loaded_extension_names:
                    logging.info(extension)
            else:
                logging.info("No extensions found in the flow configuration - OK,")
            logging.info("")

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
            Util.print_header(prefix, "L O A D E D   A C T I V I T Y   M O D U L E S   F R O M   C O N F I G U R A T I O N", level='info')
            if modules and len(modules) > 0:
                for module in modules:
                    logging.info(f'{prefix}{module}')
            else:
                logging.info(f'{prefix}No activity modules found in the flow configuration.')
            logging.info(prefix)

    # ---------------------- StateProducer implementation -----------------------#
    # fmt: off
    # pylint: disable=line-too-long
    def on_before_state(self, state_name, state_data:dict) -> None:

        # General
        state_data[sta.ADDITIONAL_EXTENSIONS]           = self._additional_extensions
        state_data[sta.CUSTOM_DATA]                     = self._custom_data
        state_data[sta.FLAGS]                           = self._flags
        state_data[sta.MODE]                            = self._mode

        # Flow
        state_data[sta.FLOW_ID]                     = self._flow_id
        state_data[sta.FLOW_CONFIG_URL]             = self._flow_config_url
        state_data[sta.FLOW_RUN_ID]                 = self._flow_run_id
        state_data[sta.FLOW_CONFIG]                 = self._flow_config
        state_data[sta.FLOW_CONTEXT]                = self._flow_context

        # Activity Block
        state_data[sta.ACTIVITY_BLOCK_ID]                   = self._activity_block_id
        state_data[sta.ACTIVITY_BLOCK_RUN_ID]               = self._activity_block_run_id
        state_data[sta.ACTIVITY_BLOCK_CONFIG]               = self._activity_block_config
        state_data[sta.ACTIVITY_BLOCK_CONTEXT]              = self._activity_block_context
        state_data[sta.ACTIVITY_BLOCK_ACTIVITIES]           = self._activity_block_activities
        state_data[sta.ACTIVITY_BLOCK_CALLBACK_EXCEPTIONS]  = self._activity_block_callback_exceptions
        state_data[sta.ACTIVITY_BLOCK_STATUS]               = self._activity_block_status
        state_data[sta.ACTIVITY_BLOCK_INTERRUPTED]          = self._activity_block_interrupted
        state_data[sta.ACTIVITY_BLOCK_LATEST_ACTIVITY]      = self._activity_block_latest_activity

        state_data[sta.ACTIVITY_BLOCK_CONFIGS_MAIN_ACTIVITIES]  = self._activity_block_configs_main_activities
        state_data[sta.ACTIVITY_BLOCK_CONFIGS_BEFORE_BLOCK]     = self._activity_block_configs_before_block
        state_data[sta.ACTIVITY_BLOCK_CONFIGS_AFTER_BLOCK]      = self._activity_block_configs_after_block
        state_data[sta.ACTIVITY_BLOCK_CONFIGS_BEFORE_ACTIVITY]  = self._activity_block_configs_before_activity
        state_data[sta.ACTIVITY_BLOCK_CONFIGS_AFTER_ACTIVITY]   = self._activity_block_configs_after_activity



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
            state_data[sta.INTERNAL_ACTIVITY_DATA]  = self._activity_data
            state_data[sta.ACTIVITY_ID]         = self._activity_data.activity_id
            state_data[sta.ACTIVITY_RUN_ID]     = self._activity_data.activity_run_id
            state_data[sta.ACTIVITY_NAME]       = self._activity_data.activity_name
            state_data[sta.ACTIVITY_GROUP_TYPE] = self._activity_data.activity_group_type
            state_data[sta.ACTIVITY_CONFIG]     = self._activity_data.activity_config
            state_data[sta.ACTIVITY_TYPE]       = self._activity_data.activity_type
            state_data[sta.ACTION]              = self._activity_data.action

            if self._activity_data.activity is not None:
                state_data[sta.ACTIVITY_INSTANCE] = self._activity_data.activity


        # Debug
        state_data[sta.DBG_EXTENSION_TEST_STR] = self._dbg_extension_test_str


    def on_after_state(self, state_name, state_data:dict) -> None:

        # General
        self._additional_extensions             = state_data[sta.ADDITIONAL_EXTENSIONS]
        self._custom_data                       = state_data[sta.CUSTOM_DATA]
        self._flags                             = state_data[sta.FLAGS]
        self._mode                              = state_data[sta.MODE]

        # Flow
        self._flow_id                   = state_data[sta.FLOW_ID]
        self._flow_config_url           = state_data[sta.FLOW_CONFIG_URL]
        self._flow_run_id               = state_data[sta.FLOW_RUN_ID]
        self._flow_config               = state_data[sta.FLOW_CONFIG]
        self._flow_context              = state_data[sta.FLOW_CONTEXT]

        # Activity Block
        self._activity_block_id                     = state_data[sta.ACTIVITY_BLOCK_ID]
        self._activity_block_run_id                 = state_data[sta.ACTIVITY_BLOCK_RUN_ID]
        self._activity_block_context                = state_data[sta.ACTIVITY_BLOCK_CONTEXT]
        self._activity_block_config                 = state_data[sta.ACTIVITY_BLOCK_CONFIG]
        self._activity_block_activities             = state_data[sta.ACTIVITY_BLOCK_ACTIVITIES]
        self._activity_block_callback_exceptions    = state_data[sta.ACTIVITY_BLOCK_CALLBACK_EXCEPTIONS]
        self._activity_block_status                 = state_data[sta.ACTIVITY_BLOCK_STATUS]
        self._activity_block_interrupted            = state_data[sta.ACTIVITY_BLOCK_INTERRUPTED]
        self._activity_block_latest_activity        = state_data[sta.ACTIVITY_BLOCK_LATEST_ACTIVITY]

        self._activity_block_configs_main_activities    = state_data[sta.ACTIVITY_BLOCK_CONFIGS_MAIN_ACTIVITIES]
        self._activity_block_configs_before_block       = state_data[sta.ACTIVITY_BLOCK_CONFIGS_BEFORE_BLOCK]
        self._activity_block_configs_after_block        = state_data[sta.ACTIVITY_BLOCK_CONFIGS_AFTER_BLOCK]
        self._activity_block_configs_before_activity    = state_data[sta.ACTIVITY_BLOCK_CONFIGS_BEFORE_ACTIVITY]
        self._activity_block_configs_after_activity     = state_data[sta.ACTIVITY_BLOCK_CONFIGS_AFTER_ACTIVITY]


        # Mode: ACTIVITY
        self._activity_module   = state_data[sta.ACTIVITY_MODULE]
        self._activity_type     = state_data[sta.ACTIVITY_TYPE]
        self._activity_config   = state_data[sta.ACTIVITY_CONFIG]
        self._input    = state_data[sta.INPUT]

        # Mode: ACTIVITY-IN-BLOCK
        self._activity_name_special     = state_data[sta.ACTIVITY_NAME_SPECIAL]
        self._activity_id_special = state_data[sta.ACTIVITY_ID_SPECIAL]

        # Activity
        if self._activity_data is not None:
            self._activity_data                     = state_data[sta.INTERNAL_ACTIVITY_DATA]
            self._activity_data.activity_id         = state_data[sta.ACTIVITY_ID]
            self._activity_data.activity_run_id     = state_data[sta.ACTIVITY_RUN_ID]
            self._activity_data.activity_name       = state_data[sta.ACTIVITY_NAME]
            self._activity_data.activity_group_type = state_data[sta.ACTIVITY_GROUP_TYPE]
            self._activity_data.activity_config     = state_data[sta.ACTIVITY_CONFIG]
            self._activity_data.activity_type       = state_data[sta.ACTIVITY_TYPE]
            self._activity_data.action              = state_data[sta.ACTION]

            if sta.ACTIVITY_INSTANCE in state_data:
                self._activity_data.activity        = state_data[sta.ACTIVITY_INSTANCE]

        # Debug
        self._dbg_extension_test_str = state_data[sta.DBG_EXTENSION_TEST_STR]

    # fmt: on
    # pylint: enable=line-too-long

    def get_context(self) -> Context:
        return self._flow_context

    def get_activity_context(self, activity_id:str) -> Context:
        return Context(activity_block=self._activity_block_id,activity=activity_id)

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


    def _create_debug_input_string(self, args, values):
        first_param_detected = False
        for i,name in enumerate(args):
            val = str(values[name])
            if i > 0 and val != "None" and val != "{}" and val != "[]":
                if not first_param_detected:
                    self._debug_input_str = val
                    first_param_detected = True
                else:
                    if name == "flow_config_url":
                        pass
                    elif name == "flow_run_id":
                        self._debug_input_str = self._debug_input_str + self._debug_separator + name
                    else:
                        self._debug_input_str = self._debug_input_str + self._debug_separator + val
