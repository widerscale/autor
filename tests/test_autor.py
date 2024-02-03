
import os.path

from autor import __version__
from autor_tester import AutorTester as test


def test_version():
    assert __version__ == "0.1.0"



def test_ACTIVITY_BLOCK():
    ab = test.run(activity_block_id='calculateMax', expectation='ACTIVITY_BLOCK_calculateMax_SUCCESS')
    ab = test.run(activity_block_id='calculateMax2', expectation='ACTIVITY_BLOCK_calculateMax2_SUCCESS_secondAB', flow_run_id=ab.get_flow_run_id())

def test_ACTIVITY_BLOCK_RERUN():
    ab = test.run(activity_block_id='calculateMax', expectation='ACTIVITY_BLOCK_calculateMax_SUCCESS')
    ab = test.run(activity_block_id='calculateMax', activity_id="calculateMax-activity2", flow_run_id=ab.get_flow_run_id(), expectation='ACTIVITY_BLOCK_RERUN_calculateMax_SUCCESS_activity2')
    ab = test.run(activity_block_id='calculateMax', activity_id="calculateMax-activity4", flow_run_id=ab.get_flow_run_id(), expectation='ACTIVITY_BLOCK_RERUN_calculateMax_SUCCESS_activity4')
    ab = test.run(activity_block_id='calculateMax', activity_id="calculateMax-activity1", flow_run_id=ab.get_flow_run_id(), expectation='ACTIVITY_BLOCK_RERUN_calculateMax_SUCCESS_activity1_missingContext')
    ab = test.run(activity_block_id='calculateMax', activity_id="calculateMax-activity1", flow_run_id=ab.get_flow_run_id(), expectation='ACTIVITY_BLOCK_RERUN_calculateMax_SUCCESS_activity1_withContext', input={'max':None})

    ab = test.run(activity_block_id='calculateMax', expectation='ACTIVITY_BLOCK_calculateMax_SUCCESS')
    ab = test.run(activity_block_id='calculateMax', activity_id="calculateMax-activity2", flow_run_id=ab.get_flow_run_id(), expectation='ACTIVITY_BLOCK_RERUN_calculateMax_SUCCESS_activity2')
    ab = test.run(activity_block_id='calculateMax', activity_id="calculateMax-activity4", flow_run_id=ab.get_flow_run_id(), expectation='ACTIVITY_BLOCK_RERUN_calculateMax_SUCCESS_activity4')
    ab = test.run(activity_block_id='calculateMax', activity_id="calculateMax-activity1", flow_run_id=ab.get_flow_run_id(), expectation='ACTIVITY_BLOCK_RERUN_calculateMax_SUCCESS_activity1_missingContext')
    ab = test.run(activity_block_id='calculateMax', activity_id="calculateMax-activity1", flow_run_id=ab.get_flow_run_id(), expectation='ACTIVITY_BLOCK_RERUN_calculateMax_SUCCESS_activity1_withContext', input={'max':None})

    ab = test.run(activity_block_id='calculateMax', expectation='ACTIVITY_BLOCK_calculateMax_SUCCESS')


def test_ACTIVITY_BLOCK_RERUN_from_failure():
    ab = test.run(activity_block_id='calculateMaxWithExceptionEverySecondRun1', expectation='ACTIVITY_BLOCK_calculateMaxWithExceptionEverySecondRun1_SUCCESS_firstRun')
    ab = test.run(activity_block_id='calculateMaxWithExceptionEverySecondRun2', flow_run_id=ab.get_flow_run_id(), expectation='ACTIVITY_BLOCK_calculateMaxWithExceptionEverySecondRun2_ERROR_secondRun')

    # Success, if run from the first activity, as we need the counter from that activity to succeed.
    ab = test.run(activity_block_id='calculateMaxWithExceptionEverySecondRun2', activity_id="calculateMaxWithExceptionEverySecondRun2-activity1", flow_run_id=ab.get_flow_run_id(), expectation='ACTIVITY_BLOCK_RERUN_calculateMaxWithExceptionEverySecondRun2_SUCCESS_thirdRun')

    # This run will succeed, as the runNbr counter will not be updated by the first activity (as we use re-run on it).
    ab = test.run(activity_block_id='calculateMaxWithExceptionEverySecondRun2', activity_id="calculateMaxWithExceptionEverySecondRun2-exceptionEverySecondRun", flow_run_id=ab.get_flow_run_id(), expectation='ACTIVITY_BLOCK_RERUN_calculateMaxWithExceptionEverySecondRun2_SUCCESS_fourthRun')






