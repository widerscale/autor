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

from autor.framework.activity_block_information import ActivityBlockInformation
from autor.framework.activity_information import ActivityInformation
from autor.framework.flow_information import FlowInformation
from autor.framework.state import Bootstrap, FrameworkStart, BeforeActivityBlock, AfterActivityBlock, State, \
    BeforeActivityPreprocess, BeforeActivityRun, ContextSynchronized, Error, FrameworkEnd, BeforeActivityBlockCallbacks, \
    SelectActivity, AfterActivityPostprocess, AfterActivityRun
from autor.framework.state_listener import StateListener




# pylint: disable=no-member, abstract-method

# This extension is used to assist in Autor framework testing. It allows to provide values that can
# be injected into Activity properties. For example, if a test activity has a property 'outcome' that is
# normally set through the configuration, the input modifier allows to override the value provided by
# the configuration.
class StatePrintExtension(StateListener):

    def on_framework_start(self, state: FrameworkStart):
        self._print(state)

    def on_before_activity_block(self, state: BeforeActivityBlock):
        self._print(state)

    def on_select_activity(self, state: SelectActivity):
        self._print(state)

    def on_before_activity_block_callbacks(self, state: BeforeActivityBlockCallbacks):
        self._print(state)

    def on_after_activity_block(self, state: AfterActivityBlock):
        self._print(state)

    def on_framework_end(self, state: FrameworkEnd):
        self._print(state)

    def on_error(self, state: Error):
        self._print(state)

    def on_context_synchronized(self, state: ContextSynchronized):
        self._print(state)

    def on_bootstrap(self, state: Bootstrap):
        self._print(state)

    def on_before_activity_preprocess(self, state: BeforeActivityPreprocess):
        self._print(state)

    def on_before_activity_run(self, state: BeforeActivityRun):
        self._print(state)

    def on_after_activity_run(self, state: AfterActivityRun):
        self._print(state)

    def on_after_activity_postprocess(self, state: AfterActivityPostprocess):
        self._print(state)

    def _print(self, state: State):
        logging.info(f"___________________________ state: {state.name}")
        if (\
           #state.name == State.BEFORE_ACTIVITY_PREPROCESS or \
           #state.name == State.BEFORE_ACTIVITY_RUN or \
           #state.name == State.AFTER_ACTIVITY_RUN or \
           state.name == State.AFTER_ACTIVITY_POSTPROCESS):
            self._print_state_content(state)
            pass

    def _print_state_content(self, state):
        activity:ActivityInformation = state.activity_information
        activity_block:ActivityBlockInformation = state.activity_block_information
        flow:FlowInformation = state.flow_information
        if flow:
            flow.print()
        if activity_block:
            activity_block.print()
        if activity:
            activity.print()




