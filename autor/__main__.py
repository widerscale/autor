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
from autor.framework.autor_runner import run
import logging

from autor.framework.logging_config import LoggingConfig

if __name__ == "__main__":
    LoggingConfig.activate_framework_logging()
    # Run the activity block
    # logging.basicConfig(level=logging.DEBUG, format="%(levelname)8s: %(message)s")
    #
    #
    # for handler in logging.root.handlers[:]:
    #     logging.root.removeHandler(handler)
    # logging.basicConfig(level=logging.DEBUG, format="%(message)s")

    #logging.basicConfig(level=logging.DEBUG, format="%(levelname)-8s %(message)s")
    #logging.basicConfig(level=logging.DEBUG, format="%(module)-15s %(lineno)-5s %(levelname)-8s %(message)s")

    run()