def test_unknown_activity_type():
    ab = test.run(activity_block_id='unknownActivityType', expectation='ACTIVITY_BLOCK_unknownActivityType_ABORTED')

def test_bootstrap_configuration():
    extensions:list = ['tests.test_extensions.ConfigBootstrapExtension.ConfigBootstrapExtension']
    custom_data:dict = {}
    data:dict = {}
    data["flowConfigUrl"] = "test-config.yml"
    data["activityBlockId"] = "calculateMax"
    custom_data["ConfigBootstrapExtension"] = data
    ab = test.run(additional_extensions=extensions, custom_data=custom_data, expectation='ACTIVITY_BLOCK_calculateMax_SUCCESS_bootstrapConfig')

def test_bootstrap_configuration_commandline_prio():
    # The extension should not override activity block id, when it's provided.
    extensions:list = ['tests.test_extensions.ConfigBootstrapExtension.ConfigBootstrapExtension']
    custom_data:dict = {}
    data:dict = {}
    data["flowConfigUrl"] = "test-config.yml"
    data["activityBlockId"] = "calculateMax"  # This should not be used by the extension (<- testing this)
    custom_data["ConfigBootstrapExtension"] = data
    ab = test.run(activity_block_id='calculateMax2',additional_extensions=extensions, custom_data=custom_data, expectation='ACTIVITY_BLOCK_calculateMax2_SUCCESS_bootstrapConfigActivityIdProvided')



def test_ACTIVITY_IN_BLOCK_all_one_by_one():
    ab = test.run(activity_block_id='calculateMaxWithNames', activity_name='first', expectation='ACTIVITY_IN_BLOCK_calculateMaxWithNames_SUCCESS_uc3_first.json')
    ab = test.run(activity_block_id='calculateMaxWithNames', activity_name='second', expectation='ACTIVITY_IN_BLOCK_calculateMaxWithNames_SUCCESS_uc3_second.json', flow_run_id=ab.get_flow_run_id())
    ab = test.run(activity_block_id='calculateMaxWithNames', activity_name='third', expectation='ACTIVITY_IN_BLOCK_calculateMaxWithNames_SUCCESS_uc3_third.json', flow_run_id=ab.get_flow_run_id())
    ab = test.run(activity_block_id='calculateMaxWithNames', activity_name='fourth', expectation='ACTIVITY_IN_BLOCK_calculateMaxWithNames_SUCCESS_uc3_fourth.json', flow_run_id=ab.get_flow_run_id())



def test_ACTIVITY_IN_BLOCK_running_activities_backwards():
    ab = test.run(activity_block_id='calculateMaxWithNames', activity_name='fourth', expectation='ACTIVITY_IN_BLOCK_calculateMaxWithNames_SUCCESS_uc5_fourth.json')
    ab = test.run(activity_block_id='calculateMaxWithNames', activity_name='third', expectation='ACTIVITY_IN_BLOCK_calculateMaxWithNames_SUCCESS_uc5_third.json', flow_run_id=ab.get_flow_run_id())
    ab = test.run(activity_block_id='calculateMaxWithNames', activity_name='second', expectation='ACTIVITY_IN_BLOCK_calculateMaxWithNames_SUCCESS_uc5_second.json', flow_run_id=ab.get_flow_run_id())
    ab = test.run(activity_block_id='calculateMaxWithNames', activity_name='first', expectation='ACTIVITY_IN_BLOCK_calculateMaxWithNames_SUCCESS_uc5_first.json', flow_run_id=ab.get_flow_run_id())


