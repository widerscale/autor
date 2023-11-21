import os.path

from autor import __version__
from autor_tester import AutorTester as test


def test_version():
    assert __version__ == "0.1.0"



def test_ACTIVITY_BLOCK():
    flow_run_id = test.run(activity_block_id='calculateMax', expectation='ACTIVITY_BLOCK_calculateMax_SUCCESS')
    flow_run_id = test.run(activity_block_id='calculateMax2', expectation='ACTIVITY_BLOCK_calculateMax2_SUCCESS_secondAB', flow_run_id=flow_run_id)

def test_ACTIVITY_BLOCK_RERUN():
    flow_run_id = test.run(activity_block_id='calculateMax', expectation='ACTIVITY_BLOCK_calculateMax_SUCCESS')
    flow_run_id = test.run(activity_block_id='calculateMax', activity_id="calculateMax-activity2", flow_run_id=flow_run_id, expectation='ACTIVITY_BLOCK_RERUN_calculateMax_SUCCESS_activity2')
    flow_run_id = test.run(activity_block_id='calculateMax', activity_id="calculateMax-activity4", flow_run_id=flow_run_id, expectation='ACTIVITY_BLOCK_RERUN_calculateMax_SUCCESS_activity4')
    flow_run_id = test.run(activity_block_id='calculateMax', activity_id="calculateMax-activity1", flow_run_id=flow_run_id, expectation='ACTIVITY_BLOCK_RERUN_calculateMax_SUCCESS_activity1_missingContext')
    flow_run_id = test.run(activity_block_id='calculateMax', activity_id="calculateMax-activity1", flow_run_id=flow_run_id, expectation='ACTIVITY_BLOCK_RERUN_calculateMax_SUCCESS_activity1_withContext', additional_context={'max':None})

    flow_run_id = test.run(activity_block_id='calculateMax', expectation='ACTIVITY_BLOCK_calculateMax_SUCCESS')
    flow_run_id = test.run(activity_block_id='calculateMax', activity_id="calculateMax-activity2", flow_run_id=flow_run_id, expectation='ACTIVITY_BLOCK_RERUN_calculateMax_SUCCESS_activity2')
    flow_run_id = test.run(activity_block_id='calculateMax', activity_id="calculateMax-activity4", flow_run_id=flow_run_id, expectation='ACTIVITY_BLOCK_RERUN_calculateMax_SUCCESS_activity4')
    flow_run_id = test.run(activity_block_id='calculateMax', activity_id="calculateMax-activity1", flow_run_id=flow_run_id, expectation='ACTIVITY_BLOCK_RERUN_calculateMax_SUCCESS_activity1_missingContext')
    flow_run_id = test.run(activity_block_id='calculateMax', activity_id="calculateMax-activity1", flow_run_id=flow_run_id, expectation='ACTIVITY_BLOCK_RERUN_calculateMax_SUCCESS_activity1_withContext', additional_context={'max':None})

    flow_run_id = test.run(activity_block_id='calculateMax', expectation='ACTIVITY_BLOCK_calculateMax_SUCCESS')






def test_ACTIVITY_BLOCK_RERUN_from_failure():
    flow_run_id = test.run(activity_block_id='calculateMaxWithExceptionEverySecondRun1', expectation='ACTIVITY_BLOCK_calculateMaxWithExceptionEverySecondRun1_SUCCESS_firstRun')
    flow_run_id = test.run(activity_block_id='calculateMaxWithExceptionEverySecondRun2', flow_run_id=flow_run_id, expectation='ACTIVITY_BLOCK_calculateMaxWithExceptionEverySecondRun2_ERROR_secondRun')

    # Success, if run from the first activity, as we need the counter from that activity to succeed.
    flow_run_id = test.run(activity_block_id='calculateMaxWithExceptionEverySecondRun2', activity_id="calculateMaxWithExceptionEverySecondRun2-activity1", flow_run_id=flow_run_id, expectation='ACTIVITY_BLOCK_RERUN_calculateMaxWithExceptionEverySecondRun2_SUCCESS_thirdRun')

    # This run will succeed, as the runNbr counter will not be updated by the first activity (as we use re-run on it).
    flow_run_id = test.run(activity_block_id='calculateMaxWithExceptionEverySecondRun2', activity_id="calculateMaxWithExceptionEverySecondRun2-exceptionEverySecondRun", flow_run_id=flow_run_id, expectation='ACTIVITY_BLOCK_RERUN_calculateMaxWithExceptionEverySecondRun2_SUCCESS_fourthRun')


def test_unknown_activity_type():
    flow_run_id = test.run(activity_block_id='unknownActivityType', expectation='ACTIVITY_BLOCK_unknownActivityType_ABORTED')

