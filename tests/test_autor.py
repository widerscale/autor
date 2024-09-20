
import os.path
from typing import List

from autor import __version__
from autor.framework.activity_block import ActivityBlock
from autor.framework.node import Node
from tests.autor_tester import AutorTester as test


def test_version():
    assert __version__ == "0.1.0"



def test_ACTIVITY_BLOCK():
    ab = test.run(activity_block_id='calculateMax', expectation='ACTIVITY_BLOCK_calculateMax_SUCCESS')
    ab = test.run(activity_block_id='calculateMax2', expectation='ACTIVITY_BLOCK_calculateMax2_SUCCESS_secondAB', flow_run_id=ab.get_flow_run_id())

# def test_ACTIVITY_BLOCK_two_activity_blocks_and_rerun():
#     ab = test.run(activity_block_id='calculateMax', expectation='ACTIVITY_BLOCK_calculateMax_SUCCESS')
#     ab = test.run(activity_block_id='calculateMax2', expectation='ACTIVITY_BLOCK_calculateMax2_SUCCESS_secondAB', flow_run_id=ab.get_flow_run_id())


def test_ACTIVITY_BLOCK_RERUN():
    ab = test.run2(expectation='ACTIVITY_BLOCK___calculateMax___SUCCESS')

    ab = test.run2(activity_id="calculateMax-activity2", flow_run_id=ab.get_flow_run_id(), expectation='ACTIVITY_BLOCK_RERUN___calculateMax___calculateMax-activity2___flow_run_id___SUCCESS')
    ab = test.run2(activity_id="calculateMax-activity4", flow_run_id=ab.get_flow_run_id(), expectation='ACTIVITY_BLOCK_RERUN___calculateMax___calculateMax-activity4___flow_run_id___SUCCESS')
    ab = test.run2(activity_id="calculateMax-activity1", flow_run_id=ab.get_flow_run_id(), expectation='ACTIVITY_BLOCK_RERUN___calculateMax___calculateMax-activity1___flow_run_id___SUCCESS')




def test_ACTIVITY_BLOCK_RERUN_input_effect():
    ab = test.run2(expectation='ACTIVITY_BLOCK___calculateMax___SUCCESS')

    # Input should have effect
    ab = test.run2(activity_id="calculateMax-activity1", input={'max':100}, expectation='ACTIVITY_BLOCK_RERUN___calculateMax___calculateMax-activity1___max=100___flow_run_id___SUCCESS', flow_run_id=ab.get_flow_run_id())


def test_ACTIVITY_BLOCK_RERUN_from_failure():

    #ab = test.run2(expectation='ACTIVITY_BLOCK___flexMaxWithInput___throw_ex=False___SUCCESS', input={'throw_ex': False})
    ab = test.run2( input={'throw_ex': True}, expectation='ACTIVITY_BLOCK___flexMaxWithInput___throw_ex=True___ERROR',)

    # providing input should not change the outcome
    ab = test.run2(input={'throw_ex': False}, activity_name='third', expectation='ACTIVITY_BLOCK_RERUN___flexMaxWithInput___throw_ex=False___third___flow_run_id___SUCCESS',  flow_run_id=ab.get_flow_run_id())

    # more tests for ACTIVITY_BLOCK_RERUN in test_doc.py




def test_unknown_activity_type():
    ab = test.run(activity_block_id='unknownActivityType', expectation='ACTIVITY_BLOCK_unknownActivityType_ABORTED')

def test_bootstrap_configuration():
    extensions:list = ['tests.test_extensions.ConfigBootstrapExtension.ConfigBootstrapExtension']
    custom_data:dict = {}
    data:dict = {}
    data["flowConfigPath"] = "test-config.yml"
    data["activityBlockId"] = "calculateMax"
    custom_data["ConfigBootstrapExtension"] = data
    ab = test.run(additional_extensions=extensions, custom_data=custom_data, expectation='ACTIVITY_BLOCK_calculateMax_SUCCESS_bootstrapConfig')