def test_ACTIVITY_IN_BLOCK_skipping_some_activities_with_extra_context_inputs():
    # Run activities 2 and 4 in a row filling the gaps with context inputs.
    ab = test.run(activity_block_id='calculateMaxWithNames', activity_name='second', input={'max':3}, expectation='ACTIVITY_IN_BLOCK_calculateMaxWithNames_SUCCESS_uc4_second.json')
    ab = test.run(activity_block_id='calculateMaxWithNames', activity_name='fourth', input={'max':5}, expectation='ACTIVITY_IN_BLOCK_calculateMaxWithNames_SUCCESS_uc4_fourth.json', flow_run_id=ab.get_flow_run_id())


def test_ACTIVITY_IN_BLOCK_skipping_some_activities_without_extra_context_inputs():
    # Run activities 2 and 4 in a row without filling the gaps with extra context inputs.
    ab = test.run(activity_block_id='calculateMaxWithNames', activity_name='second', expectation='ACTIVITY_IN_BLOCK_calculateMaxWithNames_SUCCESS_uc2_second.json')
    ab = test.run(activity_block_id='calculateMaxWithNames', activity_name='fourth', expectation='ACTIVITY_IN_BLOCK_calculateMaxWithNames_SUCCESS_uc2_fourth.json', flow_run_id=ab.get_flow_run_id())


def test_ACTIVITY_IN_BLOCK_once_per_flow():
    # Run each activity separately in a new flow run.
    ab = test.run(activity_block_id='calculateMaxWithNames', activity_name='first', expectation='ACTIVITY_IN_BLOCK_calculateMaxWithNames_SUCCESS_uc1_first.json')
    ab = test.run(activity_block_id='calculateMaxWithNames', activity_name='second', expectation='ACTIVITY_IN_BLOCK_calculateMaxWithNames_SUCCESS_uc1_second.json')
    ab = test.run(activity_block_id='calculateMaxWithNames', activity_name='third', expectation='ACTIVITY_IN_BLOCK_calculateMaxWithNames_SUCCESS_uc1_third.json')
    ab = test.run(activity_block_id='calculateMaxWithNames', activity_name='fourth', expectation='ACTIVITY_IN_BLOCK_calculateMaxWithNames_SUCCESS_uc1_fourth.json')

def test_ACTIVITY_IN_BLOCK_one_activity_fails():
    ab = test.run(activity_block_id='calculateMaxFailSecond', activity_name='first', expectation='ACTIVITY_IN_BLOCK_calculateMaxFailSecond_SUCCESS_uc6_first.json')
    ab = test.run(activity_block_id='calculateMaxFailSecond', activity_name='second', expectation='ACTIVITY_IN_BLOCK_calculateMaxFailSecond_ERROR_uc6_second.json', flow_run_id=ab.get_flow_run_id())
    ab = test.run(activity_block_id='calculateMaxFailSecond', activity_name='third', expectation='ACTIVITY_IN_BLOCK_calculateMaxFailSecond_ERROR_uc6_third.json', flow_run_id=ab.get_flow_run_id())
    ab = test.run(activity_block_id='calculateMaxFailSecond', activity_name='fourth', expectation='ACTIVITY_IN_BLOCK_calculateMaxFailSecond_ERROR_uc6_fourth.json', flow_run_id=ab.get_flow_run_id())