def test_bootsrap_configuration():
    extensions:list =['tests.test_extensions.ConfigBootstrapExtension.ConfigBootstrapExtension']
    custom_data:dict = {}
    data:dict = {}
    data["flowConfigUrl"] = "test-config.yml"
    data["activityBlockId"] = "calculateMax"
    custom_data["ConfigBootstrapExtension"] = data
    flow_run_id = test.run(additional_extensions=extensions, custom_data=custom_data, expectation='ACTIVITY_BLOCK_calculateMax_SUCCESS_bootsrapConfig')

def test_bootsrap_configuration_commandline_prio():
    # The extension should not override activity block id, when it's provided.
    extensions:list =['tests.test_extensions.ConfigBootstrapExtension.ConfigBootstrapExtension']
    custom_data:dict = {}
    data:dict = {}
    data["flowConfigUrl"] = "test-config.yml"
    data["activityBlockId"] = "calculateMax" # This should not be used by the extension (<- testing this)
    custom_data["ConfigBootstrapExtension"] = data
    flow_run_id = test.run(activity_block_id='calculateMax2',additional_extensions=extensions, custom_data=custom_data, expectation='ACTIVITY_BLOCK_calculateMax2_SUCCESS_bootstrapConfigActivityIdProvided')

def test_ACTIVITY_config_and_input():
    module = "test_activities.activities"
    type = "MAX"
    config = {"val":4}
    flow_run_id = test.run(activity_block_id='calculateMax', activity_module=module, activity_type=type, activity_config=config, expectation='ACTIVITY_generatedActivityBlock_SUCCESS_activity1.json')

    input = {"max":11}
    flow_run_id = test.run(activity_block_id='calculateMax', activity_input=input, activity_module=module, activity_type=type,activity_config=config, expectation='ACTIVITY_generatedActivityBlock_SUCCESS_activity1WithInput.json')


def test_ACTIVITY_IN_BLOCK_all_one_by_one():
    flow_run_id = test.run(activity_block_id='calculateMaxWithNames', activity_name='first', expectation='ACTIVITY_IN_BLOCK_calculateMaxWithNames_SUCCESS_uc3_first.json')
    flow_run_id = test.run(activity_block_id='calculateMaxWithNames', activity_name='second', expectation='ACTIVITY_IN_BLOCK_calculateMaxWithNames_SUCCESS_uc3_second.json', flow_run_id=flow_run_id)
    flow_run_id = test.run(activity_block_id='calculateMaxWithNames', activity_name='third', expectation='ACTIVITY_IN_BLOCK_calculateMaxWithNames_SUCCESS_uc3_third.json', flow_run_id=flow_run_id)
    flow_run_id = test.run(activity_block_id='calculateMaxWithNames', activity_name='fourth', expectation='ACTIVITY_IN_BLOCK_calculateMaxWithNames_SUCCESS_uc3_fourth.json', flow_run_id=flow_run_id)



def test_ACTIVITY_IN_BLOCK_running_activities_backwards():
    flow_run_id = test.run(activity_block_id='calculateMaxWithNames', activity_name='fourth', expectation='ACTIVITY_IN_BLOCK_calculateMaxWithNames_SUCCESS_uc5_fourth.json')
    flow_run_id = test.run(activity_block_id='calculateMaxWithNames', activity_name='third', expectation='ACTIVITY_IN_BLOCK_calculateMaxWithNames_SUCCESS_uc5_third.json', flow_run_id=flow_run_id)
    flow_run_id = test.run(activity_block_id='calculateMaxWithNames', activity_name='second', expectation='ACTIVITY_IN_BLOCK_calculateMaxWithNames_SUCCESS_uc5_second.json', flow_run_id=flow_run_id)
    flow_run_id = test.run(activity_block_id='calculateMaxWithNames', activity_name='first', expectation='ACTIVITY_IN_BLOCK_calculateMaxWithNames_SUCCESS_uc5_first.json', flow_run_id=flow_run_id)


def test_ACTIVITY_IN_BLOCK_skipping_some_activities_with_extra_context_inputs():
    # Run activities 2 and 4 in a row filling the gaps with context inputs.
    flow_run_id = test.run(activity_block_id='calculateMaxWithNames', activity_name='second', additional_context={'max':3}, expectation='ACTIVITY_IN_BLOCK_calculateMaxWithNames_SUCCESS_uc4_second.json')
    flow_run_id = test.run(activity_block_id='calculateMaxWithNames', activity_name='fourth', additional_context={'max':5}, expectation='ACTIVITY_IN_BLOCK_calculateMaxWithNames_SUCCESS_uc4_fourth.json', flow_run_id=flow_run_id)


