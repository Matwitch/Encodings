from typing import Callable, List
import time
def counting_sort(arr: List, key: Callable[[List, int], int], key_idx: int) -> List:
    N = len(arr)

    counts = {}
    for i in range(N):
        k = key(arr[i], key_idx)
        if k not in counts:
            counts[k] = []
        counts[k].append(arr[i])
    
    sorted_arr = []
    for bk in sorted(counts.keys()):
        sorted_arr.extend(counts[bk])

    return sorted_arr


def radix_sort(arr: List, key: Callable[[List, int], int]) -> List:
    N = len(arr)
    
    N_active_keys = N
    max_key_idx = -1
    while N_active_keys > 0:
        max_key_idx += 1
        N_active_keys = 0

        for i in range(N):
            try:
                _ = key(arr[i], max_key_idx) 
                N_active_keys += 1
            except IndexError:
                continue
                
    max_key_idx -= 1

    def safe_key(item, key_idx):
        try:
            k = key(item, key_idx) + 1
        except IndexError:
            k =  0

        return k

    sorted_arr = arr.copy()
    for key_idx in range(max_key_idx, -1, -1):
        sorted_arr = counting_sort(sorted_arr, safe_key, key_idx)

    return sorted_arr