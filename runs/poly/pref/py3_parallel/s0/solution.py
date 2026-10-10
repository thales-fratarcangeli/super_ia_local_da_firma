from concurrent.futures import ThreadPoolExecutor

def parallel_map(fn, items, workers=4):
    if workers < 1:
        raise ValueError("workers")
    if not items:
        return []
    with ThreadPoolExecutor(max_workers=workers) as ex:
        return list(ex.map(fn, items))
