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
import sys



from typing import List



from autor.framework.autor_framework_exception import AutorFrameworkException
from autor.framework.constants import ExceptionType
from autor.framework.context import Context
from autor.framework.debug_config import DebugConfig
from autor.framework.exception_handler import ExceptionHandler
from autor.framework.keys import StateKeys as sta
from autor.framework.key_handler import KeyConverter
from autor.framework.logging_config import LoggingConfig
from autor.framework.state import (
    AfterActivityBlock,
    AfterActivityPostprocess,
    AfterActivityRun,
    Bootstrap,
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

    _listeners = []  # A list of objects that are interested in state change events.
    _producers = []  # A list of objects that are contributing to state data.

    _framework_ended = False

    # _______________ ADMINISTRATION of STATE PRODUCER AND LISTENER LISTS _______________#
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
            Util.print_framed(prefix=DebugConfig.state_prefix, text=state_name, frame_symbol=":")

        # Dictionary that represents the state date.
        state_data = {}

        # ---------- ON-BEFORE-STATE -----------#
        for producer in StateHandler._producers:
            producer.on_before_state(state_name, state_data)

        # ------------ ON-STATE ---------------#
        # Create the state-specific state-object.
        StateHandler._run_state_callbacks(state_name, state_data, StateHandler._listeners)

        # ---------- ON-AFTER-STATE -----------#
        for producer in StateHandler._producers:
            producer.on_after_state(state_name, state_data)

        return state_data



    @staticmethod
    def _overrides_callback(listener:object, method_name:str):

        listener_callback = getattr(type(listener), method_name, None)
        base_callback = getattr(StateListener, method_name, None)

        if listener_callback is None:
            raise AutorFrameworkException(f'Expected to find method: {method_name} in listener: {listener.__name__}, but did not find.')
        if base_callback is None:
            raise AutorFrameworkException(f'Expected to find method: {method_name} in base listener: {StateListener.__name__}, but did not find.')

        return listener_callback != base_callback

    @staticmethod
    def _create_state_object(state_data:dict, class_name:str):
        state_class = getattr(sys.modules[__name__], class_name)
        state_object = state_class(state_data)
        return state_object

    @staticmethod
    # pylint: disable=too-many-branches, too-many-statements
    def _run_state_callbacks(state_name, state_data, listeners:List[StateListener]):

        #Context.print_context(f"Context before state: {state_name}")

        # Run state callbacks for all listeners that listen to the given state.
        # Callback method name and the state class name that is needed for calling the callbacks
        # are derived from the 'state_name' according to following:
        #
        # State name:           EXAMPLE_STATE                       (UPPER_CASE_UNDERSCORE)
        # Class name:           EXAMPLE_STATE -> ExampleState       (PascalCase)
        # Callback method name: EXAMPLE_STATE -> on_example_state   (snake_case)

        state_class_name = KeyConverter.UCU_to_PASCAL(state_name)
        callback_method_name = f'on_{KeyConverter.UCU_to_SNAKE(state_name)}'

        if DebugConfig.print_context_before_state:
            Context.print_context(f"Context before state: {state_name}")

        for listener in listeners:
            is_listening:bool = StateHandler._overrides_callback(listener, callback_method_name)
            if is_listening:
                state_object = StateHandler._create_state_object(state_data, state_class_name)
                callback_method = getattr(listener, callback_method_name)

                if DebugConfig.print_calls_to_extensions:
                    logging.info(f'{DebugConfig.extension_trace_prefix}{listener.__class__.__name__}: ENTER {callback_method_name}()')


                #----------------------- Extension run BEGIN -------------------------#
                try:
                    LoggingConfig.activate_extension_logging(listener.__class__.__name__)
                    callback_method(state_object)
                    LoggingConfig.activate_framework_logging()
                except Exception as e:
                    LoggingConfig.activate_framework_logging()
                    StateHandler._register_listener_exception(e, state_name, listener)

                    if listener.interrupt_on_exception:
                        logging.error(f"Exiting due to exception in extension: {listener.__class__.__name__}")
                        sys.exit(1)
                    else:
                        logging.warning(f"Exception in extension: {listener.__class__.__name__}. Extension does not request interruption -> continue running.")


                # ----------------------- Extension run END -------------------------#
                if DebugConfig.print_calls_to_extensions:
                    logging.info(f'{DebugConfig.extension_trace_prefix}{listener.__class__.__name__}: LEAVE {callback_method_name}()')

        if DebugConfig.print_context_after_state:
            Context.print_context(f"Context after state: {state_name}")


    @staticmethod
    def _register_listener_exception(e:Exception, state_name:str, listener:StateListener):
        descr = f'Extension exception in state: {state_name} in extension: {listener.__class__.__name__}'
        ExceptionHandler.register_exception(ex=e, description=descr, ex_type=ExceptionType.EXTENSION)


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
    # to the state information.

    def on_before_state(self, state_name, state_data: dict) -> None:
        # pylint: disable=no-member
        state_data[sta.STATE_LISTENERS] = StateHandler._listeners
        state_data[sta.STATE_PRODUCERS] = StateHandler._producers

    def on_after_state(self, state_name, state_data: dict) -> None:
        # pylint: disable=no-member
        StateHandler._listeners = state_data[sta.STATE_LISTENERS]
        StateHandler._producers = state_data[sta.STATE_PRODUCERS]


StateHandler.add_state_producer(StateHandler())
