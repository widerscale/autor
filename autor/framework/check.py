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
from autor.framework.autor_framework_exception import AutorFrameworkException
from autor.framework.constants import Status, ExceptionType, Mode


class Check:
    """
    This class can be used for performing checks that will
    throw AutorFrameworkException when they fail. Similar to assert.
    """

    @staticmethod
    def expected(expected, actual, msg: str = ""):
        #description = str(msg) + " <<<" + str(value1) + "==" + str(value2) + ")"
        description = f'\n\n____________________ CHECK FAIL _____________________\nexpected: {str(expected)}\ngot:      {str(actual)}\n{msg}'
        if expected != actual:
            raise AutorFrameworkException(description)

    @staticmethod
    def is_equal(value1, value2, msg: str = ""):
        #description = str(msg) + " <<<" + str(value1) + "==" + str(value2) + ")"
        description = f'\n\n____________________ CHECK FAIL _____________________\n<<< {str(value1)} != {str(value2)} >>>\n{msg}'
        if value1 != value2:
            raise AutorFrameworkException(description)


    @staticmethod
    def is_in(val, collection, msg: str = ""):
        description = f'\n\n____________________ CHECK FAIL _____________________\n<<< {val} not found in collection >>>\n{msg}'
        if not val in collection:
            raise AutorFrameworkException(description)

    @staticmethod
    def not_none(val, msg: str = ""):
        description = f'\n\n____________________ CHECK FAIL _____________________\n<<< Value may not be None >>>\n{msg}'
        if val is None:
            raise AutorFrameworkException(description)



    @staticmethod
    def is_true(value, exception_type:type=AutorFrameworkException,  msg: str = "Msg not provided"):
        if msg == "Msg not provided":
            msg = f"Expression did not evaluate to True."
            if not value:
                raise exception_type(msg)


    @staticmethod
    def true(value,  exception:type, msg:str="",):
        if value is False:
            raise exception(msg)




    @staticmethod
    def is_non_empty_string(value: str, exception_type:type=AutorFrameworkException, msg: str = "Msg not provided"):
        if msg == "Msg not provided":
            msg = f"Expected non-empty string, received: {value}"

        if (str is None) or (not isinstance(value, str)) or len(value) <= 0:
            raise exception_type(msg)


    @staticmethod
    def is_string(value: str, exception_type:type=AutorFrameworkException, msg: str = "Msg not provided"):
        if msg == "Msg not provided":
            msg = f"Expected string, received: {value}"

        if (str is None) or (not isinstance(value, str)):
            raise exception_type(msg)

    @staticmethod
    def is_none_or_empty(value, exception_type:type=AutorFrameworkException, msg: str = "Msg not provided"):
        if msg == "Msg not provided":
            msg = f'Expected one of the following values: None, "", {{}}, []. Received: {value}'

        if not ((value is None) or (value == "") or (value == {}) or (value == [])):
            raise exception_type(msg)


    @staticmethod
    def is_autor_mode(value: Mode, exception_type:type=AutorFrameworkException, msg: str = "Msg not provided"):
        if msg == "Msg not provided":
            msg = f"Expected Autor Mode, received: {value}. Valid modes: {Mode.get_valid_constants(Mode)}"

        if (str is None) or (not isinstance(value, str)) or len(value) <= 0:
            raise exception_type(msg)



    @staticmethod
    def is_none(value, msg: str = ""):
        description = str(msg) + " ([Check]: Expected None, received: " + str(value) + ")"
        if value is not None:
            raise AutorFrameworkException(description)



    @staticmethod
    def is_false(value, msg: str = ""):
        description = str(msg) + " ([Check]: Expected False, received: " + str(value) + ")"
        if value is True:
            raise AutorFrameworkException(description)

    @staticmethod
    def not_empty_list(value: list, msg: str = ""):
        description = (
            str(msg) + " ([Check]: Expected a non empty list, received: " + str(value) + ")"
        )
        if (value is None) or (not isinstance(value, list)) or len(value) <= 0:
            raise AutorFrameworkException(description)

    @staticmethod
    def is_instance_of(value, expected_type, msg: str = ""):
        description = (
            str(msg)
            + " [Check]: Expected type: "
            + str(expected_type)
            + " received: "
            + str(type(value))
        )
        if not isinstance(value, expected_type):
            raise AutorFrameworkException(description)

    @staticmethod
    def is_status(value, msg: str = ""):
        description = f"{msg}. Valid status values are: {Status.get_valid_constants(Status)}"
        status = Status()
        if not hasattr(status, value):
            raise AutorFrameworkException(description)

  #  staticmethod
  #  def _create_exception(message:str, ex_source):
   #     if ex_type == ExceptionType.