def test_bootstrap_configuration_commandline_prio():
    # The extension should not override activity block id, when it's provided.
    extensions:list = ['tests.test_extensions.ConfigBootstrapExtension.ConfigBootstrapExtension']
    custom_data:dict = {}
    data:dict = {}
    data["flowConfigPath"] = "test-config.yml"
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



def test_exception_handling1():
    # Exception thrown from activity
    ab = test.run2(expectation='ACTIVITY_BLOCK___calculateMaxWithException___ERROR')

def test_exception_handling2():
    # Activity name that does not exist.
    ab = test.run2(activity_name='activityXYZ', expectation='ACTIVITY_IN_BLOCK___calculateMaxWithException___activityXYZ___UNKNOWN')

def test_exception_handling2():
    err_msg = f"Could not find the provided activity id: calculateMaxWithException-activityXYZ in the activity block. Valid activity ids:"\
                f"\ncalculateMaxWithException-activity1"\
                f"\ncalculateMaxWithException-activity2"\
                f"\ncalculateMaxWithException-activity3"\
                f"\ncalculateMaxWithException-activity4"
    ab = test.run2(activity_name='activityXYZ', expectation='ACTIVITY_IN_BLOCK___calculateMaxWithException___activityXYZ___ABORTED', err_msg=err_msg)





def test_exception_handling3():
    # Flow allows ERROR, but activity throws an exception.
    # Autor should continue running activities after the ERROR, but mark the activity block status as ERROR.
    ab = test.run2(expectation='ACTIVITY_BLOCK___calculateMaxWithExceptionAllowError___ERROR')


def test_activity_block_status():
    ab = test.run2(expectation='ACTIVITY_BLOCK___statusFlowFail___FAIL')
    ab = test.run2(expectation='ACTIVITY_BLOCK___statusFlowSkip___SUCCESS')
    ab = test.run2(expectation='ACTIVITY_BLOCK___statusFlowAborted___ABORTED')
    ab = test.run2(expectation='ACTIVITY_BLOCK___statusFlowSuccess___SUCCESS')

def test_status_prints():
    ab = test.run2(expectation='ACTIVITY_BLOCK___flexMaxWithStatusFail___FAIL')
    ab = test.run2(expectation='ACTIVITY_BLOCK___flexMaxWithStatusSkipped___SUCCESS')
    ab = test.run2(expectation='ACTIVITY_BLOCK___flexMaxWithStatusError___ERROR')
    ab = test.run2(expectation='ACTIVITY_BLOCK___flexMaxWithException___ERROR')



def test_ACTIVITY_without_required_configuration():
    ab = test.run2(activity_type='max', activity_module='tests.test_activities.activities', expectation='ACTIVITY___autogenActivityBlock1___tests.test_activities.activities___max___ERROR.json')

def test_ACTIVITY_with_config_and_input():
    ab = test.run2(activity_type='max',  activity_module='tests.test_activities.activities',  activity_config={'val':3},expectation='ACTIVITY___autogenActivityBlock1___val=3___tests.test_activities.activities___max___SUCCESS.json')
    ab = test.run2(activity_type='max2', activity_module='tests.test_activities.activities2', activity_config={'val':1},expectation='ACTIVITY___autogenActivityBlock1___val=1___tests.test_activities.activities2___max2___SUCCESS.json')
    ab = test.run2(activity_type='max',  activity_module='tests.test_activities.activities',  activity_config={'val':5},expectation='ACTIVITY___autogenActivityBlock1___val=5___tests.test_activities.activities___max___SUCCESS.json')
    ab = test.run2(activity_type='max',  activity_module='tests.test_activities.activities',  activity_config={'val':4},expectation='ACTIVITY___autogenActivityBlock1___val=4___tests.test_activities.activities___max___SUCCESS.json')

