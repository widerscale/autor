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
import inspect
import logging

from autor import Activity
from autor.framework.activity_block_callback import ActivityBlockCallback
from autor.framework.activity_registry import ActivityRegistry
from autor.framework.constants import Status
from autor.framework.context_properties_registry import ContextPropertiesRegistry


output = ContextPropertiesRegistry.output
# pylint: disable-next=redefined-builtin
input = ContextPropertiesRegistry.input
config = ContextPropertiesRegistry.config


@ActivityRegistry.activity(type="PRINT")
class Print(Activity):

    #region property: text @config(mandatory=False, type=str)
    @property
    @config(mandatory=False, type=str)
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, n:str) -> None:
        self._text = n
    #endregion
    #region property: date @input(mandatory=False, type=str)
    @property
    @input(mandatory=False, type=str)
    def date(self) -> str: return self._date
    @date.setter
    def date(self, n:str) -> None: self._date = n
    #endregion

    def run(self):
        logging.info(f"Welcome to Autor! {self.text}")





@ActivityRegistry.activity(type="WELCOME")
class Welcome(Activity):
    def run(self):
        logging.info("Welcome to Autor!")
        #logging.info(f"Printed from: {inspect.getfile(self.__class__)}")


@ActivityRegistry.activity(type="HELLO_WORLD")
class HelloWorld(Activity):
    def run(self):
        logging.info("Hello World!")


@ActivityRegistry.activity(type="HELLO_NAME")
class HelloName(Activity):
    def run(self):
        name = self.configuration.get("name","World")
        logging.info(f"Hello {name}!")


@ActivityRegistry.activity(type="HELLO_TO_EVERYONE")
class HelloEveryone(Activity):
    def __init__(self):
        super().__init__()
        self.__all_persons:list = []
        """Hej"""

    def run(self):
        name = self.configuration.get("name", default="World")
        self.all_persons.append(name)
        for n in self.all_persons:
            logging.info(f"Hello {n}!")

    # --------------------- all_persons ------------------------ #
    @property
    @input(mandatory=False, type=list)
    @output(mandatory=True, type=list)


    def all_persons(self) -> list:
        return self.__all_persons

    @all_persons.setter
    def score(self, n:list) -> None:
        self.__all_persons = n


@ActivityRegistry.activity(type="HELLO_TO_EVERYONE_WITHOUT_INPUT")
class HelloEveryoneNoInput(Activity):
    def __init__(self):
        super().__init__()
        self.__all_persons: list = []

    def run(self):
        name = self.configuration.get("name", default="World")
        self.all_persons.append(name)
        for n in self.all_persons:
            logging.info(f"Hello {n}!")

    # --------------------- all_persons ------------------------ #
    @property
    @output(mandatory=True, type=list)
    def all_persons(self) -> list:
        return self.__all_persons

    @all_persons.setter
    def score(self, n: list) -> None:
        self.__all_persons = n


@ActivityRegistry.activity(type="HELLO_TO_EVERYONE_WITHOUT_OUTPUT")
class HelloEveryoneNoOutput(Activity):
    def __init__(self):
        super().__init__()
        self.__all_persons: list = []

    def run(self):
        name = self.configuration.get("name", default="World")
        self.all_persons.append(name)
        for n in self.all_persons:
            logging.info(f"Hello {n}!")

    # --------------------- all_persons ------------------------ #
    @property
    @input(mandatory=False, type=list)
    def all_persons(self) -> list:
        return self.__all_persons

    @all_persons.setter
    def score(self, n: list) -> None:
        self.__all_persons = n












@ActivityRegistry.activity(type="EXAMPLE")
class ExampleActivity(Activity):
    def run(self):
        logging.info("Hello World!")


@ActivityRegistry.activity(type="TYPE 1")
class Type1(Activity):
    def run(self):
        logging.info("type:  TYPE 1")
        logging.info("class: " + str(self.__class__.__name__))


@ActivityRegistry.activity(type="TYPE 2")
class Type2(Activity):
    def run(self):
        logging.info("type:  TYPE 2")
        logging.info("class: " + str(self.__class__.__name__))


@ActivityRegistry.activity(type="CONFIGURABLE")
class Configurable(Activity):
    def run(self):
        name = self.configuration.get("name", "No name provided!")
        message = self.configuration.get("message", "No message provided!")
        logging.info("name:          " + name)
        logging.info("message:       " + message)
        logging.info("configuration: " + str(self.configuration))


@ActivityRegistry.activity(type="OUTPUT")
class OutputActivity(Activity):
    def __init__(self):
        super().__init__()
        self.__score: int = None

    @property
    @output(mandatory=True, type=int)  # save the value after run() is finished
    def score(self) -> int:  # getter
        return self.__score

    @score.setter
    def score(self, n) -> None:  # setter
        self.__score = n

    def run(self):
        logging.info(f'Score is initially set to: {self.score}')
        self.score = 10
        logging.info(f'Setting score to: {self.score}')


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
        logging.info(f'Score is initially set to: {self.score}')



# Calculate the highest score in the flow.
@ActivityRegistry.activity(type="INPUT_OUTPUT")
class InputOutputActivity(Activity):
    def __init__(self):
        super().__init__()
        # initial value that is used if no value has been provided by the flow
        self.__highest_score: int = -1


    @property
    @input(mandatory=False, type=int)  # load the value before run() is called
    @output(mandatory=True, type=int)  # save the value after run() is finished
    def highest_score(self) -> int:  # getter
        return self.__highest_score

    @highest_score.setter
    def highest_score(self, n) -> None:  # setter
        self.__highest_score = n

    def run(self):
        my_score = self.configuration["myScore"]  # Read my score from the Flow Configuration file
        logging.info(f"Property:        'highest_score': {self.highest_score} (initial value)")
        logging.info(f"Configuration:   'myScore:'       {my_score}")

        self.highest_score = max(self.highest_score, my_score)  # Calculate the new highest score
        logging.info(f"Property:        'highest_score': {self.highest_score} (final value)")



@ActivityRegistry.activity(type="SKIPPED")
class StatusSkipped(Activity):
    def run(self):
        logging.info("Setting status to SKIPPED")
        self.status = Status.SKIPPED


@ActivityRegistry.activity(type="SUCCESS")
class StatusSuccess(Activity):
    def run(self):
        logging.info("A successful run, expecting status SUCCESS")


@ActivityRegistry.activity(type="ERROR")
class StatusError(Activity):
    def run(self):
        logging.info("Creating an exception, expecting status ERROR")
        # pylint: disable-next=pointless-statement
        10 / 0  # Division by zero will lead to an exception


