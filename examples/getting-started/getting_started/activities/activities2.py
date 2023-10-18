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


from autor import Activity
from autor.framework.activity_block_callback import ActivityBlockCallback
from autor.framework.activity_registry import ActivityRegistry
from autor.framework.constants import Status
from autor.framework.context_properties_registry import ContextPropertiesRegistry

output = ContextPropertiesRegistry.output
# pylint: disable-next=redefined-builtin
input = ContextPropertiesRegistry.input


# -----------------------  C a l l b a c k s   e x a m p l e  -----------------------#

# ------------- Activity ----------
@ActivityRegistry.activity(type="CALLBACK")
class CallbackActivity(Activity):
    def run(self):
        # read the activity status from the configuration
        self.status = self.configuration["status"]
        self.activity_block_callbacks.append(
            SuccesOrSkippedCallback(self, [Status.SUCCESS, Status.SKIPPED])
        )
        self.activity_block_callbacks.append(FailureCallback(self, [Status.FAIL]))
        self.activity_block_callbacks.append(AllCallback(self, [Status.ALL]))
        # self.print()


# --------- Callback classes -------
class SuccesOrSkippedCallback(ActivityBlockCallback):
    def run(self):
        print("Running SuccesOrSkippedCallback")


class FailureCallback(ActivityBlockCallback):
    def run(self):
        print("Running FailureCallback")


class AllCallback(ActivityBlockCallback):
    def run(self):
        print("Running FailureCallback")


@ActivityRegistry.activity(type="PRINT")
class PrintActivity(Activity):
    def run(self):
        self.print()


@ActivityRegistry.activity(type="EMPTY")
class EmptyActivity(Activity):
    def run(self):
        pass


@ActivityRegistry.activity(type="MESSAGE")
class MessageActivity(Activity):
    def run(self):
        print(self.configuration["message"])
