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
from autor.framework.activity_block import ActivityBlock
from autor.framework.argument_parser import CommandlineArgumentParser
from autor.framework.key_handler import KeyConverter
from autor.framework.keys import ArgParserKeys as argp



def run():
    # TODO: Re-write as click CLI
    # Get command-line parameters. Checks the mandatory params.
    args = CommandlineArgumentParser().parse()
    params = vars(args)  # Params as dict

    # pylint: disable=no-member


    # Create and run activity block
    activity_block = ActivityBlock(
        mode                    = KeyConverter.LCD_to_UCU(params.get(argp.MODE)),  # mandatory
        additional_context      = params.get(argp.ADDITIONAL_CONTEXT, None),
        #additional_config       = params.get(argp.ADDITIONAL_CONFIG, None),
        additional_extensions   = params.get(argp.ADDITIONAL_EXTENSIONS, None),
        activity_block_id       = params.get(argp.ACTIVITY_BLOCK_ID, None),
        activity_config         = params.get(argp.ACTIVITY_CONFIG, None),
        activity_id             = params.get(argp.ACTIVITY_ID, None),
        activity_input          = params.get(argp.ACTIVITY_INPUT, None),
        activity_module         = params.get(argp.ACTIVITY_MODULE, None),
        activity_name           = params.get(argp.ACTIVITY_NAME, None),
        activity_type           = params.get(argp.ACTIVITY_TYPE, None),
        custom_data             = params.get(argp.CUSTOM_DATA, None),
        flow_run_id             = params.get(argp.FLOW_RUN_ID, None),
        flow_config_url         = params.get(argp.FLOW_CONFIG_URL, None)

    )
    # pylint: enable=no-member
    activity_block.run()




if __name__ == "__main__":
    # Run the activity block
    run()
