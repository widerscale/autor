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
# fmt:off
import logging



class DebugConfig():
    # A class that helps to switch on/off functionality-specific debug prints in the framework.
    # Useful when debugging the framework.

    print_final_input = True # Prints the input that Autor has after bootstrapping
    print_activity_block_finished_summary = True
    print_context_on_finished = False
    print_stack_trace_in_error_summary = False # After execution add stack trace to the list of errors.
    print_activity_properties_details = False


    # Main flags
    trace_sequence_details = False # Activates all flags connected to sequence tracing.


    print_activity_block_started_inputs_summary = False # Gives an overview of the inputs before a run
    print_uninitiated_inputs = False # Lists also uninitiated inputs in various inputs prints.



    create_skip_with_output_flow_config = False
    save_activity_block_context_locally = True # Creates files in context/ directory. These can be used for creating test cases.


    print_activity = False # Prints activity details when it's about to run
    print_default_config_conditions = False # Prints default rules for continue/runOn

    print_autor_info = False
    autor_info_prefix = "[aut]: "

    # Detail flags

    # For internal debugging only. To see the activity details
    # use flag: print_activity
    print_selected_activity = False
    selected_activity_prefix = "[sel]: "

    trace_activity_sequence_decisions = False
    activity_sequence_decisions_trace_prefix = "[seq]: "

    trace_activity_processing = False
    activity_processing_trace_prefix = "[prc]: "

    trace_callbacks = False
    callbacks_trace_prefix = "[clb]: "

    trace_string_arg_parsing = False
    string_arg_parsing_prefix = "[srg]: "

    print_calls_to_extensions = False
    extension_trace_prefix = "[ext]: "

    print_state_names = False
    state_prefix = "[sta]: "




    # ------------  C O N T E X T  -----------------#
    trace_context = False # All context
    context_trace_prefix = "[ctx]: "




    print_context_before_activities_are_run = False
    print_context_before_state = False
    print_context_after_state = False
    save_exceptions_in_context = False

    print_loaded_extensions = False
    print_loaded_modules = False
    print_registered_exceptions = True
    exit_on_extension_exceptions = False

    if trace_sequence_details:
        print_selected_activity = True
        trace_activity_sequence_decisions = True
        trace_activity_processing = True

    if trace_context:
        print_context_before_activities_are_run = True
        print_context_on_finished = True
        print_context_before_state = True
        print_context_after_state = True

# fmt: on