def test_ACTIVITY_with_config_and_input_and_activity_block_id(): # without abid
    ab = test.run2(activity_type='max',  activity_module='tests.test_activities.activities',  activity_config={'val':3},expectation='ACTIVITY___autogenActivityBlock1___val=3___tests.test_activities.activities___max___SUCCESS.json')
    ab = test.run2(activity_type='max2', activity_module='tests.test_activities.activities2', activity_config={'val':1},expectation='ACTIVITY___autogenActivityBlock2___val=1___tests.test_activities.activities2___max2___flow_run_id___SUCCESS.json', flow_run_id=ab.get_flow_run_id())
    ab = test.run2(activity_type='max',  activity_module='tests.test_activities.activities',  activity_config={'val':5},expectation='ACTIVITY___autogenActivityBlock3___val=5___tests.test_activities.activities___max___flow_run_id___SUCCESS.json', flow_run_id=ab.get_flow_run_id())
    ab = test.run2(activity_type='max',  activity_module='tests.test_activities.activities',  activity_config={'val':4},expectation='ACTIVITY___autogenActivityBlock4___val=4___tests.test_activities.activities___max___flow_run_id___SUCCESS.json', flow_run_id=ab.get_flow_run_id())






    # return
    #
    # f1 = os.path.join("autor-config.yml")
    # f2 = os.path.join("data","ACTIVITY_uc1_generatedFlowConfig_fourth.yml")
    #
    # import yaml
    #
    # with open(f1, 'r') as file:
    #     gen = yaml.safe_load(file)
    #
    # with open(f2, 'r') as file:
    #     exp = yaml.safe_load(file)
    #
    # from deepdiff import DeepDiff
    # ddiff = DeepDiff(gen, exp, ignore_order=True)
    # assert len(ddiff) == 0, f"Flow configuration generated by Autor was not as expected. Generated config: {f1} Expected config: {f2}"




def test_ACTIVITY_BLOCK_err_misspelled_activity_block_name():
    ab = test.run(activity_block_id='thisActivityBlockDoesNotExist', mode="ACTIVITY_BLOCK", status="ABORTED", err_msg="No activity block named 'thisActivityBlockDoesNotExist' was found.")

def test_ACTIVITY_BLOCK_err_misspelled_activity_type():
    err_msg = f"No activity with the type: 'max-misspelled' registered. \n" \
              f"          - Check the spelling of the 'type' in the activity decorator. \n" \
              f"          - Make sure the activity module has been added to the Flow Configuration (if Flow Configuration is used) or provided as a parameter to Autor."
    ab = test.run2(expectation="ACTIVITY_BLOCK___activityTypeMisspelled___ERROR", err_msg=err_msg)

def test_ACTIVITY_BLOCK_err_activity_defined_without_type():
    # Flow config contains an activity that is decorated, but lacks type.
    # Running activity blocks that don't include that problematic activity should succeed
    ab = test.run(activity_block_id='calculateMax', mode="ACTIVITY_BLOCK", status="SUCCESS", flow_config_path="test_flow_configs/test-config-activity-impl-misses-type.yml")

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









def test_sequence_rules():
    ab = test.run2(expectation='ACTIVITY_BLOCK___sequenceRules1___FAIL.json')
    ab = test.run2(expectation='ACTIVITY_BLOCK___sequenceRules2___FAIL.json')

def test_sequence_rules_defaults():
    ab = test.run2(expectation='ACTIVITY_BLOCK___sequenceRulesDefaults___SUCCESS.json')

def test_sequence_rules_failing_MA():
    ab = test.run2(expectation='ACTIVITY_BLOCK___sequenceRulesFailingMainActivity___FAIL.json')

def test_sequence_rules_failing_BA():
    ab = test.run2(expectation='ACTIVITY_BLOCK___sequenceRulesFailingBeforeActivity___FAIL.json')

def test_sequence_rules_failing_BB():
    ab = test.run2(expectation='ACTIVITY_BLOCK___sequenceRulesFailingBeforeBlockActivity___FAIL.json')

def test_sequence_rules_failing_AB():
    ab = test.run2(expectation='ACTIVITY_BLOCK___sequenceRulesFailingAfterBlockActivity___FAIL.json')

def test_sequence_rules_dependency_on_BA():
    ab = test.run2(expectation='ACTIVITY_BLOCK___sequenceRulesDependencyOnBeforeActivity1___SUCCESS.json')
    ab = test.run2(expectation='ACTIVITY_BLOCK___sequenceRulesDependencyOnBeforeActivity2___SUCCESS.json')





