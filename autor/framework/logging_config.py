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

class LoggingConfig():
    framework_log_level = logging.INFO
    activity_log_level = logging.INFO
    extension_log_level = logging.INFO

    @staticmethod
    def activate_framework_logging():
        LoggingConfig.__remove_current_logging()
        logging.basicConfig(level=LoggingConfig.framework_log_level, format="%(levelname)8s: %(message)s")

    @staticmethod
    def activate_activity_logging():
        LoggingConfig.__remove_current_logging()
        logging.basicConfig(level=LoggingConfig.activity_log_level, format="%(levelname)8s: <act>: %(message)s")

    @staticmethod
    def activate_extension_logging():
        LoggingConfig.__remove_current_logging()
        logging.basicConfig(level=LoggingConfig.activity_log_level, format="%(levelname)8s: <ext>: %(message)s")

    @staticmethod
    def __remove_current_logging():
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)



