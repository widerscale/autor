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
from dataclasses import dataclass
from typing import Any, Optional

from pygments.lexer import default

from autor.framework.constants import PropertyCategory
from autor.framework.context_properties_registry import ContextPropertiesRegistry


@dataclass
class ActivityPropertyInformation:
    """An activity property information container class"""
    name:str
    type:type[Any]
    mandatory:bool
    default:Any
    category:PropertyCategory
    value:Optional[Any]=None

    def print(self):

        _type = f"{self.type}".split("'")[1]
        if self.default == ContextPropertiesRegistry.DEFAULT_PROPERTY_VALUE_NOT_DEFINED:
            default = ""
        else:
            default = f"(default={self.default})"


        logging.info(f"[{self.category}] {self.name}:{_type}={self.value} {default}")

# [cfg] val:int=7 (default=0)
# [inp] max:int=11
# [out] max:int=11
# [out] status:str=SUCCESS




