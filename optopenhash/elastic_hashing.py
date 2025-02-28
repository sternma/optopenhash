import math
import random
import sys

_EMPTY = object()  # Marks an empty slot.
_DELETED = object()  # Marks a deleted entry.
_NOT_FOUND = object()  # Indicates "not found" internally.


class ElasticHashTable:
    def __init__(self, capacity, delta=0.1):
        if capacity <= 0:
            raise ValueError("Capacity must be positive.")
        if not (0 < delta < 1):
            raise ValueError("delta must be between 0 and 1.")
        self.capacity = capacity
        self.delta = delta
        self.max_inserts = capacity - int(delta * capacity)
        self.num_inserts = 0

        num_levels = max(1, math.floor(math.log2(capacity)))
        sizes = []
        remaining = capacity
        for i in range(num_levels - 1):
            size = max(1, remaining // (2 ** (num_levels - i)))
            sizes.append(size)
            remaining -= size
        sizes.append(remaining)
        self.levels = [[_EMPTY] * s for s in sizes]
        self.salts = [random.randint(0, sys.maxsize) for _ in range(num_levels)]
        self.occupancies = [0] * num_levels
        self.c = 4

    def _hash(self, key, level):
        return hash((key, self.salts[level])) & 0x7FFFFFFF

    def _quad_probe(self, key, level, j, table_size):
        # Returns the index for the j-th quadratic probe.
        return (self._hash(key, level) + j * j) % table_size

    def __setitem__(self, key, value):
        self.insert(key, value)

    def insert(self, key, value):
        if self.num_inserts >= self.max_inserts:
            raise RuntimeError(
                "Hash table is full (maximum allowed insertions reached)."
            )
        for i, level in enumerate(self.levels):
            size = len(level)
            occ = self.occupancies[i]
            free = size - occ
            load = free / size if size > 0 else 0

            # For non-last levels, decide how many probes to do.
            if i < len(self.levels) - 1:
                next_level = self.levels[i + 1]
                next_occ = self.occupancies[i + 1]
                next_free = len(next_level) - next_occ
                load_next = (next_free / len(next_level)) if len(next_level) > 0 else 0
                threshold = 0.25
                if load > (self.delta / 2) and load_next > threshold:
                    probe_limit = int(
                        max(
                            1,
                            self.c
                            * min(
                                math.log2(1 / load) if load > 0 else 0,
                                math.log2(1 / self.delta),
                            ),
                        )
                    )
                else:
                    # Instead of skipping this level, scan the entire level so we can update if needed.
                    probe_limit = size
            else:
                probe_limit = size  # Last level: always scan entire level

            candidate = None  # index of a _DELETED slot (if any)
            empty_idx = None  # index of the first _EMPTY slot encountered
            for j in range(probe_limit):
                idx = self._quad_probe(key, i, j, size)
                slot = level[idx]
                # If the slot holds a valid entry, update if keys match.
                if slot is not _EMPTY and slot is not _DELETED:
                    if slot[0] == key:
                        level[idx] = (key, value)
                        return True
                else:
                    # Remember a candidate slot if it is marked _DELETED.
                    if slot is _DELETED and candidate is None:
                        candidate = idx
                    # If we hit an empty slot, we can stop probing.
                    if slot is _EMPTY:
                        empty_idx = idx
                        break

            # If we didn't hit an _EMPTY in the initial probe, scan the remainder of the level.
            if candidate is None and empty_idx is None:
                for j in range(probe_limit, size):
                    idx = self._quad_probe(key, i, j, size)
                    slot = level[idx]
                    if slot is _EMPTY or slot is _DELETED:
                        empty_idx = idx
                        break

            # Decide where to insert: use the candidate (_DELETED) if available,
            # otherwise the first _EMPTY slot found.
            if candidate is not None:
                idx = candidate
            elif empty_idx is not None:
                idx = empty_idx
            else:
                # No available slot in this level; try the next level.
                continue

            level[idx] = (key, value)
            self.occupancies[i] += 1
            self.num_inserts += 1
            return True

        raise RuntimeError("Insertion failed in all levels; hash table is full.")

    def _search_internal(self, key):
        for i, level in enumerate(self.levels):
            size = len(level)
            for j in range(size):
                idx = self._quad_probe(key, i, j, size)
                entry = level[idx]
                if entry is _EMPTY:
                    break
                if entry is _DELETED:
                    continue
                if entry[0] == key:
                    return True, entry[1]
        return False, _NOT_FOUND

    def __getitem__(self, key):
        found, value = self._search_internal(key)
        if not found:
            raise KeyError(key)
        return value

    def get(self, key, default=None):
        found, value = self._search_internal(key)
        return value if found else default

    def pop(self, key, default=_NOT_FOUND):
        for i, level in enumerate(self.levels):
            size = len(level)
            for j in range(size):
                idx = self._quad_probe(key, i, j, size)
                entry = level[idx]
                if entry is _EMPTY:
                    break
                if entry is _DELETED:
                    continue
                if entry[0] == key:
                    level[idx] = _DELETED
                    self.occupancies[i] -= 1
                    self.num_inserts -= 1
                    return entry[1]
        if default is _NOT_FOUND:
            raise KeyError(key)
        return default

    def delete(self, key):
        for i, level in enumerate(self.levels):
            size = len(level)
            for j in range(size):
                idx = self._quad_probe(key, i, j, size)
                entry = level[idx]
                if entry is _EMPTY:
                    break
                if entry is _DELETED:
                    continue
                if entry[0] == key:
                    level[idx] = _DELETED
                    self.occupancies[i] -= 1
                    self.num_inserts -= 1
                    return True
        return False

    def __delitem__(self, key):
        if not self.delete(key):
            raise KeyError(key)

    def search(self, key):
        found, value = self._search_internal(key)
        return value if found else _NOT_FOUND

    def __contains__(self, key):
        found, _ = self._search_internal(key)
        return found

    def __len__(self):
        return self.num_inserts
