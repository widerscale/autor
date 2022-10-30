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
class DebugConfig():
    # A class that helps to switch on/off functionality-specific debug prints in the framework.
    # Useful when debugging the framework.

    # Main flags
    trace_sequence_details = False

    # Detail falgs
    print_selected_activity = False
    print_context_on_finished = False

    trace_activity_sequence_decisions = False
    activity_sequence_decisions_trace_prefix = "[sequence]:            "

    trace_activity_processing = False
    activity_processing_trace_prefix =         "[activity-processing]: "

    trace_callbacks = False
    callbacks_trace_prefix =                   "[callbacks]:           "

    trace_context = False
    context_trace_prefix =                     "[context]:             "

    exit_on_extension_exceptions = False

    print_state_names = False
    print_loaded_helper_configurations = False
    print_loaded_extensions = False
    print_loaded_modules = False
    print_registered_exceptions = True

    if trace_sequence_details:
        print_selected_activity = True
        trace_activity_sequence_decisions = True
        trace_activity_processing = True
# fmt: on