def test_ACTIVITY_IN_BLOCK_one_activity_fails2():
    ab = test.run(activity_block_id='calculateMaxFailSecond', activity_name='third', expectation='ACTIVITY_IN_BLOCK_calculateMaxFailSecond_SUCCESS_uc7_third.json')
    ab = test.run(activity_block_id='calculateMaxFailSecond', activity_name='second', expectation='ACTIVITY_IN_BLOCK_calculateMaxFailSecond_ERROR_uc7_second.json', flow_run_id=ab.get_flow_run_id())
    ab = test.run(activity_block_id='calculateMaxFailSecond', activity_name='first', expectation='ACTIVITY_IN_BLOCK_calculateMaxFailSecond_ERROR_uc7_first.json', flow_run_id=ab.get_flow_run_id())
    ab = test.run(activity_block_id='calculateMaxFailSecond', activity_name='fourth', expectation='ACTIVITY_IN_BLOCK_calculateMaxFailSecond_ERROR_uc7_fourth.json', flow_run_id=ab.get_flow_run_id())
    ab = test.run(activity_block_id='calculateMaxFailSecond', activity_name='third', expectation='ACTIVITY_IN_BLOCK_calculateMaxFailSecond_ERROR_uc7_third2.json', flow_run_id=ab.get_flow_run_id())

##################################################
def test_ACTIVITY_IN_BLOCK_one_activity_fails3():
    # Rerun a failing activity
    ab = test.run2(activity_name='first',  expectation='ACTIVITY_IN_BLOCK___statusFlow___first___SUCCESS.json')
    ab = test.run2(activity_name='second', expectation='ACTIVITY_IN_BLOCK___statusFlow___second___flow_run_id___FAIL.json', flow_run_id=ab.get_flow_run_id())
    ab = test.run2(activity_name='second', expectation='ACTIVITY_IN_BLOCK___statusFlow___second___flow_run_id___SUCCESS.json', flow_run_id=ab.get_flow_run_id())
    ab = test.run2(activity_name='third',  expectation='ACTIVITY_IN_BLOCK___statusFlow___third___flow_run_id___SUCCESS.json', flow_run_id=ab.get_flow_run_id())



def test_exception_handling():
    # Exception thrown from activity
    ab = test.run2(expectation='ACTIVITY_BLOCK___calculateMaxWithException___ERROR')

    # Activity name that does not exist.
    ab = test.run2(activity_name='activityXYZ', expectation='ACTIVITY_IN_BLOCK___calculateMaxWithException___activityXYZ___ABORTED')

    # Flow allows ERROR, but activity throws an exception.
    # Autor should continue running activities after the ERROR, but mark the activity block status as ERROR.
    ab = test.run2(expectation='ACTIVITY_BLOCK___calculateMaxWithExceptionAllowError___ERROR')


def test_activity_block_status():
    ab = test.run2(expectation='ACTIVITY_BLOCK___statusFlowFail___FAIL')
    ab = test.run2(expectation='ACTIVITY_BLOCK___statusFlowSkip___SUCCESS')
    ab = test.run2(expectation='ACTIVITY_BLOCK___statusFlowAborted___ABORTED')
    ab = test.run2(expectation='ACTIVITY_BLOCK___statusFlowSuccess___SUCCESS')




def test_ACTIVITY():
    ab = test.run(activity_type='max', activity_module='test_activities.activities', activity_config={'val':3},expectation='ACTIVITY_generatedActivityBlock_SUCCESS_uc3_first.json')
    ab = test.run(activity_type='max', activity_module='test_activities.activities', activity_config={'val':1},expectation='ACTIVITY_generatedActivityBlock_SUCCESS_uc3_second.json')

def test_ACTIVITY_without_required_configuration():
    ab = test.run(activity_type='max', activity_module='test_activities.activities',expectation='ACTIVITY_generatedActivityBlock_ERROR_uc2.json')

