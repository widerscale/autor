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

'''
An activity without functionality that is used by Autor
when an unexpected error occurs and a user activity cannot
be created at all or in mode ACTIVIY_BLOCK_REUSE when we don't
want to run real activities.
'''


@ActivityRegistry.activity(type="AUTOR_FWK_DUMMY")
class ReuseActivity(Activity):

    def __init__(self):
        super().__init__()
        self._raw_context:Context = None


    def set_arguments(self, data: ActivityData):
        self._raw_context = data.output_context
        super().set_arguments(data)


    def run(self):
        logging.info(f"Context type: {self._raw_context.__class__.__name__}")
        ctx = self._raw_context
        ctx_dict = ctx.get_focus_activity_dict()

        for key, val in ctx_dict.items():
            logging.info(f"key: {val}  val: {val}")
            self._raw_context.set(key=key, value=val)


        pass
'''
    @property
    @input(mandatory=False, type=str)  # load the value before run() is called
    @output(mandatory=True, type=str)  # save the value after run() is finished
    def status(self) -> int:  # getter
        return super().status

    @status.setter
    def status(self, n:str):
        super(ReuseActivity, type(self)).status.fset(self, n)
'''

