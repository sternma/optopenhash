import pytest
from optopenhash import ElasticHashTable, FunnelHashTable


def test_elastic_hash_table():
    capacity = 1000
    delta = 0.1
    et = ElasticHashTable(capacity, delta)
    n_insert = capacity - int(delta * capacity)
    for i in range(n_insert):
        et.insert(f"key{i}", f"value{i}")
    # Check that inserted keys are found
    for i in range(n_insert):
        assert et.search(f"key{i}") == f"value{i}"
    # A key that was not inserted should return None
    assert et.search("nonexistent") is None


def test_funnel_hash_table():
    capacity = 1000
    delta = 0.1
    ft = FunnelHashTable(capacity, delta)
    n_insert = capacity - int(delta * capacity)
    for i in range(n_insert):
        ft.insert(f"key{i}", f"value{i}")
    # Check that inserted keys are found
    for i in range(n_insert):
        assert ft.search(f"key{i}") == f"value{i}"
    # A key that was not inserted should return None
    assert ft.search("nonexistent") is None


if __name__ == "__main__":
    pytest.main([__file__])
