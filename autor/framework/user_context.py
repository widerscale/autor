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
import abc
import copy
import logging
from typing import Dict, Any

from autor.framework.context import Context
from autor.framework.util import Util


# ------------------------------------------------------------------------------#
#                              State classes                                   #
# ------------------------------------------------------------------------------#
# redefined-builtin: dict
# pylint: disable=redefined-builtin
class UserContext:
    __metaclass__ = abc.ABCMeta

    def __init__(self, context:Context):
        self._context:Context = context


    def get(self, key: str, default: Any = Context.UNDEFINED):
        """
        key:str - Key in the context. Keys may not begin with "_".
        default:Any - default value to return if the key is not found in the context.
        return the value of 'key' or the value of 'default' if no value is found in context under 'key'.
        """
        if key.startswith("_"):
            raise ValueError("Context keys may not start with '_'.")

        return self._context.get(key=key, default=default)

    def set(self, key: str, value: Any):
        """
        key:str - Key in the context. Keys may not start with "_".
        """
        self._context.set(key=key, value=value)


    def print(self):
        ctx: Dict[str, Any] = copy.deepcopy(self._context.raw())
        # Don't print any internal context
        for key, val in self._context.raw().items():
            if key.startswith("_"):
                del ctx[key]

        Util.print_dict(ctx, level="info")