def _check_activity_started_and_finished_order(expected_started_order:List[str], expected_finished_order:List[str], ab:ActivityBlock):


    actual_started_order:List[str] = []
    started_nodes:List[Node] = ab.get_node_started_order()

    for n in started_nodes:
        actual_started_order.append(n.activity_id)


    actual_finished_order:List[str] = []
    finished_nodes:List[Node] = ab.get_node_finished_order()
    for n in finished_nodes:
        actual_finished_order.append(n.activity_id)

    # we only want to check the number of elements provided by the expected lists.
    actual_started_order = actual_started_order[:len(expected_started_order)]
    actual_finished_order = actual_finished_order[:len(expected_finished_order)]

    _check_equal_lists(actual_started_order, expected_started_order, "Activity starting order")
    _check_equal_lists(actual_finished_order, expected_finished_order, "Activity finishing order")



def _check_equal_lists(l1:List, l2:List, msg:str=""):

    l1_str = ""
    l2_str = ""
    for elem in l1:
        l1_str = f"{l1_str},{elem}"
    for elem in l2:
        l2_str = f"{l2_str},{elem}"

    assert l1_str == l2_str


def test_sleepers():
    ab = test.run2(expectation='ACTIVITY_BLOCK___sleepySleepers___print_activity_started_and_finished_order=True___SUCCESS.json', flags={'print_activity_started_and_finished_order':True})
    activities_started_order:List[str] = []
    activities_started_order.append("sleepySleepers-first")
    activities_started_order.append("sleepySleepers-second")
    activities_started_order.append("sleepySleepers-third")
    activities_started_order.append("sleepySleepers-fifth")
    activities_started_order.append("sleepySleepers-sixth")
    activities_started_order.append("sleepySleepers-fourth")
    activities_started_order.append("sleepySleepers-seventh")
    activities_finished_order:List[str] = []
    activities_finished_order.append("sleepySleepers-first")
    activities_finished_order.append("sleepySleepers-second")
    activities_finished_order.append("sleepySleepers-fifth")
    activities_finished_order.append("sleepySleepers-sixth")
    activities_finished_order.append("sleepySleepers-third")
    activities_finished_order.append("sleepySleepers-fourth")
    activities_finished_order.append("sleepySleepers-seventh")

    _check_activity_started_and_finished_order(activities_started_order, activities_finished_order, ab)

def test_lastMultiparentToFinishFails():
    ab = test.run2(expectation='ACTIVITY_BLOCK___lastMultiparentToFinishFails___FAIL.json')


def test_lastMultiparentToRunFails():
    ab = test.run2(expectation='ACTIVITY_BLOCK___lastMultiparentToRunFails___FAIL.json')


def test_lastMultiparentToRunAcceptsFail():
    ab = test.run2(expectation='ACTIVITY_BLOCK___lastMultiparentToRunAcceptsFail___FAIL.json')



