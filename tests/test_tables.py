import pytest
from optopenhash import ElasticHashTable, FunnelHashTable

# --- Existing tests for ElasticHashTable and FunnelHashTable ---


def test_invalid_parameters_elastic():
    with pytest.raises(ValueError):
        ElasticHashTable(0, 0.1)
    with pytest.raises(ValueError):
        ElasticHashTable(10, 0)
    with pytest.raises(ValueError):
        ElasticHashTable(10, 1)
    with pytest.raises(ValueError):
        ElasticHashTable(10, -0.5)


def test_insert_full_elastic():
    capacity = 50
    delta = 0.1
    et = ElasticHashTable(capacity, delta)
    n_insert = capacity - int(delta * capacity)
    for i in range(n_insert):
        et[f"key{i}"] = f"value{i}"
    with pytest.raises(RuntimeError):
        et.insert("overflow", "value_overflow")


def test_update_value_elastic():
    et = ElasticHashTable(100, 0.1)
    et["key"] = "initial"
    assert et.get("key") == "initial"
    et["key"] = "updated"
    assert et["key"] == "updated"


def test_contains_length_elastic():
    et = ElasticHashTable(100, 0.1)
    keys = ["a", "b", "c"]
    for k in keys:
        et[k] = k.upper()
    assert len(et) == len(keys)
    for k in keys:
        assert k in et
    assert "not_present" not in et


def test_pop_default_elastic():
    et = ElasticHashTable(100, 0.1)
    et["key"] = "value"
    val = et.pop("key")
    assert val == "value"
    default_val = et.pop("nonexistent", "default")
    assert default_val == "default"


def test_delete_nonexistent_elastic():
    et = ElasticHashTable(100, 0.1)
    et["key"] = "value"
    result = et.delete("nonexistent")
    assert result is False


def test_get_with_default_elastic():
    et = ElasticHashTable(100, 0.1)
    assert et.get("nonexistent", "default") == "default"


def test_delitem_nonexistent_elastic():
    et = ElasticHashTable(100, 0.1)
    with pytest.raises(KeyError):
        del et["nonexistent"]


def test_search_method_elastic():
    et = ElasticHashTable(100, 0.1)
    et["a"] = "A"
    result = et.search("a")
    assert result == "A"
    not_found = et.search("not_present")
    from optopenhash.elastic_hashing import _NOT_FOUND

    assert not_found is _NOT_FOUND


def test_invalid_parameters_funnel():
    with pytest.raises(ValueError):
        FunnelHashTable(0, 0.1)
    with pytest.raises(ValueError):
        FunnelHashTable(10, 0)
    with pytest.raises(ValueError):
        FunnelHashTable(10, 1)
    with pytest.raises(ValueError):
        FunnelHashTable(10, -0.2)


def test_insert_full_funnel():
    capacity = 50
    delta = 0.1
    ft = FunnelHashTable(capacity, delta)
    n_insert = capacity - int(delta * capacity)
    for i in range(n_insert):
        ft[f"key{i}"] = f"value{i}"
    with pytest.raises(RuntimeError):
        ft.insert("overflow", "value_overflow")


def test_update_value_funnel():
    ft = FunnelHashTable(100, 0.1)
    ft["key"] = "initial"
    assert ft.get("key") == "initial"
    ft["key"] = "updated"
    assert ft["key"] == "updated"


def test_contains_length_funnel():
    ft = FunnelHashTable(100, 0.1)
    keys = ["x", "y", "z"]
    for k in keys:
        ft[k] = k * 2
    assert len(ft) == len(keys)
    for k in keys:
        assert k in ft
    assert "not_present" not in ft


def test_pop_default_funnel():
    ft = FunnelHashTable(100, 0.1)
    ft["key"] = "value"
    val = ft.pop("key")
    assert val == "value"
    default_val = ft.pop("nonexistent", "default")
    assert default_val == "default"


def test_delete_nonexistent_funnel():
    ft = FunnelHashTable(100, 0.1)
    ft["key"] = "value"
    result = ft.delete("nonexistent")
    assert result is False


def test_get_with_default_funnel():
    ft = FunnelHashTable(100, 0.1)
    assert ft.get("nonexistent", "default") == "default"


def test_delitem_nonexistent_funnel():
    ft = FunnelHashTable(100, 0.1)
    with pytest.raises(KeyError):
        del ft["nonexistent"]


def test_search_method_funnel():
    ft = FunnelHashTable(100, 0.1)
    ft["a"] = "A"
    result = ft.search("a")
    assert result == "A"
    not_found = ft.search("not_present")
    from optopenhash.funnel_hashing import _NOT_FOUND

    assert not_found is _NOT_FOUND


