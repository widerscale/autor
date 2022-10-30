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
from autor.framework.context import Context


# A Context class wrapper for activities. It allows to read values from anywhere in the context, but
# limits writing to the area that belongs to the given activity.
class ActivityContext:
    def __init__(self, activity_block: str, activity: str):
        self._activity = activity
        self._activity_block = activity_block
        self._context = Context(activity_block=activity_block, activity=activity)

    def get_from_activity(
        self,
        key: str,
        # pylint: disable-next=protected-access
        default=Context._UNDEFINED,
        activity: str = None,
        activity_block: str = None,
        search: bool = False,
    ):
        return self._context.get_from_activity(
            key=key,
            default=default,
            activity=activity,
            activity_block=activity_block,
            search=search,
        )

    def get_from_activity_block(
        self,
        key: str,
        # pylint: disable-next=protected-access
        default=Context._UNDEFINED,
        activity_block: str = None,
        search: bool = False,
    ):
        return self._context.get_from_activity_block(
            key=key,
            default=default,
            activity_block=activity_block,
            search=search,
        )

    # pylint: disable-next=protected-access
    def get(self, key: str, default=Context._UNDEFINED, search: bool = False):
        return self._context.get(key=key, default=default, search=search)
