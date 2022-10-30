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


@ActivityRegistry.activity(type="EXAMPLE")
class ExampleActivity(Activity):
    def run(self):
        print("Hello Worlds!")


@ActivityRegistry.activity(type="TYPE 1")
class Type1(Activity):
    def run(self):
        print("type:  TYPE 1")
        print("class: " + str(self.__class__.__name__))


@ActivityRegistry.activity(type="TYPE 2")
class Type2(Activity):
    def run(self):
        print("type:  TYPE 2")
        print("class: " + str(self.__class__.__name__))


@ActivityRegistry.activity(type="CONFIGURABLE")
class Configurable(Activity):
    def run(self):
        name = self.configuration.get("name", "No name provided!")
        message = self.configuration.get("message", "No message provided!")
        print("name:          " + name)
        print("message:       " + message)
        print("configuration: " + str(self.configuration))


@ActivityRegistry.activity(type="OUTPUT")
class OutputActivity(Activity):
    @property
    @output(mandatory=True, type=int)  # save the value after run() is finished
    def score(self) -> int:  # getter
        return self.__score

    @score.setter
    def score(self, n) -> None:  # setter
        self.__score = n

    def run(self):
        self.score = 10


@ActivityRegistry.activity(type="INPUT")
class InputActivity(Activity):
    def __init__(self):
        super().__init__()
        self.__score: int = None

    @property
    @input(mandatory=False, type=int)  # load the value before run() is called
    def score(self) -> int:  # getter
        return self.__score

    @score.setter
    def score(self, n) -> None:  # setter
        self.__score = n

    def run(self):
        print("score (input) = " + str(self.score))


# Calculate the highest score in the flow.
@ActivityRegistry.activity(type="INPUT_OUTPUT")
class InputOutputActivity(Activity):
    def __init__(self):
        super().__init__()
        self.__highest_score: int = (
            -1
        )  # initial value that is used if no value has been provided by the flow

    @property
    @input(mandatory=False, type=int)  # load the value before run() is called
    @output(mandatory=True, type=int)  # save the value after run() is finished
    def highest_score(self) -> int:  # getter
        return self.__highest_score

    @highest_score.setter
    def highest_score(self, n) -> None:  # setter
        self.__highest_score = n

    def run(self):
        print("highest_score in:  " + str(self.highest_score))
        my_score = self.configuration["myScore"]  # Read my score from the Flow Configuration file
        self.highest_score = max(self.highest_score, my_score)  # Calculate the new highest score
        print("highest_score out: " + str(self.highest_score))


@ActivityRegistry.activity(type="SKIPPED")
class StatusSkipped(Activity):
    def run(self):
        print("Setting status to SKIPPED")
        self.status = Status.SKIPPED


@ActivityRegistry.activity(type="SUCCESS")
class StatusSuccess(Activity):
    def run(self):
        print("A successful run, expecting status SUCCESS")


@ActivityRegistry.activity(type="ERROR")
class StatusError(Activity):
    def run(self):
        print("Creating an exception, expecting status ERROR")
        # pylint: disable-next=pointless-statement
        10 / 0  # Division by zero will lead to an exception


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
