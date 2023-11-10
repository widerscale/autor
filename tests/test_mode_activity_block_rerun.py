import logging
import json
from typing import List

from autor.framework.activity_block import ActivityBlock
from autor.framework.check import Check


__commands:List[str] = []

def _run_autor_____(
        additional_context: dict = {},
        additional_extensions: list = None,
        activity_block_id: str = None,
        activity_config: dict = {},
        activity_id: str = None,
        activity_input: dict = {},
        activity_module: str = None,
        activity_name: str = None,
        activity_type: str = None,
        custom_data: dict = {},
        flow_run_id: str = None,
        flow_config_url: str = None) -> ActivityBlock:
    activity_block = ActivityBlock(
        additional_context=additional_context,
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
        flow_config_url=flow_config_url
    )

def _dict_to_json_string(d:dict)->str:
    json_str: str = json.dumps(d)
    logging.error(json_str)
    json_str = json_str.replace('"', '\\"')
    json_str = json_str.replace("'", "\\'")
    json_str = f'"{json_str}"'
    logging.error(json_str)
    return json_str

def _list_to_string(l:List[str]) -> str:
    list_str = ""
    first_elem = True
    for elem in l:
        if first_elem:
            list_str = l
        else:
            list_str = f'{list_str},{l}'

    list_str = list_str.replace('"', '\\"')
    list_str = list_str.replace("'", "\\'")
    list_str = f'"{list_str}"'
    return list_str


def _add_dict_to_command(d:dict, command_name:str, command:str):
    if len(d.items()) > 0:
        command = f'{command} --{command_name} {_dict_to_json_string(d)}'
    return command

def _add_list_to_command(l:list, command_name:str, command:str):
    if l is not None and len(l) > 0:
        command = f'{command} --{command_name} {_list_to_string(l)}'
    return command

def _add_to_command(val, command_name:str, command:str):
    if val is not None:
        command = f'{command} --{command_name} {val}'
    return command


