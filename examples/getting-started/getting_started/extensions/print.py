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

from autor.framework.context import Context, RemoteContext
from autor.framework.debug_config import DebugConfig
from autor.framework.file_context import FileContext
from autor.framework.keys import StateKeys as ste
from autor.framework.state import State
from autor.framework.state_listener import StateListener

# pylint: disable=no-member, abstract-method


class PrintFrameworkEndState(StateListener):
    def on_framework_end(self, state: State):  # Override
        self.log_debug("EXTENSION PrintFrameworkEndState>>>>")
        state.print_state()


class PrintHelloInEachState(StateListener):

    def on_bootstrap(self, state: State):  # Override
        self.log_debug(f"  Hello   {state.name}!!!")

    def on_error(self, state: State):  # Override
        self.log_debug(f"  Hello   {state.name}!!!")

    def on_select_activity(self, state: State):  # Override
        self.log_debug(f"  Hello   {state.name}!!!")

    def on_after_activity_postprocess(self, state: State):  # Override
        self.log_debug(f"  Hello   {state.name}!!!")

    def on_framework_start(self, state: State):  # Override
        self.log_debug(f"  Hello   {state.name}!!!")

    def on_framework_end(self, state: State):  # Override
        self.log_debug(f"  Hello   {state.name}!!!")

    def on_before_activity_preprocess(self, state: State):  # Override
        self.log_debug(f"  Hello   {state.name}!!!")

    def on_after_activity_run(self, state: State):  # Override
        self.log_debug(f"  Hello   {state.name}!!!")

    def on_before_activity_block_callbacks(self, state: State):  # Override
        self.log_debug(f"  Hello   {state.name}!!!")

    def on_before_activity_block(self, state: State):  # Override
        self.log_debug(f"  Hello   {state.name}!!!")

    def on_after_activity_block(self, state: State):  # Override
        self.log_debug(f"  Hello   {state.name}!!!")

    def on_before_activity_run(self, state: State):  # Override
        self.log_debug(f"  Hello   {state.name}!!!")

class PrintGoodbyeInEachState(StateListener):

    def on_bootstrap(self, state: State):  # Override
        self.log_debug(f"Goodbye {state.name}!!!")

    def on_error(self, state: State):  # Override
        self.log_debug(f"Goodbye {state.name}!!!")

    def on_select_activity(self, state: State):  # Override
        self.log_debug(f"Goodbye {state.name}!!!")

    def on_after_activity_postprocess(self, state: State):  # Override
        self.log_debug(f"Goodbye {state.name}!!!")

    def on_framework_start(self, state: State):  # Override
        self.log_debug(f"Goodbye {state.name}!!!")

    def on_framework_end(self, state: State):  # Override
        self.log_debug(f"Goodbye {state.name}!!!")

    def on_before_activity_preprocess(self, state: State):  # Override
        self.log_debug(f"Goodbye {state.name}!!!")

    def on_after_activity_run(self, state: State):  # Override
        self.log_debug(f"Goodbye {state.name}!!!")

    def on_before_activity_block_callbacks(self, state: State):  # Override
        self.log_debug(f"Goodbye {state.name}!!!")

    def on_before_activity_block(self, state: State):  # Override
        self.log_debug(f"Goodbye {state.name}!!!")

    def on_after_activity_block(self, state: State):  # Override
        self.log_debug(f"Goodbye {state.name}!!!")

    def on_before_activity_run(self, state: State):  # Override
        self.log_debug(f"Goodbye {state.name}!!!")