import logging
import os.path

from autor import __version__
from autor_tester import AutorTester as test


def test_version():
    assert __version__ == "0.1.0"



def test_ACTIVITY_BLOCK():
    ab = test.run(activity_block_id='calculateMax', expectation='ACTIVITY_BLOCK_calculateMax_SUCCESS')
    ab = test.run(activity_block_id='calculateMax2', expectation='ACTIVITY_BLOCK_calculateMax2_SUCCESS_secondAB', flow_run_id = ab.get_flow_run_id())

def test_ACTIVITY_BLOCK_RERUN():
    ab = test.run(activity_block_id='calculateMax', expectation='ACTIVITY_BLOCK_calculateMax_SUCCESS')
    ab = test.run(activity_block_id='calculateMax', activity_id="calculateMax-activity2", flow_run_id = ab.get_flow_run_id(), expectation='ACTIVITY_BLOCK_RERUN_calculateMax_SUCCESS_activity2')
    ab = test.run(activity_block_id='calculateMax', activity_id="calculateMax-activity4", flow_run_id = ab.get_flow_run_id(), expectation='ACTIVITY_BLOCK_RERUN_calculateMax_SUCCESS_activity4')
    ab = test.run(activity_block_id='calculateMax', activity_id="calculateMax-activity1", flow_run_id = ab.get_flow_run_id(), expectation='ACTIVITY_BLOCK_RERUN_calculateMax_SUCCESS_activity1_missingContext')
    ab = test.run(activity_block_id='calculateMax', activity_id="calculateMax-activity1", flow_run_id = ab.get_flow_run_id(), expectation='ACTIVITY_BLOCK_RERUN_calculateMax_SUCCESS_activity1_withContext', additional_context={'max':None})

    ab = test.run(activity_block_id='calculateMax', expectation='ACTIVITY_BLOCK_calculateMax_SUCCESS')
    ab = test.run(activity_block_id='calculateMax', activity_id="calculateMax-activity2", flow_run_id = ab.get_flow_run_id(), expectation='ACTIVITY_BLOCK_RERUN_calculateMax_SUCCESS_activity2')
    ab = test.run(activity_block_id='calculateMax', activity_id="calculateMax-activity4", flow_run_id = ab.get_flow_run_id(), expectation='ACTIVITY_BLOCK_RERUN_calculateMax_SUCCESS_activity4')
    ab = test.run(activity_block_id='calculateMax', activity_id="calculateMax-activity1", flow_run_id = ab.get_flow_run_id(), expectation='ACTIVITY_BLOCK_RERUN_calculateMax_SUCCESS_activity1_missingContext')
    ab = test.run(activity_block_id='calculateMax', activity_id="calculateMax-activity1", flow_run_id = ab.get_flow_run_id(), expectation='ACTIVITY_BLOCK_RERUN_calculateMax_SUCCESS_activity1_withContext', additional_context={'max':None})

    ab = test.run(activity_block_id='calculateMax', expectation='ACTIVITY_BLOCK_calculateMax_SUCCESS')


def test_ACTIVITY_BLOCK_RERUN_from_failure():
    ab = test.run(activity_block_id='calculateMaxWithExceptionEverySecondRun1', expectation='ACTIVITY_BLOCK_calculateMaxWithExceptionEverySecondRun1_SUCCESS_firstRun')
    ab = test.run(activity_block_id='calculateMaxWithExceptionEverySecondRun2', flow_run_id = ab.get_flow_run_id(), expectation='ACTIVITY_BLOCK_calculateMaxWithExceptionEverySecondRun2_ERROR_secondRun')

    # Success, if run from the first activity, as we need the counter from that activity to succeed.
    ab = test.run(activity_block_id='calculateMaxWithExceptionEverySecondRun2', activity_id="calculateMaxWithExceptionEverySecondRun2-activity1", flow_run_id = ab.get_flow_run_id(), expectation='ACTIVITY_BLOCK_RERUN_calculateMaxWithExceptionEverySecondRun2_SUCCESS_thirdRun')

    # This run will succeed, as the runNbr counter will not be updated by the first activity (as we use re-run on it).
    ab = test.run(activity_block_id='calculateMaxWithExceptionEverySecondRun2', activity_id="calculateMaxWithExceptionEverySecondRun2-exceptionEverySecondRun", flow_run_id = ab.get_flow_run_id(), expectation='ACTIVITY_BLOCK_RERUN_calculateMaxWithExceptionEverySecondRun2_SUCCESS_fourthRun')


def test_unknown_activity_type():
    ab = test.run(activity_block_id='unknownActivityType', expectation='ACTIVITY_BLOCK_unknownActivityType_ABORTED')

def test_bootsrap_configuration():
    extensions:list =['tests.test_extensions.ConfigBootstrapExtension.ConfigBootstrapExtension']
    custom_data:dict = {}
    data:dict = {}
    data["flowConfigUrl"] = "test-config.yml"
    data["activityBlockId"] = "calculateMax"
    custom_data["ConfigBootstrapExtension"] = data
    ab = test.run(additional_extensions=extensions, custom_data=custom_data, expectation='ACTIVITY_BLOCK_calculateMax_SUCCESS_bootsrapConfig')

