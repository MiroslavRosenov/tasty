# This file is used only for database and nothing else.

# fmt: off
from __future__ import annotations

import inspect
import contextlib

from collections import OrderedDict
from functools import partial
from types import MethodType
from typing import Callable, Coroutine, Optional,  Tuple, Union, Dict,  List, Any, overload


# fmt: on

__all__ = ("getter", "setter")

Coro = Coroutine
Cache = OrderedDict


class Base:
    sections: Dict[str, Cache] = {}
    def __init__(self, coro: Coro, section: str):
        if not inspect.iscoroutinefunction(coro):
            raise TypeError("Caching functions must be a coroutine ones.")
        self.coro = coro
        self.section = section
        self.cache: Cache = self.sections.setdefault(section, OrderedDict())

    def __get__(self, instance, owner):
        if not instance:
            return self
        return MethodType(self, instance)  


class Getter(Base):
    @overload
    def __init__(self, coro: Coro, section: str, max_size: Optional[int] = None) -> None: ...

    @overload
    def __init__(self, coro: Coro, section: str, max_size: Optional[int] = None, kwarg: Optional[str] = None) -> None: ...

    @overload
    def __init__(self,coro: Coro, section: str, max_size: Optional[int] = None, kwargs: Optional[List[str]] = None,) -> None: ...

    def __init__(self, coro: Coro, section: str, max_size: Optional[int] = None, raw_kwargs: Union[Tuple[int], str, List[str]] = None,) -> None:
        super().__init__(coro, section)
        self.max_size = max_size
        self.raw_kwargs = raw_kwargs

    async def __call__(self, *args: Any, **kwds: Dict[str, Any]) -> Any:
        if not self.raw_kwargs:
            keys = args[1:], tuple([(k, v) for k, v in kwds.items()])

            if not (result := self.cache.get((self.section, keys))):
                result = await self.coro(*args, **kwds)

                if self.max_size and len(self.cache) - 1 > self.max_size:
                    self.cache.popitem(last=False)

                self.cache[(self.section, keys)] = result
            
            return result
        
        if (arg := self.raw_kwargs.get("include_args")) is not None:
            _args = args[1:][:arg]
        else:
            _args = args[1:]

        if (kwarg := self.raw_kwargs.get("include_kwargs")) is not None:
            if isinstance(kwarg, str):
                kwargs = (kwarg, kwds.get(kwarg))
            elif isinstance(kwarg, List[str]):
                kwargs = tuple([(x, kwds.get(x)) for x in kwarg])
        elif self.raw_kwargs.get("include_args"):
            kwargs = ()
        else:
            kwargs = tuple([(k, v) for k, v in kwds.items()])

        combined = _args, kwargs
        if not (result := self.cache.get((self.section, combined))):
            result = await self.coro(*args, **kwds)

            if self.max_size and len(self.cache) - 1 > self.max_size:
                self.cache.popitem(last=False)

            self.cache[(self.section, combined)] = result
        return result

    async def bypass_call(self, *args, **kwgs):
        """
        Bypass the call function and directly call the coroutine.
        
        Note: the result will not be added to cache.
        """
        return await self.coro(*args, **kwgs)

    def remove(self, *args, **kwargs) -> Any:
        """Remove a key from cache manually."""
        keys = args, tuple([(k, v) for k, v in kwargs.items()])
        
        with contextlib.suppress(KeyError):
            return self.cache.pop((self.section, keys))


@overload 
def getter(section: str, max_size: Optional[int] = None) -> Callable[[Coro], Getter]: ...

@overload
def getter(section: str, max_size: Optional[int] = None, include_args: Optional[int] = None) -> Callable[[Coro], Getter]: ...

@overload
def getter(section: str, max_size: Optional[int] = None, include_kwargs: Optional[str] = None) -> Callable[[Coro], Getter]: ...

@overload
def getter(section: str, max_size: Optional[int] = None, include_kwargs: Optional[List[str]] = None) -> Callable[[Coro], Getter]: ...

def getter(section: str, max_size: Optional[int] = None, **kwargs: Union[Tuple[int, ...], str, List[str], None]) -> Callable[[Coro], Getter]:
    """
    Create a "getter", a function that fetches values from the database
    This decorator is similar to :func:`functools.lru_cache`, but allows setters
    that reset the value of the cache.
    Parameters
    ----------
    section : :class:`str`
        The section to cache the values in.
    max_size : Optional[:class:`int`]
        The maximum number of values to cache. If None, no limit is imposed.
    type_ : Union[Tuple[:class:`int`, `...`], :class:`str`, List[:class:`str`], `None`]
        The way it should store the key in cache.
    """
    return partial(Getter, section=section, max_size=max_size, raw_kwargs=kwargs)

class Setter(Base):
    @overload
    def __init__(self, coro: Coro, section: str) -> None: ...

    @overload
    def __init__(self, coro: Coro, section: str, raw_kwargs: int) -> None: ...

    @overload
    def __init__(self, coro: Coro, section: str, raw_kwargs: str) -> None: ...

    @overload
    def __init__(self, coro: Coro, section: str, raw_kwargs: List[str]) -> None: ...

    def __init__(self, coro: Coro, section: str, raw_kwargs: Optional[Dict[str, Any]]) -> None:
        super().__init__(coro, section)
        self.raw_kwargs = raw_kwargs

    async def __call__(self, *args: Any, **kwds: Dict[str, Any]) -> Any:
        result = await self.coro(*args, **kwds)

        if not self.raw_kwargs:
            keys = args[1:], tuple([(k, v) for k, v in kwds.items()])
            self.cache[(self.section, keys)] = result
            return result
        
        if (arg := self.raw_kwargs.get("include_args")) is not None:
            args = args[1:][:arg]
        else:
            args = args[1:]
            
        if (kwarg := self.raw_kwargs.get("include_kwargs")):
            if isinstance(kwarg, str):
                kwargs = (kwarg, kwds.get(kwarg))
            elif isinstance(kwarg, List[str]):
                kwargs = tuple([(x, kwds.get(x)) for x in kwarg])
        else:
            kwargs = ()
        
        combined = args, kwargs
        self.cache[(self.section, combined)] = result
        return result

@overload
def setter(section: str) -> Callable[[Coro], Setter]:...

@overload
def setter(section: str, include_args: Optional[int] = None) -> Callable[[Coro], Setter]: ...

@overload
def setter(section: str, include_kwargs: Optional[str] = None) -> Callable[[Coro], Setter]: ...

@overload
def setter(section: str, include_kwargs: Optional[List[str]] = None) -> Callable[[Coro], Setter]: ...

def setter(section: str, **kwargs: Union[int, str, List[str]]) -> Callable[[Coro], Setter]:
    """
    Create a "setter", a function that changes values in the database
    This resets the value in the cache.
    Parameters
    ----------
    section : :class:`str`
        The section to reset the value for.
    include_args: :class:`int`
        The first X arguments to take for the call.
    include_kwargs: Union[:class:`str`, :class:`List[str]`] 
        Which kwargs to take for the call
    """
    
    return partial(Setter, section=section, raw_kwargs=kwargs)