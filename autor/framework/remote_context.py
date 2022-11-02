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


class RemoteContext:
    __metaclass__ = abc.ABCMeta

    """
    RemoteContext is an abstract class that provides an interface that is needed by the framework.\
         Inherit from this
    class when creating own remote context classes.
    """

    @abc.abstractmethod
    # pylint: disable-next=redefined-builtin
    def sync(self, id: str, context: dict) -> None:
        """Synchronize the local context with the remote context. \
            After the synchronization both the local context
        and the remote context should contain exactly the same values.

        Arguments:
            id {str} -- Unique identifier of the flow instance context.
            context {dict} -- The local dictionary that should be synchronized with \
                the remote context.
        """