def test_bootsrap_configuration_commandline_prio():
    # The extension should not override activity block id, when it's provided.
    extensions:list =['tests.test_extensions.ConfigBootstrapExtension.ConfigBootstrapExtension']
    custom_data:dict = {}
    data:dict = {}
    data["flowConfigUrl"] = "test-config.yml"
    data["activityBlockId"] = "calculateMax" # This should not be used by the extension (<- testing this)
    custom_data["ConfigBootstrapExtension"] = data
    ab = test.run(activity_block_id='calculateMax2',additional_extensions=extensions, custom_data=custom_data, expectation='ACTIVITY_BLOCK_calculateMax2_SUCCESS_bootstrapConfigActivityIdProvided')



def test_ACTIVITY_IN_BLOCK_all_one_by_one():
    ab = test.run(activity_block_id='calculateMaxWithNames', activity_name='first', expectation='ACTIVITY_IN_BLOCK_calculateMaxWithNames_SUCCESS_uc3_first.json')
    ab = test.run(activity_block_id='calculateMaxWithNames', activity_name='second', expectation='ACTIVITY_IN_BLOCK_calculateMaxWithNames_SUCCESS_uc3_second.json', flow_run_id = ab.get_flow_run_id())
    ab = test.run(activity_block_id='calculateMaxWithNames', activity_name='third', expectation='ACTIVITY_IN_BLOCK_calculateMaxWithNames_SUCCESS_uc3_third.json', flow_run_id = ab.get_flow_run_id())
    ab = test.run(activity_block_id='calculateMaxWithNames', activity_name='fourth', expectation='ACTIVITY_IN_BLOCK_calculateMaxWithNames_SUCCESS_uc3_fourth.json', flow_run_id = ab.get_flow_run_id())



def test_ACTIVITY_IN_BLOCK_running_activities_backwards():
    ab = test.run(activity_block_id='calculateMaxWithNames', activity_name='fourth', expectation='ACTIVITY_IN_BLOCK_calculateMaxWithNames_SUCCESS_uc5_fourth.json')
    ab = test.run(activity_block_id='calculateMaxWithNames', activity_name='third', expectation='ACTIVITY_IN_BLOCK_calculateMaxWithNames_SUCCESS_uc5_third.json', flow_run_id = ab.get_flow_run_id())
    ab = test.run(activity_block_id='calculateMaxWithNames', activity_name='second', expectation='ACTIVITY_IN_BLOCK_calculateMaxWithNames_SUCCESS_uc5_second.json', flow_run_id = ab.get_flow_run_id())
    ab = test.run(activity_block_id='calculateMaxWithNames', activity_name='first', expectation='ACTIVITY_IN_BLOCK_calculateMaxWithNames_SUCCESS_uc5_first.json', flow_run_id = ab.get_flow_run_id())


def test_ACTIVITY_IN_BLOCK_skipping_some_activities_with_extra_context_inputs():
    # Run activities 2 and 4 in a row filling the gaps with context inputs.
    ab = test.run(activity_block_id='calculateMaxWithNames', activity_name='second', additional_context={'max':3}, expectation='ACTIVITY_IN_BLOCK_calculateMaxWithNames_SUCCESS_uc4_second.json')
    ab = test.run(activity_block_id='calculateMaxWithNames', activity_name='fourth', additional_context={'max':5}, expectation='ACTIVITY_IN_BLOCK_calculateMaxWithNames_SUCCESS_uc4_fourth.json', flow_run_id = ab.get_flow_run_id())


def test_ACTIVITY_IN_BLOCK_skipping_some_activities_without_extra_context_inputs():
    # Run activities 2 and 4 in a row without filling the gaps with extra context inputs.
    ab = test.run(activity_block_id='calculateMaxWithNames', activity_name='second', expectation='ACTIVITY_IN_BLOCK_calculateMaxWithNames_SUCCESS_uc2_second.json')
    ab = test.run(activity_block_id='calculateMaxWithNames', activity_name='fourth', expectation='ACTIVITY_IN_BLOCK_calculateMaxWithNames_SUCCESS_uc2_fourth.json', flow_run_id = ab.get_flow_run_id())


def test_ACTIVITY_IN_BLOCK_once_per_flow():
    # Run each activity separately in a new flow run.
    ab = test.run(activity_block_id='calculateMaxWithNames', activity_name='first', expectation='ACTIVITY_IN_BLOCK_calculateMaxWithNames_SUCCESS_uc1_first.json')
    ab = test.run(activity_block_id='calculateMaxWithNames', activity_name='second', expectation='ACTIVITY_IN_BLOCK_calculateMaxWithNames_SUCCESS_uc1_second.json')
    ab = test.run(activity_block_id='calculateMaxWithNames', activity_name='third', expectation='ACTIVITY_IN_BLOCK_calculateMaxWithNames_SUCCESS_uc1_third.json')
    ab = test.run(activity_block_id='calculateMaxWithNames', activity_name='fourth', expectation='ACTIVITY_IN_BLOCK_calculateMaxWithNames_SUCCESS_uc1_fourth.json')

