import logging

from autor.framework.extension_exception import AutorExtensionException
from autor.framework.state import Bootstrap
from autor.framework.state_listener import StateListener


class ConfigBootstrapExtension(StateListener):
    def on_bootstrap(self, state: Bootstrap):

        """
        Provide flow-config-path and/or activity-block-id values in case these were not provided as input arguments.
        The values to set should be provided through the custom_data argument to Autor.
        """

        logging.info("RTE____RTE")
        logging.info("RTE____RTE")
        logging.info("RTE____RTE")

        logging.info(f"custom_data type: {type(state.custom_data)}")
        data = state.custom_data.get("ConfigBootstrapExtension", {})

        flow_config_path = state.custom_data.get("ConfigBootstrapExtension", {}).get("flowConfigPath", None)
        activity_block_id = state.custom_data.get("ConfigBootstrapExtension", {}).get("activityBlockId", None)

        if state.flow_config_path is None or state.flow_config_path == "":
            if flow_config_path is None:
                raise AutorExtensionException("Expected ConfigBootstrapExtension.flowConfigPath in custom_data (command-line argument)")
            else:
                self.log_info(f'flow-config-path: {state.flow_config_path} -> {flow_config_path}')
                state.flow_config_path = flow_config_path


        if state.activity_block_id is None or state.activity_block_id == "":
            if activity_block_id is None:
                raise AutorExtensionException("Expected ConfigBootstrapExtension.activityBlockId in custom_data (command-line argument)")
            else:
                self.log_info(f'activity-block-id: {state.activity_block_id} -> {activity_block_id}')
                state.activity_block_id = activity_block_id