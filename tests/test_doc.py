from autor_tester import AutorTester as test

# A collection of examples used in Autor documentation.

def test_ACTIVITY_BLOCK():
    ab = test.run2(expectation='ACTIVITY_BLOCK___calculateMax___SUCCESS', flow_config_path="test_flow_configs/doc-config.yml")
    ab = test.run2(expectation='ACTIVITY_BLOCK___calculateMax___flow_run_id___SUCCESS', flow_config_path="test_flow_configs/doc-config.yml", flow_run_id=ab.get_flow_run_id())

def test_ACTIVITY_IN_BLOCK_all_one_by_one():
    ab = test.run(activity_block_id='calculateMaxWithNames', activity_name='first', expectation='ACTIVITY_IN_BLOCK_calculateMaxWithNames_SUCCESS_uc3_first.json')
    ab = test.run(activity_block_id='calculateMaxWithNames', activity_name='second', expectation='ACTIVITY_IN_BLOCK_calculateMaxWithNames_SUCCESS_uc3_second.json', flow_run_id=ab.get_flow_run_id())
    ab = test.run(activity_block_id='calculateMaxWithNames', activity_name='third', expectation='ACTIVITY_IN_BLOCK_calculateMaxWithNames_SUCCESS_uc3_third.json', flow_run_id=ab.get_flow_run_id())
    ab = test.run(activity_block_id='calculateMaxWithNames', activity_name='fourth', expectation='ACTIVITY_IN_BLOCK_calculateMaxWithNames_SUCCESS_uc3_fourth.json', flow_run_id=ab.get_flow_run_id())

