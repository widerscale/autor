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
import humps

from autor.activity import Activity
import autor.framework.autor_framework_activities
from autor.framework.activity_data import ActivityData
from autor.framework.activity_factory import ActivityFactory
from autor.framework.check import Check
from autor.framework.constants import Action, ExceptionType, Status, ContextPropertyPrefix
from autor.framework.context_properties_handler import ContextPropertiesHandler
from autor.framework.debug_config import DebugConfig
from autor.framework.exception_handler import ExceptionHandler
from autor.framework.keys import FlowContextKeys as ctx
from autor.framework.logging_config import LoggingConfig
from autor.framework.state_handler import StateHandler
from autor.framework.state_listener import State
from autor.framework.util import Util

# Keys are populated dynamically
# pylint: disable=no-member


# Activity runner handles running of one activity.
class ActivityRunner:
    """
    ActivityRunner handles running of one activity.
    It creates the activity, runs it.
    """

    def __init__(self):
        self._data:ActivityData = None
        self._need_to_abort = False  # If Autor cannot be run in a meaningful way after an exception, set this to True
        self._need_to_abort_reason = ""
        self._activity_processing_error_occurred = False # An exception outside Activity.run() due to problem with activity.
        self._activity_run_exception_occurred = False  # An exception inside Activity.run()
        self._data:ActivityData = None
        self._context_properties_handler = None

    def run_activity(self, data: ActivityData):
        self._data = data
        self._preprocess()
        self._run()
        self._postprocess()

        return self._need_to_abort, self._need_to_abort_reason

    def _ok_to_run(self):
        # An activity will be run only if it is allowed by the framework and by the configuration
        #  AND no error has occurred.
        ok = (
            not self._need_to_abort
            and not self._activity_processing_error_occurred
            and not self._activity_run_exception_occurred
            and (self._data.action != Action.SKIP_BY_FRAMEWORK)
            and (self._data.action != Action.SKIP_BY_CONFIGURATION)
            and (self._data.action != Action.KEEP_AS_IS)
        )

        return ok

    def _preprocess(self):
        try:
            # self._data.activity = Activity()  # Default value in case the activity creation fails

            # ----------------------------------------------------------------#
            StateHandler.change_state(State.BEFORE_ACTIVITY_PREPROCESS)
            # ----------------------------------------------------------------#

            Check.not_none(self._data.action, "Action not provided in the activity data.")

            # Create activity
            self._create_activity()  # Can set activity status to ERROR

            # Create ContextPropertiesHandler (can also be used by Activity)
            self._context_properties_handler = ContextPropertiesHandler(
                self._data.activity,
                input_context=self._data.input_context,
                output_context=self._data.output_context,
                config = self._data.activity_config.configuration)
            #self._data.output_context_properties_handler = self._context_properties_handler

            # Load activity properties.
            self._load_activity_properties()

            # Save the loaded properties for reference int the data object. Used for report creation.
            self._data.inputs  = self._context_properties_handler.get_input_properties_values()
            self._data.configs = self._context_properties_handler.get_config_properties_values()

            # Set activity arguments
            self._data.activity.set_arguments(self._data)

        finally:
            if self._data.action in (Action.SKIP_BY_FRAMEWORK, Action.SKIP_BY_CONFIGURATION):
                self._data.activity.status = Status.SKIPPED
                self._print("skipping activity...")
            elif self._data.action == Action.KEEP_AS_IS:
                self._data.activity.status = self._data.output_context.get(ctx.STATUS, default=Status.UNKNOWN)  # Keep the same status
                self._print("keeping activity data from previous run unchanged...")
            elif self._activity_processing_error_occurred:
                self._data.activity.status = Status.ERROR
                self._print("Not calling activity run() due to problems creating the activity or loading inputs/configurations for the activity...")
            elif self._need_to_abort:
                self._data.activity.status = Status.ERROR
                self._print("skipping activity due to an error (likely Autor framework error)...")



    def _print_activity_started(self):
        arrow = "> "
        logging.info(f'{DebugConfig.autor_info_prefix}Activity Started')
        logging.info(f'{DebugConfig.autor_info_prefix}{arrow}Name:  {self._data.activity_name}')
        logging.info(f'{DebugConfig.autor_info_prefix}{arrow}Type:  {self._data.activity_type}')
        logging.info(f'{DebugConfig.autor_info_prefix}{arrow}Class: {self._data.activity.__class__.__name__}')


    def _run(self):

        if self._ok_to_run():
            try:
                # ----------------------------------------------------------------#
                StateHandler.change_state(State.BEFORE_ACTIVITY_RUN)
                # ----------------------------------------------------------------#
                activity_full_class_name:str = f"{self._data.activity.__module__}.{self._data.activity.__class__.__name__}"
                logging.info(f'{DebugConfig.autor_info_prefix}')
                logging.info(f'{DebugConfig.autor_info_prefix}')
                self._print_activity_inputs_and_configs()
                logging.info(f"{DebugConfig.autor_info_prefix}---------> Started activity: [Name:{self._data.activity_name} Type:{self._data.activity_type}, Class:{activity_full_class_name}] -------->")
                #logging.info(f'{DebugConfig.autor_info_prefix}')
                #logging.info(f'{DebugConfig.autor_info_prefix}Started activity name:  {self._data.activity_name}')
                #logging.info(f'{DebugConfig.autor_info_prefix}Started activity type:  {self._data.activity_type}')
                #logging.info(f'{DebugConfig.autor_info_prefix}Started activity class: {activity_full_class_name}')


                LoggingConfig.activate_activity_logging()
                if DebugConfig.print_activity:
                    self._data.activity.print()
                self._data.activity.run()
                LoggingConfig.activate_framework_logging()

                #logging.info(f'{DebugConfig.autor_info_prefix}')
                logging.info(f"{DebugConfig.autor_info_prefix}<-------- Finished activity: [Name:{self._data.activity_name} Type:{self._data.activity_type}, Class:{activity_full_class_name}] <--------")


            except Exception as e:
                LoggingConfig.activate_framework_logging()
                logging.warning(f"Exception caught during activity run: {e.__class__.__name__}: {str(e)}")
                self._activity_run_exception_occurred = True
                self._register_error(e, ExceptionType.ACTIVITY_RUN, description=f"Exception caught during activity run: {e.__class__.__name__}: {str(e)}")
            finally:

                # ----------------------------------------------------------------#
                StateHandler.change_state(State.AFTER_ACTIVITY_RUN)
                # ----------------------------------------------------------------#

    def _print_activity_inputs_and_configs(self):
        props:dict = self._data.output_context.get(ContextPropertyPrefix.props)
        for key,val in props.items():
            if isinstance(val, str):
                self._trim_string(val)

            if key.startswith(ContextPropertyPrefix.inp_default):
                logging.info(f"{DebugConfig.autor_info_prefix}input   (default): {key.replace(ContextPropertyPrefix.inp_default,'')}={val}")
            if key.startswith(ContextPropertyPrefix.inp_provide):
                logging.info(f"{DebugConfig.autor_info_prefix}input  (provided): {key.replace(ContextPropertyPrefix.inp_provide,'')}={val}")
            if key.startswith(ContextPropertyPrefix.cfg_default):
                logging.info(f"{DebugConfig.autor_info_prefix}config  (default): {key.replace(ContextPropertyPrefix.cfg_default,'')}={val}")
            if key.startswith(ContextPropertyPrefix.cfg_provide):
                logging.info(f"{DebugConfig.autor_info_prefix}config (provided): {key.replace(ContextPropertyPrefix.cfg_provide,'')}={val}")

    def _print_activity_outputs(self):
        props: dict = self._data.output_context.get(ContextPropertyPrefix.props)
        for key, val in props.items():
            if isinstance(val, str):
                self._trim_string(val)
            if key.startswith(ContextPropertyPrefix.out_provide) and key != f"{ContextPropertyPrefix.out_provide}status":
                logging.info(f"{DebugConfig.autor_info_prefix}output: {key.replace(ContextPropertyPrefix.out_provide,'')}={val}")

    def _trim_string(self, string:str)->str:
        if len(string) > 100:
            string = string[0:90]
            string = f"{string} ..."
            return string


    def _postprocess(self):
        try:
            self._print("PRELIMINARY activity status: " + self._data.activity.status)
            # See rules: https://jira-dowhile.atlassian.net/l/c/zy6Q0oJ8

            if self._data.action != Action.KEEP_AS_IS:
                self._adjust_activity_status()

            if self._ok_to_run():
                logging.info(f'{DebugConfig.autor_info_prefix}Activity status: {self._data.activity.status}')
                #logging.info(DebugConfig.autor_info_prefix)


            # Add more data to the activity context.
            self._update_activity_context()

            # Save activity output properties
            if self._data.action != Action.KEEP_AS_IS:
                self._save_activity_properties(status_only = not self._ok_to_run()) # if something is wrong, we should only save status
                # Store the activity values in the data object.
                self._data.outputs = self._context_properties_handler.get_output_properties_values(status_only = not self._ok_to_run())
                self._print_activity_outputs()
                logging.info(DebugConfig.autor_info_prefix)


        except Exception as e:
            self._register_error(e, ExceptionType.ACTIVITY_POSTPROCESS, description="Exception during activity post-processing")

        finally:
            # ----------------------------------------------------------------#
            StateHandler.change_state(State.AFTER_ACTIVITY_POSTPROCESS)
            # ----------------------------------------------------------------#


    def _register_error(self, exception, ex_type: ExceptionType, description: str, context=None):

        if ex_type == ExceptionType.ACTIVITY_RUN:
            self._activity_run_exception_occurred = True
        elif ex_type == ExceptionType.ACTIVITY_CONFIGURATION or ex_type == ExceptionType.ACTIVITY_INPUT or ex_type == ExceptionType.ACTIVITY_OUTPUT:
            self._activity_processing_error_occurred = True
        else:
            if self._need_to_abort is not True:
                self._need_to_abort = True
                self._need_to_abort_reason = description

        # Crete custom data to save with the error.
        custom = {ctx.ACTIVITY_ID: self._data.activity_id}
        if self._data.activity is not None:
            self._data.activity.status = Status.ERROR
            custom[ctx.ACTIVITY_STATUS] = Status.ERROR

        ExceptionHandler.register_exception(
            ex=exception,
            ex_type=ex_type,
            description=description,
            context=context,
            custom=custom)

    def _create_activity(self):
        try:
            self._data.activity = ActivityFactory.create(self._data.activity_type)
        except Exception as e:
            self._register_error(e, ExceptionType.ACTIVITY_CREATION,description=f"Failed to create activity of type: {self._data.activity_type}")
            try:
                self._data.activity = ActivityFactory.create("exception")
            except Exception as e:
                self._register_error(e, ExceptionType.INTERNAL, description="Could not create a special 'exception' activity to handle a previous exception.")

    def _load_activity_properties(self):
        #handler = ContextPropertiesHandler(self._data.activity, context=self._data.input_context, config=self._data.activity_config.configuration)

        try:
            # If the framework has decided that the activity status is ERROR,
            #  no input parameter checks should be performed.
            self._context_properties_handler.load_config_properties(check_mandatory_properties=self._ok_to_run())
        except Exception as e:
            self._register_error(e, ExceptionType.ACTIVITY_CONFIGURATION, description="Exception loading activity configuration properties.")

        # Ok to continue after failing with configuration in the previous step -> gives us more information in case there are problems.
        try:
            self._context_properties_handler.load_input_properties(check_mandatory_properties=self._ok_to_run())
        except Exception as e:
            self._register_error(e, ExceptionType.ACTIVITY_INPUT, description="Exception loading activity input properties.")

    def _save_activity_properties(self, status_only:bool):
        status = self._data.activity.status

        try:
            # Save activity output properties to context and push the context to remote.
            # Mandatory output properties are required only from the activities with the status
            #  SUCCESS.
            self._context_properties_handler.save_output_properties(mandatory_outputs_check=(status == Status.SUCCESS), save_status_only=status_only)
        except Exception as e:
            self._register_error(e, ExceptionType.ACTIVITY_OUTPUT, description="Could not save activity output properties")





    def _update_activity_context(self):
        activity = self._data.activity
        context = self._data.output_context
        action = self._data.action

        # Sanity check
        if action in (Action.SKIP_BY_FRAMEWORK, Action.SKIP_BY_CONFIGURATION):
            Check.is_true(
                activity.status == Status.SKIPPED,
                (
                    "Unexpected activity status: {}. Action SKIPPED_BY_FRAMEWORK or "
                    + "SKIPPED_BY_CONFIGURATION should always lead to activity status SKIPPED"
                ),
            )


        # Add the action to the context
        context.set(ctx.ACTION, action)

    def _adjust_activity_status(self):
        # If an activity statys is UNKNOWN then it can mean either that
        # - an exception occurred and the activity did not manage to set the status OR
        # - an activity was successful, but did not explicitly set the status (in that case the default status is SUCCESS)
        #
        if self._data.activity.status == Status.UNKNOWN:
            if self._activity_run_exception_occurred:
                self._data.activity.status = Status.ERROR
            else:
                self._data.activity.status = Status.SUCCESS

    # pylint: disable-next=no-self-use
    def _print(self, text):
        if DebugConfig.trace_activity_processing:
            logging.info(f"{DebugConfig.activity_processing_trace_prefix}{str(text)}")
