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

import logging
from typing import Type

from autor.framework.autor_framework_exception import (
    AutorFrameworkException,
    AutorFrameworkValueException,
)
from autor.framework.debug_config import DebugConfig
from autor.framework.remote_context import RemoteContext
from autor.framework.util import Util


# An internal class that represents the possible context focus level. A focus level
# defines some of the context's default values (see Context.get()).
class Focus:
    FLOW = "FLOW"
    ACTIVITY_BLOCK = "ACTIVITY_BLOCK"
    ACTIVITY = "ACTIVITY"


# pylint: disable=raise-missing-from
class Context:

    #                               C O N T E X T
    #
    # Context is a representation of the data produced by parts of flow instance, that
    # needs to be persisted and made available for the other parts of the same flow
    # instance.
    #

    # ---------------------------------------------------------------------------------------------#
    # ----------------------------------   S T A T I C   S E C T I O N  ---------------------------#
    # ---------------------------------------------------------------------------------------------#

    # Static attributes and constants shared by all Context objects.

    # C O N S T A N T S
    # ------------------
    # A string constant used as a value for undefined values.
    _UNDEFINED = "_UNDEFINED"

    # String constants that represent internal structure of the Context.
    _ACTIVITY_BLOCKS = "_activityBlocks"
    _ACTIVITIES = "_activities"

    # I D
    # -----------------------------------
    # A unique identifier of the context
    _id: str = _UNDEFINED

    # L O C A L   A N D   R E M O T E   C O N T E X T
    # -------------------------------------------------
    # All Context objects share the same local context and remote context. The local context
    # is the representation of the context that we're working with right now. The remote context,
    # that is optional, is typically a data store where the context can be persisted.
    #
    # If no remote context is provided, then the information in the context will exist only
    # during the execution.
    #
    # If remote context is provided, then it can be used to synchronize the changes in the
    # local context.
    _local_context: dict = {}  # The internal representation of the local context.
    _remote_context: RemoteContext = None  # Remote context that can be added by an extension.

    @staticmethod
    def get_context_dict() -> dict:
        return Context._local_context

    @staticmethod
    def print_context(message="") -> None:
        #Util.print_framed(prefix=DebugConfig.context_trace_prefix,text="Context",frame_symbol='-',level='info')
        Util.print_header(prefix=DebugConfig.context_trace_prefix,text=message,level='info')
        Util.print_dict(Context._local_context,level='info',prefix=DebugConfig.context_trace_prefix)

    @staticmethod
    def set_context(context: dict) -> None:
        Context._local_context = context

    @staticmethod
    def reset_static_data():
        Context._id: str = Context._UNDEFINED
        Context._local_context: dict = {}              # The internal representation of the local context.
        Context._remote_context: RemoteContext = None  # Remote context that can be added by an extension.


    # -------------------------------- I N I T  --------------------------------------#
    def __init__(self, activity_block=None, activity=None):
        self._activity_block = activity_block
        self._activity = activity

        if activity is not None and activity_block is None:
            raise AutorFrameworkValueException(
                (
                    "If 'activity' is provided to the Context,"
                    + " the 'activity_block' must also be provided"
                )
            )  # How to handle exceptions in init?

        if activity is not None:
            self._focus = Focus.ACTIVITY
        elif activity_block is not None:
            self._focus = Focus.ACTIVITY_BLOCK
        else:
            self._focus = Focus.FLOW


    # -------------------------  P R O P E R T I E S  -------------------------------#

    # The unique identifier of the context (both for local and remote context)
    # pylint: disable=no-self-use
    @property
    def id(self) -> str:
        return Context._id

    @id.setter
    def id(self, n):
        Context._id = n

    # The representation of the local context as a dictionary
    @property
    def local_context(self) -> str:
        return Context._local_context

    # Remote context is not mandatory. If set, the local context will be syncrhonized
    # with the remote context. If not set, the local context will not be synchronized
    # with remote context.
    @property
    def remote_context(self) -> str:
        return Context._remote_context

    # pylint: enable=no-self-use

    @remote_context.setter
    def remote_context(self, n):
        self._print("set_remote_context: " + str(n))
        Context._remote_context = n

    # ----------------------------------    R E M O T E   C O N T E X T   -------------------------#
    def sync_remote(self) -> None:
        if self.remote_context:
            self._print("sync_remote: " + str(self.remote_context))
            self.remote_context.sync(self.id, self.local_context)
        else:
            self._print("sync_remote: None -> skipping remote sync")

    # ---------------------------------------------------------------------------------------------#
    # --------------------------------------   G E T   M E T H O D S   ----------------------------#
    # ---------------------------------------------------------------------------------------------#

    # -------------------------------   P U B L I C   G E T   M E T H O D S   ---------------------#
    def get(self, key: str, default=_UNDEFINED, search: bool = False) -> Type:
        # pylint: disable=no-else-return
        # A C T I V I T Y
        if self._focus == Focus.ACTIVITY:
            return self.get_from_activity(key=key, default=default, search=search)

        # A C T I V I T Y   B L O C K
        elif self._focus == Focus.ACTIVITY_BLOCK:
            return self.get_from_activity_block(key=key, default=default, search=search)

        # F L O W
        elif self._focus == Focus.FLOW:
            return self.get_from_flow(key=key, default=default)

        # E R R O R
        raise AutorFrameworkException("Focus type not set.")

    def get_from_activity(
        self,
        key: str,
        default=_UNDEFINED,
        activity_block: str = None,
        activity: str = None,
        search: bool = False,
    ) -> Type:
        self._validate_key(key)

        # Validate the parameters and set the default values if necessary.
        activity_block = self._set_variable("activity_block", activity_block, self._activity_block)
        activity = self._set_variable("activity", activity, self._activity)

        if search:
            value = self._search_from_activity(
                key=key, default=default, activity_block=activity_block, activity=activity
            )
        else:
            value = self._get_from_activity(
                key=key, default=default, activity_block=activity_block, activity=activity
            )

        return value

    def get_from_activity_block(
        self, key: str, default=_UNDEFINED, activity_block: str = None, search: bool = False
    ) -> Type:
        self._validate_key(key)

        # Validate the parameters and set the default values if necessary.
        activity_block = self._set_variable("activity_block", activity_block, self._activity_block)

        if search:
            value = self._search_from_activity_block(
                key=key, default=default, activity_block=activity_block
            )
        else:
            value = self._get_from_activity_block(
                key=key, default=default, activity_block=activity_block
            )

        return value

    def get_from_flow(self, key: str, default=_UNDEFINED) -> Type:
        self._validate_key(key)
        return self._get_from_flow(key=key, default=default)

    # ------------------------------   P R I V A T E   G E T   M E T H O D S   --------------------#

    def _get_from_activity(
        self, key: str = None, default=_UNDEFINED, activity_block: str = None, activity: str = None
    ):
        value = None
        try:
            value = (
                self.local_context.get(self._ACTIVITY_BLOCKS)
                .get(activity_block)
                .get(self._ACTIVITIES)
                .get(activity)
                .get(key, default)
            )  # pylint: disable=no-member
            if value == self._UNDEFINED:
                raise AutorFrameworkContextKeyNotFoundException(
                    (
                        "The activity context does not have the requested"
                        + " key and no default value was provided."
                    )
                )

        except Exception:
            if default == self._UNDEFINED:
                raise AutorFrameworkContextKeyNotFoundException(
                    (
                        f"The path to the context key: {key!r}"
                        + " does not exist and no default value was provided."
                    )
                )
            value = default
        return value

    def _get_from_activity_block(
        self, key: str = None, default=_UNDEFINED, activity_block: str = None
    ):
        value = None
        try:
            value = (
                self.local_context.get(self._ACTIVITY_BLOCKS).get(activity_block).get(key, default)
            )  # pylint: disable=no-member
            if value == self._UNDEFINED:
                raise AutorFrameworkContextKeyNotFoundException(
                    (
                        "The activity block context does not have the requested key:'{key}'"
                        + " and no default value was provided."
                    )
                )

        except Exception:
            if default == self._UNDEFINED:
                raise AutorFrameworkContextKeyNotFoundException(
                    (
                        "The path to the context key does not exist and no default"
                        + " value was provided."
                    )
                )

            value = default
        return value

    def _get_from_flow(self, key: str = None, default=_UNDEFINED):

        value = self.local_context.get(key, default)
        if value == self._UNDEFINED:
            raise AutorFrameworkContextKeyNotFoundException(
                (
                    "The flow context does not have the requested"
                    + " key and no default value was provided."
                )
            )

        return value

    # ----------------------------   P R I V A T E   S E A R C H   M E T H O D S   ----------------#

    def _search_from_activity(
        self, key: str = None, default=_UNDEFINED, activity_block: str = None, activity: str = None
    ):

        try:  # Search on the activity level
            return self._get_from_activity(
                key=key, activity_block=activity_block, activity=activity
            )  # without default
        except AutorFrameworkContextKeyNotFoundException:
            pass

        try:  # No value found on activity level -> try activity block level
            return self._get_from_activity_block(
                key=key, activity_block=activity_block
            )  # without default
        except AutorFrameworkContextKeyNotFoundException:
            pass

        # No value found on the activity block level -> try flow level
        #   (and now with the default value)
        return self._get_from_flow(key=key, default=default)  # with default

    def _search_from_activity_block(
        self, key: str = None, default=_UNDEFINED, activity_block: str = None
    ):

        try:  # Search on the activity block level
            return self._get_from_activity_block(
                key=key, activity_block=activity_block
            )  # without default
        except AutorFrameworkContextKeyNotFoundException:
            pass

        # No value found on the activity block level -> try flow level
        # (and now with the default value)
        return self._get_from_flow(key=key, default=default)  # with default

    # ---------------------------------------------------------------------------------------------#
    # --------------------------------------   S E T   M E T H O D S   ----------------------------#
    # ---------------------------------------------------------------------------------------------#

    # -------------------------------   P U B L I C   S E T   M E T H O D S   ---------------------#

    def set(self, key: str, value: type, propagate_value: bool = True):

        # A C T I V I T Y
        if self._focus == Focus.ACTIVITY:
            self._set_to_activity(key=key, value=value, propagate_value=propagate_value)

        # A C T I V I T Y   B L O C K
        elif self._focus == Focus.ACTIVITY_BLOCK:
            self._set_to_activity_block(key=key, value=value, propagate_value=propagate_value)

        # F L O W
        elif self._focus == Focus.FLOW:
            self._set_to_flow(key=key, value=value)

        # E R R O R
        else:
            raise AutorFrameworkException("Focus type not set.")

    def set_to_activity(
        self,
        key: str,
        value: Type,
        activity: str = None,
        activity_block: str = None,
        propagate_value: bool = True,
    ):
        self._set_to_activity(
            key=key,
            value=value,
            activity=activity,
            activity_block=activity_block,
            propagate_value=propagate_value,
        )

    def set_to_activity_block(
        self, key: str, value: Type, activity_block: str = None, propagate_value: bool = True
    ):
        self._set_to_activity_block(
            key=key, value=value, activity_block=activity_block, propagate_value=propagate_value
        )

    def set_to_flow(self, key: str, value: Type):
        self._set_to_flow(key=key, value=value)

    # ------------------------------   P R I V A T E   S E T   M E T H O D S   --------------------#

    def _set_to_activity(
        self,
        key: str,
        value: Type,
        propagate_value: bool,
        activity: str = None,
        activity_block: str = None,
    ):
        self._validate_key(key)

        # Validate the parameters and set the default values if necessary.
        activity_block = self._set_variable("activity_block", activity_block, self._activity_block)
        activity = self._set_variable("activity", activity, self._activity)

        # Create the dictionary structure all the way to the key location,
        #  if it does not exist, and set the value.
        self._local_context.setdefault(self._ACTIVITY_BLOCKS, {}).setdefault(
            activity_block, {}
        ).setdefault(self._ACTIVITIES, {}).setdefault(activity, {})[key] = value

        if propagate_value:
            self._set_to_activity_block(key=key, value=value, propagate_value=propagate_value)
            self._set_to_flow(key=key, value=value)

    def _set_to_activity_block(
        self, key: str, value: Type, propagate_value: bool, activity_block: str = None
    ):
        self._validate_key(key)

        # Validate the parameters and set the default values if necessary.
        activity_block = self._set_variable("activity_block", activity_block, self._activity_block)

        # Create the dictionary structure all the way to the key location, if it does not exist,
        #  and set the value.
        self._local_context.setdefault(self._ACTIVITY_BLOCKS, {}).setdefault(activity_block, {})[
            key
        ] = value

        if propagate_value:
            self._set_to_flow(key=key, value=value)

    def _set_to_flow(self, key: str, value: Type):
        self._validate_key(key)

        # Create the dictionary structure all the way to the key location, if it does not exist,
        #  and set the value.
        self._local_context[key] = value

    # -------------------------------   P R I V A T E   H E L P   M E T H O D S   -----------------#

    # Return the correct value for the parameter.
    # pylint: disable-next=no-self-use
    def _set_variable(self, name: str, value: str, default_value: str) -> str:

        if value is None:
            if default_value is not None:
                value = default_value
            else:
                raise AutorFrameworkValueException("Missing parameter: '" + name + "'")

        return value

    def _validate_key(self, key):
        if key is None:
            raise AutorFrameworkValueException("The context key may not be None")

        if not isinstance(key, str):
            raise AutorFrameworkValueException(
                "The context key: " + str(key) + "  must be of type 'str'"
            )

        if key in (self._ACTIVITY_BLOCKS, self._ACTIVITIES):
            raise AutorFrameworkValueException(
                "The context key may not use one of the reserved context words: "
                + self._ACTIVITY_BLOCKS
                + " or "
                + self._ACTIVITIES
            )

    # -----------------------------   P R I N T S   -------------------------------#
    # pylint: disable=no-self-use
    def _print(self, text):
        if DebugConfig.trace_context:
            logging.debug(DebugConfig.context_trace_prefix + str(text))

    # pylint: disable=no-self-use
    def _print_set(self, key, value):
        if DebugConfig.trace_context:
            logging.debug(
                "%s set(key: %s, value: %s)", DebugConfig.context_trace_prefix, str(key), str(value)
            )

    def _print_get(self, key, value):
        if DebugConfig.trace_context:
            logging.debug(
                DebugConfig.context_trace_prefix + "fullpath_get(key: " + key + ") -> " + str(value)
            )

    def _print_fullpath_get(self, activity_block=None, activity=None, key=None, value=None):
        if DebugConfig.trace_context:
            path = ""
            if activity_block:
                path = path + activity_block
            if activity:
                path = path + "/" + activity
            if key:
                path = path + "/" + key

            logging.debug(
                DebugConfig.context_trace_prefix + "fullpath_get(" + path + ") -> " + str(value)
            )

    def print_focus(self):
        logging.info(f'focus:          {self._focus}')
        logging.info(f'activity:       {self._activity}')
        logging.info(f'activity_block: {self._activity_block}')

    def get_focus_activity_dict(self):
        value = None
        try:
            value = (
                self.local_context.get(self._ACTIVITY_BLOCKS)
                .get(self._activity_block)
                .get(self._ACTIVITIES)
                .get(self._activity)
            )  # pylint: disable=no-member

        except Exception:
            return {}

        return value

    def get_focus_activity_block_dict(self):
        value = None
        try:
            value = (
                self.local_context.get(self._ACTIVITY_BLOCKS)
                .get(self._activity_block)
            )  # pylint: disable=no-member

        except Exception:
            return {}

        return value


class AutorFrameworkContextKeyNotFoundException(AutorFrameworkException):
    pass
