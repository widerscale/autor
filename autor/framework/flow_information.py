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
from dataclasses import dataclass
from lib2to3.fixes.fix_input import context
from typing import List, Optional, Dict

from autor.flow_configuration.activity_block_configuration import ActivityBlockConfiguration
from autor.flow_configuration.activity_configuration import ActivityConfiguration
from autor.framework.activity_block_context import ActivityBlockContext
from autor.framework.activity_context import ActivityContext
from autor.framework.activity_property import ActivityProperty
from autor.framework.activity_property_information import ActivityPropertyInformation
from autor.framework.constants import Mode, Status
from autor.framework.context import Context
from autor.framework.flow_context import FlowContext
from autor.framework.util import Util


@dataclass
class FlowInformation:
    """
    Container for flow related information.
    """
    id: Optional[str] = None
    """ Unique identifier of the flow. Provided by the user in the Flow Configuration.
    Human-readable.
    """
    configuration: Optional[Dict[str,str]] = None
    """ Flow configuration as provided in the Flow Configuration file on flow level.
    """
    context: Optional[FlowContext] = None
    """ Utility for reading and writing from/to internal flow context.
        None, if the flow has not yet been instantiated.
    """
    run_id: Optional[str] = None
    """ UUID of the flow run.
        None, if the flow has not yet been instantiated by the framework.
    """


    def print(self):
        Util.print_header("",text="F L O W   I N F O R M A T I O N", level='info')
        logging.info(f"id:            {self.id}")

        # ----------------- Configuration ---------------
        if self.configuration is None or self.configuration == {}:
            logging.info(f"configuration: {self.configuration}")
        else:
            logging.info(f"configuration:")
            Util.print_dict(self.configuration, level='info')
        logging.info(f"run_id:        {self.run_id}")

        # ----------------- Context --------------------
        if self.context is None or self.context.raw() == {}:
            logging.info(f"context:       {self.context}")

        else:
            logging.info(f"context:")
            self.context.print()
            #Util.print_dict(dict=self.context.raw(), level='info')
