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
# fmt:off
import logging



class Flags():
    # A class that helps to switch on/off functionality. Flags can be provided by users.

    allow_flow_run_id_in_mode_activity = False

    @staticmethod
    def reset_static_data():
        allow_flow_run_id_in_mode_activity = False

    @staticmethod
    def set_flags(flags:dict):
        for attr_name,val in flags.items():
            if hasattr(Flags, attr_name):
                setattr(Flags, attr_name, val)
            else:
                raise ValueError(f"Could not set a value for flag: {attr_name}. The flag with that name does not exist.")




# fmt: on
