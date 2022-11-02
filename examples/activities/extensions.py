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


class AddDummyRemoteContext(StateListener):
    def on_state(self, state: State):
        print("EXTENSION AddDummyRemoteContext>>>>")
        if state.name == State.FRAMEWORK_START:
            state.dict[ste.FLOW_CONTEXT].remote_context = DummyRemoteContext()


class DummyRemoteContext(RemoteContext):
    # pylint: disable=redefined-builtin
    def sync(self, id: str, context: Context) -> None:
        if DebugConfig.trace_context:
            logging.debug("'%s' DummyRemoteContext.sync()", DebugConfig.context_trace_prefix)


class PrintStateName(StateListener):
    def on_state(self, state: State):  # Override StateListener.on_state()
        print("EXTENSION PrintStateName>>>>")
        print(state.name)


class PrintFrameworkEndState(StateListener):
    def on_framework_end(self, state: State):  # Override StateListener.on_state()
        print("EXTENSION PrintFrameworkEndState>>>>")
        state.print_state()


class AddFileContext(StateListener):
    def on_state(self, state: State):
        print("EXTENSION AddFileContext>>>>")
        if state.name == State.FRAMEWORK_START:
            state.dict[ste.FLOW_CONTEXT].remote_context = FileContext()
