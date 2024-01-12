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


class ContextProperty:
    """A context property container class"""

    def __init__(self, name, class_name, mandatory, property_type, default):
        self.__name = name
        self.__class_name = class_name
        self.__mandatory = mandatory
        self.__property_type = property_type
        self.__default = default

    def print(self):
       #default_value_def = ""
       # if self.default != "DEFAULT_PROPERTY_VALUE_NOT_DEFINED":
           # default_value_def = f",default={self.default}"
        #logging.info(f"{self.class_name}.{self.name} @{self.property_type}(mandatory={self.mandatory},type={self.property_type}{default_value_def}")

        logging.info(f"{self.name} {self.property_type} {self.mandatory} {self.default} {self.class_name}")



    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, n):
        self.__name = n

    @property
    def class_name(self) -> str:
        return self.__class_name

    @class_name.setter
    def class_name(self, n):
        self.__class_name = n

    @property
    def mandatory(self) -> str:
        return self.__mandatory

    @mandatory.setter
    def mandatory(self, n):
        self.__mandatory = n

    @property
    def property_type(self) -> str:
        return self.__property_type

    @property_type.setter
    def property_type(self, n):
        self.__property_type = n

    @property
    def default(self) -> str:
        return self.__default

    @default.setter
    def default(self, n):
        self.__default = n
