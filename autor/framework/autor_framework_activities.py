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

from autor import Activity
from autor.framework.activity_data import ActivityData

from autor.framework.activity_registry import ActivityRegistry
from autor.framework.context import Context
from autor.framework.context_properties_registry import ContextPropertiesRegistry
from autor.framework.util import Util

output = ContextPropertiesRegistry.output
# pylint: disable-next=redefined-builtin
input = ContextPropertiesRegistry.input



#---------------------------- EXCEPTION ---------------------------------#
''' An activity without functionality that is used by Autor
when an unexpected error occurs and a user activity cannot
be created at all. These activities can be used as placeholders.'''
@ActivityRegistry.activity(type="exception")
class ExceptionActivity(Activity):
    def run(self):
        pass


#---------------------------- SKIP ---------------------------------#
''' An activity without functionality that is used by Autor
to skipe activities. These activities can be used as placeholders.'''
@ActivityRegistry.activity(type="skip")
class SkipActivity(Activity):
    def run(self):
        logging.info("Skipping activity...")
        pass



#---------------------------- DUMMY ---------------------------------#
''' An activity without functionality that is used by Autor
when an unexpected error occurs and a user activity cannot
be created at all. These activities can be used as placeholders.'''
@ActivityRegistry.activity(type="dummy")
class DummyActivity(Activity):
    def run(self):
        pass


#---------------------------- REUSE ---------------------------------#
''' An activity that provides the same output it reads from its context. '''
@ActivityRegistry.activity(type="reuse")
class ReuseActivity(Activity):

    def __init__(self):
        super().__init__()
        self._activity_output_context:Context = None


    def set_arguments(self, data: ActivityData):
        self._activity_output_context = data.output_context
        super().set_arguments(data)


    def run(self):
        '''
        Read values from context and add them back to the context to simulate
        a real run.
        '''
        logging.info("Reusing the results...")
        ctx_dict:dict = self._activity_output_context.get_focus_activity_dict()

        for key, val in ctx_dict.items():
            #logging.info(f"key: {key}  val: {val}")
            self._activity_output_context.set(key=key, value=val)

#---------------------------- SKIP_WITH_OUTPUT_VALUES ---------------------------------#
''' An activit that provides the output read from skipWithOutputs configuration. '''
@ActivityRegistry.activity(type="skip-with-output-values")
class SkipReuseActivity(Activity):

    def __init__(self):
        super().__init__()
        self._activity_output_context:Context = None
        self._skip_with_outputs_outputs:dict = None


    def set_arguments(self, data: ActivityData):
        self._activity_output_context = data.output_context
        self._skip_with_outputs_outputs = data.activity_config.skip_with_outputs_values
        super().set_arguments(data)


    def run(self):
        '''
        Read values from skip-with-outputs configuration and copy the values into
        the output context.
        '''

        for key,val in self._skip_with_outputs_outputs.items():
            self._activity_output_context.set(key=key,value=val)
