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
from typing import Dict, Any

from autor.framework.context import Context



"""
A class for reading and writing values to activity block context. Intended for use by Autor users in callbacks
and extensions.
"""
class ActivityBlockContext:
    def __init__(self, activity_block_id: str):
        self._context = Context(activity_block=activity_block_id)

    def get(self, key:str, default:Any=Context.UNDEFINED):
        """
        key:str - key in the context.
        default:Any - default value to return if the key is not found in the context.
        return the value of 'key' or the value of 'default' if no value is found in context under 'key'.
        """
        return self._context.get(key=key,default=default)

    def set(self, key:str, value, propagate_value:bool=False):
        """
        key:str - key in the context
        propagate_value:boor - True - the value is made visible also to the flow context.
                               False - the value is visible only for the activity block context.
        """
        self._context.set(key=key, value=value, propagate_value=propagate_value)

    def raw(self)->Dict:
        """
        return:Dict[str,Any] - return the raw dictionary that represents the activity block context.
        """
        return self._context.raw()


