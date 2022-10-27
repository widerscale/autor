from typing import Any, Dict


class Configurable:
    """Base class for configuration entries."""

    def __init__(
        self, name: str, configuration_dict: Dict[str, Any], parent_configuration: Dict[str, Any]
    ) -> None:
        """TODO."""
        self.__name = name
        self.__configuration_dict = configuration_dict
        self.__parent_configuration = parent_configuration
        self.__configuration: Dict[str, Any] = dict()

    @property
    def name(self) -> str:
        """TODO."""
        return self.__name

    @name.setter
    def name(self, name: str) -> None:
        """TODO."""
        self.__name = name

    @property
    def configuration(self) -> Dict[str, Any]:
        """TODO."""
        if self.__configuration is not None:
            return self.__configuration

        configuration = self.__parent_configuration.copy()

        if self.__configuration_dict is not None:
            configuration.update(self.__configuration_dict)

        self.__configuration = configuration
        return self.__configuration
