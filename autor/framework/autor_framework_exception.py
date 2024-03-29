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
class AutorFrameworkException(Exception):
    """Exception for all framework errors"""


class AutorFrameworkValueException(AutorFrameworkException):
    """Exception for errors detected in the framework caused by incorrect usage \
        of the framework by a user"""


class AutorFrameworkNotImplementedException(AutorFrameworkException):
    """Exception for errors due to missing implementation in Autor"""