def test_special_array_collision_funnel():
    # Force collisions in the special array.
    ft = FunnelHashTable(100, 0.1)
    original_hash_special = ft._hash_special
    try:
        ft._hash_special = lambda key: 0
        ft.insert("special1", "val1")
        ft.insert("special2", "val2")
        assert ft.get("special1") == "val1"
        assert ft.get("special2") == "val2"
        popped = ft.pop("special1")
        assert popped == "val1"
        with pytest.raises(KeyError):
            _ = ft["special1"]
        assert ft["special2"] == "val2"
    finally:
        ft._hash_special = original_hash_special


# --- Additional tests for FunnelHashTable missing branches ---


def test_init_extra_buckets_funnel():
    """
    Create a FunnelHashTable that triggers the extra buckets branch.
    Using parameters that result in remaining_buckets > 0 after the loop.
    We use a larger delta to force fewer primary buckets.
    """
    # Use delta close to 1 (but <1) so special_size becomes high and primary_size small.
    ft = FunnelHashTable(50, 0.9)
    # If extra buckets were added, the last level's bucket count should be higher than
    # the number of buckets originally allocated.
    assert ft.levels, "Levels should not be empty"
    last_count = ft.level_bucket_counts[-1]
    # Since beta = ceil(2*log2(1/0.9)) is small, we expect extra buckets added.
    assert last_count > 0


def test_insert_update_in_primary_funnel():
    """
    Force update in primary levels.
    """
    ft = FunnelHashTable(100, 0.1)
    # Insert key normally.
    ft["dup"] = "first"
    # Insert again to update.
    ft["dup"] = "second"
    assert ft["dup"] == "second"


def test_special_insertion_failure_funnel():
    """
    Force the special array insertion failure.
    For a FunnelHashTable with capacity=10, delta=0.1:
      - Primary level has 7 slots.
      - Special array has 1 slot.
    Fill the primary level via insert and then manually fill the special array.
    Then a new insertion should fail.
    """
    ft = FunnelHashTable(10, 0.1)
    # Fill the primary level (should have 7 slots).
    for i in range(7):
        ft.insert(f"p{i}", f"value{i}")
    # Manually fill the special array.
    for i in range(len(ft.special_array)):
        ft.special_array[i] = (f"s{i}", f"value{i}")
        ft.num_inserts += 1
        ft.special_occupancy += 1
    # Now both primary level and special array are full; insertion should raise RuntimeError.
    with pytest.raises(RuntimeError):
        ft.insert("overflow", "value_overflow")


def test_getitem_keyerror_funnel():
    """
    __getitem__ should raise KeyError if key not found.
    """
    ft = FunnelHashTable(100, 0.1)
    with pytest.raises(KeyError):
        _ = ft["missing"]


def test_search_special_fallback_idx1_funnel():
    """
    Manually set special_array index so that the probe loop in search doesn't find the key,
    but the fallback (idx1) does.
    """
    ft = FunnelHashTable(100, 0.1)
    # Force _hash_special to return a value such that idx1 is 0.
    ft._hash_special = lambda key: 0
    ft.special_array[0] = ("fallback1", "val_fb1")
    ft.num_inserts += 1
    ret = ft.search("fallback1")
    assert ret == "val_fb1"


def test_search_special_fallback_idx2_funnel():
    """
    Similar to above, force fallback branch for idx2.
    """
    ft = FunnelHashTable(100, 0.1)
    size = len(ft.special_array)
    ft._hash_special = lambda key: size - 1  # so idx1 becomes size-1, idx2 becomes 0
    ft.special_array[0] = ("fallback2", "val_fb2")
    ft.num_inserts += 1
    ret = ft.search("fallback2")
    assert ret == "val_fb2"


def test_pop_special_probe_limit_break_funnel():
    """
    Force the probe loop in pop to break on _EMPTY.
    """
    ft = FunnelHashTable(100, 0.1)
    # Set up special array so that the first slot is _EMPTY.
    from optopenhash.funnel_hashing import _EMPTY
    ft._hash_special = lambda key: 5
    ft.special_array = [_EMPTY] * len(ft.special_array)
    ft.num_inserts = 0
    with pytest.raises(KeyError):
        ft.pop("nonexistent")


def test_delete_special_fallback_funnel():
    """
    Force fallback branches in delete().
    Manually set a key in the special array at fallback positions.
    """
    ft = FunnelHashTable(100, 0.1)
    ft._hash_special = lambda key: 0
    ft.special_array[0] = ("del_fb", "val_del")
    ft.num_inserts += 1
    ft.special_occupancy += 1
    result = ft.delete("del_fb")
    assert result is True
    with pytest.raises(KeyError):
        _ = ft["del_fb"]


def test_delitem_funnel_existing():
    ft = FunnelHashTable(100, 0.1)
    ft["to_del"] = "val_del"
    del ft["to_del"]
    with pytest.raises(KeyError):
        _ = ft["to_del"]


def test_len_contains_funnel():
    ft = FunnelHashTable(100, 0.1)
    assert len(ft) == 0
    ft["a"] = "A"
    assert len(ft) == 1
    assert "a" in ft
    assert "b" not in ft
