def two_sum(nums, target):
    seen = {}
    for j, v in enumerate(nums):
        if target - v in seen:
            return (seen[target - v], j)
        seen.setdefault(v, j)
    return None
