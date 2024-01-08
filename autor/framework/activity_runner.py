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

from autor.activity import Activity
from autor.framework.activity_data import ActivityData
from autor.framework.activity_factory import ActivityFactory
from autor.framework.autor_framework_activities import ReuseActivity, DummyActivity
from autor.framework.check import Check
from autor.framework.constants import Action, ExceptionType, Status
from autor.framework.context_properties_handler import ContextPropertiesHandler
from autor.framework.debug_config import DebugConfig
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
        self._framework_error_occurred = False  # An exception related to an error in Autor framework.
        self._activity_processing_error_occurred = False # An exception outside Activity.run() due to problem with activity.
        self._activity_run_exception_occurred = False  # An exception inside Activity.run()
        self._data:ActivityData = None

    def run_activity(self, data: ActivityData):
        self._data = data
        self._preprocess()
        self._run()
        self._postprocess()

        return self._framework_error_occurred

    def _ok_to_run(self):
        # An activity will be run only if it is allowed by the framework and by the configuration
        #  AND no error has occurred.
        ok = (
            not self._framework_error_occurred
            and not self._activity_processing_error_occurred
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
            self._data.output_context_properties_handler = ContextPropertiesHandler(self._data.activity, context=self._data.output_context)

            # Load activity properties.
            self._load_activity_properties()

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
                self._print("Not calling activitu run() due to problems creating the activity or loading inputs/configurations for the activity...")
            elif self._framework_error_occurred:
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
                self._register_error(e,description=f"Exception caught during activity run: {e.__class__.__name__}: {str(e)}", activity_run_error=True)
            finally:
                # ----------------------------------------------------------------#
                StateHandler.change_state(State.AFTER_ACTIVITY_RUN)
                # ----------------------------------------------------------------#

    def _postprocess(self):
        try:
            self._print("PRELIMINARY activity status: " + self._data.activity.status)
            # See rules: https://jira-dowhile.atlassian.net/l/c/zy6Q0oJ8

            if self._data.action != Action.KEEP_AS_IS:
                self._adjust_activity_status()

            if self._ok_to_run():
                logging.info(f'{DebugConfig.autor_info_prefix}Activity status: {self._data.activity.status}')
                logging.info(DebugConfig.autor_info_prefix)


            # Add more data to the activity context.
            self._update_activity_context()

            # Save activity output properties
            if self._data.action != Action.KEEP_AS_IS:
                self._save_activity_properties()


        except Exception as e:
            self._register_error(e, "Exception during activity post-processing", framework_error=True)

        finally:
            # ----------------------------------------------------------------#
            StateHandler.change_state(State.AFTER_ACTIVITY_POSTPROCESS)
            # ----------------------------------------------------------------#

    def _register_error(self, exception, description="", context=None, framework_error=False, activity_run_error=False, activity_processing_error=False):
        if framework_error:
            self._framework_error_occurred = True
        if activity_processing_error:
            self._activity_processing_error_occurred = True
        if activity_run_error:
            self._activity_run_exception_occurred = True

        # Crete custom data to save with the error.
        custom = {}
        custom[ctx.ACTIVITY_ID] = self._data.activity_id
        if self._data.activity is not None:
            self._data.activity.status = Status.ERROR
            custom[ctx.ACTIVITY_STATUS] = Status.ERROR

        Util.register_exception(
            ex=exception,
            type=ExceptionType.ACTIVITY,
            description=description,
            context=context,
            custom=custom,
            framework_error=framework_error,
        )

    def _create_activity(self):
        try:
            self._data.activity = ActivityFactory.create(self._data.activity_type)
        except Exception as e:
            self._data.activity = ActivityFactory.create("EXCEPTION")
            self._register_error(e, description="Failed to create activity", activity_processing_error=True)  # Framework rules not followed by the activity

    def _load_activity_properties(self):
        handler = ContextPropertiesHandler(self._data.activity, context=self._data.input_context, config=self._data.activity_config.configuration)

        try:
            # If the framework has decided that the activity status is ERROR,
            #  no input parameter checks should be performed.
            handler.load_config_properties(check_mandatory_properties=self._ok_to_run())
            handler.load_input_properties(check_mandatory_properties=self._ok_to_run())

        except Exception as e:
            self._register_error(e, "Exception loading activity input and/or configuration properties.", activity_processing_error=True)

    def _save_activity_properties(self):
        status = self._data.activity.status

        try:
            # Save activity output properties to context and push the context to remote.
            # Mandatory output properties are required only from the activities with the status
            #  SUCCESS.
            self._data.output_context_properties_handler.save_output_properties(mandatory_outputs_check=(status == Status.SUCCESS))
        except Exception as e:
            self._register_error(e, "Could not save activity output properties", activity_processing_error=True)

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