def test_ACTIVITY_IN_BLOCK_one_activity_fails():
    ab = test.run(activity_block_id='calculateMaxFailSecond', activity_name='first', expectation='ACTIVITY_IN_BLOCK_calculateMaxFailSecond_SUCCESS_uc6_first.json')
    ab = test.run(activity_block_id='calculateMaxFailSecond', activity_name='second', expectation='ACTIVITY_IN_BLOCK_calculateMaxFailSecond_ERROR_uc6_second.json', flow_run_id = ab.get_flow_run_id())
    ab = test.run(activity_block_id='calculateMaxFailSecond', activity_name='third', expectation='ACTIVITY_IN_BLOCK_calculateMaxFailSecond_ERROR_uc6_third.json', flow_run_id = ab.get_flow_run_id())
    ab = test.run(activity_block_id='calculateMaxFailSecond', activity_name='fourth', expectation='ACTIVITY_IN_BLOCK_calculateMaxFailSecond_ERROR_uc6_fourth.json', flow_run_id = ab.get_flow_run_id())


def test_ACTIVITY_IN_BLOCK_one_activity_fails():
    ab = test.run(activity_block_id='calculateMaxFailSecond', activity_name='third', expectation='ACTIVITY_IN_BLOCK_calculateMaxFailSecond_SUCCESS_uc7_third.json')
    ab = test.run(activity_block_id='calculateMaxFailSecond', activity_name='second', expectation='ACTIVITY_IN_BLOCK_calculateMaxFailSecond_ERROR_uc7_second.json', flow_run_id = ab.get_flow_run_id())
    ab = test.run(activity_block_id='calculateMaxFailSecond', activity_name='first', expectation='ACTIVITY_IN_BLOCK_calculateMaxFailSecond_ERROR_uc7_first.json', flow_run_id = ab.get_flow_run_id())
    ab = test.run(activity_block_id='calculateMaxFailSecond', activity_name='fourth', expectation='ACTIVITY_IN_BLOCK_calculateMaxFailSecond_ERROR_uc7_fourth.json', flow_run_id = ab.get_flow_run_id())
    ab = test.run(activity_block_id='calculateMaxFailSecond', activity_name='third', expectation='ACTIVITY_IN_BLOCK_calculateMaxFailSecond_ERROR_uc7_third2.json', flow_run_id = ab.get_flow_run_id())

def test_ACTIVITY():
    ab = test.run(activity_type='MAX', activity_module='test_activities.activities', activity_config={'val':3},expectation='ACTIVITY_generatedActivityBlock_SUCCESS_uc3_first.json')
    #ab = test.run(activity_type='MAX', activity_module='test_activities.activities', activity_config={'val':1},expectation='ACTIVITY_generatedActivityBlock_SUCCESS_uc3_second.json')

def test_ACTIVITY_without_required_configuration():
    ab = test.run(activity_type='MAX', activity_module='test_activities.activities',expectation='ACTIVITY_generatedActivityBlock_ERROR_uc2.json')

def test_ACTIVITY_with_config_and_input():
    ab = test.run(activity_type='MAX', activity_module='test_activities.activities', activity_config={'val':3},expectation='ACTIVITY_generatedActivityBlock_SUCCESS_uc1_first.json')
    ab = test.run(activity_type='MAX2', activity_module='test_activities.activities2', activity_config={'val':1},expectation='ACTIVITY_generatedActivityBlock_SUCCESS_uc1_second.json', flow_run_id = ab.get_flow_run_id())
    ab = test.run(activity_type='MAX', activity_module='test_activities.activities', activity_config={'val':5},expectation='ACTIVITY_generatedActivityBlock_SUCCESS_uc1_third.json', flow_run_id = ab.get_flow_run_id())
    ab = test.run(activity_type='MAX', activity_module='test_activities.activities', activity_config={'val':4},expectation='ACTIVITY_generatedActivityBlock_SUCCESS_uc1_fourth.json', flow_run_id = ab.get_flow_run_id())


    import filecmp

    f1 = os.path.join("autor-config.yml")
    f2 = os.path.join("data","ACTIVITY_uc1_generatedFlowConfig_fourth.yml")

    # shallow comparison
    result = filecmp.cmp(f1, f2)
    logging.info(f"Shallow comparison: {result}")
    print(result)
    assert result, f"Generated flow configuration file: 'autor-config.yml' was not as expected."

    # deep comparison
    result = filecmp.cmp(f1, f2, shallow=False)
    logging.info(f"Deep comparison: {result}")
    print(result)
    assert result, f"Generated flow configuration file: 'autor-config.yml' was not as expected."

