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
#
# Utility functions. Small functions that didn't have a better place to end up in.
# Currently contains some support for error registering and printing that should probably be
# lifted out to a separate class.



import datetime
import json
import logging
import os
import pprint
import traceback
import uuid

from autor.framework.constants import ExceptionType
from autor.framework.debug_config import DebugConfig
from autor.framework.extension_exception import AutorExtensionException
from autor.framework.keys import FlowContextKeys as ctx
from autor.framework.util import Util


# pylint: disable=no-member


class ExceptionHandler:

    _first_exception:Exception = None
    _abort_exception:Exception = None

    @staticmethod
    def get_first_exception_message():
        if ExceptionHandler._first_exception is not None:
            return str(ExceptionHandler._first_exception)
        return None

    @staticmethod
    def get_first_exception():
        return ExceptionHandler._first_exception

    @staticmethod
    def get_abort_exception_message():
        if ExceptionHandler._abort_exception is not None:
            return str(ExceptionHandler._abort_exception)
        return None

    @staticmethod
    def get_abort_exception():
        return ExceptionHandler._abort_exception

   # _framework_exceptions = []
   # _other_exceptions = []
    _raw_exceptions = []

    @staticmethod
    def debug_reset():
        ExceptionHandler._framework_exceptions = [] # Original
        ExceptionHandler._other_exceptions = [] # Original
        ExceptionHandler._raw_exceptions = [] # All registered raw exceptions with ID [{raw,uuid}]
        ExceptionHandler._first_exception = None
        ExceptionHandler._abort_exception = None


    @staticmethod
    def print_all_exceptions():

        if len(ExceptionHandler._raw_exceptions) == 0:
            logging.info(f"{DebugConfig.autor_info_prefix}No registered exceptions")
            return

        else:
            logging.info(f'')
            logging.info(f'')
            logging.info(f'')
            Util.print_header("","List of registered exceptions",'info')
            logging.info('Use <UUID> to find the exception in the log.')
            logging.info(f'')


            for i,exception in enumerate(ExceptionHandler._raw_exceptions):
                logging.info(f"EXCEPTION: {i+1}")
                logging.info(f"UUID: {exception[ctx.UUID]} ")
                logging.info(f"TYPE: {exception[ctx.TYPE]} ")
                logging.info(f"MESSAGE: {exception[ctx.RAW]}")

                if exception.get(ctx.DESCRIPTION, None) is not None:
                    logging.info(f"DESCRIPTION: {exception[ctx.DESCRIPTION]}")
                if DebugConfig.print_stack_trace_in_error_summary:
                    logging.info("", exc_info=exception[ctx.RAW])
                logging.info(f'')
                logging.info(f'')
                logging.info(f'')



    @staticmethod
    def register_exception(ex: Exception, ex_type: ExceptionType, context=None, description="", custom=None):
        # pylint: disable=redefined-builtin, too-many-branches
        # pylint: disable=import-outside-toplevel
        from autor.framework.context import Context

        exception = {}
        if ExceptionHandler._first_exception is None:
            ExceptionHandler._first_exception = ex

        exception[ctx.UUID] = str(uuid.uuid4())
        exception[ctx.CUSTOM] = custom
        exception[ctx.MESSAGE] = str(ex)
        exception[ctx.CLASS] = ex.__class__.__name__

        if description != "":
            exception[ctx.DESCRIPTION] = description

        if ex_type != "":
            exception[ctx.TYPE] = ex_type
        elif isinstance(ex, AutorExtensionException):
            exception[ctx.TYPE] = ExceptionType.EXTENSION

        from autor.framework.state_handler import StateHandler

        exception[ctx.STATE] = StateHandler.get_current_state_name()

        st_list = list(traceback.TracebackException.from_exception(ex).format())
        formatted_st = []
        # pylint: disable-next=invalid-name
        for el in st_list:
            elem = el.split("\n")
            elem = list(filter(None, elem))  # Remove empty stirng elements
            for line in elem:
                formatted_st.append(line)

        exception[ctx.STACK_TRACE] = (
            "".join(traceback.TracebackException.from_exception(ex).format())
        ).split("\n")
        exception[ctx.STACK_TRACE] = formatted_st


        tot_len = 110
        message = exception.get(ctx.MESSAGE, "")
        padding_len = (int)((tot_len - len(message))/2)
        padding = "-" * padding_len


        logging.warning("", exc_info=ex)

        ExceptionHandler._print("", 'info')
        ExceptionHandler._print("R E G I S T E R I N G   E X C E P T I O N", 'info')
        ExceptionHandler._print("UUID:                    " + exception[ctx.UUID], 'info')
        if exception.get(ctx.CUSTOM, None) is not None:
            ExceptionHandler._print("CUSTOM:                  " + str(exception[ctx.CUSTOM]), 'info')
        if exception.get(ctx.MESSAGE, None) is not None:
            ExceptionHandler._print("MESSAGE:                 " + exception[ctx.MESSAGE], 'info')
        if exception.get(ctx.DESCRIPTION, None) is not None:
            ExceptionHandler._print("DESCRIPTION:             " + exception[ctx.DESCRIPTION], 'info')
        if exception.get(ctx.CLASS, None) is not None:
            ExceptionHandler._print("EXCEPTION CLASS:         " + exception[ctx.CLASS], 'info')
        if exception.get(ctx.TYPE, None) is not None:
            ExceptionHandler._print("TYPE:                    " + exception[ctx.TYPE], 'info')
        if exception.get(ctx.STATE, None) is not None:
            ExceptionHandler._print("LATEST EVENT:            " + exception[ctx.STATE], 'info')


        ExceptionHandler._print("", "info")
        ExceptionHandler._print("", "info")



        raw_ex = {}
        raw_ex[ctx.RAW] = ex
        raw_ex[ctx.UUID] = exception[ctx.UUID]
        raw_ex[ctx.TYPE] = exception[ctx.TYPE]
        if exception.get(ctx.DESCRIPTION, None) is not None:
            raw_ex[ctx.DESCRIPTION] = exception[ctx.DESCRIPTION]
        ExceptionHandler._raw_exceptions.append(raw_ex)

        if DebugConfig.save_exceptions_in_context:
            if context is None:
                context = Context()
            exceptions = context.get(ctx.EXCEPTIONS, [])
            exceptions.append(exception)
            context.set(ctx.EXCEPTIONS, exceptions)

        return exception

    @staticmethod
    def _print(txt, level='debug'):
        ExceptionHandler.log(DebugConfig.autor_info_prefix + txt,level)

    @staticmethod
    def log(txt:str, level='debug'):
        if level == 'info':
            logging.info(txt)
        elif level == 'warning':
            logging.warning(txt)
        elif level == 'error':
            logging.error(txt)
        else:
            logging.debug(txt)




