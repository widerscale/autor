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
from autor.framework.keys import ArgParserKeys as argp


def run():
    # TODO: Re-write as click CLI
    # Get command-line parameters. Checks the mandatory params.
    args = CommandlineArgumentParser().parse()
    params = vars(args)  # Params as dict

    # pylint: disable=no-member
    flow_run_id = params.get(argp.FLOW_RUN_ID, None)

    # Create and run activity block
    activity_block = ActivityBlock(
        flow_config_url=params[argp.FLOW_CONFIG_URL],
        activity_block_id=params[argp.ACTIVITY_BLOCK_ID],
        flow_run_id=flow_run_id,
    )
    # pylint: enable=no-member
    activity_block.run()


if __name__ == "__main__":
    # Run the activity block
    run()
