# OptOpenHash

This package implements two new open‐addressing hash tables inspired by the research paper

> **Optimal Bounds for Open Addressing Without Reordering**  
> Martín Farach‐Colton, Andrew Krapivin, William Kuszmaul  
> [Link](https://arxiv.org/pdf/2501.02305)

In this implementation I provide:

- **ElasticHashTable** – an “elastic hashing” table that partitions the table into levels (arrays) of geometrically decreasing size and uses a non‐greedy (i.e. “elastic”) insertion strategy.
- **FunnelHashTable** – a greedy open‐addressing table that partitions the table into multiple “funnel” levels (with each level subdivided into buckets) and falls back on a special “overflow” array.

Both tables support `insert(key, value)` and `search(key)` operations (as well as Python’s “in” and `len()`).

## Installation

Install via pip:
```
pip install optopenhash
```

Clone the repository and install via pip:

```
bash
git clone https://github.com/sternma/optopenhash.git
cd optopenhash
pip install .

```

## Usage

```
from optopenhash import ElasticHashTable, FunnelHashTable

# Create a table with capacity 1000 and delta = 0.1 (so up to 900 insertions)
etable = ElasticHashTable(capacity=1000, delta=0.1)
fhtable = FunnelHashTable(capacity=1000, delta=0.1)

# Insert some key-value pairs
for i in range(800):
    etable.insert(f"key{i}", f"value{i}")
    fhtable.insert(f"key{i}", f"value{i}")

# Search for a key
print(etable.search("key123"))
print(fhtable.search("key123"))
```

## Testing

A basic test suite is provided in the `tests` directory. To run the tests use:
```
pytest tests
```