def test_concurrency_graph_order_and_rerun():

    activities_started_order: List[str] = []
    activities_started_order.append("concurrency_1-one")
    activities_started_order.append("concurrency_1-two")
    activities_started_order.append("concurrency_1-three")
    activities_started_order.append("concurrency_1-four")
    activities_started_order.append("concurrency_1-seven")
    activities_started_order.append("concurrency_1-ten")
    activities_started_order.append("concurrency_1-five")
    activities_started_order.append("concurrency_1-eight")
    activities_started_order.append("concurrency_1-nine")
    activities_started_order.append("concurrency_1-six")
    activities_started_order.append("concurrency_1-eleven")
    activities_started_order.append("concurrency_1-twelve")
    activities_finished_order: List[str] = []
    activities_finished_order.append("concurrency_1-one")
    activities_finished_order.append("concurrency_1-two")
    activities_finished_order.append("concurrency_1-ten")
    activities_finished_order.append("concurrency_1-four")
    activities_finished_order.append("concurrency_1-seven")
    activities_finished_order.append("concurrency_1-eight")
    activities_finished_order.append("concurrency_1-nine")
    activities_finished_order.append("concurrency_1-five")
    activities_finished_order.append("concurrency_1-three")
    activities_finished_order.append("concurrency_1-six")
    activities_finished_order.append("concurrency_1-twelve")
    activities_finished_order.append("concurrency_1-eleven")

   # ab = test.run2(expectation='ACTIVITY_BLOCK___concurrency_1___print_activity_started_and_finished_order=True___SUCCESS.json',flags={'print_activity_started_and_finished_order': True})
    ab = test.run2(expectation='ACTIVITY_BLOCK___concurrency_1___print_activity_started_and_finished_order=True___SUCCESS.json')
    _check_activity_started_and_finished_order(activities_started_order, activities_finished_order, ab)
    ab = test.run2(flow_run_id=ab.get_flow_run_id(), activity_name="eight", expectation='ACTIVITY_BLOCK_RERUN___concurrency_1___eight___flow_run_id___SUCCESS.json')
    _check_activity_started_and_finished_order(activities_started_order[:6], activities_finished_order[:2], ab)
    ab = test.run2(flow_run_id=ab.get_flow_run_id(), activity_name="three", expectation='ACTIVITY_BLOCK_RERUN___concurrency_1___three___flow_run_id___SUCCESS.json')
    _check_activity_started_and_finished_order(activities_started_order[:6], activities_finished_order[:2], ab)
    ab = test.run2(flow_run_id=ab.get_flow_run_id(), activity_names=["six", "eight"], expectation='ACTIVITY_BLOCK_RERUN___concurrency_1___six_eight___flow_run_id___SUCCESS.json')
    _check_activity_started_and_finished_order(activities_started_order[:6], activities_finished_order[:2], ab)

    # Rerun from eight.



def test_concurrency_input_modifier():
   # ab = test.run2(expectation='ACTIVITY_BLOCK___concurrency_quick___SUCCESS.json')

    custom_data:dict = {}
    data:dict = {}
    custom_data["AutorFrameworkActivityInputModifier"] = data

    data["eight"] = {}
    data["eight"]["outcome"] = "FAIL"

    ab = test.run2(custom_data=custom_data, expectation='ACTIVITY_BLOCK___concurrency_1___AutorFrameworkActivityInputModifier=eight=outcome=FAIL___FAIL.json')


