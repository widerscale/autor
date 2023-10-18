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

# Utility functions. Small functions that didn't have a better place to end up in.
# Currently contains some support for error registering and printing that should probably be
# lifted out to a separate class.

import json
import logging
import os
import pprint
import sys
import traceback

from autor.framework.constants import ExceptionType
from autor.framework.debug_config import DebugConfig
from autor.framework.extension_exception import AutorExtensionException
from autor.framework.keys import FlowContextKeys as ctx

# pylint: disable=no-member


class Util:
    @staticmethod
    def print_framed(prefix:str, text: str, frame_symbol: str, frame_width=56, level ='debug'):
        text = f"   {text}   "
        text_length = len(text)
        full = frame_symbol * frame_width
        left = frame_symbol * round((frame_width - text_length) / 2)
        right = frame_symbol * (frame_width - text_length - len(left))

        if level == 'info':
            logging.info(prefix)
            logging.info(prefix + full)
            logging.info(prefix + left + text + right)
            logging.info(prefix + full)
        elif level == 'warning':
            logging.warning(prefix)
            logging.warning(prefix + full)
            logging.warning(prefix + left + text + right)
            logging.warning(prefix + full)
        elif level == 'error':
            logging.error(prefix)
            logging.error(prefix + full)
            logging.error(prefix + left + text + right)
            logging.error(prefix + full)
        else:
            logging.debug(prefix)
            logging.debug(prefix + full)
            logging.debug(prefix + left + text + right)
            logging.debug(prefix + full)

    @staticmethod
    def print_header(prefix:str, text:str, level='debug'):
        # FIXME: remove unused variables?
        # text_lenght = len(text)
        indent_len = 1
        side_left  = "*** "
        side_right = " ***"
        width = 56
        indent = " " * indent_len
        line_len = max(len(text) + len(side_left) + len(side_right), width)
        line = "-" * line_len
        header = f'{side_left}{text}{side_right}'
        # left = "." * round((width - text_lenght) / 2)
        # right = "." * (width - text_lenght - len(left))





        if level == 'info':
            logging.info(f'{prefix}')
            logging.info(f'{prefix}{line}')
            logging.info(f'{prefix}{header}')
            logging.info(f'{prefix}{line}')
        elif level == 'error':
            logging.error(f'{prefix}')
            logging.error(f'{prefix}{line}')
            logging.error(f'{prefix}{header}')
            logging.error(f'{prefix}{line}')
        elif level == 'warning':
            logging.warning(f'{prefix}')
            logging.warning(f'{prefix}{line}')
            logging.warning(f'{prefix}{header}')
            logging.warning(f'{prefix}{line}')
        else:
            logging.debug(f'{prefix}')
            logging.debug(f'{prefix}{line}')
            logging.debug(f'{prefix}{header}')
            logging.debug(f'{prefix}{line}')


    @staticmethod
    def old____print_header(text: str, prefix:str = "", level='debug'):
        # FIXME: remove unused variables?
        # text_lenght = len(text)
        indent_len = 1
        width = 56
        indent = " " * indent_len
        line_len = max(len(text) + 2*indent_len, width)
        line = "_" * line_len
        # left = "." * round((width - text_lenght) / 2)
        # right = "." * (width - text_lenght - len(left))


        if level == 'info':
            logging.info(prefix)
            logging.info(f'{prefix}{indent}{text}')
            logging.info(f'{prefix}{line}')
        elif level == 'error':
            logging.error(prefix)
            logging.error(f'{prefix}{indent}{text}')
            logging.error(f'{prefix}{line}')
        elif level == 'warning':
            logging.warning(prefix)
            logging.warning(f'{prefix}{indent}{text}')
            logging.warning(f'{prefix}{line}')
        else:
            logging.debug(prefix)
            logging.debug(f'{prefix}{indent}{text}')
            logging.debug(f'{prefix}{line}')

    @staticmethod
    def format_banner(text: str, length: int = 100, pad_with: str = "*") -> str:
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
    def print_dict(dict, comment=None, level='debug'):
        if comment is None:
            comment = ""
        Util.log(comment,level)


        string = Util.dict_to_str(dict)
        Util.log(string, level)


    @staticmethod
    # pylint: disable-next=redefined-builtin
    def dict_to_str(dict):
        string = ""
        if dict:
            try:
                string = json.dumps(dict, sort_keys=False, indent=2)
            except Exception:
                # If the dict contains an object, we cannot used json, so we
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

    @staticmethod
    def debug_reset():
        Util._framework_exceptions = []
        Util._other_exceptions = []
        Util._first_exception = None
        Util._abort_exception = None

    @staticmethod
    def print_all_exceptions():
        if len(Util._framework_exceptions) == 0 and len(Util._other_exceptions) == 0:
            logging.info(f"{DebugConfig.autor_info_prefix}No registered exceptions")
            return

        if len(Util._framework_exceptions) > 0:
            logging.info(f"{DebugConfig.autor_info_prefix}Framework exceptions:")
            for ex in Util._framework_exceptions:
                logging.info(f"{DebugConfig.autor_info_prefix} * {str(ex)}")

        if len(Util._other_exceptions) > 0:
            logging.info(f"{DebugConfig.autor_info_prefix}Non-framework exceptions:")
            for ex in Util._other_exceptions:
                logging.info(f"{DebugConfig.autor_info_prefix} * {str(ex)}")

    @staticmethod
    def register_exception(
        ex: Exception, context=None, description="", type="", custom=None, framework_error=True
    ):
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

       # Util._print_registered_exception("\n\n\n")
        #Util._print_registered_exception("")
        #Util._print_registered_exception("")
       # Util._print_registered_exception("")
        Util._print_registered_exception("\n\n\n" + "- " * 55, 'error')
        Util._print_registered_exception(
            "                 R E G I S T E R I N G   E X C E P T I O N ", 'error'
        )

        if custom is not None:
            exception[ctx.CUSTOM] = custom

        if exception.get(ctx.MESSAGE, None) is not None:
            Util._print_registered_exception(" MESSAGE:                 " + exception[ctx.MESSAGE], 'error')

        if exception.get(ctx.CLASS, None) is not None:
            Util._print_registered_exception(" EXCEPTION CLASS:         " + exception[ctx.CLASS], 'error')

        if exception.get(ctx.DESCRIPTION, None) is not None:
            Util._print_registered_exception(
                " DESCRIPTION:             " + exception[ctx.DESCRIPTION]
            , 'error')

        if exception.get(ctx.TYPE, None) is not None:
            Util._print_registered_exception(" TYPE:                    " + exception[ctx.TYPE], 'error')

        if exception.get(ctx.STATE, None) is not None:
            Util._print_registered_exception(" LATEST EVENT:            " + exception[ctx.STATE], 'error')

        if DebugConfig.print_registered_exceptions:
            logging.error("", exc_info=ex)

        Util._print_registered_exception("\n" + "- " * 55 + "\n\n\n", 'error')
        #Util._print_registered_exception("")
        #Util._print_registered_exception("")

        exceptions.append(exception)
        context.set(ctx.EXCEPTIONS, exceptions)

        if type == ExceptionType.EXTENSION and DebugConfig.exit_on_extension_exceptions:
            logging.error("Exiting due to extension exception.")
            sys.exit(1)

        return exception

    @staticmethod
    def _print_registered_exception(txt, level='debug'):
        if DebugConfig.print_registered_exceptions:
            Util.log(txt,level)

    staticmethod
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
