import pytest
from optopenhash import ElasticHashTable, FunnelHashTable


def test_elastic_hash_table():
    capacity = 1000
    delta = 0.1
    et = ElasticHashTable(capacity, delta)
    n_insert = capacity - int(delta * capacity)
    for i in range(n_insert):
        if i % 2:
            et.insert(f"key{i}", f"value{i}")
        else:
            et[f"key{i}"] = f"value{i}"
    # Check that inserted keys are found
    for i in range(n_insert):
        if i % 2:
            assert et[f"key{i}"] == f"value{i}"
        else:
            assert et.search(f"key{i}") == f"value{i}"
    # A key that was not inserted should return None
    assert et.search("nonexistent") is None


def test_funnel_hash_table():
    capacity = 1000
    delta = 0.1
    ft = FunnelHashTable(capacity, delta)
    n_insert = capacity - int(delta * capacity)
    for i in range(n_insert):
        if i % 2:
            ft.insert(f"key{i}", f"value{i}")
        else:
            ft[f"key{i}"] = f"value{i}"
    # Check that inserted keys are found
    for i in range(n_insert):
        if i % 2:
            assert ft[f"key{i}"] == f"value{i}"
        else:
            assert ft.search(f"key{i}") == f"value{i}"
    # A key that was not inserted should return None
    assert ft.search("nonexistent") is None


if __name__ == "__main__":
    pytest.main([__file__])