def test_ACTIVITY_IN_BLOCK_skipping_some_activities_without_extra_context_inputs():
    # Run activities 2 and 4 in a row without filling the gaps with extra context inputs.
    flow_run_id = test.run(activity_block_id='calculateMaxWithNames', activity_name='second', expectation='ACTIVITY_IN_BLOCK_calculateMaxWithNames_SUCCESS_uc2_second.json')
    flow_run_id = test.run(activity_block_id='calculateMaxWithNames', activity_name='fourth', expectation='ACTIVITY_IN_BLOCK_calculateMaxWithNames_SUCCESS_uc2_fourth.json', flow_run_id=flow_run_id)


    # Normal mode
    #flow_run_id = test.run(activity_block_id='calculateMaxWithNames', expectation='ACTIVITY_BLOCK_calculateMaxWithNames_SUCCESS.json')
    #flow_run_id = test.run(activity_block_id='calculateMaxWithNames', activity_name='first', expectation='ACTIVITY_IN_BLOCK_calculateMaxWithNames_SUCCESS_firstSeq.json')
    #flow_run_id = test.run(activity_block_id='calculateMaxWithNames', activity_name='second', expectation='ACTIVITY_IN_BLOCK_calculateMaxWithNames_SUCCESS_secondSeq.json', flow_run_id=flow_run_id)
    #flow_run_id = test.run(activity_block_id='calculateMaxWithNames', activity_name='third', expectation='ACTIVITY_IN_BLOCK_calculateMaxWithNames_SUCCESS_thirdSeq.json', flow_run_id=flow_run_id)
    #flow_run_id = test.run(activity_block_id='calculateMaxWithNames', activity_name='fourth', expectation='ACTIVITY_IN_BLOCK_calculateMaxWithNames_SUCCESS_fourthSeq.json', flow_run_id=flow_run_id)


def test_ACTIVITY_IN_BLOCK_once_per_flow():
    # Run each activity separately in a new flow run.
    flow_run_id = test.run(activity_block_id='calculateMaxWithNames', activity_name='first', expectation='ACTIVITY_IN_BLOCK_calculateMaxWithNames_SUCCESS_uc1_first.json')
    flow_run_id = test.run(activity_block_id='calculateMaxWithNames', activity_name='second', expectation='ACTIVITY_IN_BLOCK_calculateMaxWithNames_SUCCESS_uc1_second.json')
    flow_run_id = test.run(activity_block_id='calculateMaxWithNames', activity_name='third', expectation='ACTIVITY_IN_BLOCK_calculateMaxWithNames_SUCCESS_uc1_third.json')
    flow_run_id = test.run(activity_block_id='calculateMaxWithNames', activity_name='fourth', expectation='ACTIVITY_IN_BLOCK_calculateMaxWithNames_SUCCESS_uc1_fourth.json')

def test_ACTIVITY_IN_BLOCK_one_activity_fails():
    flow_run_id = test.run(activity_block_id='calculateMaxFailSecond', activity_name='first', expectation='ACTIVITY_IN_BLOCK_calculateMaxFailSecond_SUCCESS_uc6_first.json')
    flow_run_id = test.run(activity_block_id='calculateMaxFailSecond', activity_name='second', expectation='ACTIVITY_IN_BLOCK_calculateMaxFailSecond_ERROR_uc6_second.json', flow_run_id=flow_run_id)
    flow_run_id = test.run(activity_block_id='calculateMaxFailSecond', activity_name='third', expectation='ACTIVITY_IN_BLOCK_calculateMaxFailSecond_ERROR_uc6_third.json', flow_run_id=flow_run_id)
    flow_run_id = test.run(activity_block_id='calculateMaxFailSecond', activity_name='fourth', expectation='ACTIVITY_IN_BLOCK_calculateMaxFailSecond_ERROR_uc6_fourth.json', flow_run_id=flow_run_id)


def test_ACTIVITY_IN_BLOCK_one_activity_fails():
    flow_run_id = test.run(activity_block_id='calculateMaxFailSecond', activity_name='third', expectation='ACTIVITY_IN_BLOCK_calculateMaxFailSecond_SUCCESS_uc7_third.json')
    flow_run_id = test.run(activity_block_id='calculateMaxFailSecond', activity_name='second', expectation='ACTIVITY_IN_BLOCK_calculateMaxFailSecond_ERROR_uc7_second.json', flow_run_id=flow_run_id)
    flow_run_id = test.run(activity_block_id='calculateMaxFailSecond', activity_name='first', expectation='ACTIVITY_IN_BLOCK_calculateMaxFailSecond_ERROR_uc7_first.json', flow_run_id=flow_run_id)
    flow_run_id = test.run(activity_block_id='calculateMaxFailSecond', activity_name='fourth', expectation='ACTIVITY_IN_BLOCK_calculateMaxFailSecond_ERROR_uc7_fourth.json', flow_run_id=flow_run_id)
    flow_run_id = test.run(activity_block_id='calculateMaxFailSecond', activity_name='third', expectation='ACTIVITY_IN_BLOCK_calculateMaxFailSecond_ERROR_uc7_third2.json', flow_run_id=flow_run_id)
