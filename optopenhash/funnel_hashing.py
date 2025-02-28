import math
import random
import sys

_EMPTY = object()      # Marks an empty slot.
_DELETED = object()    # Marks a deleted entry.
_NOT_FOUND = object()  # Internal "not found" sentinel.


class FunnelHashTable:
    def __init__(self, capacity, delta=0.1):
        if capacity <= 0:
            raise ValueError("Capacity must be positive.")
        if not (0 < delta < 1):
            raise ValueError("delta must be between 0 and 1.")
        self.capacity = capacity
        self.delta = delta
        self.max_inserts = capacity - int(delta * capacity)
        self.num_inserts = 0

        self.alpha = int(math.ceil(4 * math.log2(1 / delta) + 10))
        self.beta = int(math.ceil(2 * math.log2(1 / delta)))

        self.special_size = max(1, int(math.floor(3 * delta * capacity / 4)))
        self.primary_size = capacity - self.special_size

        total_buckets = self.primary_size // self.beta
        a1 = (
            total_buckets / (4 * (1 - (0.75) ** self.alpha))
            if self.alpha > 0
            else total_buckets
        )
        self.levels = []
        self.level_bucket_counts = []
        self.level_salts = []
        remaining_buckets = total_buckets
        for i in range(self.alpha):
            a_i = max(1, int(round(a1 * (0.75) ** i)))
            if remaining_buckets <= 0 or a_i <= 0:
                break
            a_i = min(a_i, remaining_buckets)
            self.level_bucket_counts.append(a_i)
            level_size = a_i * self.beta
            level_array = [_EMPTY] * level_size
            self.levels.append(level_array)
            self.level_salts.append(random.randint(0, sys.maxsize))
            remaining_buckets -= a_i
        if remaining_buckets > 0 and self.levels:
            extra = remaining_buckets * self.beta
            self.levels[-1].extend([_EMPTY] * extra)
            self.level_bucket_counts[-1] += remaining_buckets
            remaining_buckets = 0

        self.special_array = [_EMPTY] * self.special_size
        self.special_salt = random.randint(0, sys.maxsize)
        self.special_occupancy = 0

    def _hash_level(self, key, level_index):
        return hash((key, self.level_salts[level_index])) & 0x7FFFFFFF

    def _hash_special(self, key):
        return hash((key, self.special_salt)) & 0x7FFFFFFF

    def __setitem__(self, key, value):
        self.insert(key, value)

    def insert(self, key, value):
        if self.num_inserts >= self.max_inserts:
            raise RuntimeError(
                "Hash table is full (maximum allowed insertions reached)."
            )
        for i in range(len(self.levels)):
            level = self.levels[i]
            num_buckets = self.level_bucket_counts[i]
            bucket_index = self._hash_level(key, i) % num_buckets
            start = bucket_index * self.beta
            end = start + self.beta
            for idx in range(start, end):
                if level[idx] is _EMPTY or level[idx] is _DELETED:
                    level[idx] = (key, value)
                    self.num_inserts += 1
                    return True
                elif level[idx][0] == key:
                    level[idx] = (key, value)
                    return True
        special = self.special_array
        size = len(special)
        for j in range(size):
            idx = (self._hash_special(key) + j) % size
            if special[idx] is _EMPTY or special[idx] is _DELETED:
                special[idx] = (key, value)
                self.special_occupancy += 1
                self.num_inserts += 1
                return True
            elif special[idx][0] == key:
                special[idx] = (key, value)
                return True
        raise RuntimeError("Special array insertion failed; table is full.")

    def __getitem__(self, key):
        ret = self.search(key)
        if ret is _NOT_FOUND:
            raise KeyError(key)
        return ret

    def get(self, key, default=None):
        ret = self.search(key)
        return ret if ret is not _NOT_FOUND else default

    def pop(self, key, default=_NOT_FOUND):
        for i in range(len(self.levels)):
            level = self.levels[i]
            num_buckets = self.level_bucket_counts[i]
            bucket_index = self._hash_level(key, i) % num_buckets
            start = bucket_index * self.beta
            end = start + self.beta
            for idx in range(start, end):
                entry = level[idx]
                if entry is _EMPTY:
                    break
                if entry is _DELETED:
                    continue
                if entry[0] == key:
                    level[idx] = _DELETED
                    self.num_inserts -= 1
                    return entry[1]
        special = self.special_array
        size = len(special)
        probe_limit = int(max(1, math.ceil(math.log(math.log(self.capacity + 1) + 1))))
        for j in range(probe_limit):
            idx = (self._hash_special(key) + j) % size
            entry = special[idx]
            if entry is _EMPTY:
                break
            if entry is _DELETED:
                continue
            if entry[0] == key:
                special[idx] = _DELETED
                self.num_inserts -= 1
                self.special_occupancy -= 1
                return entry[1]
        idx1 = self._hash_special(key) % size
        idx2 = (self._hash_special(key) + 1) % size
        if (
            special[idx1] is not _EMPTY
            and special[idx1] is not _DELETED
            and special[idx1][0] == key
        ):
            value = special[idx1][1]
            special[idx1] = _DELETED
            self.num_inserts -= 1
            self.special_occupancy -= 1
            return value
        if (
            special[idx2] is not _EMPTY
            and special[idx2] is not _DELETED
            and special[idx2][0] == key
        ):
            value = special[idx2][1]
            special[idx2] = _DELETED
            self.num_inserts -= 1
            self.special_occupancy -= 1
            return value
        if default is _NOT_FOUND:
            raise KeyError(key)
        return default

    def delete(self, key):
        for i in range(len(self.levels)):
            level = self.levels[i]
            num_buckets = self.level_bucket_counts[i]
            bucket_index = self._hash_level(key, i) % num_buckets
            start = bucket_index * self.beta
            end = start + self.beta
            for idx in range(start, end):
                entry = level[idx]
                if entry is _EMPTY:
                    break
                if entry is _DELETED:
                    continue
                if entry[0] == key:
                    level[idx] = _DELETED
                    self.num_inserts -= 1
                    return True
        special = self.special_array
        size = len(special)
        probe_limit = int(max(1, math.ceil(math.log(math.log(self.capacity + 1) + 1))))
        for j in range(probe_limit):
            idx = (self._hash_special(key) + j) % size
            entry = special[idx]
            if entry is _EMPTY:
                break
            if entry is _DELETED:
                continue
            if entry[0] == key:
                special[idx] = _DELETED
                self.num_inserts -= 1
                self.special_occupancy -= 1
                return True
        idx1 = self._hash_special(key) % size
        idx2 = (self._hash_special(key) + 1) % size
        if (
            special[idx1] is not _EMPTY
            and special[idx1] is not _DELETED
            and special[idx1][0] == key
        ):
            special[idx1] = _DELETED
            self.num_inserts -= 1
            self.special_occupancy -= 1
            return True
        if (
            special[idx2] is not _EMPTY
            and special[idx2] is not _DELETED
            and special[idx2][0] == key
        ):
            special[idx2] = _DELETED
            self.num_inserts -= 1
            self.special_occupancy -= 1
            return True
        return False

    def __delitem__(self, key):
        if not self.delete(key):
            raise KeyError(key)

    def search(self, key):
        for i in range(len(self.levels)):
            level = self.levels[i]
            num_buckets = self.level_bucket_counts[i]
            bucket_index = self._hash_level(key, i) % num_buckets
            start = bucket_index * self.beta
            end = start + self.beta
            for idx in range(start, end):
                entry = level[idx]
                if entry is _EMPTY:
                    break
                if entry is _DELETED:
                    continue
                if entry[0] == key:
                    return entry[1]
        special = self.special_array
        size = len(special)
        probe_limit = int(max(1, math.ceil(math.log(math.log(self.capacity + 1) + 1))))
        for j in range(probe_limit):
            idx = (self._hash_special(key) + j) % size
            entry = special[idx]
            if entry is _EMPTY:
                break
            if entry is _DELETED:
                continue
            if entry[0] == key:
                return entry[1]
        idx1 = self._hash_special(key) % size
        idx2 = (self._hash_special(key) + 1) % size
        if (
            special[idx1] is not _EMPTY
            and special[idx1] is not _DELETED
            and special[idx1][0] == key
        ):
            return special[idx1][1]
        if (
            special[idx2] is not _EMPTY
            and special[idx2] is not _DELETED
            and special[idx2][0] == key
        ):
            return special[idx2][1]
        return _NOT_FOUND

    def __contains__(self, key):
        return self.search(key) is not _NOT_FOUND

    def __len__(self):
        return self.num_inserts
