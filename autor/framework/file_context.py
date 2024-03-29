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
import json

from autor.framework.extension_exception import AutorExtensionException
from autor.framework.remote_context import RemoteContext


class FileContext(RemoteContext):

    # C O N S T A N T S
    # ------------------
    # A string constant to use as the name of file which is going to be the file context.
    _FILENAME = "file_context.json"
    # pylint: disable-next=redefined-builtin
    def sync(self, id: str, context: dict) -> None:
        file_content = {}
        try:
            with open(self._FILENAME, "r", encoding="utf8") as file_context:
                file_content = json.load(file_context)
                remote_context = file_content.get(id, {})  # File may contain more than one context
        except FileNotFoundError:
            remote_context = {}
        except Exception as exception:
            raise AutorExtensionException(
                f"Failed to open file context for syncing. Exception: {exception.args}"
            ) from exception

        remote_context.update(context)
        context.update(remote_context)
        file_content.update({id: remote_context})

        try:
            with open(self._FILENAME, "w", encoding="utf8") as file_context:
                json.dump(file_content, file_context, indent=2)
        except Exception as exception:
            # logging.error(f"Failed to open file context for syncing. Exception: {e.args}")
            raise AutorExtensionException(
                f"Failed to open file context for syncing. Exception: {exception.args}"
            ) from exception
