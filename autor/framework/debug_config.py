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





    # Main flags
    trace_sequence_details = False # Activates all flags connected to sequence tracing.

    print_final_input = False # Prints the input that Autor has after bootstrapping


    print_autor_info = False
    autor_info_prefix = "[aut]: "

    # Detail flags
    print_selected_activity = False
    selected_activity_prefix = "[sel]: "

    trace_activity_sequence_decisions = False
    activity_sequence_decisions_trace_prefix = "[seq]: "

    trace_activity_processing = False
    activity_processing_trace_prefix = "[prc]: "

    trace_callbacks = False
    callbacks_trace_prefix = "[clb]: "

    trace_context = False
    context_trace_prefix = "[ctx]: "

    trace_string_arg_parsing = False
    string_arg_parsing_prefix = "[srg]: "

    print_calls_to_extensions = False
    extension_trace_prefix = "[ext]: "

    print_state_names = False
    state_prefix = "[sta]: "

    # ------------ context -----------------#
    print_context_before_activities_are_run = False
    print_context_on_finished = False

    print_loaded_extensions = False
    print_loaded_modules = False
    print_registered_exceptions = False

    exit_on_extension_exceptions = False

    if trace_sequence_details:
        print_selected_activity = True
        trace_activity_sequence_decisions = True
        trace_activity_processing = True

    if trace_context:
        print_context_before_activities_are_run = True
        print_context_on_finished = True

# fmt: on
