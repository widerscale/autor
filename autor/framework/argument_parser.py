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
import argparse
import json
import logging

from autor.framework.debug_config import DebugConfig
from autor.framework.keys import CommandLineKeys as cln
from autor.framework.util import Util


class CommandlineArgumentParser:
    """
    Command line argument parser for Autor parameters.
    """

    def parse(self):
        """Parses the command-line arguments.

        Returns:
            argparse.Namespace -- The parser with the parsed parameters.
        """
        return self._configure_parser().parse_args()

    # pylint: disable-next=no-self-use
    def _configure_parser(self):
        """Get configured parser.

        Returns:
            argparse.Namespace -- The configured parser.
        """


        description = """
Note that in Autor all the command-line arguments can be provided
through extensions instead. This means that none of the command-line
arguments is mandatory. In this documentation we indicate what sets
of arguments are mandatory or optional once Autor starts running.

Autor can be run in three modes:
1. ACTIVITY BLOCK mode
   Autor runs activities in a specified activity block
   Mandatory: --flow-config-url
   Mandatory: --activity-block-id
   Optional:  --flow-run-id
   
   --flow-config-url - URL to the flow configuration file. If this 
                       argument is not provided, the URL needs to 
                       be provided by an extension. 
                       
   --activity-block-id - The identifier of the activity block that will
                        be run. The identifier must match the activity
                        block identifier within the Flow Configuration
                        (pointed out by --flow-config-url)
                        
   --flow-run-id - An identifier that binds together several Autor runs.
                   Each Autor run creates data that is saved in context.
                   If a flow-run-id is provided the data in the context
                   can be used by Autor.
   
   
2. ACTIVITY IN BLOCK mode (for development)
   Autor runs one specified activity within a specified activity block
   Mandatory: --flow-config-url
   Mandatory: --activity-block-id
   Mandatory: --activity-name

    --flow-config-url - URL to the flow configuration file. If this 
                       argument is not provided, the URL needs to 
                       be provided by an extension. 
                       
   --activity-block-id - The identifier of the activity block that will
                        be run. The identifier must match the activity
                        block identifier within the Flow Configuration
                        (pointed out by --flow-config-url)
                        
   --activity-name - An identifier that points out the activity to run
                     inside the Flow Configuration (pointed out by 
                     --flow-config-url)      
   
   
   
3. ACTIVITY mode (for development)
   Autor runs one specified activity.
   Autor uses the provided information and
   Mandatory: --activity-module
   Mandatory: --activity-type
   Optional:  --activity-config
   Optional:  --activity-input
   Optional:  --flow-run-id
   
   --activity-module - Python module that contains the activity to run.
                       Autor will load the module.
                       
   --activity-type - The 'type' that is used in the activity decorator.
                     Note that the module specified in --activity-module
                     may not contain several activities decorated with
                     the same type.
   
   --activity-config - JSON string that contains the configuration to the 
                      activity to run. The format of the configuration 
                      corresponds to the format that would be used in flow
                      configuration.
                      
   --activity-input - JSON string that contains a JSON object where keys 
                      correspond to the activity's INPUT or INPUT_OUTPUT
                      properties. Note that the key names must have 
                      camelCase format.
                      
                      Example JSON String: 
                     "{\\"highestScore\\":13,\\"nbrContestants\\":5}"
                      
   --flow-run-id - An identifier that binds together several Autor runs.
                   Each Autor run creates data that is saved in context.
                   If a flow-run-id is provided the data in the context
                   can be used by Autor.
        """



        parser = argparse.ArgumentParser(description="")

        parser.add_argument(
            # pylint: disable-next=no-member
            "--" + cln.MODE,
            required=True,
            action="store",
            type=str,
            help="Autor mode",
        )

        parser.add_argument(
            # pylint: disable-next=no-member
            "--" + cln.FLOW_CONFIG_URL,
            required=False,
            action="store",
            type=str,
            help="Flow Configuration file URL",
        )

        parser.add_argument(
            # pylint: disable-next=no-member
            "--" + cln.ACTIVITY_BLOCK_ID,
            required=False,
            action="store",
            type=str,
            help="The unique identifier of the activity block within the Flow Configuration",
        )

        parser.add_argument(
            # pylint: disable-next=no-member
            "--" + cln.FLOW_RUN_ID,
            required=False,
            action="store",
            type=str,
            help=(
                "The unique identifier of a flow run."
                + " Generated by Autor if not provided as an argument."
            )
        )

        parser.add_argument(
            # pylint: disable-next=no-member
            "--" + cln.ACTIVITY_NAME,
            required=False,
            action="store",
            type=str,
            help="The unique identifier of the activity within Flow Configuration."
        )

        parser.add_argument(
            # pylint: disable-next=no-member
            "--" + cln.ACTIVITY_ID,
            required=False,
            action="store",
            type=str,
            help="The unique identifier of the activity run within an activity block run."
        )

        # An argument type for a list of strings
        def list_of_strings(arg):
            if arg is None or arg == "":
                return []
            return arg.split(',')

        parser.add_argument(
            # pylint: disable-next=no-member
            "--" + cln.ADDITIONAL_EXTENSIONS,
            required=False,
            action="store",
            type=list_of_strings,
            help=("Extensions that will be loaded in addition to the extensions" +
                  " listed in the flow configuration. The additional extensions" +
                  " have access to BOOTSTRAP state in Autor."
                  )
        )

        def json_string_or_simple_format(arg)->dict:
            try:
                dict_data: dict = json.loads(arg)
                logging.info(f"{DebugConfig.string_arg_parsing_prefix}Argument is JSON string: {arg}")

            except:
                try:
                    logging.info(f"{DebugConfig.string_arg_parsing_prefix}Argument is NOT JSON string: {arg}")
                    eq_split = arg.split('=')

                    # E X A M P L E
                    #
                    # Arguments in simple format:
                    # argInt=1,argFloat=0.5,argStr='Hello world!',argList=1,2,3,4
                    #
                    #
                    # After split on '='
                    #
                    # [argInt] 						#first arg name
                    # [1,argFloat] 					#<previous arg value, this arg name>
                    # [0.5,argStr]  				#<previous arg value, this arg name>
                    # ['Hello world!',argList]  	#<previous arg value, this arg name>
                    # [1,2,3,4] 					#last arg value

                    key = eq_split[0] #first arg name

                    dict_data:dict = {}

                    for item in eq_split[1:-1]:
                        next_key = item.split(',')[-1]
                        val = item.split(f',{next_key}')[0]
                        val = self._string_to_type(val)
                        dict_data[key] = val
                        key = next_key

                    val = eq_split[-1] #last arg value
                    dict_data[key] = self._string_to_type(val)

                except Exception as e:
                    logging.error(f"Could not parse argument. Expected JSON string or simple format (key1=val1,...,keyN=valN). Received: {arg}")
                    raise e

            return dict_data


        parser.add_argument(
            # pylint: disable-next=no-member
            "--" + cln.CUSTOM_DATA,
            required=False,
            action="store",
            type=json_string_or_simple_format,
            help=(
                "Custom data/configurations that can be provided to extensions. Format: JSON string or simple format: 'key1=1,key2=2,..,keyN=N'."
            )
        )



        parser.add_argument(
            # pylint: disable-next=no-member
            "--" + cln.ACTIVITY_MODULE,
            required=False,
            action="store",
            type=str,
            help="Python module that contains the activity to run."
        )
        parser.add_argument(
            # pylint: disable-next=no-member
            "--" + cln.ACTIVITY_TYPE,
            required=False,
            action="store",
            type=str,
            help="Activity type that identifies the activity class within a module."
        )

        parser.add_argument(
            # pylint: disable-next=no-member
            "--" + cln.ACTIVITY_CONFIG,
            required=False,
            action="store",
            type=json_string_or_simple_format,
            help="Configuration that becomes available for the activity during the run."
        )

        parser.add_argument(
            # pylint: disable-next=no-member
            "--" + cln.INPUT,
            required=False,
            action="store",
            type=json_string_or_simple_format,
            help="Values that become available for Activities as inputs. To remove an existing value set the value to null."
        )


        return parser

    def _string_to_type(self, val:str):
        prefix = DebugConfig.string_arg_parsing_prefix

        if val.lower() in ('none','null'):
            if DebugConfig.trace_string_arg_parsing:
                logging.info(f"{prefix}Value:{val} is None")
            return None


        try:
            final_val = int(val)
            if DebugConfig.trace_string_arg_parsing:
                logging.info(f"{prefix}Value:{val} is int")
        except:
            if DebugConfig.trace_string_arg_parsing:
                logging.info(f"{prefix}Value:{val} is NOT int")
            try:
                final_val = float(val)
                if DebugConfig.trace_string_arg_parsing:
                    logging.info(f"{prefix}Value:{val} is float")
            except:
                if DebugConfig.trace_string_arg_parsing:
                    logging.info(f"{prefix}Value:{val} is NOT float")


                if val in ('True','true'):
                    final_val = True
                    if DebugConfig.trace_string_arg_parsing:
                        logging.info(f"{prefix}Value:{val} is bool")
                elif val in ('False', 'false'):
                    final_val = False
                    if DebugConfig.trace_string_arg_parsing:
                        logging.info(f"{prefix}Value:{val} is bool")
                else:
                    if DebugConfig.trace_string_arg_parsing:
                        logging.info(f"{prefix}Value:{val} is NOT bool")


                    # Either string or a list
                    elems = val.split(',')

                    if len(elems)>1: # List
                        if DebugConfig.trace_string_arg_parsing:
                            logging.info(f"{prefix}Value:{val} is list")
                        final_val = []
                        for elem in elems:
                            elem = self._string_to_type(elem)
                            final_val.append(elem)

                    else:
                        if DebugConfig.trace_string_arg_parsing:
                            logging.info(f"{prefix}Value:{val} is string")
                        if (val[0] == "'" and val[-1] == "'") or (val[0] == '"' and val[-1] == '"'):
                            if DebugConfig.trace_string_arg_parsing:
                                logging.info(f"{prefix}Removing quotes from the string")
                            final_val = val[1:-1]
                        else:
                            final_val = val
        return final_val

