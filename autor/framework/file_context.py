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
import logging
import traceback
from typing import Dict

from autor.framework.debug_config import DebugConfig
from autor.framework.extension_exception import AutorExtensionException
from autor.framework.remote_context import RemoteContext
from autor.framework.util import Util


class FileContext(RemoteContext):

    # C O N S T A N T S
    # ------------------
    # A string constant to use as the name of file which is going to be the file context.
    _FILENAME = "file_context.json"
    _BACKUP_FILENAME = "file_context_backup.json"
    # pylint: disable-next=redefined-builtin
    def sync(self, id: str, context: dict) -> None:
        file_content = {}



        # Read the remote context
        try:
            with open(self._FILENAME, "r", encoding="utf8") as file_context:
                file_content = json.load(file_context)
                remote_context = file_content.get(id, {})  # File may contain more than one context
        except FileNotFoundError:
            remote_context = {}

        except Exception as exception:
            logging.warning(f"Failed to open context file:{self._FILENAME} for syncing. Exception: {exception.args}")
            logging.warning(f"Trying to use backup: {self._BACKUP_FILENAME}")
            try:
                with open(self._BACKUP_FILENAME, "r", encoding="utf8") as file_context:
                    file_content = json.load(file_context)
                    logging.warning(f"Successfully read: {self._BACKUP_FILENAME}")
                    remote_context = file_content.get(id, {})  # File may contain more than one context
            except FileNotFoundError:
                logging.error(f"Could not find the backup file: {self._BACKUP_FILENAME} -> raising an exception.")
                raise AutorExtensionException(
                    f"Failed to open file context: {self._FILENAME} and context backup: {self._BACKUP_FILENAME} does not exist .Exception: {exception.args}"
                ) from exception

            except Exception as exception:
                raise AutorExtensionException(
                    f"Failed to open file context: {self._FILENAME} and {self._BACKUP_FILENAME} for syncing. Exception: {exception.args}"
                ) from exception


        if DebugConfig.trace_context:
            logging.info(f"ID:     {id}")
            Util.print_dict(context, "local context before sync", 'info')
            Util.print_dict(remote_context, "remote context before sync", 'info')


        # Update the context of the remote flow with the local flow context
        remote_context.update(context)

        # Update the local flow context with the remote flow context
        context.update(remote_context)

        if DebugConfig.trace_context:
            logging.info(f"ID:     {id}")
            Util.print_dict(context, "context after sync", 'info')

        # Update the file context with the updated flow context
        file_content.update({id: remote_context})

        self._write(file_content, self._BACKUP_FILENAME)
        self._write(file_content, self._FILENAME)



    def _write(self, file_content:Dict, file_name:str):
        try:
            with open(file_name, "w", encoding="utf8") as file_context:
                json.dump(file_content, file_context, indent=2)
        except Exception as exception:
            raise AutorExtensionException(
                f"Failed to open file context: {file_name} for writing. Exception: {exception.args}"
            ) from exception