def test_concurrency_input_modifier_and_rerun():
    activities_started_order: List[str] = []
    activities_started_order.append("concurrency_1-one")
    activities_started_order.append("concurrency_1-two")
    activities_started_order.append("concurrency_1-three")
    activities_started_order.append("concurrency_1-four")
    activities_started_order.append("concurrency_1-seven")
    activities_started_order.append("concurrency_1-ten")
    activities_started_order.append("concurrency_1-five")
    activities_started_order.append("concurrency_1-eight")
    activities_started_order.append("concurrency_1-nine")
    activities_started_order.append("concurrency_1-six")
    activities_started_order.append("concurrency_1-eleven")
    activities_started_order.append("concurrency_1-twelve")
    activities_finished_order: List[str] = []
    activities_finished_order.append("concurrency_1-one")
    activities_finished_order.append("concurrency_1-two")
    activities_finished_order.append("concurrency_1-ten")
    activities_finished_order.append("concurrency_1-four")
    activities_finished_order.append("concurrency_1-seven")
    activities_finished_order.append("concurrency_1-eight")
    activities_finished_order.append("concurrency_1-nine")
    activities_finished_order.append("concurrency_1-five")
    activities_finished_order.append("concurrency_1-three")
    activities_finished_order.append("concurrency_1-six")
    activities_finished_order.append("concurrency_1-twelve")
    activities_finished_order.append("concurrency_1-eleven")

    custom_data:dict = {}
    data:dict = {}
    custom_data["AutorFrameworkActivityInputModifier"] = data

    data["eight"] = {}
    data["eight"]["outcome"] = "FAIL"
    data["three"] = {}
    data["three"]["outcome"] = "FAIL"
    data["five"] = {}
    data["five"]["outcome"] = "FAIL"


    ab = test.run2(custom_data=custom_data, expectation='ACTIVITY_BLOCK___concurrency_1___AutorFrameworkActivityInputModifier=eight=outcome=FAIL_three=outcome=FAIL_five=outcome=FAIL___FAIL.json')
    # _check_activity_started_and_finished_order(activities_started_order[:8], activities_finished_order[:8], ab)
    # ab = test.run2(flow_run_id=ab.get_flow_run_id(), activity_name="eight", expectation='ACTIVITY_BLOCK_RERUN___concurrency_1___eight___flow_run_id___FAIL.json')
    # _check_activity_started_and_finished_order(activities_started_order[:3], activities_finished_order[:2], ab)
    # ab = test.run2(flow_run_id=ab.get_flow_run_id(), activity_names=["three", "five"], expectation='ACTIVITY_BLOCK_RERUN___concurrency_1___three_five___flow_run_id___SUCCESS.json')
    # _check_activity_started_and_finished_order(activities_started_order[:4], activities_finished_order[:2], ab)
    # ab = test.run2(flow_run_id=ab.get_flow_run_id(), activity_names=["eight"], expectation='ACTIVITY_BLOCK_RERUN___concurrency_1___eight2___flow_run_id___SUCCESS.json')
    # _check_activity_started_and_finished_order(activities_started_order[:6], activities_finished_order[:2], ab)
    # ab = test.run2(flow_run_id=ab.get_flow_run_id(), activity_names=["six","nine"], expectation='ACTIVITY_BLOCK_RERUN___concurrency_1___six_nine___flow_run_id___SUCCESS.json')


def test_concurrency2():
    ab = test.run2(expectation='ACTIVITY_BLOCK___concurrency_2___SUCCESS.json',flags={'print_activity_started_and_finished_order': True})

    activities_started_order: List[str] = []
    activities_started_order.append("concurrency_2-one")
    activities_started_order.append("concurrency_2-two")
    activities_started_order.append("concurrency_2-nine")
    activities_started_order.append("concurrency_2-four")
    activities_started_order.append("concurrency_2-five")
    activities_started_order.append("concurrency_2-three")
    activities_started_order.append("concurrency_2-eight")
    activities_started_order.append("concurrency_2-six")
    activities_started_order.append("concurrency_2-seven")
    activities_started_order.append("concurrency_2-ten")
    activities_started_order.append("concurrency_2-twelve")
    activities_started_order.append("concurrency_2-eleven")
    activities_finished_order: List[str] = []
    activities_finished_order.append("concurrency_2-one")
    activities_finished_order.append("concurrency_2-two")
    activities_finished_order.append("concurrency_2-three")
    activities_finished_order.append("concurrency_2-four")
    activities_finished_order.append("concurrency_2-five")
    activities_finished_order.append("concurrency_2-six")
    activities_finished_order.append("concurrency_2-seven")
    activities_finished_order.append("concurrency_2-eight")
    activities_finished_order.append("concurrency_2-nine")
    activities_finished_order.append("concurrency_2-ten")
    activities_finished_order.append("concurrency_2-eleven")
    activities_finished_order.append("concurrency_2-twelve")
    _check_activity_started_and_finished_order(activities_started_order, activities_finished_order, ab)

def test_parentSkipLeadsToChildSkip():
    ab = test.run2(expectation='ACTIVITY_BLOCK___concurrency2ParentSkipLeadsToChildSKip___SUCCESS.json')

def test_parentSkipLeadsToChildSKipAndInterrupt():
    ab = test.run2(expectation='ACTIVITY_BLOCK___concurrency2ParentSkipLeadsToChildSKipAndInterrupt___ABORTED.json')

# def test_concurrency2ParentSkipLeadsToChildSKipAndInterrupt_interruptDesc():
#     ab = test.run2(expectation='ACTIVITY_BLOCK___concurrency2ParentSkipLeadsToChildSKipAndInterrupt_interruptDescendents___ABORTED.json')
