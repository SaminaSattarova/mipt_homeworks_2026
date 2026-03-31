from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, TypeVar

from part4_oop.interfaces import Cache, HasCache, Policy, Storage

K = TypeVar("K")
V = TypeVar("V")


@dataclass
class DictStorage(Storage[K, V]):
    _data: dict[K, V] = field(default_factory=dict, init=False)

    def set(self, key: K, value: V) -> None:
        self._data[key] = value

    def get(self, key: K) -> V | None:
        if self.exists(key):
            return self._data[key]
        return None

    def exists(self, key: K) -> bool:
        return key in self._data

    def remove(self, key: K) -> None:
        if self.exists(key):
            del self._data[key]

    def clear(self) -> None:
        self._data = {}


@dataclass
class FIFOPolicy(Policy[K]):
    capacity: int = 5
    _order: list[K] = field(default_factory=list, init=False)

    def __init__(self, capacity: int = 5):
        self.capacity = capacity
        self._order = []

    def register_access(self, key: K) -> None:
        if key not in self._order:
            self._order.append(key)

    def get_key_to_evict(self) -> K | None:
        if len(self._order) >= self.capacity:
            return self._order[0]
        return None

    def remove_key(self, key: K) -> None:
        if key in self._order:
            self._order.remove(key)

    def clear(self) -> None:
        self._order = []

    @property
    def has_keys(self) -> bool:
        return len(self._order) != 0


@dataclass
class LRUPolicy(Policy[K]):
    capacity: int = 5
    _order: list[K] = field(default_factory=list, init=False)

    def __init__(self, capacity: int = 5):
        self.capacity = capacity
        self._order = []

    def register_access(self, key: K) -> None:
        if key in self._order:
            self._order.remove(key)
        self._order.append(key)

    def get_key_to_evict(self) -> K | None:
        if len(self._order) >= self.capacity:
            return self._order[0]
        return None

    def remove_key(self, key: K) -> None:
        if key in self._order:
            self._order.remove(key)

    def clear(self) -> None:
        self._order = []

    @property
    def has_keys(self) -> bool:
        return len(self._order) != 0


@dataclass
class LFUPolicy(Policy[K]):
    capacity: int = 5
    _key_counter: dict[K, int] = field(default_factory=dict, init=False)

    def __init__(self, capacity: int = 5):
        self.capacity = capacity
        self._key_counter = {}
        self._last: K | None = None

    def register_access(self, key: K) -> None:
        if self._key_counter.get(key) is None:
            self._key_counter[key] = 1
            self._last = key
        else:
            self._key_counter[key] += 1
            self._last = None

    def get_key_to_evict(self) -> K | None:
        remove_key: K | None = None
        remove_count = 100000
        if len(self._key_counter) >= self.capacity:
            for key, count in self._key_counter.items():
                if key == self._last:
                    continue
                if count < remove_count:
                    remove_key = key
                    remove_count = count
            return remove_key
        return None

    def remove_key(self, key: K) -> None:
        if key in self._key_counter:
            self._key_counter.pop(key, None)
        if key == self._last:
            self._last = None

    def clear(self) -> None:
        self._key_counter = {}
        self._last = None

    @property
    def has_keys(self) -> bool:
        return len(self._key_counter) != 0


class MIPTCache(Cache[K, V]):
    def __init__(self, storage: Storage[K, V], policy: Policy[K]) -> None:
        self.storage = storage
        self.policy = policy

    def set(self, key: K, value: V) -> None:
        value_key = self.policy.get_key_to_evict()
        if value_key is not None:
            self.policy.remove_key(value_key)
            self.storage.remove(value_key)
        self.storage.set(key, value)
        self.policy.register_access(key)

    def get(self, key: K) -> V | None:
        self.policy.register_access(key)
        if self.storage.exists(key):
            return self.storage.get(key)
        return None

    def exists(self, key: K) -> bool:
        return self.storage.exists(key)

    def remove(self, key: K) -> None:
        self.storage.remove(key)
        self.policy.remove_key(key)

    def clear(self) -> None:
        self.storage.clear()
        self.policy.clear()


class CachedProperty[V]:
    def __init__(self, func: Callable[..., V]) -> None:
        self.func = func

    def __get__(self, instance: HasCache[Any, Any] | None, owner: type) -> V:
        if instance is None:
            return self  # type: ignore[return-value]
        if instance.cache.exists(self.func.__name__) is not None:
            return instance.cache.get(self.func.__name__)  # type: ignore[return-value]
        value = self.func(instance)
        instance.cache.set(self.func.__name__, value)
        return value
