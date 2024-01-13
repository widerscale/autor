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
#    License for the specific language governing permi
#     *******************ssions and limitations
#    under the License.

import logging

from autor import Activity
from autor.framework.activity_registry import ActivityRegistry
from autor.framework.context_properties_registry import ContextPropertiesRegistry

output = ContextPropertiesRegistry.output
# pylint: disable-next=redefined-builtin
input = ContextPropertiesRegistry.input



@ActivityRegistry.activity()
class ProblematicActivity_MissingType(Activity):
    def run(self):
        logging.info("My decorator has no type")

@ActivityRegistry.activity(type=None)
class ProblematicActivity_TypeIsNone(Activity):
    def run(self):
        logging.info("My decorator has no type=None")


@ActivityRegistry.activity(type="happy")
class Happy(Activity):

    def run(self):
        logging.info("I'm happy!")


