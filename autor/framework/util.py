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
    def print_header(prefix:str, text:str, level:str, line_above:bool=True, line_below:bool=True):

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