def _run_autor(
        nbr_activities,
        additional_context: dict = {},
        additional_extensions: list = None,
        activity_block_id: str = None,
        activity_config: dict = {},
        activity_id: str = None,
        activity_input: dict = {},
        activity_module: str = None,
        activity_name: str = None,
        activity_type: str = None,
        custom_data: dict = {},
        flow_run_id: str = None,
        flow_config_url: str = None,
        expected_ab_status: str = "SUCCESS",
        activity_ids:List[str] = None,
        expected_activity_statuses:List[str] = None,
        expected_activity_actions:List[str] = None,
        expected_activity_values:List[dict] = None

)->str:


    # Create a commandline command for debugging purposes
    command = "python -m autor "
    command = _add_dict_to_command(additional_context, "additional-context", command)
    command = _add_list_to_command(additional_extensions,"additional-extensions", command)
    command = _add_to_command(activity_block_id, "activity-block-id", command)
    command = _add_dict_to_command(activity_config, "activity-config", command)
    command = _add_to_command(activity_id, "activity-id", command)
    command = _add_dict_to_command(additional_context, "additional-context", command)
    command = _add_dict_to_command(activity_input, "activity-input", command)
    command = _add_to_command(activity_module, "activity-module", command)
    command = _add_to_command(activity_name, "activity-name", command)
    command = _add_to_command(activity_type, "activity-type", command)
    command = _add_dict_to_command(custom_data, "custom-data", command)
    command = _add_to_command(flow_run_id, "flow-run-id", command)
    command = _add_to_command(flow_config_url, "flow-config-url", command)

    __commands.append(command)

    for c in __commands:
        logging.info(c)











    activity_block = ActivityBlock(
        additional_context = additional_context,
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

    if activity_ids is None:
        activity_ids = _create_default_activity_ids(activity_block_id,nbr_activities)
    if expected_activity_statuses is None:
        expected_activity_statuses = _create_default_activity_statuses(nbr_activities)
    if expected_activity_values is None:
        expected_activity_values = _create_default_activity_values(nbr_activities)
    if expected_activity_actions is None:
        expected_activity_actions = _create_default_activity_actions(nbr_activities)

    logging.info(f'nbr activities: {nbr_activities}')
    logging.info(f'nbr activities: {nbr_activities}')
    Check.is_equal(len(activity_ids), nbr_activities, "Internal error: nbr activity ids does not match nbr activities")
    Check.is_equal(len(expected_activity_statuses), nbr_activities, "Internal error: nbr activity statuses does not match nbr activities")
    Check.is_equal(len(expected_activity_values), nbr_activities, "Internal error: nbr activity values does not match nbr activities")
    Check.is_equal(len(expected_activity_actions), nbr_activities, "Internal error: nbr activity actions does not match nbr activities")


    # --------------- RUN AUTOR --------------#
    activity_block.run()
    # --------------- RUN AUTOR --------------#

    message_base = (
                f"\nflow_config_url:     {flow_config_url}" +
                f"\nactivity_block_id:   {activity_block_id}" +
                f"\nrerun from activity: {activity_id}")

    for i in range(nbr_activities):
        logging.info(f'i:{i}')
        ctx = activity_block.get_activity_context(activity_ids[i])
        activity_ctx_dict:dict = ctx.get_focus_activity_dict()

        message = (
                f"{message_base}" +
                f"\nactivity_id:         {activity_ids[i]}" +
                f"\nactivity_context:    {activity_ctx_dict}")

        Check.expected(expected_activity_statuses[i], ctx.get("status"), f"Unexpected activity status.{message}")
        Check.expected(expected_activity_actions[i], ctx.get("action"), f"Unexpected activity action.{message}")


        expected_vals:dict = expected_activity_values[i]
        if expected_vals is not None:
            for key,val in expected_vals.items():
                Check.expected(val, ctx.get(key), f"Unexpected activity value for key: '{key}'.{message}")


    actual_ab_status = activity_block.get_activity_block_status()
    Check.expected(expected_ab_status, actual_ab_status, message_base)

    return activity_block.get_flow_run_id()











def _run_activity_block(expected_vals:List[int],
                        value_name:str,
                        expected_ab_status:str = "SUCCESS",
                        flow_run_id=None,
                        rerun_from_activity_nbr=None,
                        add_context:dict={})->str:

    activity_block_id:str = "modeActivityBlockRerun"
    flow_config_url:str = "test-config.yml"
    nbr_activities = len(expected_vals)

    # Prepare activity values data
    expected_activity_values:List[dict] = []
    for val in expected_vals:
        val_dict = {value_name:val}
        expected_activity_values.append(val_dict)

    # Prepare activity actions data
    expected_activity_actions: List[str] = None
    if rerun_from_activity_nbr is not None:

        expected_activity_actions = []
        for i in range(nbr_activities):
            if i < rerun_from_activity_nbr-1:
                expected_activity_actions.append("REUSE")
            else:
                expected_activity_actions.append("RUN")


    # If we want to perform a rerun, create the id for the activity to rerun
    rerun_activity_id = None
    if rerun_from_activity_nbr:
        rerun_activity_id = f'{activity_block_id}-activity{rerun_from_activity_nbr}'

    logging.error(f'rerun_activity_id: {rerun_activity_id}')

    flow_run_id = _run_autor(
        nbr_activities=nbr_activities,
        flow_config_url=flow_config_url,
        activity_block_id=activity_block_id,
        flow_run_id=flow_run_id,
        activity_id=rerun_activity_id,
        expected_activity_values=expected_activity_values,
        expected_activity_actions=expected_activity_actions,
        additional_context=add_context)

    return flow_run_id

def _create_default_activity_values(nbr_activities:int)->List[dict]:
    values = []
    for _ in range(nbr_activities):
        values.append({})
    return values # Return empty values

def _create_default_activity_statuses(nbr_activities:int)->List[str]:
    results:List[str] = []
    for _ in range(nbr_activities):
        results.append("SUCCESS")
    return results

def _create_default_activity_actions(nbr_activities:int)->List[str]:
    results:List[str] = []
    for _ in range(nbr_activities):
        results.append("RUN")
    return results

def _create_default_activity_ids(activity_block_id:str, nbr_activities:int)->List[str]:
    results:List[str] = []
    for i in range(nbr_activities):
        results.append(f'{activity_block_id}-activity{i+1}') # first activity number is 1
    return results

def test_mode_activity_block_rerun():
    flow_run_id = _run_activity_block(expected_vals=[1, 7, 7, 9], value_name='max')
    flow_run_id = _run_activity_block(expected_vals=[1, 7, 7, 9], value_name='max', rerun_from_activity_nbr=2, flow_run_id=flow_run_id)
    flow_run_id = _run_activity_block(expected_vals=[1, 7, 7, 9], value_name='max', rerun_from_activity_nbr=3, flow_run_id=flow_run_id)
    flow_run_id = _run_activity_block(expected_vals=[1, 7, 7, 9], value_name='max', rerun_from_activity_nbr=2, flow_run_id=flow_run_id)
    flow_run_id = _run_activity_block(expected_vals=[1, 7, 7, 9], value_name='max', rerun_from_activity_nbr=4, flow_run_id=flow_run_id)
    flow_run_id = _run_activity_block(expected_vals=[9, 9, 9, 9], value_name='max', rerun_from_activity_nbr=1, flow_run_id=flow_run_id)
    flow_run_id = _run_activity_block(expected_vals=[1, 7, 7, 9], value_name='max', rerun_from_activity_nbr=1, flow_run_id=flow_run_id, add_context={'max':None})
    flow_run_id = _run_activity_block(expected_vals=[1, 7, 7, 9], value_name='max', rerun_from_activity_nbr=1, flow_run_id=flow_run_id, add_context={'max':None})
    flow_run_id = _run_activity_block(expected_vals=[1, 7, 7, 9], value_name='max', rerun_from_activity_nbr=2, flow_run_id=flow_run_id)
    flow_run_id = _run_activity_block(expected_vals=[1, 7, 7, 9], value_name='max')

def test_mode_activity():
    pass

def test_rerun_from_first_activity_that_optionally_reads_context():
    pass