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

# pylint: disable=no-member


class Util:
    @staticmethod
    def is_camel_case(string:str):
        return string.isalnum() and not string.istitle()



    @staticmethod
    def print_framed(prefix:str, text: str, frame_symbol: str, frame_width=56, level ='debug'):
        text = f"   {text}   "
        text_length = len(text)
        full = frame_symbol * frame_width
        left = frame_symbol * round((frame_width - text_length) / 2)
        right = frame_symbol * (frame_width - text_length - len(left))

        Util.log(prefix,level)
        Util.log(prefix + full,level)
        Util.log(prefix + left + text + right,level)
        Util.log(prefix + full,level)



    @staticmethod
    def print_header(prefix:str, text:str, level='debug',line_above:bool=True, line_below:bool=True):

        indent_len = 1
        side_left  = "*** "
        side_right = " ***"
        width = 56

        line_len = max(len(text) + len(side_left) + len(side_right), width)
        line = "-" * line_len
        header = f'{side_left}{text}{side_right}'

        Util.log(f'{prefix}',level)
        if line_above:
            Util.log(f'{prefix}{line}',level)
        Util.log(f'{prefix}{header}',level)
        if line_below:
            Util.log(f'{prefix}{line}',level)


    @staticmethod
    def format_banner(text: str, length: int = 100, pad_with: str = "-") -> str:
        format_string = "{" + f":{pad_with}^{length}" + "}"
        return format_string.format(f" {text} ")

    @staticmethod
    # pylint: disable-next=redefined-builtin
    def print_dict_old(dict, comment=None):
        string = ""
        if not comment:
            comment = ""

        logging.debug(comment)
        if dict:
            try:
                string = json.dumps(dict, sort_keys=False, indent=2)
            except Exception:
                # If the dict contains an object, we cannot used json, so we
                # use pprint, which doesn't look as good as json.
                pp = pprint.PrettyPrinter(indent=2)
                string = os.linesep + pp.pformat(dict)
        else:
            string = "dict is None"

        logging.debug(string)

    @staticmethod
    # pylint: disable-next=redefined-builtin
    def print_dict(dict, comment=None, level='debug', prefix=""):

        if comment is not None:
            Util.log(prefix+comment,level)

        string = Util.dict_to_str(dict)

        lines = string.split('\n')
        for line in lines:
            Util.log(f'{prefix}{line}', level)

        #Util.log(f'{prefix}\n{string}', level)

    def read_json(file_name:str)->dict:
        import json

        with open(file_name) as json_data:
            d = json.load(json_data)
            json_data.close()

        return d

    @staticmethod
    def get_datetime_str()->str:
        now = datetime.datetime.now()
        now_str = f'{now}'
        now_str = now_str.replace(' ','-')
        now_str = now_str.replace('.', '-')
        now_str = now_str.replace(':', '-')
        return now_str

    @staticmethod
    # pylint: disable-next=redefined-builtin
    def dict_to_str(dict):
        string = ""
        if dict:
            try:
                string = json.dumps(dict, sort_keys=False, indent=2)
            except Exception:
                # If the dict contains an object, we cannot use json, so we
                # use pprint, which doesn't look as good as json.
                pp = pprint.PrettyPrinter(indent=2)
                string = os.linesep + pp.pformat(dict)
        else:
            string = str(dict)
        return string

    _first_exception = None
    _abort_exception = None

    @staticmethod
    def get_first_exception_message():
        if Util._first_exception is not None:
            return str(Util._first_exception)

        return None

    @staticmethod
    def get_first_exception():
        return Util._first_exception

    @staticmethod
    def get_abort_exception_message():
        if Util._abort_exception is not None:
            return str(Util._abort_exception)

        return None

    @staticmethod
    def get_abort_exception():
        return Util._abort_exception

    _framework_exceptions = []
    _other_exceptions = []
    _raw_exceptions = []

    @staticmethod
    def debug_reset():
        Util._framework_exceptions = [] # Original
        Util._other_exceptions = [] # Original
        Util._raw_exceptions = [] # All registered raw exceptions with ID [{raw,uuid}]
        Util._first_exception = None
        Util._abort_exception = None


    @staticmethod
    def print_all_exceptions():

        nbr_fwk_exceptions = len(Util._framework_exceptions)
        nbr_other_exceptions = len(Util._other_exceptions)

        if nbr_fwk_exceptions == 0 and nbr_other_exceptions == 0:
            logging.info(f"{DebugConfig.autor_info_prefix}No registered exceptions")
            return


        if nbr_other_exceptions + nbr_fwk_exceptions > 1:
            logging.info(f'')
            logging.info(f'')
            logging.info(f'')


            Util.print_header("","List of registered exceptions",'info')
            logging.info('Use <UUID> to find the exception in the log.')
            logging.info(f'')
            '''
            for ex in Util._framework_exceptions:
                logging.info(f"{DebugConfig.autor_info_prefix} Framework exception: {str(ex)}")

            if len(Util._other_exceptions) > 0:
                for ex in Util._other_exceptions:
                    logging.info(f"{DebugConfig.autor_info_prefix} Non-framework exception: {str(ex)}")
            '''

        i = 0
        for exception in Util._raw_exceptions:
            i = i + 1
            logging.info(f"EXCEPTION: {i}")
            logging.info(f"UUID: {exception[ctx.UUID]} ")
            logging.info(f"TYPE: {exception[ctx.TYPE]} ")
            logging.info("", exc_info=exception[ctx.RAW])
            logging.info(f'')
            logging.info(f'')
            logging.info(f'')



    @staticmethod
    def register_exception(ex: Exception, context=None, description="", type="", custom=None, framework_error=True):
        # pylint: disable=redefined-builtin, too-many-branches



        if framework_error:
            Util._framework_exceptions.append(ex)
        else:
            Util._other_exceptions.append(ex)
        # pylint: disable=import-outside-toplevel
        from autor.framework.context import Context

        if context is None:
            context = Context()
        exceptions = context.get(ctx.EXCEPTIONS, [])
        exception = {}

        if Util._first_exception is None:
            Util._first_exception = ex

        if Util._abort_exception is None and framework_error:
            Util._abort_exception = ex

        exception[ctx.UUID] = str(uuid.uuid4())
        exception[ctx.CUSTOM] = custom
        exception[ctx.MESSAGE] = str(ex)
        exception[ctx.CLASS] = ex.__class__.__name__

        if description != "":
            exception[ctx.DESCRIPTION] = description

        if type != "":
            exception[ctx.TYPE] = type
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

        Util._print("", 'info')
        Util._print("R E G I S T E R I N G   E X C E P T I O N", 'info')
        Util._print("UUID:                    " + exception[ctx.UUID], 'info')
        if exception.get(ctx.CUSTOM, None) is not None:
            Util._print("CUSTOM:                  " + str(exception[ctx.CUSTOM]), 'info')
        if exception.get(ctx.DESCRIPTION, None) is not None:
            Util._print("DESCRIPTION:             " + exception[ctx.DESCRIPTION], 'info')
        if exception.get(ctx.CLASS, None) is not None:
            Util._print("EXCEPTION CLASS:         " + exception[ctx.CLASS], 'info')
        if exception.get(ctx.TYPE, None) is not None:
            Util._print("TYPE:                    " + exception[ctx.TYPE], 'info')
        if exception.get(ctx.STATE, None) is not None:
            Util._print("LATEST EVENT:            " + exception[ctx.STATE], 'info')
        if exception.get(ctx.MESSAGE, None) is not None:
            Util._print("MESSAGE:                 " + exception[ctx.MESSAGE], 'info')

        Util._print("", "info")
        Util._print("", "info")

        exceptions.append(exception)

        raw_ex = {}
        raw_ex[ctx.RAW] = ex
        raw_ex[ctx.UUID] = exception[ctx.UUID]
        raw_ex[ctx.TYPE] = exception[ctx.TYPE]
        Util._raw_exceptions.append(raw_ex)

        if DebugConfig.save_exceptions_in_context:
            context.set(ctx.EXCEPTIONS, exceptions)

        return exception

    @staticmethod
    def _print(txt, level='debug'):
        Util.log(DebugConfig.autor_info_prefix + txt,level)

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


class ExceptionContainer:
    def __init__(self, e: Exception, data: dict):
        self._exception = e
        self._data = data
