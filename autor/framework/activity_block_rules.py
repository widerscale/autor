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

from autor.framework.activity_data import ActivityData
from autor.framework.autor_framework_exception import (
    AutorFrameworkException,
    AutorFrameworkNotImplementedException,
)
from autor.framework.check import Check
from autor.framework.constants import Action
from autor.framework.constants import ActivityGroupType as agt
from autor.framework.constants import Configuration, Mode, Status
from autor.framework.context import Context
from autor.framework.debug_config import DebugConfig
from autor.framework.keys import FlowConfigurationKeys as cfg
from autor.framework.keys import FlowContextKeys as ctx
from autor.framework.transition_summary import TransitionSummary
from autor.framework.util import Util







# pylint: disable=line-too-long,no-member, no-else-return

# A class that contains and evaluates rules for decision taking in Autor
#
# There are three public methods:
#
# continue_on() - Evaluates if the continueOn condition (provided in the activity configuration) for an activity is fulfilled.
#
# get_action()  - Decides what action (RUN/SKIP see Action) to perform on an activity that is picked for running.
#                 The decision is based on the activity configuration and on the history of previous activiy runs in the activity block.
#
# get_activity_block_status() - Calculates the activity block status based on the current status and the latest activity status.

# pylint: enable=line-too-long


class ActivityBlockRules:

    # Default configuration values for different activity group types.
    # Note that when an activity group type has a configuration that is None,
    # then that means that that group type is not allowed to have that configuration and if present
    # in the configuration, it will be considered as an error.

    # ----------------------------- continueOn --------------------------------#
    # If continueOn is not fulfilled, the activity block will be interrupted.

    # fmt: off
    d = {}
    DEFAULT_CONTINUE_ON = d
    d[agt.BEFORE_BLOCK]    = [Status.SUCCESS, Status.SKIPPED]
    d[agt.BEFORE_ACTIVITY] = [Status.SUCCESS, Status.SKIPPED]
    d[agt.MAIN_ACTIVITY]   = [Status.SUCCESS, Status.SKIPPED]
    d[agt.AFTER_ACTIVITY]  = [Status.SUCCESS, Status.SKIPPED]
    d[agt.AFTER_BLOCK]     = [Status.SUCCESS, Status.SKIPPED]




    # ------------------------------- runOn -------------------------------------#
    # If runOn is not fulfilled, the activity will be SKIPPED_BY_CONFIGURATION.

    DEFAULT_RUN_ON = {}


    d = {}
    DEFAULT_RUN_ON[agt.BEFORE_BLOCK] = d
    d[cfg.ACTIVITY_STATUS]       = {Configuration.ANY: [Status.ALL]}
    d[cfg.MAIN_ACTIVITY_STATUS]  = None # Not applicable
    d[cfg.ACTIVITY_BLOCK_STATUS] = None # Not applicable

    d = {}
    DEFAULT_RUN_ON[agt.BEFORE_ACTIVITY] = d
    d[cfg.ACTIVITY_STATUS]       = {Configuration.ANY:[Status.ALL]}
    d[cfg.MAIN_ACTIVITY_STATUS]  = None # Not applicable
    d[cfg.ACTIVITY_BLOCK_STATUS] = None # Not applicable

    d = {}
    DEFAULT_RUN_ON[agt.MAIN_ACTIVITY] = d
    d[cfg.ACTIVITY_STATUS]       = {Configuration.ANY: [Status.ALL]}
    d[cfg.MAIN_ACTIVITY_STATUS]  = None # Not applicable
    d[cfg.ACTIVITY_BLOCK_STATUS] = None # Not applicable

    d = {}
    DEFAULT_RUN_ON[agt.AFTER_ACTIVITY] = d
    d[cfg.ACTIVITY_STATUS]       = {Configuration.ANY: [Status.ALL]}
    d[cfg.MAIN_ACTIVITY_STATUS]  = [Status.ALL]
    d[cfg.ACTIVITY_BLOCK_STATUS] = None # Not applicable

    d = {}
    DEFAULT_RUN_ON[agt.AFTER_BLOCK] = d
    d[cfg.ACTIVITY_STATUS]       = {Configuration.ANY: [Status.ALL]}
    d[cfg.MAIN_ACTIVITY_STATUS]  = None # Not applicable
    d[cfg.ACTIVITY_BLOCK_STATUS] = [Status.ALL]

    _rerun_activated = False # static attribute used for mode ACTIVITY_BLOCK_RERUN
    _special_activity_detected = False # static attribute used for mode ACTIVITY_IN_BLOCK
    _transition_summary:TransitionSummary = TransitionSummary() # summary of activity block status changes

    @staticmethod
    def get_transition_summary() -> TransitionSummary:
        return ActivityBlockRules._transition_summary

    # fmt: on

    def __init__(self):
        # Used in mode ACTIVITY_BLOCK_RERUN. In this mode
        # The first activities are RE-USED until Autor
        # reaches the activity from which the RE-RUN should
        # start. Once this activity is reached _rerun_activated
        # is set to True

        self._max_len_activity_name = None  # For prints


    @staticmethod
    def reset_static_data():
        ActivityBlockRules._rerun_activated = False
        ActivityBlockRules._special_activity_detected = False
        ActivityBlockRules._transition_summary = TransitionSummary()

    # pylint: disable=invalid-name
    def _choose_most_important_action(self, a1, a2, a3):
        a = self._max(a1, a2)
        return self._max(a, a3)

    # pylint: disable-next=no-self-use
    def _max(self, action1: Action, action2: Action):

        # The order: RUN < SKP_BY_CONFIGURATION < SKIP_BY_FRAMEWORK

        if action1 == Action.RUN:
            return action2
        elif action1 == Action.SKIP_BY_CONFIGURATION:
            if action2 == Action.RUN:
                return action1
            else:
                return action2
        else:
            return action1


    def get_action(self, data:ActivityData, mode: Mode, ignore_unrun=False, activity_id_special:str=None):
        # pylint: disable=no-else-raise

        '''
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
        '''
        skip_with_outputs = data.activity_config.skip_with_outputs


        #______________________________ ACTIVITY_IN_BLOCK _________________________________#
        if mode == Mode.ACTIVITY_IN_BLOCK:
            if data.activity_id == activity_id_special:

                Check.is_false(self._special_activity_detected, "_special_activity_detected should not be activated twice")
                ActivityBlockRules._special_activity_detected = True


                if skip_with_outputs:
                    return Action.SKIP_WITH_OUTPUT_VALUES
                else:
                    return self._get_action(data, ignore_unrun=ignore_unrun)
            else:
                #if ActivityBlockRules._special_activity_detected:
                    #return Action.SKIP_BY_FRAMEWORK # Activities that follow after the special activity
                #else:
                return Action.KEEP_AS_IS # Activities before the special activity should not have any impact on the flow.
                #return Action.SKIP_BY_FRAMEWORK
                #return Action.REUSE


        # ______________________________ ACTIVITY_BLOCK_RERUN _________________________________#
        elif mode == Mode.ACTIVITY_BLOCK_RERUN:
            if data.activity_id == activity_id_special: # The activity from which the re-run starts

                Check.is_false(self._rerun_activated, "rerun_activated should not be activated twice")
                ActivityBlockRules._rerun_activated = True
                logging.info("Re-run initiated")

            if ActivityBlockRules._rerun_activated:
                if skip_with_outputs:
                    return Action.SKIP_WITH_OUTPUT_VALUES
                else:
                    return self._get_action(data, ignore_unrun=ignore_unrun)
            else:
                return Action.REUSE

        # ______________________________ ACTIVITY_BLOCK _________________________________#
        elif mode == Mode.ACTIVITY_BLOCK:
            if skip_with_outputs:
                return Action.SKIP_WITH_OUTPUT_VALUES
            else:
                return self._get_action(data, ignore_unrun=ignore_unrun)

        # ______________________________ ACTIVITY _________________________________#
        elif mode == Mode.ACTIVITY: # In mode ACTIVITY there is always only ONE activity in the activity block
            if skip_with_outputs:
                return Action.SKIP_WITH_OUTPUT_VALUES
            else:
                return Action.RUN

        raise AutorFrameworkException(f"Unknown Autor run mode: {str(mode)}")



    def _get_action(self, data, ignore_unrun=False):

        activity_group_type = data.activity_group_type
        interrupted = data.interrupted
        self._print("(run-decision) activity_group_type       = " + str(activity_group_type))

        # @TODO add warnings if wrong configuration is added
        # @TODO add before-activity skipped_by_framework because of skipping main-activity

        action = Action.RUN

        action_based_on_run_on_config = Action.RUN
        action_based_on_interrupt = Action.RUN
        action_based_on_necessity = Action.RUN

        # Configuration (runOn) is relevant for all activity group types.
        action_based_on_run_on_config = self._get_run_on_action(data, ignore_unrun)

        # ------------------ BEFORE-BLOCK -----------------#
        if activity_group_type == agt.BEFORE_BLOCK:
            if interrupted:
                action_based_on_interrupt = Action.SKIP_BY_FRAMEWORK

        # ---------------- BEFORE-ACTIVITY -----------------#
        if activity_group_type == agt.BEFORE_ACTIVITY:
            if interrupted:  # -> main activity will be skipped by framework
                action_based_on_interrupt = Action.SKIP_BY_FRAMEWORK

            if self._main_activity_will_be_skipped_by_config(data):
                action_based_on_necessity = Action.SKIP_BY_CONFIGURATION

        # ---------------- MAIN-ACTIVITY -----------------#
        if activity_group_type == agt.MAIN_ACTIVITY:

            if interrupted:
                action_based_on_interrupt = Action.SKIP_BY_FRAMEWORK

        # ---------------- AFTER-ACTIVITY -----------------#
        if activity_group_type == agt.AFTER_ACTIVITY:

            if self._main_was_skipped_by_framework(data) and self._all_before_activities_were_skipped_by_framework(data):
                action_based_on_necessity = Action.SKIP_BY_FRAMEWORK

        # ---------------- AFTER-BLOCK -----------------#
        if activity_group_type == agt.AFTER_BLOCK:

            if self._all_before_block_activities_were_skipped_by_framework(data):
                action_based_on_necessity = Action.SKIP_BY_FRAMEWORK

        self._print("ACTION: based on runOn config: " + action_based_on_run_on_config)
        self._print("ACTION: based on interrupt:    " + action_based_on_interrupt)
        self._print("ACTION: based on necessity:    " + action_based_on_necessity)
        action = self._choose_most_important_action(action_based_on_run_on_config, action_based_on_interrupt, action_based_on_necessity)

        self._print("(run-decision) -----> " + action)
        return action

    def _get_run_on_action(self, data, ignore_unrun=False):  # ->Action:
        self._print("-> self._get_run_on_action")

        assert data.activity_config is not None
        assert data.activity_group_type is not None

        group = data.activity_group_type
        run_on_config = data.activity_config.run_on

        # Go through the configuration, validate it and add the default values
        # where no values are provided.
        run_on_config = self._add_run_on_defaults(run_on_config, group, data)

        if run_on_config is None:
            self._print("(aaaa) runOn: None -> using defaults for group: " + str(group))
            run_on_config = ActivityBlockRules.DEFAULT_RUN_ON[group]

        # Evaluate the configurations.
        run_on_activity_status = self._run_on_activity_status(
            run_on_config[cfg.ACTIVITY_STATUS], data, ignore_unrun
        )  # Returns True if cfg is None
        run_on_main_activity_status = self._run_on_main_activity_status(
            run_on_config[cfg.MAIN_ACTIVITY_STATUS], data
        )  # Returns True if cfg is None
        run_on_activity_block_status = self._run_on_activity_block_status(
            run_on_config[cfg.ACTIVITY_BLOCK_STATUS], data
        )  # Returns True if cfg is None

        # Decide on the action:
        run = (
            run_on_activity_status and run_on_main_activity_status and run_on_activity_block_status
        )

        if run:
            return Action.RUN
        else:
            return Action.SKIP_BY_CONFIGURATION

    # Add default values to the whole runOn configuration and validate the
    # configuration.
    def _add_run_on_defaults(self, run_on_config, activity_group_type, data):
        self._print("-> self._add_run_on_defaults")
        default_run_on = ActivityBlockRules.DEFAULT_RUN_ON[activity_group_type]

        if run_on_config is None:
            # Logger.print_dict(default_run_on, "runOn: complete")
            return default_run_on

        Check.is_instance_of(run_on_config, dict, "runOn value should be a dctionary")

        run_on_config = self._complete_run_on_activity_status_config(run_on_config, default_run_on)
        run_on_config = self._complete_run_on_config(
            run_on_config, default_run_on, cfg.MAIN_ACTIVITY_STATUS, data
        )
        run_on_config = self._complete_run_on_config(
            run_on_config, default_run_on, cfg.ACTIVITY_BLOCK_STATUS, data
        )

        return run_on_config

    def _complete_run_on_activity_status_config(self, original_config, default_config):  # -> dict
        self._print("-> self._complete_run_on_activity_status_config")
        missing = "___missing___"

        default = default_config[cfg.ACTIVITY_STATUS]
        original = original_config.get(cfg.ACTIVITY_STATUS, missing)

        if (original is not None) and original != missing:
            Check.is_instance_of(
                original, dict, "runOn." + cfg.ACTIVITY_STATUS + " value should be a dctionary"
            )

        if default is None:
            assert original == missing  # Original config must be missing if default has None
            original_config[cfg.ACTIVITY_STATUS] = default
            # Logger.print_dict(original_config, "runOn.activityStatus: completed")
            return original_config

        else:  # we have default config -> ok to have real config
            if original == missing:
                original_config[cfg.ACTIVITY_STATUS] = default
                #  Logger.print_dict(original_config, "runOn.activityStatus: completed")
                return original_config
            else:
                # If config exists, it must not be empty.
                # print("ORIGINAL: " + str(original))

                items = original.items()
                assert len(items) > 0

                # Loop through the elements in runOn.activityStatus and
                # check that they are not empty and that they are lists
                for key, value in items:
                    assert value is not None
                    Check.is_instance_of(
                        value,
                        list,
                        "runOn." + cfg.ACTIVITY_STATUS + "." + key + " value should be a list",
                    )
                    assert len(value) > 0
                    for val in value:
                        Check.is_status(val)
                        # assert self._is_status(val)

                return original_config

    def _complete_run_on_config(
        self, original_config: dict, default_config: dict, on_config_type: str, data: ActivityData
    ):  # -> dict
        self._print("-> self._complete_run_on_config")
        missing = "___missing___"

        default: list = default_config[on_config_type]
        original: list = original_config.get(on_config_type, missing)

        if (original is not None) and original != missing:
            Check.is_instance_of(
                original, list, "runOn." + on_config_type + " value should be a list"
            )

        self._print("on_config_type: " + on_config_type)

        # No configuration allowed
        if default is None:
            Check.is_true(
                original is None or original == missing,
                "runOn."
                + on_config_type
                + " is not allowed for activity group type: "
                + str(data.activity_group_type)
                + ". Activity: "
                + str(data.activity_name),
            )
            original_config[on_config_type] = None
            return original_config

        # Configuration allowed, but not provided
        elif original is None or original == missing:
            original_config[on_config_type] = default
            return original_config

        # Configuration allowed and provided -> check the format
        else:
            # Must not be an empty list
            assert len(original) > 0

            # Check that the values are valid statuses
            for val in original:
                assert Check.is_status(val)

            return original_config

    def _run_on_activity_block_status(self, statuses, data):
        if statuses is None:  # None means that no configuration is expected.
            self._print("runOn.activityBlockStatus: None ---> True")
            return True

        Check.not_empty_list(
            statuses,
            (
                "Empty list is not a valid value for runOn.activityBlockStatus."
                + " Add at least one element or remove from the configuration."
            ),
        )
        run = (data.activity_block_status in statuses) or (Status.ALL in statuses)

        self._print("runOn.activityBlockStatus --->" + str(run))
        return run

    def _run_on_main_activity_status(self, statuses, data):
        if statuses is None:  # None means that no configuration is expected.
            self._print("runOn.mainActivityStatus: None ---> True")
            return True

        Check.not_empty_list(
            statuses,
            (
                "Empty list is not a valid value for runOn.mainActivityStatus."
                + " Add at least one element or remove from the configuration."
            ),
        )
        Check.not_empty_list(
            data.main_activities,
            "runOn.mainActivityStatus cannot be applied, as no main activity has previously run.",
        )

        # If it is the first main activity that runs, then the configuration will be ignored.
        if len(data.main_activities) <= 0:
            logging.debug(
                "first main activitiy -> ignoring runOn.mainActivityStatus -> return True"
            )

        latest_main_activity = data.main_activities[-1]
        run = (latest_main_activity.status in statuses) or (Status.ALL in statuses)

        self._print("(aaaa) runOn.mainActivityStatus --->" + str(run))
        return run

    def _run_on_activity_status(self, config, data, ignore_unrun):

        if config is None:  # None means that no configuration is expected.
            self._print("runOn.activityStatus: None ---> True")
            return True

        run = True

        # If it is the first activity that runs, then the configuration will be ignored.
        if len(data.activities) <= 0:
            self._print("first activity -> ignoring runOn.activityStatus ---> return True")

        # Go through all the requirements for the activity statuses and see if they can
        # all be evaluated to True.
        for activity_name, statuses in config.items():
            self._print("runOn.activityStatus." + activity_name + ": " + str(statuses))
            Check.not_none(statuses, "runOn.activityStatus." + activity_name)

            if activity_name == Configuration.ANY:
                self._print(activity_name + " -> condition: True")
            else:
                activity = self._get_activity_by_name(activity_name, data)  # Returns None, if not found

                if activity is None:
                    Check.is_true(
                        ignore_unrun,
                        "Exception in configuration for activity: "
                        + data.activity_name
                        + ": Cannot check runOn.activityStatus for "
                        + activity_name
                        + " as the activity has not run and produced any status value.",
                    )
                else:
                    Check.not_empty_list(
                        statuses,
                        "Empty list is not a valid value for runOn.activityStatus."
                        + activity_name
                        + "="
                        + str(statuses)
                        + ".  Add at least one element or remove from the configuration.",
                    )
                    run = run and ((activity.status in statuses) or (Status.ALL in statuses))
                    self._print(
                        activity_name
                        + ".status = "
                        + str(activity.status)
                        + " -> condition: "
                        + str(run)
                    )

            if not run:
                break

        self._print("runOn.activityStatus --->" + str(run))
        return run

    # Returns None if not found.
    # pylint: disable-next=no-self-use
    def _get_activity_by_name(self, activity_name, data):
        if activity_name == Configuration.PREVIOUS:
            group = data.activity_group_type
            group_activities = data.get_activities(group)
            if len(group_activities) > 0:
                return group_activities[-1]
            else:
                return None  # Ok

        elif activity_name == Configuration.LATEST:

            if len(data.activities) > 0:
                return data.activities[-1]
            else:
                return None

        else:
            activity = data.activities_by_name.get(activity_name, None)
            return activity

    # Only for after-block activities.
    # Indicates on which activity block statuses the after-activity will be run.
    def old__rr_(self, activity_block_status, after_activity_config):

        run_on_activity_block_status = after_activity_config.configuration.get(
            cfg.RUN_ON_ACTIVITY_BLOCK_STATUS, None
        )
        if run_on_activity_block_status is None:  # Value not obligatory -> use default
            self._print(
                (
                    "(run-decision) runOnActivityBlockStatus = None"
                    + " -> use DEFAULT_RUN_ON_ACTIVITY_BLOCK_STATUS"
                )
            )

        self._print(
            "(run-decision) runOnActivityBlockStatus = " + str(run_on_activity_block_status)
        )
        self._print("(run-decision) activity_block_status:   = " + str(activity_block_status))

        ok_to_run_activity = False
        if (Status.ALL in run_on_activity_block_status) or (
            activity_block_status in run_on_activity_block_status
        ):
            ok_to_run_activity = True

        return ok_to_run_activity

    def _main_was_skipped_by_framework(self, data):
        last_main_context = data.main_activities[-1].context
        skip_type = last_main_context.get(ctx.ACTION, None)
        skipped = (skip_type == Action.SKIP_BY_FRAMEWORK)
        self._print("_main_was_skipped_by_framework ---> " + str(skipped))
        return skipped

    def _all_before_activities_were_skipped_by_framework(self, data):
        all_skipped = True
        for activity in data.before_activities:
            skip_type = activity.context.get(ctx.ACTION, None)
            # print("skip_type: " + str(skip_type) + " " + activity.id)
            all_skipped = all_skipped and (skip_type == Action.SKIP_BY_FRAMEWORK)
        self._print("_all_before_activities_were_skipped_by_framework ---> " + str(all_skipped))
        # print("_all_before_activities_were_skipped_by_framework ---> " + str(all_skipped))
        return all_skipped

    def _all_before_block_activities_were_skipped_by_framework(self, data):
        all_skipped = True
        for activity in data.before_block_activities:
            skip_type = activity.context.get(ctx.ACTION, None)
            all_skipped = all_skipped and (skip_type == Action.SKIP_BY_FRAMEWORK)
        self._print(
            "_all_before_block_activities_were_skipped_by_framework ---> " + str(all_skipped)
        )
        return all_skipped

    # Look at the configuration of the main activity that this activity and return
    # True if there is currently no reason for this activity not to run
    # False if we already now know that the activity will not be run.
    def _main_activity_will_be_skipped_by_config(self, data):

        next_main_data = data.next_main_activity_data
        action = self._get_action(next_main_data, ignore_unrun=True)
        # pylint: disable-next=superfluous-parens
        skip = not (action == Action.RUN)
        self._print("_main_activity_will_be_skipped_by_config ---> " + str(skip))
        return skip

    # continueOn
    # Return True if the flow should continue based on the latest activity status.
    def continue_on(self, data:ActivityData, mode:Mode, action:Action):

        activity = data.activity
        activity_group_type = data.activity_group_type

        if activity is None:
            raise AutorFrameworkException("parameter 'activity' may not be None")

        # Read the activity's continueOnStatus requirements from the configuration.
        continue_on:list = data.activity_config.continue_on

        if continue_on is None:  # Value not obligatory -> use default
            continue_on = ActivityBlockRules.DEFAULT_CONTINUE_ON[activity_group_type]
            self._print(
                "(continue-decision) continueOnStatus = None -> use DEFAULT_CONTINUE_ON["
                + activity_group_type
                + "]"
            )

        if mode == Mode.ACTIVITY_IN_BLOCK and action == Action.KEEP_AS_IS:
            # An activity can have status UNKNOWN ony if it has never been run for real, but we've
            # been skipping it with action KEEP_AS_IS to make sure that no changes are made
            # to the context. A status for an unrun activity should not have impact on wether the
            # activity block will continue to run or not.
            self._print(f"(continue-decision) mode={mode} && action={action} -> add UNKNOWN to continue_on")
            continue_on = continue_on + [Status.UNKNOWN]
            #continue_on.append(Status.UNKNOWN)

        self._print("(continue-decision) continue_on     = " + str(continue_on))
        self._print("(continue-decision) activity.status = " + str(activity.status))

        ok_to_continue_with_next_activity = False
        # Continue if:
        # - The activity states that the flow should ALWAYS continue,regardless the activity status.
        # - The activity status is listed as one of the required statuses for the flow to continue.
        if (Status.ALL in continue_on) or (activity.status in continue_on):
            ok_to_continue_with_next_activity = True

        self._print(
            "(continue-decision) -----> ok_to_continue_with_next_activity = "
            + str(ok_to_continue_with_next_activity)
        )
        return ok_to_continue_with_next_activity

    # Only for after-activities.
    # Indicates on which main activity statuses the after-activity should be run.
    def _run_on_main_activity_status_old(self, main_activity, after_activity_config):

        # pylint: disable=no-member
        run_on_main_activity_status = after_activity_config.configuration.get(
            cfg.RUN_ON_MAIN_ACTIVITY_STATUS, None
        )
        # Value not obligatory -> use default
        if run_on_main_activity_status is None:
            ####run_on_main_activity_status = ActivityBlockRules.DEFAULT_RUN_ON_MAIN_ACTIVITY_STATUS
            self._print(
                (
                    "(run-decision) runOnMainActivityStatus = None"
                    + " -> use DEFAULT_RUN_ON_MAIN_ACTIVITY_STATUS"
                )
            )

        self._print("(run-decision) runOnMainActivityStatus = " + str(run_on_main_activity_status))
        self._print("(run-decision) main_activity.status:   = " + str(main_activity.status))

        ok_to_run_activity = False

        # Continue if:
        # - The activity states that the flow should ALWAYS continue,
        #  regardless the activity status.
        # - The activity status is listed as one of the required statuses for the flow to continue.
        if (Status.ALL in run_on_main_activity_status) or (
            main_activity.status in run_on_main_activity_status
        ):
            ok_to_run_activity = True

        return ok_to_run_activity

    # Only for after-block activities. Indicates on which activity block statuses,
    # the after-activity will be run.
    def old___(self, activity_block_status, after_activity_config):

        # pylint: disable=no-member
        run_on_activity_block_status = after_activity_config.configuration.get(
            cfg.RUN_ON_ACTIVITY_BLOCK_STATUS, None
        )
        # Value not obligatory -> use default
        if run_on_activity_block_status is None:
            self._print(
                (
                    "(run-decision) runOnActivityBlockStatus = None"
                    + " -> use DEFAULT_RUN_ON_ACTIVITY_BLOCK_STATUS"
                )
            )

        self._print(
            "(run-decision) runOnActivityBlockStatus = " + str(run_on_activity_block_status)
        )
        self._print("(run-decision) activity_block_status:   = " + str(activity_block_status))

        ok_to_run_activity = False
        if (Status.ALL in run_on_activity_block_status) or (
            activity_block_status in run_on_activity_block_status
        ):
            ok_to_run_activity = True

        return ok_to_run_activity

    def get_activity_block_status(self, data, autor_aborted)->(str,str):

        assert len(data.activities) > 0

        current_block_status = data.activity_block_status
        # list is never empty.
        activity = data.activities[-1]
        activity_block_interrupted = data.interrupted

        self._print("(block-status) current_block_status:       " + str(current_block_status))
        self._print("(block-status) activity.status:            " + str(activity.status))
        self._print("(block-status) activity_block_interrupted: " + str(activity_block_interrupted))
        self._print("(block-status) autor_aborted:              " + str(autor_aborted))

        # See the diagram for the rules: https://jira-dowhile.atlassian.net/l/c/w3pkZPM1
        activity_status = activity.status
        new_block_status = current_block_status

        if autor_aborted:
            Check.is_true(
                current_block_status == Status.ABORTED,
                (
                    "Activity block status should always be {Status.ABORTED} once autor has been"
                    + " aborted by (due to framework or other unrecoverable errors). "
                    + "Current status: {current_block_status}"
                ),
            )

        elif current_block_status == Status.UNKNOWN:
            raise AutorFrameworkException(
                "A running activity block should never have status UNKNOWN"
            )
            # UNKNOWN -> SUCCESS
            # UNKNOWN -> FAIL
            # UNKNOWN -> ERROR
            # pylint: disable-next=line-too-long
            # if activity_status == Status.SUCCESS or activity_status == Status.FAIL or activity_status == Status.ERROR:
            # new_block_status = activity_status

            # UNKNOWN -> SKIPPED
            # UNKNOWN -> ABORTED
            # elif activity_status == Status.SKIPPED or activity_status == Status.ABORTED:
            # if activity_block_interrupted:
            #  new_block_status = activity_status

        elif current_block_status == Status.SUCCESS:
            # SUCCESS -> FAIL
            # SUCCESS -> ERROR
            if activity_status in (Status.FAIL, Status.ERROR):
                new_block_status = activity_status

            # SUCCESS -> SKIPPED
            # SUCCESS -> ABORTED
            elif activity_status in (Status.SKIPPED, Status.ABORTED):
                if activity_block_interrupted:
                    new_block_status = activity_status

        elif current_block_status in (Status.SKIPPED, Status.ABORTED):
            # SKIPPED -> FAIL
            # SKIPPED -> ERROR
            # ABORTED -> FAIL
            # ABORTED -> ERROR
            if activity_status in (Status.FAIL, Status.ERROR):
                new_block_status = activity_status

        elif current_block_status == Status.ERROR:
            # ERROR -> FAIL
            if activity_status == Status.FAIL:
                new_block_status = activity_status


        self._print("(block-status) ---------> new_block_status = " + str(new_block_status))
        state_transition_summary = self._create_state_transition_summary(activity, current_block_status, new_block_status)
        action_str: str = activity.context.get_from_activity(key=ctx.ACTION)
        ActivityBlockRules._transition_summary.add(activity.id,activity.status,action_str,current_block_status,new_block_status)
        return new_block_status, state_transition_summary


    def _create_state_transition_summary(self, activity, current_block_status, new_block_status)->str:

        name_len = len(str(activity.id))

        # Make a guess for a longest activity name (needed for having nice columns in prints)
        if self._max_len_activity_name is None:
            self._max_len_activity_name = max(name_len, 30)

        # If our guess was too short, make a new guess.
        if name_len > self._max_len_activity_name:
            self._max_len_activity_name = name_len + 5

        # status as str
        status_str = str(activity.status)

        # Was the activity skipped by the framework?
        skip_type = activity.context.get_from_activity(key=ctx.SKIP_TYPE, default=None)

        action_str:str = activity.context.get_from_activity(key=ctx.ACTION)

        return (
            str(activity.id).ljust(self._max_len_activity_name)
            + " " + action_str.ljust(6)
            + status_str.ljust(15)
            + "Activity-block: "
            + current_block_status
            + " -> "
            + new_block_status
        )


    def print_default_config_conditions(self):
        Util.print_dict(ActivityBlockRules.DEFAULT_CONTINUE_ON, "DEFAULT_CONTINUE_ON", 'info')
        Util.print_dict(ActivityBlockRules.DEFAULT_RUN_ON, "DEFAULT_RUN_ON", 'info')


    # pylint: disable-next=no-self-use
    def _print(self, text):
        if DebugConfig.trace_activity_sequence_decisions:
            logging.info(f'{DebugConfig.activity_sequence_decisions_trace_prefix}{str(text)}')






