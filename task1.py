import random
import time
from collections import OrderedDict
from typing import Iterable, List, Sequence, Tuple

Query = Tuple[str, int, int]

class LRUCache:
    def __init__(self, capacity: int = 1000):
        self.capacity = capacity
        self.cache: OrderedDict[tuple[int, int], int] = OrderedDict()

    def get(self, key: tuple[int, int]) -> int:
        if key not in self.cache:
            return -1

        self.cache.move_to_end(key)
        return self.cache[key]

    def put(self, key: tuple[int, int], value: int) -> None:
        if key in self.cache:
            self.cache.move_to_end(key)

        self.cache[key] = value

        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)

cache = LRUCache(capacity=1000)

def range_sum_no_cache(array: Sequence[int], left: int, right: int) -> int:
    return sum(array[left : right + 1])

def update_no_cache(array: List[int], index: int, value: int) -> None:
    array[index] = value

def range_sum_with_cache(array: Sequence[int], left: int, right: int) -> int:
    key = (left, right)
    cached_value = cache.get(key)

    if cached_value != -1:
        return cached_value

    result = sum(array[left : right + 1])
    cache.put(key, result)
    return result

def update_with_cache(array: List[int], index: int, value: int) -> None:
    array[index] = value

    keys_to_remove = [
        key for key in cache.cache.keys() if key[0] <= index <= key[1]
    ]
    for key in keys_to_remove:
        del cache.cache[key]

def make_queries(n, q, hot_pool=30, p_hot=0.95, p_update=0.03):
    hot = [(random.randint(0, n//2), random.randint(n//2, n-1))
           for _ in range(hot_pool)]
    queries = []
    for _ in range(q):
        if random.random() < p_update:        # ~3% запитів — Update
            idx = random.randint(0, n-1)
            val = random.randint(1, 100)
            queries.append(("Update", idx, val))
        else:                                 # ~97% — Range
            if random.random() < p_hot:       # 95% — «гарячі» діапазони
                left, right = random.choice(hot)
            else:                             # 5% — випадкові діапазони
                left = random.randint(0, n-1)
                right = random.randint(left, n-1)
            queries.append(("Range", left, right))
    return queries

def run_no_cache(array: List[int], queries: Iterable[Query]) -> int:
    checksum = 0

    for query_type, first, second in queries:
        if query_type == "Range":
            checksum += range_sum_no_cache(array, first, second)
        else:
            update_no_cache(array, first, second)
    return checksum

def run_with_cache(array: List[int], queries: Iterable[Query]) -> int:
    checksum = 0

    for query_type, first, second in queries:
        if query_type == "Range":
            checksum += range_sum_with_cache(array, first, second)
        else:
            update_with_cache(array, first, second)
    return checksum

def measure_time(func, array: List[int], queries: list[Query]) -> tuple[float, int]:
    started_at = time.perf_counter()
    checksum = func(array, queries)
    elapsed = time.perf_counter() - started_at
    return elapsed, checksum

def main() -> None:
    n = 100_000
    q = 50_000

    random.seed(42)
    source_array = [random.randint(1, 100) for _ in range(n)]
    queries = make_queries(n, q)

    no_cache_array = source_array.copy()
    with_cache_array = source_array.copy()

    global cache
    cache = LRUCache(capacity=1000)

    no_cache_time, no_cache_checksum = measure_time(
        run_no_cache, no_cache_array, queries
    )
    cache_time, cache_checksum = measure_time(
        run_with_cache, with_cache_array, queries
    )

    if no_cache_checksum != cache_checksum:
        raise RuntimeError("Results with and without cache are different")

    speedup = no_cache_time / cache_time if cache_time > 0 else float("inf")

    print("=== Порівняння обробки Range/Update запитів ===")
    print(f"Кількість елементів масиву : {n:,}")
    print(f"Кількість запитів          : {q:,}")
    print(f"Розмір LRU-кешу            : {cache.capacity:,}")
    print()
    print(f"Без кешу : {no_cache_time:7.2f} c")
    print(f"LRU-кеш  : {cache_time:7.2f} c  (прискорення x{speedup:.1f})")

if __name__ == "__main__":
    main()
