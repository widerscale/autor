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
from typing import Dict

from autor.framework.context import Context


# A class for reading and writing values to one specific activity context.
class ActivityContext:
    def __init__(self, activity_block_id: str, activity_id: str):
        self._context = Context(activity_block=activity_block_id, activity=activity_id)

    def get(self, key:str, default=Context.UNDEFINED):
        return self._context.get(key=key,default=default)

    def set(self, key:str, value, propagate_value:bool=False):
        self._context.set(key=key, value=value, propagate_value=propagate_value)

    def raw(self)->Dict:
        return self._context.raw()


