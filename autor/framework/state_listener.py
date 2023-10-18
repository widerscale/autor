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
import abc
import logging

from autor.framework.debug_config import DebugConfig
from autor.framework.state import (
    Bootstrap,
    FrameworkStart,
    BeforeActivityBlock,
    SelectActivity,
    BeforeActivityPreprocess,
    BeforeActivityRun,
    AfterActivityRun,
    AfterActivityPostprocess,
    AfterActivityBlock,
    BeforeActivityBlockCallbacks,
    FrameworkEnd,
    Error,
    State
)

# --------------------------------------------------------------------------#
#                      Class for receiving events                          #
# --------------------------------------------------------------------------#


# _______________ S T A T E   L I S T E N E R  _______________#
# The interface that should be implemented by the listeners of the events.
#
# Related classes:
# - StateProducer
# - StateHandler
# - State
class StateListener:
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def on_bootstrap(self, state: Bootstrap):
        pass

    @abc.abstractmethod
    def on_framework_start(self, state: FrameworkStart):
        pass

    @abc.abstractmethod
    def on_before_activity_block(self, state: BeforeActivityBlock):
        pass

    @abc.abstractmethod
    def on_before_activity_preprocess(self, state: BeforeActivityPreprocess):
        pass

    @abc.abstractmethod
    def on_before_activity_run(self, state: BeforeActivityRun):
        pass

    @abc.abstractmethod
    def on_after_activity_run(self, state: AfterActivityRun):
        pass

    @abc.abstractmethod
    def on_after_activity_postprocess(self, state: AfterActivityPostprocess):
        pass

    @abc.abstractmethod
    def on_select_activity(self, state: SelectActivity):
        pass

    @abc.abstractmethod
    def on_before_activity_block_callbacks(self, state: BeforeActivityBlockCallbacks):
        pass

    @abc.abstractmethod
    def on_after_activity_block(self, state: AfterActivityBlock):
        pass

    @abc.abstractmethod
    def on_framework_end(self, state: FrameworkEnd):
        pass

    @abc.abstractmethod
    def on_error(self, state: Error):
        pass

    def log_debug(self, text:str=None):
        """
        Recommended logging method for inheriting state listeners. Prints a unique prefix
        containing the listener name before each print.
        """
        logging.debug(f'{DebugConfig.extension_trace_prefix}{self.__class__.__name__}: {text}')


    def log_error(self, text:str=None):
        """
        Recommended logging method for inheriting state listeners. Prints a unique prefix
        containing the listener name before each print.
        """
        logging.error(f'{DebugConfig.extension_trace_prefix}{self.__class__.__name__}: {text}')

    def log_warning(self, text:str=None):
        """
        Recommended logging method for inheriting state listeners. Prints a unique prefix
        containing the listener name before each print.
        """
        logging.warning(f'{DebugConfig.extension_trace_prefix}{self.__class__.__name__}: {text}')

    def log_info(self, text:str=None):
        """
        Recommended logging method for inheriting state listeners. Prints a unique prefix
        containing the listener name before each print.
        """
        logging.info(f'{DebugConfig.extension_trace_prefix}{self.__class__.__name__}: {text}')


    def log_enter_extension(self):
        logging.debug(f'--> Extension: {self.__class__.__name__}')

    def log_leave_extension(self):
        logging.debug(f'<-- Extension: {self.__class__.__name__}')
