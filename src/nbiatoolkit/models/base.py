from abc import ABC
from datetime import datetime
from typing import Any, Callable, Dict, Generic, List, Optional, Type, TypeVar, Union

from pandas import DataFrame
from pydantic import BaseModel, Field

T = TypeVar("T", bound="AbstractModel")


class AbstractModel(BaseModel, ABC):
    """
    Abstract base model for common functionality across all models.
    """

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the model instance to a dictionary.
        """
        return self.model_dump(by_alias=True)

    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        """
        Creates a model instance from a dictionary.
        """
        return cls(**data)

    @classmethod
    def from_dicts(cls: Type[T], data: List[Dict[str, Any]]) -> List[T]:
        """
        Creates a list of model instances from a list of dictionaries.
        """
        return [cls.from_dict(item) for item in data]

    @staticmethod
    def convert_date(input_date: Union[str, datetime]) -> datetime:
        """
        Converts the input date to a datetime object.
        """
        possible_formats = [
            "%Y-%m-%d",
            "%Y/%m/%d",
            "%Y%m%d",
            "%m/%d/%Y",
            "%d/%m/%Y",
            "%d-%m-%Y",
            "%Y-%m-%d %H:%M:%S.%f",
        ]
        if isinstance(input_date, datetime):
            return input_date
        for date_format in possible_formats:
            try:
                return datetime.strptime(input_date, date_format)
            except ValueError:
                continue
        msg = f"Invalid date format: {input_date}"
        raise ValueError(msg)


M = TypeVar("M", bound=AbstractModel)


class AbstractListModel(BaseModel, Generic[M]):
    """
    Abstract base class for list models.
    """

    items: List[M] = Field(default_factory=list)

    __key__: Optional[str] = None

    @property
    def df(self) -> DataFrame:
        """
        Converts the list of models to a pandas DataFrame.
        """
        return DataFrame([item.to_dict() for item in self.items])

    @property
    def keys(self) -> List[str]:
        """
        Returns a list of keys for the items in the list.
        """
        if not self.__key__:
            msg = "Key attribute `__key__` not set for the list model."
            raise AttributeError(msg)
        return [getattr(item, self.__key__) for item in self.items]

    def filter(
        self, condition: Optional[Callable[[M], bool]] = None
    ) -> "AbstractListModel[M]":
        """
        Filters the models in the list based on a condition function.

        Args:
            condition (Callable[[M], bool]): A function that returns True for items to keep.

        Returns:
            AbstractListModel[M]: A new instance of the model list containing filtered items.
        """
        if not condition:
            return self
        filtered_items = [item for item in self.items if condition(item)]
        return self.__class__(items=filtered_items)

    def __getitem__(self, index: Union[int, str]) -> M:
        """
        Access an item by index or by the value of the key attribute.

        Args:
            index (Union[int, str]): The index of the item or the key value.

        Returns:
            M: The item at the specified index or matching the key value.
        """
        if isinstance(index, int):
            return self.items[index]
        if isinstance(index, str) and self.__key__:
            for item in self.items:
                if getattr(item, self.__key__) == index:
                    return item
            msg = f"No item found with {self.__key__}='{index}'"
            raise KeyError(msg)
        msg = "Index must be an integer or a string representing the key value."
        raise TypeError(
            msg
        )

    def __len__(self) -> int:
        """
        Returns the number of items in the list.

        Returns:
            int: The number of items.
        """
        return len(self.items)

    def __contains__(self, item: M) -> bool:
        """
        Checks if an item is in the list.
        """
        return item in self.items