def test_ACTIVITY_with_config_and_input():
    ab = test.run(activity_type='max', activity_module='test_activities.activities', activity_config={'val':3},expectation='ACTIVITY_generatedActivityBlock_SUCCESS_uc1_first.json')
    ab = test.run(activity_type='max2', activity_module='test_activities.activities2', activity_config={'val':1},expectation='ACTIVITY_generatedActivityBlock_SUCCESS_uc1_second.json', flow_run_id=ab.get_flow_run_id())
    ab = test.run(activity_type='max', activity_module='test_activities.activities', activity_config={'val':5},expectation='ACTIVITY_generatedActivityBlock_SUCCESS_uc1_third.json', flow_run_id=ab.get_flow_run_id())
    ab = test.run(activity_type='max', activity_module='test_activities.activities', activity_config={'val':4},expectation='ACTIVITY_generatedActivityBlock_SUCCESS_uc1_fourth.json', flow_run_id=ab.get_flow_run_id())


    f1 = os.path.join("autor-config.yml")
    f2 = os.path.join("data","ACTIVITY_uc1_generatedFlowConfig_fourth.yml")

    import yaml

    with open(f1, 'r') as file:
        gen = yaml.safe_load(file)

    with open(f2, 'r') as file:
        exp = yaml.safe_load(file)

    from deepdiff import DeepDiff
    ddiff = DeepDiff(gen, exp, ignore_order=True)
    assert len(ddiff) == 0, f"Flow configuration generated by Autor was not as expected. Generated config: {f1} Expected config: {f2}"




def test_ACTIVITY_BLOCK_err_misspelled_activity_block_name():
    ab = test.run(activity_block_id='thisActivityBlockDoesNotExist', mode="ACTIVITY_BLOCK", status="ABORTED", err_msg="Could not create activity configurations: ValueError: No activity block named 'thisActivityBlockDoesNotExist' was found.")

def test_ACTIVITY_BLOCK_err_misspelled_activity_type():
    err_msg = f"No activity with the type: 'max-misspelled' registered. \n          - Check the spelling of the 'type' int the activity decorator. \n          - Make sure the activity module has been added to the Flow Configuration (if it is used) or provided as a parameter to Autor."
    ab = test.run2(expectation="ACTIVITY_BLOCK___activityTypeMisspelled___ABORTED", err_msg=err_msg)

def test_ACTIVITY_BLOCK_err_activity_defined_without_type():
    # Flow config contains an activity that is decorated, but lacks type.
    # Running activity blocks that don't include that problematic activity should succeed
    ab = test.run(activity_block_id='calculateMax', mode="ACTIVITY_BLOCK", status="SUCCESS", flow_config_url="test_flow_configs/test-config-activity-impl-misses-type.yml")

def test_ACTIVITY_BLOCK_err_input_misspelling():
    #assert False, "Test not implemented"
    pass

def test_ACTIVITY_BLOCK_err_config_missing_mandatory():
    #assert False, "Test not implemented"
    pass

def test_ACTIVITY_BLOCK_err_input_missing_mandatory():
    #assert False, "Test not implemented"
    pass

def test_ACTIVITY_BLOCK_err_output_missing():
    #assert False, "Test not implemented"
    pass



def test_mandatory_inputs_should_not_have_default_values_in_decorator():
    ab = test.run(activity_block_id='decoratorRuleBreaking1', mode="ACTIVITY_BLOCK", status="SUCCESS")
    #TODO: add warning checks

def test_mandatory_inputs_should_not_have_default_values_in_constructor():
    ab = test.run(activity_block_id='decoratorRuleBreaking2', mode="ACTIVITY_BLOCK", status="SUCCESS")
    ab = test.run(activity_block_id='decoratorRuleBreaking3', mode="ACTIVITY_BLOCK", status="ERROR")
    #TODO: add warning checks

def test_mandatory_inputs_must_have_a_value_in_context():
    ab = test.run(activity_block_id='missingMandatoryMax', mode="ACTIVITY_BLOCK", status="ERROR")




# Rules
# ___________________________________________________________
# + Mandatory inputs must not have default values in decorators
# + Mandatory inputs must not have default values in constructor
# Mandatory inputs must have a value in context
# Mandatory configs must have a value in configuration
# A context value must not replace a configuration (a configuration should always be fetched from config and not context)
# Non-mandatory inputs must not have default values defined BOTH in constructor and decorator
# Non-mandatory inputs are set to None if no default value is found in constructor nor decorator
# Outputs may not have default values
# Provided values must be of right type
# Provided default values must be of right type




