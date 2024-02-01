import logging
import json
import os.path
from pathlib import Path
from typing import List

from autor.framework.activity_block import ActivityBlock
from autor.framework.check import Check
from autor.framework.constants import Mode
from autor.framework.context import Context
from autor.framework.key_handler import KeyConverter
from autor.framework.keys import CommandLineKeys as key
from autor.framework.util import Util




class AutorTester():
    __commands: List[str] = []


    @staticmethod
    def _parse_expectation(expectation:str)->(str,str):

        if expectation.startswith(Mode.ACTIVITY_BLOCK_RERUN):
            mode = key.ACTIVITY_BLOCK_RERUN
            expectation = expectation.removeprefix(f'{Mode.ACTIVITY_BLOCK_RERUN}_')
        elif expectation.startswith(Mode.ACTIVITY_IN_BLOCK):
            mode = key.ACTIVITY_IN_BLOCK
            expectation = expectation.removeprefix(f'{Mode.ACTIVITY_IN_BLOCK}_')
        elif expectation.startswith(Mode.ACTIVITY_BLOCK):
            mode = key.ACTIVITY_BLOCK
            expectation = expectation.removeprefix(f'{Mode.ACTIVITY_BLOCK}_')
        elif expectation.startswith(Mode.ACTIVITY):
            mode = key.ACTIVITY
            expectation = expectation.removeprefix(f'{Mode.ACTIVITY}_')
        else:
            raise ValueError(f"The file name for the expected result should begin with Autor mode name (ex: ACTIVITY_BLOCK_RERUN_calculateMax_SUCCESS_activity4.json). Received: {expectation}")

        #print(f"\nExpectation after remove mode: {expectation}")

        activity_block_id = expectation.split('_')[0]

        return mode, activity_block_id


    @staticmethod
    def _parse_expectation2(expectation:str)->(str,str):

        if expectation.startswith(Mode.ACTIVITY_BLOCK_RERUN):
            mode = key.ACTIVITY_BLOCK_RERUN
        elif expectation.startswith(Mode.ACTIVITY_IN_BLOCK):
            mode = key.ACTIVITY_IN_BLOCK
        elif expectation.startswith(Mode.ACTIVITY_BLOCK):
            mode = key.ACTIVITY_BLOCK
        elif expectation.startswith(Mode.ACTIVITY):
            mode = key.ACTIVITY
        else:
            raise ValueError(f"The file name for the expected result should begin with Autor mode name (ex: ACTIVITY_BLOCK_RERUN_calculateMax_SUCCESS_activity4.json). Received: {expectation}")

        activity_block_id = expectation.split('___')[1]

        return mode, activity_block_id


    @staticmethod
    def run(
            additional_context: dict = None,
            additional_extensions: List[str] = None,
            #additional_config: dict = {},
            activity_block_id: str = None,
            activity_config: dict = None,
            activity_id: str = None,
            activity_input: dict = None,
            activity_module: str = None,
            activity_name: str = None,
            activity_type: str = None,
            custom_data: dict = None,
            expectation: str = None,
            err_msg: str = None,
            flow_run_id: str = None,
            flow_config_url: str = "test_flow_configs/test-config.yml",
            mode: str = None, # mandatory if 'expectation' is not provided,
            status: str = None, # mandatory if 'expectation' is not provided
    )->ActivityBlock:


        if additional_context is None: additional_context = {}
        if activity_config is None: activity_config = {}
        if activity_input is None: activity_input = {}
        if custom_data is None: custom_data = {}

        if expectation is not None:
            mode,_ = AutorTester._parse_expectation(expectation)
        else:
            Check.not_none(mode, "Test framework value error: 'mode' must be provided if 'expectation' is not provided.")

        AutorTester._create_commands(
            additional_context=additional_context,
            #additional_config=additional_config,
            additional_extensions=additional_extensions,
            activity_block_id=activity_block_id,
            activity_config=activity_config,
            activity_id=activity_id,
            activity_input=activity_input,
            activity_module=activity_module,
            activity_name=activity_name,
            activity_type=activity_type,
            custom_data=custom_data,
            flow_run_id=flow_run_id,
            flow_config_url=flow_config_url,
            mode=mode
        )


        activity_block = ActivityBlock(
            mode = KeyConverter.LCD_to_UCU(mode),  # mandatory
            additional_context = additional_context,
            #additional_config = additional_config,
            additional_extensions = additional_extensions,
            activity_block_id = activity_block_id,
            activity_config = activity_config,
            activity_id = activity_id,
            activity_input = activity_input,
            activity_module = activity_module,
            activity_name = activity_name,
            activity_type = activity_type,
            custom_data = custom_data,
            flow_run_id = flow_run_id,
            flow_config_url = flow_config_url
        )

        # --------------- RUN AUTOR --------------#
        activity_block.run()
        # --------------- RUN AUTOR --------------#

        if expectation is not None:
            AutorTester._validate_context(expectation)
        else:
            AutorTester._validate(activity_block, expected_status=status, expected_err_msg=err_msg)


        return activity_block

    @staticmethod
    def run2(
            additional_context: dict = None,
            additional_extensions: List[str] = None,
            activity_block_id: str = None,
            activity_config: dict = None,
            activity_id: str = None,
            activity_input: dict = None,
            activity_module: str = None,
            activity_name: str = None,
            activity_type: str = None,
            custom_data: dict = None,
            expectation: str = None,
            err_msg: str = None,
            flow_run_id: str = None,
            flow_config_url: str = "test_flow_configs/test-config.yml",
            mode: str = None, # mandatory if 'expectation' is not provided,
            status: str = None, # mandatory if 'expectation' is not provided
    )->ActivityBlock:

        if additional_context is None: additional_context = {}
        if activity_config is None: activity_config = {}
        if activity_input is None: activity_input = {}
        if custom_data is None: custom_data = {}

        #parent_directory = Path(__file__).parent
        #flow_config_url = str(parent_directory/flow_config_url)


        if expectation is not None:
            p_mode,p_activity_block_id = AutorTester._parse_expectation2(expectation)
            if p_activity_block_id == "generatedActivityBlock":
                p_activity_block_id = None

            if mode is None:
                mode = p_mode
            if activity_block_id is None:
                activity_block_id = p_activity_block_id
        else:
            Check.not_none(mode, "Test framework value error: 'mode' must be provided if 'expectation' is not provided.")

        AutorTester._create_commands(
            additional_context=additional_context,
            #additional_config=additional_config,
            additional_extensions=additional_extensions,
            activity_block_id=activity_block_id,
            activity_config=activity_config,
            activity_id=activity_id,
            activity_input=activity_input,
            activity_module=activity_module,
            activity_name=activity_name,
            activity_type=activity_type,
            custom_data=custom_data,
            flow_run_id=flow_run_id,
            flow_config_url=flow_config_url,
            mode=mode
        )


        activity_block = ActivityBlock(
            mode = KeyConverter.LCD_to_UCU(mode),  # mandatory
            additional_context = additional_context,
            #additional_config = additional_config,
            additional_extensions = additional_extensions,
            activity_block_id = activity_block_id,
            activity_config = activity_config,
            activity_id = activity_id,
            activity_input = activity_input,
            activity_module = activity_module,
            activity_name = activity_name,
            activity_type = activity_type,
            custom_data = custom_data,
            flow_run_id = flow_run_id,
            flow_config_url = flow_config_url
        )

        # --------------- RUN AUTOR --------------#
        activity_block.run()
        # --------------- RUN AUTOR --------------#

        if expectation is not None:
            AutorTester._validate_context(expectation)
        else:
            AutorTester._validate(activity_block, expected_status=status, expected_err_msg=err_msg)


        return activity_block

    @staticmethod
    def _validate(activity_block:ActivityBlock, expected_status:str, expected_err_msg:str=None):
        Check.not_none(expected_status, "'expected_status' is mandatory - was not provided")
        actual_status = activity_block.get_activity_block_status()
        Check.expected(expected_status, actual_status, "Activity block did not have expected status")
        if expected_err_msg is not None:
            ex:Exception = activity_block.get_exception()
            Check.not_none(ex, f"No exception provided by ActivityBlock. Expected exception with message: {expected_err_msg}")
            actual_err_msg = str(ex)
            Check.expected(expected_err_msg, actual_err_msg, "Exception error message was not as expected.")



    @staticmethod
    def _validate_context(file_name:str)->bool:

        if not '.json' in file_name:
            file_name = f"{file_name}.json"

        full_file_name = os.path.join('data', file_name)
        expected_ctx = Util.read_json(full_file_name)
        actual_ctx = Context.get_context_dict() # Context has a global dict

        expected_abs:dict = expected_ctx["_activityBlocks"]
        Check.is_true(len(expected_abs.keys()) == 1, "Expected context should contain only one activity block")

        expected_ab_id:str =list(expected_abs.keys())[0]
        expected_ab:dict = expected_abs[expected_ab_id]
        expected_activities:dict = expected_ab["_activities"]

        # Actual
        actual_abs:dict = actual_ctx["_activityBlocks"]
        Check.is_in(expected_ab_id, actual_abs, f"Expected activity block id: {expected_ab_id}. Did not find it.\n{Util.dict_to_str(actual_abs)}")
       # Check.is_true(expected_ab_id in actual_abs, f"Expected activity block id: {expected_ab_id}. Did not find it.")

        actual_ab:dict = actual_abs[expected_ab_id]
        actual_activities:dict = actual_ab["_activities"]

        # Check activity block data
        Check.is_equal(expected_ab['mode'],actual_ab['mode'], f"Expected mode:{expected_ab['mode']}, got: {actual_ab['mode']}")


        for expected_activity_id, expected_activity in expected_activities.items():
            Check.is_in(expected_activity_id, actual_activities, f"Expected to find activity with id: {expected_activity_id} in activity block: {expected_ab_id}.\n{Util.dict_to_str(actual_activities)}")
            actual_activity:str = actual_activities[expected_activity_id]

            for expected_key,expected_val in expected_activity.items():
                Check.is_in(expected_key, actual_activity, f"Expected to find key: {expected_key} in activity: {expected_activity_id}.\n{Util.dict_to_str(actual_activity)}")
                actual_val = actual_activity[expected_key]
                err_msg = (
                    f"Expected {expected_key}={expected_val}, got {expected_key}={actual_val}." +
                    f"\nActivity id: {expected_activity_id}" +
                    f"\n\nExpected activity context: " +
                    f"\n{Util.dict_to_str(expected_activity)}" +
                    f"\nReceived activity context: " +
                    f"\n{Util.dict_to_str(actual_activity)}"

                )
                Check.is_equal(expected_val,actual_val,msg=err_msg)

        return True

    @staticmethod
    def _create_commands(
            additional_context: dict = None,
            #additional_config: dict = None,
            additional_extensions: list = None,
            activity_block_id: str = None,
            activity_config: dict = None,
            activity_id: str = None,
            activity_input: dict = None,
            activity_module: str = None,
            activity_name: str = None,
            activity_type: str = None,
            custom_data: dict = None,
            flow_run_id: str = None,
            flow_config_url: str = None,
            mode: str = None
    ):
        if additional_context is None: additional_context = {}
        if activity_config is None: activity_config = {}
        if activity_input is None: activity_input = {}
        if custom_data is None: custom_data = {}


        # Create a commandline command for debugging purposes
        command = "python -m autor "
        command = AutorTester._add_to_command(mode, "mode", command)
        command = AutorTester._add_dict_to_command(additional_context, "additional-context", command)
        command = AutorTester._add_list_to_command(additional_extensions, "additional-extensions", command)
        command = AutorTester._add_to_command(activity_block_id, "activity-block-id", command)
        command = AutorTester._add_dict_to_command(activity_config, "activity-config", command)
        command = AutorTester._add_to_command(activity_id, "activity-id", command)
        command = AutorTester._add_dict_to_command(activity_input, "activity-input", command)
        command = AutorTester._add_to_command(activity_module, "activity-module", command)
        command = AutorTester._add_to_command(activity_name, "activity-name", command)
        command = AutorTester._add_to_command(activity_type, "activity-type", command)
        command = AutorTester._add_dict_to_command(custom_data, "custom-data", command)
        command = AutorTester._add_to_command(flow_run_id, "flow-run-id", command)
        command = AutorTester._add_to_command(flow_config_url, "flow-config-url", command)

        AutorTester.__commands.append(command)


        print("---------------- all commands ------------------")
        print("Must be run from directory autor/tests")
        for c in AutorTester.__commands:
            print(c)

    @staticmethod
    def _dict_to_json_string(d:dict)->str:
        json_str: str = json.dumps(d)
        json_str = json_str.replace('"', '\\"')
        json_str = json_str.replace("'", "\\'")
        json_str = f'"{json_str}"'
        return json_str

    def _list_to_string(l:List[str]) -> str:
        list_str:str = ""
        first_elem = True
        for elem in l:
            if first_elem:
                list_str = elem
            else:
                list_str = f'{list_str},{elem}'

        list_str = list_str.replace('"', '\\"')
        list_str = list_str.replace("'", "\\'")
        list_str = f'"{list_str}"'
        return list_str

    @staticmethod
    def _add_dict_to_command(d:dict, command_name:str, command:str):
        if len(d.items()) > 0:
            command = f'{command} --{command_name} {AutorTester._dict_to_json_string(d)}'
        return command

    @staticmethod
    def _add_list_to_command(l:list, command_name:str, command:str):
        if l is not None and len(l) > 0:
            command = f'{command} --{command_name} {AutorTester._list_to_string(l)}'
        return command

    @staticmethod
    def _add_to_command(val, command_name:str, command:str):
        if val is not None:
            command = f'{command} --{command_name} {val}'
        return command