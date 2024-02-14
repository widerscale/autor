from autor_tester import AutorTester as test
from autor.framework.constants import Mode, Status

# A collection of examples used in Autor documentation.

def test_ACTIVITY_BLOCK():
    ab = test.run2(expectation='ACTIVITY_BLOCK___calculateMax___SUCCESS', flow_config_path="test_flow_configs/doc-config.yml")
    ab = test.run2(expectation='ACTIVITY_BLOCK___calculateMax___flow_run_id___SUCCESS', flow_config_path="test_flow_configs/doc-config.yml", flow_run_id=ab.get_flow_run_id())

def test_ACTIVITY_IN_BLOCK_by_activity_id():
    ab = test.run2(expectation='ACTIVITY_IN_BLOCK___calculateMax___calculateMax-activity1___SUCCESS', activity_id='calculateMax-activity1', flow_config_path="test_flow_configs/doc-config.yml",)
    ab = test.run2(expectation='ACTIVITY_IN_BLOCK___calculateMax___calculateMax-activity2___flow_run_id___SUCCESS', activity_id='calculateMax-activity2', flow_config_path="test_flow_configs/doc-config.yml", flow_run_id=ab.get_flow_run_id())
    ab = test.run2(expectation='ACTIVITY_IN_BLOCK___calculateMax___calculateMax-activity3___flow_run_id___SUCCESS', activity_id='calculateMax-activity3', flow_config_path="test_flow_configs/doc-config.yml", flow_run_id=ab.get_flow_run_id())
    ab = test.run2(expectation='ACTIVITY_IN_BLOCK___calculateMax___calculateMax-activity4___flow_run_id___SUCCESS', activity_id='calculateMax-activity4', flow_config_path="test_flow_configs/doc-config.yml", flow_run_id=ab.get_flow_run_id())

def test_ACTIVITY_IN_BLOCK_by_activity_name():
    ab = test.run2(expectation='ACTIVITY_IN_BLOCK___calculateMaxWithNames___first___SUCCESS', activity_name='first', flow_config_path="test_flow_configs/doc-config.yml")
    ab = test.run2(expectation='ACTIVITY_IN_BLOCK___calculateMaxWithNames___second___flow_run_id___SUCCESS', activity_name='second', flow_config_path="test_flow_configs/doc-config.yml", flow_run_id=ab.get_flow_run_id())
    ab = test.run2(expectation='ACTIVITY_IN_BLOCK___calculateMaxWithNames___third___flow_run_id___SUCCESS', activity_name='third', flow_config_path="test_flow_configs/doc-config.yml", flow_run_id=ab.get_flow_run_id())
    ab = test.run2(expectation='ACTIVITY_IN_BLOCK___calculateMaxWithNames___fourth___flow_run_id___SUCCESS', activity_name='fourth', flow_config_path="test_flow_configs/doc-config.yml", flow_run_id=ab.get_flow_run_id())


def test_ACTIVITY():
    ab = test.run2(expectation='ACTIVITY___val=3___test_activities.doc_activities___max___SUCCESS', activity_type='max', activity_module='test_activities.doc_activities', activity_config={'val': 3})
    ab = test.run2(expectation='ACTIVITY___val=3___max=2___test_activities.doc_activities___max___SUCCESS', activity_type='max', activity_module='test_activities.doc_activities', activity_config={'val': 3}, input={'max':2})



def test_ACTIVITY_BLOCK_RERUN_2():
    # These tests do not perform any testing as they contain a random element. Used for generating examples.
    ab = test.run2(mode=Mode.ACTIVITY_BLOCK, activity_block_id="calculateMaxWithFailureChance", status=Status.ALL, flow_config_path="test_flow_configs/doc-config.yml")
    ab = test.run2(mode=Mode.ACTIVITY_BLOCK_RERUN, activity_block_id="calculateMaxWithFailureChance", activity_name='third', status=Status.ALL, flow_config_path="test_flow_configs/doc-config.yml", flow_run_id=ab.get_flow_run_id())
    #ab = test.run2(expectation='ACTIVITY_BLOCK_RERUN___everyOtherActivityRunFails___second___flow_run_id___FAIL', activity_name='second', flow_config_path="test_flow_configs/doc-config.yml", flow_run_id=ab.get_flow_run_id())
