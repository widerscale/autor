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

from autor.framework.autor_framework_exception import AutorFrameworkException
from autor.framework.constants import ExceptionType
from autor.framework.debug_config import DebugConfig
from autor.framework.keys import StateKeys as ste
from autor.framework.state import (
    AfterActivityBlock,
    AfterActivityPostprocess,
    AfterActivityRun,
    BeforeActivityBlock,
    BeforeActivityBlockCallbacks,
    BeforeActivityPreprocess,
    BeforeActivityRun,
    Error,
    FrameworkEnd,
    FrameworkStart,
    SelectActivity,
    State,
)
from autor.framework.state_listener import StateListener
from autor.framework.state_producer import StateProducer
from autor.framework.util import Util

# ------------------------------------------------------------------------------#
#     Class for:                                                               #
#            - registering state event listeners                               #
#            - registering state data producers                                #
#            - creating state related events for listeners and producers       #
# ------------------------------------------------------------------------------#


# ________________________ S T A T E   H A N D L E R ______________________________#


class StateHandler(StateProducer):

    _current_state_name: State = State.UNKNOWN

    _listeners = []  # A list of objects who are interested in state change events.
    _producers = []  # A list of objects who are contirbuting to state data.

    _framework_ended = False

    # _______________ ADMINISTRATION of STATE PRODUCER AND LISTNER LISTS _______________#
    @staticmethod
    def framework_ended():
        return StateHandler._framework_ended

    @staticmethod
    def get_current_state_name():
        return StateHandler._current_state_name

    @staticmethod
    def add_state_producer(producer: StateProducer):
        StateHandler._producers.append(producer)

    @staticmethod
    def remove_state_producer(producer: StateProducer):
        if producer in StateHandler._producers:
            StateHandler._producers.remove(producer)
        else:
            logging.debug(
                (
                    "WARNING: Could not remove producer: "
                    + "%s from producers list. Producer not in the list."
                ),
                producer,
            )

    @staticmethod
    def add_state_listener(listener: StateListener):
        StateHandler._listeners.append(listener)

    @staticmethod
    def remove_state_listener(listener: StateListener):
        if listener in StateHandler._listeners:
            StateHandler._listeners.remove(listener)
        else:
            logging.debug(
                (
                    "WARNING: Could not remove listener: %s from listeners list. "
                    + "Listener not in the list."
                ),
                listener,
            )

    @staticmethod
    def remove_all_listeners():
        StateHandler._listeners = []

    @staticmethod
    def change_state(state_name: str) -> dict:

        StateHandler._current_state_name = state_name
        if state_name == State.FRAMEWORK_END:
            StateHandler._framework_ended = True

        if DebugConfig.print_state_names:
            Util.print_framed(text=state_name, frame_symbol=":")

        # Dictionary that represents the state date.
        state_data = {}

        # ---------- ON-BEFORE-STATE -----------#
        for producer in StateHandler._producers:
            producer.on_before_state(state_name, state_data)

        # ------------ ON-STATE ---------------#
        # Create the state-specific state-object.
        StateHandler._run_callbacks(state_name, state_data, StateHandler._listeners)

        # ---------- ON-AFTER-STATE -----------#
        for producer in StateHandler._producers:
            producer.on_after_state(state_name, state_data)

        return state_data

    @staticmethod
    # pylint: disable=too-many-branches, too-many-statements
    def _run_callbacks(state_name, state_data, listeners):

        state = None

        if state_name == State.FRAMEWORK_START:
            state = FrameworkStart(state_data)
            for listener in listeners:
                try:
                    listener.on_framework_start(state)
                except Exception as e:
                    Util.register_exception(
                        ex=e,
                        description="Extension exception in: {listener.__class__.__name__}",
                        type=ExceptionType.EXTENSION,
                        framework_error=False,
                    )

        elif state_name == State.BEFORE_ACTIVITY_BLOCK:
            state = BeforeActivityBlock(state_data)
            for listener in listeners:
                try:
                    listener.on_before_activity_block(state)
                except Exception as e:
                    Util.register_exception(
                        ex=e,
                        description="Extension exception in: {listener.__class__.__name__}",
                        type=ExceptionType.EXTENSION,
                        framework_error=False,
                    )

        elif state_name == State.SELECT_ACTIVITY:
            state = SelectActivity(state_data)
            for listener in listeners:
                try:
                    listener.on_select_activity(state)
                except Exception as e:
                    Util.register_exception(
                        ex=e,
                        description="Extension exception in: {listener.__class__.__name__}",
                        type=ExceptionType.EXTENSION,
                        framework_error=False,
                    )

        elif state_name == State.BEFORE_ACTIVITY_PREPROCESS:
            state = BeforeActivityPreprocess(state_data)
            for listener in listeners:
                try:
                    listener.on_before_activity_preprocess(state)
                except Exception as e:
                    Util.register_exception(
                        ex=e,
                        description="Extension exception in: {listener.__class__.__name__}",
                        type=ExceptionType.EXTENSION,
                        framework_error=False,
                    )

        elif state_name == State.BEFORE_ACTIVITY_RUN:
            state = BeforeActivityRun(state_data)
            for listener in listeners:
                try:
                    listener.on_before_activity_run(state)
                except Exception as e:
                    Util.register_exception(
                        ex=e,
                        description="Extension exception in: {listener.__class__.__name__}",
                        type=ExceptionType.EXTENSION,
                        framework_error=False,
                    )

        elif state_name == State.AFTER_ACTIVITY_RUN:
            state = AfterActivityRun(state_data)
            for listener in listeners:
                try:
                    listener.on_after_activity_run(state)
                except Exception as e:
                    Util.register_exception(
                        ex=e,
                        description="Extension exception in: {listener.__class__.__name__}",
                        type=ExceptionType.EXTENSION,
                        framework_error=False,
                    )

        elif state_name == State.AFTER_ACTIVITY_POSTPROCESS:
            state = AfterActivityPostprocess(state_data)
            for listener in listeners:
                try:
                    listener.on_after_activity_postprocess(state)
                except Exception as e:
                    Util.register_exception(
                        ex=e,
                        description="Extension exception in: {listener.__class__.__name__}",
                        type=ExceptionType.EXTENSION,
                        framework_error=False,
                    )

        elif state_name == State.BEFORE_ACTIVITY_BLOCK_CALLBACKS:
            state = BeforeActivityBlockCallbacks(state_data)
            for listener in listeners:
                try:
                    listener.on_before_activity_block_callbacks(state)
                except Exception as e:
                    Util.register_exception(
                        ex=e,
                        description="Extension exception in: {listener.__class__.__name__}",
                        type=ExceptionType.EXTENSION,
                        framework_error=False,
                    )

        elif state_name == State.AFTER_ACTIVITY_BLOCK:
            state = AfterActivityBlock(state_data)
            for listener in listeners:
                try:
                    listener.on_after_activity_block(state)
                except Exception as e:
                    Util.register_exception(
                        ex=e,
                        description="Extension exception in: {listener.__class__.__name__}",
                        type=ExceptionType.EXTENSION,
                        framework_error=False,
                    )

        elif state_name == State.FRAMEWORK_END:
            state = FrameworkEnd(state_data)
            for listener in listeners:
                try:
                    listener.on_framework_end(state)
                except Exception as e:
                    Util.register_exception(
                        ex=e,
                        description="Extension exception in: {listener.__class__.__name__}",
                        type=ExceptionType.EXTENSION,
                        framework_error=False,
                    )

        elif state_name == State.ERROR:
            state = Error(state_data)
            for listener in listeners:
                try:
                    listener.on_error(state)
                except Exception as e:
                    Util.register_exception(
                        ex=e,
                        description="Extension exception in: {listener.__class__.__name__}",
                        type=ExceptionType.EXTENSION,
                        framework_error=False,
                    )

        else:
            raise AutorFrameworkException("Unknown state_name: " + str(state_name))

        for listener in listeners:
            try:
                listener.on_state(state)
            except Exception as e:
                Util.register_exception(
                    ex=e,
                    description="Extension exception in: {listener.__class__.__name__}",
                    type=ExceptionType.EXTENSION,
                    framework_error=False,
                )

    @staticmethod
    def _create_state(state_name: str, state_data: dict) -> State:

        state = None

        if state_name == State.FRAMEWORK_START:
            state = FrameworkStart(state_data)

        if state_name == State.BEFORE_ACTIVITY_BLOCK:
            state = BeforeActivityBlock(state_data)

        if state_name == State.SELECT_ACTIVITY:
            state = SelectActivity(state_data)

        if state_name == State.BEFORE_ACTIVITY_PREPROCESS:
            state = BeforeActivityPreprocess(state_data)

        if state_name == State.BEFORE_ACTIVITY_RUN:
            state = BeforeActivityRun(state_data)

        if state_name == State.AFTER_ACTIVITY_RUN:
            state = AfterActivityRun(state_data)

        if state_name == State.AFTER_ACTIVITY_POSTPROCESS:
            state = AfterActivityPostprocess(state_data)

        if state_name == State.BEFORE_ACTIVITY_BLOCK_CALLBACKS:
            state = BeforeActivityBlockCallbacks(state_data)

        if state_name == State.AFTER_ACTIVITY_BLOCK:
            state = AfterActivityBlock(state_data)

        if state_name == State.FRAMEWORK_END:
            state = FrameworkEnd(state_data)

        if state_name == State.ERROR:
            state = Error(state_data)

        if state is None:
            raise AutorFrameworkException(f"Cannot create state: Unknown state_name: {state_name}")

        return state

    # ____________________ PRINT METHODS ________________________#

    @staticmethod
    def _print_producers():
        logging.debug("PRODUCERS:")
        for producer in StateHandler._producers:
            logging.debug("   - " + str(producer))

    @staticmethod
    def _print_listeners():
        logging.debug("LISTENERS:")
        for listener in StateHandler._listeners:
            logging.debug("   - " + str(listener))

    @staticmethod
    def _print_state_name(state_name):
        # Create a divider consisting of a line of dashes as long as the actual log statement

        width = 40
        name_len = len(state_name)
        line = "_"
        end = "#"
        left = line * round((width - name_len) / 2)
        right = line * (width - name_len - len(left))

        logging.debug(end + left + " " + state_name + " " + right + end)

    # ____________________ STATE HANDLER as a STATE PRODUCER ________________________#

    # Let the StateHandler add the lists with state producers and listeners
    # to the state infomration.

    def on_before_state(self, state_name, state_data: dict) -> None:
        # pylint: disable=no-member
        state_data[ste.STATE_LISTENERS] = StateHandler._listeners
        state_data[ste.STATE_PRODUCERS] = StateHandler._producers

    def on_after_state(self, state_name, state_data: dict) -> None:
        # pylint: disable=no-member
        StateHandler._listeners = state_data[ste.STATE_LISTENERS]
        StateHandler._producers = state_data[ste.STATE_PRODUCERS]


StateHandler.add_state_producer(StateHandler())
