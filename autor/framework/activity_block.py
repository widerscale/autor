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

# The entry point to Autor
# Call run() to run Autor.

import importlib
import logging
import uuid
from typing import List
from urllib.request import url2pathname

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
    Status,
)
from autor.framework.context import Context
from autor.framework.debug_config import DebugConfig
from autor.framework.keys import FlowConfigurationKeys as cfg
from autor.framework.keys import FlowContextKeys as ctx
from autor.framework.keys import StateKeys as sta
from autor.framework.keys import ArgParserKeys as arg
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
        flow_config_url: str = None,
        activity_block_id: str = None,
        flow_run_id: str = None,
        activity_name: str = None,
        additional_extensions: list = None,
        custom_data: dict = {},
        activity_module: str = None,   # mode: ACTIVITY
        activity_type: str = None,     # mode: ACTIVITY
        activity_input: dict = {},     # mode: ACTIVITY
        activity_config: dict = {}     # mode: ACTIVITY
    ):
        """
        Autor constructor lists all autor attributes and initiates
        the ones that con be initiated.

        The following attributes can be overriden in state BOOTSTRAP:
        - self._flow_config_url
        - self._activity_block_id
        - self._flow_run_id
        - self._activity_name

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



        #------------------------- mode: ACTIVITY ------------------------------#
        self._activity_module: str = activity_module   # mode: ACTIVITY
        self._activity_type: str = activity_type     # mode: ACTIVITY
        self._activity_input: dict = activity_input     # mode: ACTIVITY
        self._activity_config: dict = activity_config     # mode: ACTIVITY
        # ------------------------- mode: ACTIVITY ------------------------------#



        # Extension classes that should be added to the extensions
        # provided in the flow configuration.
        # These additional extensions will be able to get on_bootstrap()
        # callbacks, that is not available for the extensions provided
        # through flow configuration.
        if additional_extensions is None:
            self._additional_extensions = []
        else:
            self._additional_extensions:list = additional_extensions

        # Any data that the user of Autor would like to provide for
        # extensions.
        self._custom_data:dict = custom_data


        # True, if the activity block has been aborted by the framework
        self._autor_aborted = False
        self._autor_aborted_reason = ""

        # The name of the activity to run.
        # Used only in Autor runs when only one activity is run.
        self._activity_name = activity_name # Can be overriden by extensions in state BOOTSTRAP




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
        self._mode = None




        # ----------------------------------  F L O W   D A T A  -----------------------------------#

        # Attributes that may be OVERRIDEN in state BOOTSTRAP
        self._flow_run_id = flow_run_id
        self._flow_config_url = flow_config_url
        self._flow_run_id_generated = False # Will be set to true if Autor will generate the flow_run_id



        # Attributes that are INITIATED after state BOOTSTRAP
        self._flow_id = None          # Unique identifier of the flow provided by flow configuration.
        self._flow_context_id = None  # Unique identifier of a context for a flow run.
        self._flow_config = None      # The configuration object representing the whole flow.
        self._flow_context:Context = None     # Context, focused on the root (flow) level.


        # ------------------------------  A C T I V I T Y   B L O C K   D A T A   -----------------#

        self._activity_block_run_id = str(uuid.uuid4())
        self._activity_block_activities = [] # A list of activities that is created as the activities are run.
        self._activity_block_callback_exceptions = [] # [dict{str:str}] Exceptions in activity block callbacks.
        self._activity_block_status = Status.UNKNOWN # Current status of the activity block. Updated as the activities are run.
        self._activity_block_latest_activity = None # The latest activity that has been run (or skipped) in the activity block.
        # Set to true when the activity-block is considered to be interrupted
        #  (== before or main activities interrupted)
        self._activity_block_interrupted = False

        self._activity_block_config = None
        self._activity_block_configs_main_activities = None
        self._activity_block_configs_before_block    = None
        self._activity_block_configs_after_block     = None
        self._activity_block_configs_before_activity = None
        self._activity_block_configs_after_activity  = None
        self._activity_block_name = None

        self._before_block_activities = []
        self._before_activities = [] # Reset for each main-loop iteration
        self._main_activities = []
        self._after_activities = []
        self._after_block_activities = []
        self._activities_by_name = {}


        # Keep track of the configuration for the next main activity.
        self._next_main_index = 0


        # Attributes that may be OVERRIDEN in state BOOTSTRAP
        self._activity_block_id = activity_block_id

        # Attributes that are INITIATED after state BOOTSTRAP
        self._activity_block_context = None # Empty context focused on the activity block level


        # ---------------------------------  A C T I V I T Y   D A T A   --------------------------#
        self._activity_data:ActivityData = None # Contains activity data and the activity instance



        #---------------------------------- DEBUGGING SUPPORT -------------------------------------#
        # This value will be added to the state data for the extensions to play around with.
        # Key: DBG_EXTENSION_TEST_STR
        self._dbg_extension_test_str = ""


        # fmt: on

    def run(self) -> dict:
        try:
            self._set_up()
            self._run()
            self._tear_down()

        except Exception as e:
            self._register_exception(e, "Unhandled exception in Autor")

        finally:
            if self._autor_aborted:
                e = Util.get_abort_exception()

                logging.error("\n%s", Util.format_banner("A U T O R   A B O R T E D"))
                logging.error(f"Reason:     {self._autor_aborted_reason}")
                logging.error(f"Exception:  {str(e)}")
                logging.error("Stacktrace:", exc_info=e)
                logging.error("\n%s", "-" * 100)

            logging.info(f'{DebugConfig.autor_info_prefix}Activity block status: {self._activity_block_status}')

            # Print all exceptions that occurred during the run
            Util.print_all_exceptions()



    def _set_up(self):
        try:
            if DebugConfig.print_autor_info:
                self._print_input_args_before_bootstrap()

            # Register extensions that were provided through arguments or that
            # are needed internally in Autor framework.
            self._register_bootstrap_extensions(self._additional_extensions)

            StateHandler.add_state_producer(self)
            # ---------------------------------------------------------------#
            StateHandler.change_state(State.BOOTSTRAP)
            # ---------------------------------------------------------------#

            if DebugConfig.print_final_input or DebugConfig.print_autor_info:
                self._print_input_args_after_bootstrap()


            # Initiate attributes that may be affected by changes done in
            # state BOOTSTRAP.
            self._initiate_autor_mode()
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
            self._create_activities_configurations()

        except Exception as e:
            self._register_exception(
                e, "Unhandled exception during Autor set up", ExceptionType.SET_UP
            )

    def _run(self):
        if self._autor_aborted:
            logging.info("Autor aborted -> not running any activities")
            return

        # Run activities
        try:
            # ---------------------------------------------------------------#
            StateHandler.change_state(State.BEFORE_ACTIVITY_BLOCK)
            # ---------------------------------------------------------------#
            self._print_activity_block_started()
            if DebugConfig.print_context_before_activities_are_run:
                self._flow_context.print_context("Context before activities are run")
            self._run_activity_block()

        except Exception as e:
            self._register_exception(
                e,
                "Unhandled exception during activity block execution",
                ExceptionType.ACTIVITY_BLOCK,
            )

        # Run callbacks
        try:
            # ---------------------------------------------------------------#
            StateHandler.change_state(State.BEFORE_ACTIVITY_BLOCK_CALLBACKS)
            # ---------------------------------------------------------------#
            self._run_activity_block_callbacks()
        except Exception as e:
            self._register_exception(
                e,
                "Unhandled exception during activity block callbacks execution",
                ExceptionType.ACTIVITY_BLOCK,
            )

        # Finalize activity block run
        try:
            # ---------------------------------------------------------------#
            StateHandler.change_state(State.AFTER_ACTIVITY_BLOCK)
            # ---------------------------------------------------------------#
            self._activity_block_context.set(ctx.ACTIVITY_BLOCK_STATUS, self._activity_block_status)
            if len(self._activity_block_callback_exceptions) > 0:
                self._activity_block_context.set(
                    ctx.CALLBACK_EXCEPTIONS, self._activity_block_callback_exceptions
                )
            self._flow_context.sync_remote()

            if DebugConfig.print_context_on_finished:
                self._flow_context.print_context("Context at the end of the activity block run")

        except Exception as e:
            self._register_exception(
                e,
                "Unhandled exception during activity block finalization",
                ExceptionType.ACTIVITY_BLOCK,
            )

        finally:
            self._print_activity_block_finished()

    def _tear_down(self):

        # Remove all listeners
        try:
            # ---------------------------------------------------------------#
            StateHandler.change_state(State.FRAMEWORK_END)
            # ---------------------------------------------------------------#
            StateHandler().remove_all_listeners()
            # logging.debug(f"FLOW ID: {self._flow_id}")

        except Exception as e:
            self._register_exception(
                e, "Unhandled exception during Autor tear down", ExceptionType.TEAR_DOWN
            )

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
        if self._activity_module is not None:
            self._mode = Mode.ACTIVITY
            Check.is_non_empty_string(self._flow_config_url)
            Check.is_non_empty_string(self._activity_block_id)

        elif self._activity_name is not None:
            self._mode = Mode.ACTIVITY_IN_BLOCK
            Check.is_non_empty_string(self._flow_config_url)
            Check.is_non_empty_string(self._activity_block_id)

        else:
            self._mode = Mode.ACTIVITY_BLOCK
            Check.is_non_empty_string(self._flow_config_url)
            Check.is_non_empty_string(self._activity_block_id)


    def _initiate_flow(self):
        # If flow_run_id is provided, then we already have an existing flow and
        # this Autor run is not the first activity block run in the flow.
        # If flow_run_id is not provided, then it is the first job in a flow and
        # a new flow_run_id needs to be created.
        if self._flow_run_id is None:
            self._flow_run_id = str(uuid.uuid4())
            self._flow_run_id_generated = True

        # Fetch the flow configuration
        self._flow_config = self._get_flow_configuration()
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



    def _print_input_args_before_bootstrap(self):
        prefix = DebugConfig.autor_info_prefix
        Util.print_header(prefix, "C O M M A N D - L I N E   A R G U M E N T S", level='info')
        logging.info(f'{prefix}flow_run_id:           {self._flow_run_id}')
        logging.info(f'{prefix}flow_config_url:       {self._flow_config_url}')
        logging.info(f'{prefix}activity_block_id:     {self._activity_block_id}')
        logging.info(f'{prefix}activity_name:         {self._activity_name}')
        logging.info(f'{prefix}additional_extensions: {self._additional_extensions}')
        logging.info(f'{prefix}custom_data:           {self._custom_data}')
        logging.info(f'{prefix}')

    def _print_input_args_after_bootstrap(self):
        prefix = DebugConfig.autor_info_prefix
        Util.print_header(prefix, "I N P U T S", level='info')
        logging.info(f'{prefix}flow_run_id:           {self._flow_run_id}')
        logging.info(f'{prefix}flow_config_url:       {self._flow_config_url}')
        logging.info(f'{prefix}activity_block_id:     {self._activity_block_id}')
        logging.info(f'{prefix}activity_name:         {self._activity_name}')
        logging.info(f'{prefix}additional_extensions: {self._additional_extensions}')
        logging.info(f'{prefix}custom_data:           {self._custom_data}')
        logging.info(f'{prefix}')


    def _print_activity_block_started(self):
        prefix = DebugConfig.autor_info_prefix
        Util.print_header(prefix, 'A C T I V I T Y   B L O C K   S T A R T E D', level='info')
        padding = 70
        logging.info(f'{prefix}mode:                  {self._mode}')
        if self._mode == Mode.ACTIVITY:
            logging.info(f'{prefix}flow_run_id:           {self._flow_run_id}'.ljust(padding) + ' (generated by Autor)')
            logging.info(f'{prefix}activity_module:       {self._activity_module}')
            logging.info(f'{prefix}activity_type:         {self._activity_type}')
            logging.info(f'{prefix}activity_input:        {self._activity_input}')
            logging.info(f'{prefix}activity_config:       {self._activity_config}')
            logging.info(f'{prefix}additional_extensions: {self._additional_extensions}')
            logging.info(f'{prefix}custom_data:           {self._custom_data}')
            logging.info(f'{prefix}activity_block_id:     {self._activity_block_id}'.ljust(padding) + ' (generated by Autor)')
            logging.info(f'{prefix}activity_name:         {self._activity_name}'.ljust(padding) + ' (generated by Autor)')
            logging.info(f'{prefix}flow_config_url:       {self._flow_config_url}'.ljust(padding) + ' (generated by Autor)')

        else:
            logging.info(f'{prefix}additional_extensions: {self._additional_extensions}')
            logging.info(f'{prefix}custom_data:           {self._custom_data}')
            logging.info(f'{prefix}activity_block_id:     {self._activity_block_id}'.ljust(padding) + ' (generated by Autor)')
            logging.info(f'{prefix}flow_config_url:       {self._flow_config_url}'.ljust(padding) + ' (generated by Autor)')
            if self._flow_run_id_generated:
                logging.debug(f'{prefix}flow_run_id:           {self._flow_run_id}'.ljust(padding) + ' (generated by Autor)')
            else:
                logging.debug(f'{prefix}flow_run_id:           {self._flow_run_id}')

        logging.info(f'{prefix}')


    def _print_activity_block_finished(self):
        prefix = DebugConfig.autor_info_prefix
        Util.print_header(prefix, 'A C T I V I T Y   B L O C K   F I N I S H E D', level='info')
        logging.info(f'{prefix}flow_run_id:           {self._flow_run_id}')
        logging.info(f'{prefix}activity_block_run_id: {self._activity_block_run_id}')
        logging.info(f'{prefix}flow_id:               {self._flow_id}')
        logging.info(f'{prefix}activity_block_id:     {self._activity_block_id}')
        logging.info(f'{prefix}activity_block_status: {self._activity_block_status}')
        logging.info(f'{prefix}')


    # pylint: disable-next=redefined-builtin
    def _register_exception(self, e, description, type=None, abort_autor=True):
        # Sanity check
        if self._autor_aborted:
            Check.is_true(
                self._activity_block_status == Status.ABORTED,
                (
                    "An activity block that has been aborted by the framework should always have"
                    + f" status: {Status.ABORTED}."
                    + f" Current block status: {self._activity_block_status}"
                ),
            )

        if abort_autor and not self._autor_aborted:
            self._abort_autor(str(description))

        Util.register_exception(ex=e, description=description, type=type)

    def _get_flow_configuration(self):
        # TODO: Refactor, don't assume file URL
        flow_config = load_flow_configuration(self._flow_config_url)
        return flow_config

    def _force_run_activity(self, activity_block_id: str, activity_name: str):
        self._create_activities_configurations()

        activity_block_config = self._flow_config.activity_block(activity_block_id)
        activity_config = activity_block_config.activity(activity_name)
        Check.not_none(activity_config)
        self._run_activity(activity_name, None, None, activity_config=activity_config)

    def _print_activity_preparation_msg(self, activity_name, activity_id, activity_group_type, activity_type):
        # fmt: off
        if DebugConfig.print_selected_activity:
            prefix = DebugConfig.selected_activity_prefix
            Util.print_header(prefix, "S E L E C T E D   A C T I V I T Y")
            logging.debug(f"{prefix}ACTIVITY_ID:                {activity_id}")
            logging.debug(f"{prefix}ACTIVITY_NAME:              {activity_name}")
            logging.debug(f"{prefix}ACTIVITY_TYPE:              {activity_type}")
            logging.debug(f"{prefix}ACTIVITY_GROUP_TYPE:        {activity_group_type}")
            logging.debug(f"{prefix}ACTIVITY_BLOCK_INTERRUPTED: {self._activity_block_interrupted}")
            logging.debug(f"{prefix}")
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
            self._activity_block_name = self._activity_block_config.name
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

    def _create_data(self, activity_id, activity_group_type, activity_config):  # -> ActivityData

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
        data.context =                  Context(activity_block=data.activity_block_id, activity=data.activity_id)
        #data.context = Context()
        data.activity_context = ActivityContext(activity_block=data.activity_block_id, activity=data.activity_id)

        if activity_group_type == ActivityGroupType.BEFORE_ACTIVITY:
            Check.is_true(
                len(self._activity_block_configs_main_activities) > self._next_main_index,
                "No main acivity configuration exists for the before activity.",
            )
            next_main_conf = self._activity_block_configs_main_activities[self._next_main_index]
            data.next_main_activity_data = self._create_data(
                "_NEXT_MAIN_ACTIVITY", ActivityGroupType.MAIN_ACTIVITY, next_main_conf
            )

        return data

    def _update_activity_lists(
        self, activity, activity_config, activity_group_type
    ):  # TODO take from data object
        self._activity_block_activities.append(activity)
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

    def _update_activity_block_status(self, rules, error_occurred):

        data = self._activity_data

        if (
            self._activity_block_interrupted is False
        ):  # Once the activity block has been interrupted it will remain interrupted.
            if error_occurred:
                self._activity_block_interrupted = True  # All framework and framework usage errors
                data.interrupted = self._activity_block_interrupted
            else:
                self._activity_block_interrupted = not rules.continue_on(data)
                data.interrupted = self._activity_block_interrupted

        self._activity_block_status = rules.get_activity_block_status(data, self._autor_aborted)
        data.activity_block_status = self._activity_block_status

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

    def _run_activity(self, activity_name, activity_id, activity_group_type, activity_config):

        rules = ActivityBlockRules()
        self._activity_data = self._create_data(activity_id, activity_group_type, activity_config)

        # ---------------------------------------------------------------------#
        StateHandler.change_state(State.SELECT_ACTIVITY)
        # ---------------------------------------------------------------------#

        # Run the activities in the activity block according to Autor rules.
        if self._mode == Mode.ACTIVITY_BLOCK or self._mode == Mode.ACTIVITY:
            self._activity_data.action = rules.get_action(self._activity_data, self._mode)

        # Only run the activity that should be run. Skip the rest.
        elif self._mode == Mode.ACTIVITY_IN_BLOCK:
            if activity_name == self._activity_name:
                self._activity_data.action = Action.RUN
            else:
                self._activity_data.action = Action.SKIP_BY_FRAMEWORK
        else:
            raise AutorFrameworkException(
                f"Autor mode: {self._mode} not supported in _run_activity()"
            )

        # -----------------   R U N   A C T I V I T Y   --------------------- #
        error_occurred = ActivityRunner().run_activity(self._activity_data)

        if error_occurred:
            self._abort_autor("Error occurred during activity run")

        self._update_activity_lists(
            self._activity_data.activity, activity_config, activity_group_type
        )
        self._update_activity_block_status(rules, error_occurred)

    def _run_activity_block(self):
        # Create an ordered list of data tuples that are needed for creating activities.
        # The order is the order in which the activities will be run.
        self._activity_block_status = (
            Status.SUCCESS
        )  # If an acivity block has intitiated corretly, the start status is SUCCESS.

        # --------------------- BEFORE-BLOCK ----------------------------#
        for act_conf_before_block in self._activity_block_configs_before_block:
            activity_id = (
                self._activity_block_name
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
                    self._activity_block_name
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
            activity_id = self._activity_block_name + "-" + main_name
            self._run_activity(
                act_conf_main.name, activity_id, ActivityGroupType.MAIN_ACTIVITY, act_conf_main
            )
            self._next_main_index = self._next_main_index + 1

            # ------------------------ AFTER-ACTIVITY ---------------------------#
            for act_conf_after in self._activity_block_configs_after_activity:
                activity_id = (
                    self._activity_block_name
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
                self._activity_block_name
                + "-"
                + self._get_activity_name(act_conf_after_block, ActivityGroupType.AFTER_BLOCK)
            )
            self._run_activity(
                self._activity_block_name,
                activity_id,
                ActivityGroupType.AFTER_BLOCK,
                act_conf_after_block,
            )

    _bb_counter = 0
    _ba_counter = 0
    _ma_counter = 0
    _aa_counter = 0
    _ab_counter = 0

    def _get_activity_name(self, conf, group):
        default_name = "lll"
        if self._mode == Mode.ACTIVITY:
            Check.is_non_empty_string(self._activity_name, "Autor mode: ACTIVITY requires activity_name, which should be provided by Autor's extension.")
            default_name= self._activity_name

        elif group == ActivityGroupType.BEFORE_BLOCK:
            ActivityBlock._bb_counter = ActivityBlock._bb_counter + 1
            default_name = cfg.BEFORE_BLOCK + str(ActivityBlock._bb_counter)

        elif group == ActivityGroupType.BEFORE_ACTIVITY:
            ActivityBlock._ba_counter = ActivityBlock._ba_counter + 1
            default_name = cfg.BEFORE_ACTIVITY + str(ActivityBlock._ba_counter)

        elif group == ActivityGroupType.MAIN_ACTIVITY:
            ActivityBlock._ma_counter = ActivityBlock._ma_counter + 1
            default_name = cfg.ACTIVITY + str(ActivityBlock._ma_counter)

        elif group == ActivityGroupType.AFTER_ACTIVITY:
            ActivityBlock._aa_counter = ActivityBlock._aa_counter + 1
            default_name = cfg.AFTER_ACTIVITY + str(ActivityBlock._aa_counter)

        elif group == ActivityGroupType.AFTER_BLOCK:
            ActivityBlock._ab_counter = ActivityBlock._ab_counter + 1
            default_name = cfg.AFTER_BLOCK + str(ActivityBlock._ab_counter)
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
            Util.print_header(prefix=DebugConfig.callbacks_trace_prefix, text="R U N N I N G   C A L L B A C K S   B L O C K")

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
                        logging.error(
                            "%s Callback exception during activity: %s. Exception: %s",
                            prefix,
                            activity.id,
                            exception,
                        )
                        Util.register_exception(
                            exception,
                            description=(
                                f"Callback exception during activity: {activity.id}."
                                + " Exception: {exception}"
                            ),
                            type=ExceptionType.ACTIVITY_BLOCK_CALLBACK,
                            framework_error=False,
                        )
                        self._activity_block_callback_exceptions.append(
                            self._create_callback_exception(callback, activity, exception)
                        )

                else:
                    if DebugConfig.trace_callbacks:
                        self._callback_debug_prints(callback, activity, prefix, run=False)

    def _callback_debug_prints(self, callback, activity, prefix, run):
        if run:
            logging.debug("")
            logging.debug(prefix + "%s______ R U N N I N G     c a l l b a c k  ______")
            logging.debug(prefix + "activity:  " + activity.id)
            logging.debug(prefix + "activity.status: " + activity.status)
            logging.debug(prefix + "callback.run_on: " + str(callback.run_on))
        else:
            logging.debug("")
            logging.debug(prefix + "______ I G N O R I N G   c a l l b a c k  _______")
            logging.debug(prefix + "activity:  " + activity.id)
            logging.debug(prefix + "activity.status: " + activity.status)
            logging.debug(prefix + "callback.run_on: " + str(callback.run_on))

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
            Util.print_header("A D D E D   E X T E N S I O N")
            logging.debug(f"{extension.__class__}")


    def _add_listeners(self, listeners:list):
        """
        Load and add the listeners in the list.
        """
        listener_names = []
        for listener in listeners:
            [module_name, class_name] = listener.rsplit(".", 1) # retrieve module name and class name
            module = importlib.import_module(module_name)       # import the module
            class_ = getattr(module, class_name)                # create the class
            instance = class_()                                 # create a listener instance of the class
            StateHandler.add_state_listener(instance)
        pass

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
                item_names = extensions,
                title = "L O A D E D   E X T E N S I O N S   F R O M   C O N F I G U R A T I O N",
                no_extensions_found_msg = "Flow configuration contains no extensions -> nothing to load -> OK")
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
            Util.print_header(
                "L O A D E D   E X T E N S I O N S   F R O M   C O N F I G U R A T I O N"
            )
            if len(loaded_extension_names) > 0:
                for extension in loaded_extension_names:
                    logging.debug(extension)
            else:
                logging.debug("No extensions found in the flow configuration - OK,")
            logging.debug("")

    def _unregister_extensions(self):
        StateHandler.remove_all_listeners()

    def _load_activity_modules(self, config: FlowConfiguration):
        modules = config.activity_modules
        if modules:
            for module in modules:
                module = importlib.import_module(module)

        # ----------------- Debug prints -------------------------#
        if DebugConfig.print_loaded_modules or DebugConfig.print_autor_info:
            prefix = DebugConfig.autor_info_prefix
            Util.print_header(prefix,
                (
                    "L O A D E D   A C T I V I T Y   M O D U L E S"
                    + "   F R O M   C O N F I G U R A T I O N"),
                    level='info'
            )
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
        state_data[sta.ADDITIONAL_EXTENSIONS]   = self._additional_extensions
        state_data[sta.CUSTOM_DATA]             = self._custom_data
        state_data[sta.MODE]                    = self._mode

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
        state_data[sta.ACTIVITY_INPUT] = self._activity_input

        # Mode: ACTIVITY-IN-Block
        state_data[sta.ACTIVITY_NAME] = self._activity_name


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
        self._additional_extensions   = state_data[sta.ADDITIONAL_EXTENSIONS]
        self._custom_data             = state_data[sta.CUSTOM_DATA]
        self._mode                    = state_data[sta.MODE]

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
        self._activity_input    = state_data[sta.ACTIVITY_INPUT]

        # Mode: ACTIVITY-IN-BLOCK
        self._activity_name     = state_data[sta.ACTIVITY_NAME]

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
